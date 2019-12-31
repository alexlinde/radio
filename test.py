#!/usr/bin/env python3

import sys

import gi
gi.require_version('Gst', '1.0')
from gi.repository import GObject, Gst, GLib

URI = "http://bbcmedia.ic.llnwd.net/stream/bbcmedia_radio1_mf_p"

def bus_call(bus, message, loop):
    t = message.type
    if t == Gst.MessageType.EOS:
        sys.stdout.write("End-of-stream\n")
        loop.quit()
    elif t == Gst.MessageType.ERROR:
        err, debug = message.parse_error()
        sys.stderr.write("Error: %s: %s\n" % (err, debug))
        loop.quit()
    return True

Gst.init(None)
    
playbin = Gst.ElementFactory.make("playbin", None)
if not playbin:
    sys.stderr.write("'playbin' gstreamer plugin missing\n")
    sys.exit(1)

# take the commandline argument and ensure that it is a uri
# if Gst.uri_is_valid(args[1]):
#     uri = args[1]
# else:
#     uri = Gst.filename_to_uri(args[1])
playbin.set_property('uri', URI)

# create and event loop and feed gstreamer bus mesages to it
loop = GLib.MainLoop()

bus = playbin.get_bus()
bus.add_signal_watch()
bus.connect ("message", bus_call, loop)

# start play back and listed to events
playbin.set_state(Gst.State.PLAYING)
try:
    loop.run()
except:
    pass

# cleanup
playbin.set_state(Gst.State.NULL)
