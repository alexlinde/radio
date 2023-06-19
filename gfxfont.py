from matrix import Matrix8x8

class Glyph:
    def __init__(self, bitmapLocation, width, height, xAdvance, xOffset, yOffset):
        self.bitmapLocation = bitmapLocation
        self.width = width
        self.height = height
        self.xAdvance = xAdvance
        self.xOffset = xOffset
        self.yOffset = yOffset
        
class GFXFont:
    def __init__(self,bitmap,glyphs,first,last,yadvance):
        self._bitmap = bitmap
        self._glyphs = glyphs
        self._first = first
        self._last = last
        self._yadvance = yadvance

    def measureText(self, s):
        w = 0
        for c in s:
            glyph = self._glyphs[ord(c) - self._first]
            w += glyph.xAdvance
        return w

    def drawText(self, matrix, x, y, s):
        for c in s:
            x = x + self.drawCharacter(matrix, x, y, c) 

    def drawCharacter(self, matrix, x, y, c):
        bit = 0
        glyph = self._glyphs[ord(c) - self._first]
        offset = glyph.bitmapLocation
        for yy in range(glyph.height):
            for xx in range(glyph.width):
                if (bit & 7 == 0):
                    bits = self._bitmap[offset]
                    offset = offset + 1
                bit += 1
                if (bits & 0x80):
                    matrix.pixel(x+glyph.xOffset+xx, y+glyph.yOffset+yy, True)
                bits = bits << 1
        return glyph.xAdvance
