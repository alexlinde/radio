from gfxfont import Glyph, GFXFont

# bitmap font with variable size glyphs
PicopixelBitmaps = [
    0xE8, 0xB4, 0x57, 0xD5, 0xF5, 0x00, 0x4E, 0x3E, 0x80, 0xA5, 0x4A, 0x4A,
    0x5A, 0x50, 0xC0, 0x6A, 0x40, 0x95, 0x80, 0xAA, 0x80, 0x5D, 0x00, 0x60,
    0xE0, 0x80, 0x25, 0x48, 0x56, 0xD4, 0x75, 0x40, 0xC5, 0x4E, 0xC5, 0x1C,
    0x97, 0x92, 0xF3, 0x1C, 0x53, 0x54, 0xE5, 0x48, 0x55, 0x54, 0x55, 0x94,
    0xA0, 0x46, 0x64, 0xE3, 0x80, 0x98, 0xC5, 0x04, 0x56, 0xC6, 0x57, 0xDA,
    0xD7, 0x5C, 0x72, 0x46, 0xD6, 0xDC, 0xF3, 0xCE, 0xF3, 0x48, 0x72, 0xD4,
    0xB7, 0xDA, 0xF8, 0x24, 0xD4, 0xBB, 0x5A, 0x92, 0x4E, 0x8E, 0xEB, 0x58,
    0x80, 0x9D, 0xB9, 0x90, 0x56, 0xD4, 0xD7, 0x48, 0x56, 0xD4, 0x40, 0xD7,
    0x5A, 0x71, 0x1C, 0xE9, 0x24, 0xB6, 0xD4, 0xB6, 0xA4, 0x8C, 0x6B, 0x55,
    0x00, 0xB5, 0x5A, 0xB5, 0x24, 0xE5, 0x4E, 0xEA, 0xC0, 0x91, 0x12, 0xD5,
    0xC0, 0x54, 0xF0, 0x90, 0xC7, 0xF0, 0x93, 0x5E, 0x71, 0x80, 0x25, 0xDE,
    0x5E, 0x30, 0x6E, 0x80, 0x77, 0x9C, 0x93, 0x5A, 0xB8, 0x45, 0x60, 0x92,
    0xEA, 0xAA, 0x40, 0xD5, 0x6A, 0xD6, 0x80, 0x55, 0x00, 0xD7, 0x40, 0x75,
    0x90, 0xE8, 0x71, 0xE0, 0xBA, 0x40, 0xB5, 0x80, 0xB5, 0x00, 0x8D, 0x54,
    0xAA, 0x80, 0xAC, 0xE0, 0xE5, 0x70, 0x6A, 0x26, 0xFC, 0xC8, 0xAC, 0x5A ]

