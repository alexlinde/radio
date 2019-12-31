from matrix import Matrix8x8
from picopixel import PicoPixelFont
import threading

class Display:
  def __init__(self):
      self._matrix = Matrix8x8(auto_write=False,rotation=2)
      self._font = PicoPixelFont()
      self._width = 8
      self._yPosition = 6
      self._timer = None
      self._power = True
      self._scroll = ""

  def destroy(self):
    self.stop()
    self._matrix.destroy()

  def start(self):
      self._matrix.active = True
      self._update()

  def stop(self):
    if self._timer:
      self._timer.cancel()
    self._matrix.fill(0)
    self._matrix.show()
    self._matrix.active = False

  def _update(self):
    if (self._timer):
      self._timer.cancel()
    self._timer = None
    self._matrix.fill(0)

    if len(self._scroll) > 0:
      characterIndex = self._currentCharacter
      xPosition = self._xStart
      xFirst = None
      while xPosition < self._width:
        xAdvance = self._font.drawCharacter(self._matrix, 
          xPosition, self._yPosition, 
          self._scroll[characterIndex])
        if xFirst is None:
          xFirst = xAdvance
        xPosition = xPosition + xAdvance
        characterIndex = characterIndex + 1
        if characterIndex == len(self._scroll):
          break
      
      self._xStart = self._xStart - 1
      if self._xStart + xFirst == 0:
        self._currentCharacter = self._currentCharacter + 1
        if self._currentCharacter == len(self._scroll):
          self._currentCharacter = 0
          self._xStart = self._width - 1
        else:
          self._xStart = 0

      # 60ms update frequency
      self._timer = threading.Timer(200/1000.0,self._update)
      self._timer.start() 

    self._matrix.show()

  def _priority_done(self):
    self._update()

  def priorityText(self, text, duration=2.0):
    if (self._timer):
      self._timer.cancel()
    s = str(text)
    x = (8 - self._font.measureText(s)) // 2
    self._matrix.fill(0)
    self._font.drawText(self._matrix,x,6,s)
    self._matrix.show()
    
    self._timer = threading.Timer(duration,self._priority_done)
    self._timer.start() 

  def scrollText(self, text):
    if (self._timer):
      self._timer.cancel()
    self._scroll = str(text)
    self._xStart = self._width - 1
    self._currentCharacter = 0
    self._update()