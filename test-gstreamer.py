#!/usr/bin/env python3

import sys

import gi
gi.require_version('Gst', '1.0')
from gi.repository import GObject, Gst, GLib

def debug(str,end='\n'):
  if not DEBUG:
    return
  print(str,end=end)

DEBUG = True

URI = "http://bbcmedia.ic.llnwd.net/stream/bbcmedia_radio1_mf_p"
is_live = True
pipe = None

Gst.init(None)

def decode_src_created(element, new_pad, data):
    debug("Received new pad '{0}' from '{1}'".format(new_pad.get_name(), src.get_name()))

    if new_pad.is_linked():
        debug("  We are already linked. Ignoring.")
        return None

    new_pad_type = new_pad.query_caps(None).to_string()
    if not new_pad_type.startswith("audio/x-raw"):
        debug("  It has type '{0}' which is not raw audio. Ignoring.".format(new_pad_type))
        return None

    audiopad = audio.get_static_pad('sink')
    ret = new_pad.link(audiopad)
    if ret is not Gst.PadLinkReturn.OK:
        debug("  Failed to link pad: {0}".format(ret))

pipe = Gst.Pipeline.new('pipeline')

try:

    src = Gst.ElementFactory.make('souphttpsrc','source')
    src.set_property('is-live', True)
    src.set_property('location', URI)
    pipe.add(src)

    queue = Gst.ElementFactory.make('queue2','queue')
    queue.set_property("use-buffering", True)
    pipe.add(queue)
    src.link(queue)

    decode = Gst.ElementFactory.make('decodebin','decoder')
    decode.connect("pad-added", decode_src_created, None) 
    pipe.add(decode)
    queue.link(decode)

    audio = Gst.Bin.new('audiobin')

    queue = Gst.ElementFactory.make('queue','queue')
    audio.add(queue)
    audiopad = queue.get_static_pad('sink')
    ghost = Gst.GhostPad.new('sink',audiopad)
    audio.add_pad(ghost)

    convert = Gst.ElementFactory.make('audioconvert','aconv')
    audio.add(convert)
    queue.link(convert)

    sink = Gst.ElementFactory.make('autoaudiosink')
    audio.add(sink)
    convert.link(sink)

    pipe.add(audio)

    # valid uri only, not filename
    debug("Attempting to play {0}".format(URI))

    # start play back and listed to events
    ret = pipe.set_state(Gst.State.PLAYING)
    if ret == Gst.StateChangeReturn.FAILURE:
        debug("Unable to set the pipeline to the playing state")
        sys.exit(1)
    elif ret == Gst.StateChangeReturn.NO_PREROLL:
        debug("Stream is live")
        is_live = True

    bus = pipe.get_bus()
    tags = {}
    while True:
        message = bus.timed_pop(100 * Gst.MSECOND)
        if message is None:
            continue
        elif message.type == Gst.MessageType.EOS:
            debug("End-of-stream")
            break
        elif message.type == Gst.MessageType.BUFFERING:
            percent = message.parse_buffering()
            debug("Buffering {0}%   ".format(percent),'\r')

            # don't try to pause/resume for live streams, will fail 
            if is_live:
                continue

            # wait until buffering is complete before start/resume playing
            if (percent < 100):
                debug("Pausing, waiting for data")
                pipe.set_state(Gst.State.PAUSED)
            else:
                debug("Resuming")
                pipe.set_state(Gst.State.PLAYING)
        elif message.type == Gst.MessageType.CLOCK_LOST:
            debug("Lost clock, recovering stream")
            pipe.set_state(Gst.State.PAUSED)
            pipe.set_state(Gst.State.PLAYING)
        elif message.type == Gst.MessageType.STATE_CHANGED:            
            if message.src.get_name() == 'pipeline':
                old_state, new_state, pending_state = message.parse_state_changed()
                debug("Pipeline changed from {0} to {1}.".format(old_state.value_nick, new_state.value_nick))
        elif message.type == Gst.MessageType.ERROR:
            err, msg = message.parse_error()
            debug("Error: {0}: {1}".format(err, msg))
            break
        elif message.type == Gst.MessageType.WARNING:
            err, msg = message.parse_warning()
            debug("Warning: {0}: {1}".format(err, msg))        
        elif message.type == Gst.MessageType.TAG:
            tag_list = message.parse_tag()
            for n in range(tag_list.n_tags()):
                tag = str(tag_list.nth_tag_name(n))
                for i in range(tag_list.get_tag_size(tag)):
                    value = str(tag_list.get_value_index(tag, i))
                    if tag not in tags or tags[tag] != value:
                        tags[tag] = value
                        debug("{0}: {1}".format(tag,value))
        # else:
        #     print("Message from {0}: {1}".format(message.src.get_name(),
        #         Gst.message_type_get_name(message.type)))
except (KeyboardInterrupt, SystemExit):
    debug("User exit, shutting down")
    # Gst.debug_bin_to_dot_file_with_ts(pipe,Gst.DebugGraphDetails.ALL,"state")
finally:
    # cleanup
    pipe.set_state(Gst.State.NULL)