# bitmapLocation, width, height, xAdvance, xOffset, yOffset
# where offset is distance from cursor to upper left corner
PicopixelGlyphs = [
  Glyph(     0,   0,   0,   2,    0,    1 ),   # 0x20 ' '
  Glyph(     0,   1,   5,   2,    0,   -4 ),   # 0x21 '!'
  Glyph(     1,   3,   2,   4,    0,   -4 ),   # 0x22 '"'
  Glyph(     2,   5,   5,   6,    0,   -4 ),   # 0x23 '#'
  Glyph(     6,   3,   6,   4,    0,   -4 ),   # 0x24 '$'
  Glyph(     9,   3,   5,   4,    0,   -4 ),   # 0x25 '%'
  Glyph(    11,   4,   5,   5,    0,   -4 ),   # 0x26 '&'
  Glyph(    14,   1,   2,   2,    0,   -4 ),   # 0x27 '''
  Glyph(    15,   2,   5,   3,    0,   -4 ),   # 0x28 '('
  Glyph(    17,   2,   5,   3,    0,   -4 ),   # 0x29 ')'
  Glyph(    19,   3,   3,   4,    0,   -3 ),   # 0x2A '*'
  Glyph(    21,   3,   3,   4,    0,   -3 ),   # 0x2B '+'
  Glyph(    23,   2,   2,   3,    0,    0 ),   # 0x2C ','
  Glyph(    24,   3,   1,   4,    0,   -2 ),   # 0x2D '-'
  Glyph(    25,   1,   1,   2,    0,    0 ),   # 0x2E '.'
  Glyph(    26,   3,   5,   4,    0,   -4 ),   # 0x2F '/'
  Glyph(    28,   3,   5,   4,    0,   -4 ),   # 0x30 '0'
  Glyph(    30,   2,   5,   3,    0,   -4 ),   # 0x31 '1'
  Glyph(    32,   3,   5,   4,    0,   -4 ),   # 0x32 '2'
  Glyph(    34,   3,   5,   4,    0,   -4 ),   # 0x33 '3'
  Glyph(    36,   3,   5,   4,    0,   -4 ),   # 0x34 '4'
  Glyph(    38,   3,   5,   4,    0,   -4 ),   # 0x35 '5'
  Glyph(    40,   3,   5,   4,    0,   -4 ),   # 0x36 '6'
  Glyph(    42,   3,   5,   4,    0,   -4 ),   # 0x37 '7'
  Glyph(    44,   3,   5,   4,    0,   -4 ),   # 0x38 '8'
  Glyph(    46,   3,   5,   4,    0,   -4 ),   # 0x39 '9'
  Glyph(    48,   1,   3,   2,    0,   -3 ),   # 0x3A ':'
  Glyph(    49,   2,   4,   3,    0,   -3 ),   # 0x3B ';'
  Glyph(    50,   2,   3,   3,    0,   -3 ),   # 0x3C '<'
  Glyph(    51,   3,   3,   4,    0,   -3 ),   # 0x3D '='
  Glyph(    53,   2,   3,   3,    0,   -3 ),   # 0x3E '>'
  Glyph(    54,   3,   5,   4,    0,   -4 ),   # 0x3F '?'
  Glyph(    56,   3,   5,   4,    0,   -4 ),   # 0x40 '@'
  Glyph(    58,   3,   5,   4,    0,   -4 ),   # 0x41 'A'
  Glyph(    60,   3,   5,   4,    0,   -4 ),   # 0x42 'B'
  Glyph(    62,   3,   5,   4,    0,   -4 ),   # 0x43 'C'
  Glyph(    64,   3,   5,   4,    0,   -4 ),   # 0x44 'D'
  Glyph(    66,   3,   5,   4,    0,   -4 ),   # 0x45 'E'
  Glyph(    68,   3,   5,   4,    0,   -4 ),   # 0x46 'F'
  Glyph(    70,   3,   5,   4,    0,   -4 ),   # 0x47 'G'
  Glyph(    72,   3,   5,   4,    0,   -4 ),   # 0x48 'H'
  Glyph(    74,   1,   5,   2,    0,   -4 ),   # 0x49 'I'
  Glyph(    75,   3,   5,   4,    0,   -4 ),   # 0x4A 'J'
  Glyph(    77,   3,   5,   4,    0,   -4 ),   # 0x4B 'K'
  Glyph(    79,   3,   5,   4,    0,   -4 ),   # 0x4C 'L'
  Glyph(    81,   5,   5,   6,    0,   -4 ),   # 0x4D 'M'
  Glyph(    85,   4,   5,   5,    0,   -4 ),   # 0x4E 'N'
  Glyph(    88,   3,   5,   4,    0,   -4 ),   # 0x4F 'O'
  Glyph(    90,   3,   5,   4,    0,   -4 ),   # 0x50 'P'
  Glyph(    92,   3,   6,   4,    0,   -4 ),   # 0x51 'Q'
  Glyph(    95,   3,   5,   4,    0,   -4 ),   # 0x52 'R'
  Glyph(    97,   3,   5,   4,    0,   -4 ),   # 0x53 'S'
  Glyph(    99,   3,   5,   4,    0,   -4 ),   # 0x54 'T'
  Glyph(   101,   3,   5,   4,    0,   -4 ),   # 0x55 'U'
  Glyph(   103,   3,   5,   4,    0,   -4 ),   # 0x56 'V'
  Glyph(   105,   5,   5,   6,    0,   -4 ),   # 0x57 'W'
  Glyph(   109,   3,   5,   4,    0,   -4 ),   # 0x58 'X'
  Glyph(   111,   3,   5,   4,    0,   -4 ),   # 0x59 'Y'
  Glyph(   113,   3,   5,   4,    0,   -4 ),   # 0x5A 'Z'
  Glyph(   115,   2,   5,   3,    0,   -4 ),   # 0x5B '('
  Glyph(   117,   3,   5,   4,    0,   -4 ),   # 0x5C '\'
  Glyph(   119,   2,   5,   3,    0,   -4 ),   # 0x5D ')'
  Glyph(   121,   3,   2,   4,    0,   -4 ),   # 0x5E '^'
  Glyph(   122,   4,   1,   4,    0,    1 ),   # 0x5F '_'
  Glyph(   123,   2,   2,   3,    0,   -4 ),   # 0x60 '`'
  Glyph(   124,   3,   4,   4,    0,   -3 ),   # 0x61 'a'
  Glyph(   126,   3,   5,   4,    0,   -4 ),   # 0x62 'b'
  Glyph(   128,   3,   3,   4,    0,   -2 ),   # 0x63 'c'
  Glyph(   130,   3,   5,   4,    0,   -4 ),   # 0x64 'd'
  Glyph(   132,   3,   4,   4,    0,   -3 ),   # 0x65 'e'
  Glyph(   134,   2,   5,   3,    0,   -4 ),   # 0x66 'f'
  Glyph(   136,   3,   5,   4,    0,   -3 ),   # 0x67 'g'
  Glyph(   138,   3,   5,   4,    0,   -4 ),   # 0x68 'h'
  Glyph(   140,   1,   5,   2,    0,   -4 ),   # 0x69 'i'
  Glyph(   141,   2,   6,   3,    0,   -4 ),   # 0x6A 'j'
  Glyph(   143,   3,   5,   4,    0,   -4 ),   # 0x6B 'k'
  Glyph(   145,   2,   5,   3,    0,   -4 ),   # 0x6C 'l'
  Glyph(   147,   5,   3,   6,    0,   -2 ),   # 0x6D 'm'
  Glyph(   149,   3,   3,   4,    0,   -2 ),   # 0x6E 'n'
  Glyph(   151,   3,   3,   4,    0,   -2 ),   # 0x6F 'o'
  Glyph(   153,   3,   4,   4,    0,   -2 ),   # 0x70 'p'
  Glyph(   155,   3,   4,   4,    0,   -2 ),   # 0x71 'q'
  Glyph(   157,   2,   3,   3,    0,   -2 ),   # 0x72 'r'
  Glyph(   158,   3,   4,   4,    0,   -3 ),   # 0x73 's'
  Glyph(   160,   2,   5,   3,    0,   -4 ),   # 0x74 't'
  Glyph(   162,   3,   3,   4,    0,   -2 ),   # 0x75 'u'
  Glyph(   164,   3,   3,   4,    0,   -2 ),   # 0x76 'v'
  Glyph(   166,   5,   3,   6,    0,   -2 ),   # 0x77 'w'
  Glyph(   168,   3,   3,   4,    0,   -2 ),   # 0x78 'x'
  Glyph(   170,   3,   4,   4,    0,   -2 ),   # 0x79 'y'
  Glyph(   172,   3,   4,   4,    0,   -3 ),   # 0x7A 'z'
  Glyph(   174,   3,   5,   4,    0,   -4 ),   # 0x7B '['
  Glyph(   176,   1,   6,   2,    0,   -4 ),   # 0x7C '|'
  Glyph(   177,   3,   5,   4,    0,   -4 ),   # 0x7D ']'
  Glyph(   179,   4,   2,   5,    0,   -3 )    # 0x7E '~'
]  

PicoPixelFirst = 0x20
PicoPixelLast = 0x7E
PicoPixelYAdvance = 7

class PicoPixelFont(GFXFont):
    def __init__(self):
        super().__init__(PicopixelBitmaps,PicopixelGlyphs,PicoPixelFirst,PicoPixelLast,PicoPixelYAdvance)
