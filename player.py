import gi
gi.require_version('Gst', '1.0')
from gi.repository import GObject, Gst, GLib
from threading import Thread
import logging

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
        logging.debug("Received new pad '{0}' from '{1}'".format(
            new_pad.get_name(), element.get_name()))

        if new_pad.is_linked():
            logging.debug("  We are already linked. Ignoring.")
            return None

        new_pad_type = new_pad.query_caps(None).to_string()
        if not new_pad_type.startswith("audio/x-raw"):
            logging.debug("  It has type '{0}' which is not raw audio. Ignoring.".format(
                new_pad_type))
            return None

        audiopad = data.get_static_pad('sink')
        ret = new_pad.link(audiopad)
        if ret is not Gst.PadLinkReturn.OK:
            logging.warning("  Failed to link pad: {0}".format(ret))
            # todo: how to handle this??

    def handle_message(self, bus, message):
        if message.type == Gst.MessageType.EOS:
            # this shouldn't happen with our internet radio streams..
            logging.warning("End-of-stream occurred, shouldn't happen with live stream")
            return False
        elif message.type == Gst.MessageType.BUFFERING:
            percent = message.parse_buffering()
            logging.debug("Buffering {0}%   ".format(percent))
            # todo: callback to let user know we're buffering

            # don't try to pause/resume for live streams, will fail
            if not self._is_live:
                # wait until buffering is complete before start/resume playing
                if (percent < 100):
                    logging.debug("Pausing, waiting for data")
                    self._pipe.set_state(Gst.State.PAUSED)
                else:
                    logging.debug("Resuming")
                    self._pipe.set_state(Gst.State.PLAYING)
        elif message.type == Gst.MessageType.CLOCK_LOST:
            logging.debug("Lost clock, recovering stream")
            self._pipe.set_state(Gst.State.PAUSED)
            self._pipe.set_state(Gst.State.PLAYING)
        elif message.type == Gst.MessageType.STATE_CHANGED:
            if message.src.get_name() == 'pipeline':
                old_state, new_state, pending_state = message.parse_state_changed()
                logging.debug("Pipeline changed from {0} to {1}.".format(
                    old_state.value_nick, new_state.value_nick))
        elif message.type == Gst.MessageType.TAG:
            tag_list = message.parse_tag()
            for n in range(tag_list.n_tags()):
                tag = str(tag_list.nth_tag_name(n))
                for i in range(tag_list.get_tag_size(tag)):
                    value = str(tag_list.get_value_index(tag, i))
                    if tag not in self._tags or self._tags[tag] != value:
                        self._tags[tag] = value
                        logging.debug("{0}: {1}".format(tag, value))
                        # todo: callback to update UX 
        elif message.type == Gst.MessageType.WARNING:
            err, msg = message.parse_warning()
            logging.warning("Warning: {0}: {1}".format(err, msg))
        elif message.type == Gst.MessageType.ERROR:
            err, msg = message.parse_error()
            logging.warning("Error: {0}: {1}".format(err, msg))
            # todo: not sure when this happens, but need to handle it?
            return False
        return True

    def create_pipeline(self, uri, is_live=False):
        # valid uri only, not filename
        logging.debug("Attempting to play {0}".format(uri))
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

        # todo: should split out all the .add to a for in [] to handle None response
        # todo: don't think that .link can fail until pipeline starts, but should handle

        # start play back and listed to events
        ret = pipe.set_state(Gst.State.PLAYING)
        if ret == Gst.StateChangeReturn.FAILURE:
            logging.warning("Unable to set the pipeline to the playing state")
            # todo: not sure when this happens, but confirm this is handled elegently
            return False
        elif ret == Gst.StateChangeReturn.NO_PREROLL:
            logging.debug("Stream is live")
            self._is_live = True

        self._running = True
        self._pipe = pipe
        self._thread = Thread(target=self._process_loop)
        self._thread.start()
        return True

    def _process_loop(self):
        bus = self._pipe.get_bus()
        # todo: check all this is thread safe!
        while self._running:
            message = bus.timed_pop(100 * Gst.MSECOND)
            if message is not None:
                if not self.handle_message(bus, message):
                    break

        # handle stream ending..?

    def destroy_pipeline(self):
        if self._pipe is not None:
            logging.debug("Stopping pipeline")
            self._pipe.set_state(Gst.State.NULL)
            self._running = False
            self._thread.join()
            self._pipe = None

    @property
    def playing(self):        
        return self._pipe is not None and self._pipe.get_state(0) == Gst.State.PLAYING
