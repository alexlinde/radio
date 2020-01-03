#!/usr/bin/env python3

"""
The daemon responsible for handling the channel selection of the radio.

The tuning knob is a rotary encoder and is used to select the stream. The mode knob is a
rotary switch with three positions, we'll just use it for off/on for now.

The display is 8x8 matrix connected via I2C.

"""

import os
import signal
import subprocess
import sys
import threading
import math
import time

from queue import Queue

from volume import Volume
from switches import RotaryEncoder, RotarySwitch
from display import Display
from player import Player

from RPi import GPIO

DEBUG = True

# SETTINGS
# ========

# The two pins that the tuning encoder uses (BCM numbering).
TUNE_GPIO_A = 5   
TUNE_GPIO_B = 6

# The three pins for the mode knob
MODE_GPIO_1 = 22
MODE_GPIO_2 = 27
MODE_GPIO_3 = 17

# Rotary encoder and switch for the volume knob
VOLUME_GPIO_A = 23
VOLUME_GPIO_B = 24
VOLUME_GPIO_BUTTON = 25

# The minimum and maximum volumes, as percentages.
# The default max is less than 100 to prevent distortion. 
VOLUME_CONTROL = "Digital"
VOLUME_MIN = 40
VOLUME_MAX = 96

# Power LED to show that radio service is running
POWER_GPIO = 16

# The streams we can tune between
STREAMS = [
  ("BBC Radio 1", "http://bbcmedia.ic.llnwd.net/stream/bbcmedia_radio1_mf_p"),
  ("BBC Radio 2", "http://bbcmedia.ic.llnwd.net/stream/bbcmedia_radio2_mf_p"),
  ("BBC Radio 3", "http://bbcmedia.ic.llnwd.net/stream/bbcmedia_radio3_mf_p"),
  ("BBC Radio 4", "http://bbcmedia.ic.llnwd.net/stream/bbcmedia_radio4fm_mf_p")
]

# (END SETTINGS)
# 

# Callbacks happens in a separate thread. If turn callbacks fire erratically 
# or out of order, we'll use a queue to enforce FIFO. 
QUEUE = Queue()

# When we put something in the queue, we'll use an event to signal to the
# main thread that there's something in there. Then the main thread will
# process the queue and reset the event. 
EVENT = threading.Event()

def debug(str):
  if not DEBUG:
    return
  print(str)

class Power:
  def __init__(self, gpio):
    self._gpio = gpio
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(self._gpio, GPIO.OUT)
    self._pwm = GPIO.PWM(self._gpio, 1000)
    self._pwm.start(25)

  def destroy(self):
    self._pwm.stop()
    
if __name__ == "__main__":
  v = Volume(VOLUME_CONTROL,VOLUME_MIN,VOLUME_MAX)
  d = Display()
  p = Player()
  l = Power(POWER_GPIO)
  currentStream = 0
  
  def on_volume_press(value):
    v.toggle()
    debug("Toggled mute to: {}".format(v.is_muted))
    EVENT.set()
  
  def on_volume_turn(delta):
    if (mode.pole > 0):
      QUEUE.put(('V',delta))
      EVENT.set()

  def on_tune(delta):
    if (mode.pole > 0):
      QUEUE.put(('T',delta))
      EVENT.set()

  def on_mode(mode):
    QUEUE.put(('M',mode))
    EVENT.set()

  def consume_queue():
    while not QUEUE.empty():
      msg = QUEUE.get()
      if msg[0] == 'T':
        handle_tune(msg[1])
      elif msg[0] == 'M':
        handle_mode(msg[1])
      elif msg[0] == 'V':
        handle_volume(msg[1])
  
  def handle_mode(mode):
    debug("Set mode to: {}".format(mode))
    if mode == 0:
      # radio off
      stop()
    else:
      # for mode 1 radio on, ignore mode 2
      if not p.playing:
        play()

  def handle_volume(delta):
    if v.is_muted:
      debug("Unmuting")
      v.toggle()
    if delta == 1:
      vol = v.up()
    else:
      vol = v.down()
    d.priorityText(int(v.scaled_volume(vol)))
    debug("Set volume to: {}".format(vol))

  def handle_tune(delta):
    if delta == 1:
      p.next()
    else:
      p.prev()
  
  def play():
    debug("Set stream to: {}".format(STREAMS[currentStream][1]))
    d.scrollText(STREAMS[currentStream][0])
    d.priorityText("R{}".format(currentStream+1))
    p.destroy_pipeline()
    if p.create_pipeline(STREAMS[currentStream][1], True) is True:
      d.start()
    else:
      debug("failed to start streaming pipeline")

  def stop():
    p.destroy_pipeline()
    d.stop()

  def next():
    currentStream = (currentStream + 1) % len(STREAMS)
    play()

  def prev():
    currentStream = (currentStream - 1) % len(STREAMS)
    play()    

  def on_exit(a, b):
    print("Exiting...")
    stop()
    volume.destroy()
    tune.destroy()
    mode.destroy()
    d.destroy()
    l.destroy()
    GPIO.cleanup()
    EVENT.set()
    sys.exit()

  debug("Volume knob using pins {} and {}".format(VOLUME_GPIO_A, VOLUME_GPIO_B))
  debug("Volume button using pin {}".format(VOLUME_GPIO_BUTTON))
  debug("Initial volume: {}".format(v.volume))
  volume = RotaryEncoder(VOLUME_GPIO_A, VOLUME_GPIO_B, callback=on_volume_turn, 
    buttonPin=VOLUME_GPIO_BUTTON, buttonCallback=on_volume_press)

  debug("Tuning knob using pins {} and {}".format(TUNE_GPIO_A, TUNE_GPIO_B))
  tune = RotaryEncoder(TUNE_GPIO_A, TUNE_GPIO_B, callback=on_tune)

  debug("Mode knob using pins {}, {} and {}".format(MODE_GPIO_1, MODE_GPIO_2, MODE_GPIO_3))
  mode = RotarySwitch([MODE_GPIO_1, MODE_GPIO_2, MODE_GPIO_3], callback=on_mode)
  debug("Initial mode: {}".format(mode.pole))
  handle_mode(mode.pole)

  signal.signal(signal.SIGTERM, on_exit)
  signal.signal(signal.SIGINT, on_exit)

  while True:
    EVENT.wait(1200)
    consume_queue()
    EVENT.clear()
