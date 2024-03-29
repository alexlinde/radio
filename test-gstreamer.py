#!/usr/bin/env python3

import sys
import time
import gi
gi.require_version('Gst', '1.0')
from gi.repository import GObject, Gst, GLib

#URI = "http://bbcmedia.ic.llnwd.net/stream/bbcmedia_radio1_mf_p"
URI = "http://a.files.bbci.co.uk/media/live/manifesto/audio/simulcast/dash/nonuk/dash_low/llnw/bbc_radio_one.mpd" # MPEG-DASH, 96k

is_live = True
pipe = None
shift = False

Gst.init(None)

# def timezone_shift():
#     time.localtime()

def query_time_seconds(pipeline):
    rc, pos_int = pipeline.query_position(Gst.Format.TIME)
    if rc:
        s = pos_int / Gst.SECOND
        print("Current position is {0} ({1})".format(s,time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(s))))
        return s
    print("  Failed to query position")
    return None

def seek_to_time_seconds(pipeline, seek_s):
    print("Seeking to: {0} ({1})".format(seek_s,time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(seek_s))))
    if pipeline.seek_simple(Gst.Format.TIME, Gst.SeekFlags.FLUSH, seek_s * Gst.SECOND) == False:
        print("  Failed to seek")

def decode_src_created(element, new_pad, data):
    print("Received new pad '{0}' from '{1}'".format(new_pad.get_name(), element.get_name()))

    if new_pad.is_linked():
        print("  We are already linked. Ignoring.")
        return None

    new_pad_type = new_pad.query_caps(None).to_string()
    if not new_pad_type.startswith("audio/x-raw"):
        print("  It has type '{0}' which is not raw audio. Ignoring.".format(new_pad_type))
        return None

    audiopad = audio.get_static_pad('sink')
    ret = new_pad.link(audiopad)
    if ret is not Gst.PadLinkReturn.OK:
        print("  Failed to link pad: {0}".format(ret))

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
    print("Attempting to play {0}".format(URI))

    # start play back and listed to events
    ret = pipe.set_state(Gst.State.PLAYING)
    if ret == Gst.StateChangeReturn.FAILURE:
        print("Unable to set the pipeline to the playing state")
        sys.exit(1)
    elif ret == Gst.StateChangeReturn.NO_PREROLL:
        print("Stream is live")
        is_live = True

    bus = pipe.get_bus()
    tags = {}
    while True:
        message = bus.timed_pop(100 * Gst.MSECOND)
        if message is None:
            continue
        elif message.type == Gst.MessageType.EOS:
            print("End-of-stream")
            break
        elif message.type == Gst.MessageType.BUFFERING:
            percent = message.parse_buffering()
            print("Buffering {0}%   ".format(percent),end='\r')

            # don't try to pause/resume for live streams, will fail 
            if is_live:
                continue

            # wait until buffering is complete before start/resume playing
            if (percent < 100):
                print("Pausing, waiting for data")
                pipe.set_state(Gst.State.PAUSED)
            else:
                print("Resuming")
                pipe.set_state(Gst.State.PLAYING)
        elif message.type == Gst.MessageType.CLOCK_LOST:
            print("Lost clock, recovering stream")
            pipe.set_state(Gst.State.PAUSED)
            pipe.set_state(Gst.State.PLAYING)
        elif message.type == Gst.MessageType.STATE_CHANGED:            
            old_state, new_state, pending_state = message.parse_state_changed()
            print("{0} changed from {1} to {2}.".format(message.src.get_name(), old_state.value_nick, new_state.value_nick))
            current_s = query_time_seconds(pipe)

            if new_state == Gst.State.PLAYING and message.src == pipe and not shift:
                seek_to_time_seconds(pipe,current_s - 8*3600)
                shift = True
        elif message.type == Gst.MessageType.ERROR:
            err, msg = message.parse_error()
            print("Error: {0}: {1}".format(err, msg))
            break
        elif message.type == Gst.MessageType.WARNING:
            err, msg = message.parse_warning()
            print("Warning: {0}: {1}".format(err, msg))        
        elif message.type == Gst.MessageType.TAG:
            tag_list = message.parse_tag()
            for n in range(tag_list.n_tags()):
                tag = str(tag_list.nth_tag_name(n))
                for i in range(tag_list.get_tag_size(tag)):
                    value = str(tag_list.get_value_index(tag, i))
                    if tag not in tags or tags[tag] != value:
                        tags[tag] = value
                        print("{0}: {1}".format(tag,value))
        else:
            print("Message from {0}: {1}".format(message.src.get_name(),
                Gst.message_type_get_name(message.type)))
except (KeyboardInterrupt, SystemExit):
    print("User exit, shutting down")
    # dump current pipeline to file, use "dot -Tpdf *.dot > *.pdf" to make readable
    # Gst.print_bin_to_dot_file_with_ts(pipe,Gst.printGraphDetails.ALL,"state")
finally:
    # cleanup
    pipe.set_state(Gst.State.NULL)
