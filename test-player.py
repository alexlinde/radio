from player import Player
import time, logging

logging.basicConfig(level=logging.DEBUG)
# bitrate vlow / low / med / high as per uri, only vlow and low outside UK
#URI = "http://open.live.bbc.co.uk/mediaselector/5/select/version/2.0/mediaset/http-icy-mp3-a/vpid/bbc_radio_one/format/pls.pls" # MP3, 128k
#URI = "http://bbcmedia.ic.llnwd.net/stream/bbcmedia_radio1_mf_p" # MP3, 128k
#URI = "http://a.files.bbci.co.uk/media/live/manifesto/audio/simulcast/hls/nonuk/sbr_low/llnw/bbc_radio_one.m3u8" # HLS Stream, 96k
URI = "http://a.files.bbci.co.uk/media/live/manifesto/audio/simulcast/dash/nonuk/dash_low/llnw/bbc_radio_one.mpd" # MPEG-DASH, 96k
p = Player()

try:
    p.create_pipeline(URI,True)

    while True:
        time.sleep(10)

except (KeyboardInterrupt, SystemExit):
    pass

finally:
    p.destroy_pipeline()
