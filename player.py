import gi
gi.require_version('Gst', '1.0')
from gi.repository import GObject, Gst, GLib
from threading import Thread

DEBUG = True

def debug(str, end='\n'):
    if not DEBUG:
        return
    print(str, end=end)

class Player:
    """
    Use GStreamer to play audio, handles network issues and
    broken streams much more elegently
    """

    def __init__(self):
        Gst.init(None)
        self._pipe = None
        self._thread = None
        self._is_live = False
        self._tags = {}

    def decode_src_created(self, element, new_pad, data):
        debug("Received new pad '{0}' from '{1}'".format(
            new_pad.get_name(), element.get_name()))

        if new_pad.is_linked():
            debug("  We are already linked. Ignoring.")
            return None

        new_pad_type = new_pad.query_caps(None).to_string()
        if not new_pad_type.startswith("audio/x-raw"):
            debug("  It has type '{0}' which is not raw audio. Ignoring.".format(
                new_pad_type))
            return None

        audiopad = data.get_static_pad('sink')
        ret = new_pad.link(audiopad)
        if ret is not Gst.PadLinkReturn.OK:
            debug("  Failed to link pad: {0}".format(ret))

    def handle_message(self, bus, message):
        if message.type == Gst.MessageType.EOS:
            # this shouldn't happen with our internet radio streams..
            debug("End-of-stream")
            return False
        elif message.type == Gst.MessageType.BUFFERING:
            percent = message.parse_buffering()
            debug("Buffering {0}%   ".format(percent), '\r')

            # don't try to pause/resume for live streams, will fail
            if not self._is_live:
                # wait until buffering is complete before start/resume playing
                if (percent < 100):
                    debug("Pausing, waiting for data")
                    self._pipe.set_state(Gst.State.PAUSED)
                else:
                    debug("Resuming")
                    self._pipe.set_state(Gst.State.PLAYING)
        elif message.type == Gst.MessageType.CLOCK_LOST:
            debug("Lost clock, recovering stream")
            self._pipe.set_state(Gst.State.PAUSED)
            self._pipe.set_state(Gst.State.PLAYING)
        elif message.type == Gst.MessageType.STATE_CHANGED:
            if message.src.get_name() == 'pipeline':
                old_state, new_state, pending_state = message.parse_state_changed()
                debug("Pipeline changed from {0} to {1}.".format(
                    old_state.value_nick, new_state.value_nick))
        elif message.type == Gst.MessageType.TAG:
            tag_list = message.parse_tag()
            for n in range(tag_list.n_tags()):
                tag = str(tag_list.nth_tag_name(n))
                for i in range(tag_list.get_tag_size(tag)):
                    value = str(tag_list.get_value_index(tag, i))
                    if tag not in self._tags or self._tags[tag] != value:
                        self._tags[tag] = value
                        debug("{0}: {1}".format(tag, value))
        elif message.type == Gst.MessageType.WARNING:
            err, msg = message.parse_warning()
            debug("Warning: {0}: {1}".format(err, msg))
        elif message.type == Gst.MessageType.ERROR:
            err, msg = message.parse_error()
            debug("Error: {0}: {1}".format(err, msg))
            return False
        return True

    def create_pipeline(self, uri, is_live=False):
        # valid uri only, not filename
        debug("Attempting to play {0}".format(uri))
        self._is_live = is_live

        pipe = Gst.Pipeline.new('pipeline')

        audio = Gst.Bin.new('audiobin')

        queue = Gst.ElementFactory.make('queue', 'queue')
        audio.add(queue)
        audiopad = queue.get_static_pad('sink')
        ghost = Gst.GhostPad.new('sink', audiopad)
        audio.add_pad(ghost)

        convert = Gst.ElementFactory.make('audioconvert', 'aconv')
        audio.add(convert)
        queue.link(convert)

        sink = Gst.ElementFactory.make('autoaudiosink')
        audio.add(sink)
        convert.link(sink)

        pipe.add(audio)

        src = Gst.ElementFactory.make('souphttpsrc', 'source')
        src.set_property('is-live', self._is_live)
        src.set_property('location', uri)
        pipe.add(src)

        queue = Gst.ElementFactory.make('queue2', 'queue')
        queue.set_property("use-buffering", True)
        pipe.add(queue)
        src.link(queue)

        decode = Gst.ElementFactory.make('decodebin', 'decoder')
        decode.connect("pad-added", self.decode_src_created, audio)
        pipe.add(decode)
        queue.link(decode)

        # start play back and listed to events
        ret = pipe.set_state(Gst.State.PLAYING)
        if ret == Gst.StateChangeReturn.FAILURE:
            debug("Unable to set the pipeline to the playing state")
            return False
        elif ret == Gst.StateChangeReturn.NO_PREROLL:
            debug("Stream is live")
            self._is_live = True

        self._running = True
        self._pipe = pipe
        self._thread = Thread(target=self._process_loop)
        self._thread.start()
        return True

    def _process_loop(self):
        bus = self._pipe.get_bus()
        while self._running: # need some sync
            message = bus.timed_pop(100 * Gst.MSECOND)
            if message is not None:
                if not self.handle_message(bus, message):
                    break

        # handle stream ending..?

    def destroy_pipeline(self):
        if self._pipe is not None:
            debug("Stopping pipeline")
            self._pipe.set_state(Gst.State.NULL)
            self._running = False
            self._thread.join()
            self._pipe = None

    @property
    def playing(self):        
        return self._pipe is not None and self._pipe.get_state(0) == Gst.State.PLAYING
