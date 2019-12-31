from RPi import GPIO
import threading

class RotarySwitchException(Exception):
  pass

class RotarySwitch:
  """
  A class to decode a mechanical rotary switch.
  """
  
  def __init__(self, gpioList, callback=None):
    """
    Instantiate the class. Takes two arguments: an array of pin numbers to
    which the poles are connected, plus a callback to run when the switch is turned.
    """
    self._gpio     = gpioList
    self._callback = callback
    self._pole     = None
    self._timer    = None

    GPIO.setmode(GPIO.BCM)
    for channel in self._gpio:
      GPIO.setup(channel, GPIO.IN, pull_up_down=GPIO.PUD_UP)
      GPIO.add_event_detect(channel, GPIO.BOTH, self._on_event)
      if (GPIO.input(channel) == 0): # active low
        if (self._pole == None):
          # Store the currently active pole index
          self._pole = self._gpio.index(channel)
        else:
          # More than one pole is active, not possible for a stable rotary switch
          raise RotarySwitchException
  
  @property 
  def pole(self):
    return self._pole

  def _on_timer(self):
    """
    Read final state and callback
    """
    for channel in self._gpio:
      if (GPIO.input(channel) == 0): # active low
          self._pole = self._gpio.index(channel)
          break
    self._callback(self._pole)

  def _on_event(self, channel):
    """
    Allow time for poles to be stable
    """
    if self._timer:
      self._timer.cancel()
    self._timer = threading.Timer(50/1000.0,self._on_timer)
    self._timer.start() 

  def destroy(self):
    GPIO.setmode(GPIO.BCM)
    for channel in self._gpio:
      GPIO.remove_event_detect(channel)

class RotaryEncoder:
  """
  A class to decode mechanical rotary encoder pulses.

  Ported to RPi.GPIO from the pigpio sample here: 
  http://abyz.co.uk/rpi/pigpio/examples.html
  """
  
  def __init__(self, gpioA, gpioB, callback=None, buttonPin=None, buttonCallback=None):
    """
    Instantiate the class. Takes three arguments: the two pin numbers to
    which the rotary encoder is connected, plus a callback to run when the
    switch is turned.
    
    The callback receives one argument: a `delta` that will be either 1 or -1.
    One of them means that the dial is being turned to the right; the other
    means that the dial is being turned to the left. I'll be damned if I know
    yet which one is which.
    """
    
    self.lastGpio = None
    self.gpioA    = gpioA
    self.gpioB    = gpioB
    self.callback = callback
    
    self.gpioButton     = buttonPin
    self.buttonCallback = buttonCallback
    
    self.levA = 0
    self.levB = 0
    
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(self.gpioA, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(self.gpioB, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    
    GPIO.add_event_detect(self.gpioA, GPIO.BOTH, self._callback)
    GPIO.add_event_detect(self.gpioB, GPIO.BOTH, self._callback)
    
    if self.gpioButton:
      GPIO.setup(self.gpioButton, GPIO.IN, pull_up_down=GPIO.PUD_UP)
      GPIO.add_event_detect(self.gpioButton, GPIO.FALLING, self._buttonCallback, bouncetime=500)
    
    
  def destroy(self):
    GPIO.setmode(GPIO.BCM)
    GPIO.remove_event_detect(self.gpioA)
    GPIO.remove_event_detect(self.gpioB)
    
  def _buttonCallback(self, channel):
    self.buttonCallback(GPIO.input(channel))
    
  def _callback(self, channel):
    level = GPIO.input(channel)
    if channel == self.gpioA:
      self.levA = level
    else:
      self.levB = level
      
    # Debounce.
    if channel == self.lastGpio:
      return
    
    # When both inputs are at 1, we'll fire a callback. If A was the most
    # recent pin set high, it'll be forward, and if B was the most recent pin
    # set high, it'll be reverse.
    self.lastGpio = channel
    if channel == self.gpioA and level == 1:
      if self.levB == 1:
        self.callback(1)
    elif channel == self.gpioB and level == 1:
      if self.levA == 1:
        self.callback(-1)
