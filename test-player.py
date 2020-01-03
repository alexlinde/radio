from player import Player
import time

URI = "http://bbcmedia.ic.llnwd.net/stream/bbcmedia_radio1_mf_p"

p = Player()

p.create_pipeline(URI,True)
time.sleep(10)
p.destroy_pipeline()
