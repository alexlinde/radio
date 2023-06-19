from player import Player
import time, logging

logging.basicConfig(level=logging.DEBUG)
# bitrate vlow / low / med / high as per uri, only vlow and low outside UK
URI = "http://a.files.bbci.co.uk/media/live/manifesto/audio/simulcast/dash/nonuk/dash_low/ak/bbc_radio_one.mpd"
p = Player()

try:
    p.create_pipeline(URI,True)

    while True:
        time.sleep(10)

except (KeyboardInterrupt, SystemExit):
    pass

finally:
    p.destroy_pipeline()
