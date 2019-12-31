#!/usr/bin/env python3

import Adafruit_PureIO.smbus as smbus

_HT16K33_DEFAULT_ADDRESS =  0x70

_HT16K33_BLINK_CMD =        0x80
_HT16K33_BLINK_DISPLAYON =  0x01
_HT16K33_CMD_BRIGHTNESS =   0xE0
_HT16K33_SYSTEM_SETUP =     0x20
_HT16K33_OSCILATOR_ON =     0x01

_DISPLAY_WIDTH =            8
_DISPLAY_HEIGHT =           8

class HT16K33:
    """
    The base class for all displays. Contains common methods.
    :param int address: The I2C addess of the HT16K33.
    :param bool auto_write: True if the display should immediately change when
        set. If False, `show` must be called explicitly.
    """
    def __init__(self, channel=1, address=_HT16K33_DEFAULT_ADDRESS, 
                    auto_write=True, active=True, rotation=0):
        self.bus = smbus.SMBus()
        self.bus.open(channel)
        self._address = address
        self._temp = None
        self._buffer = [0] * 16
        self.show()
        self._rotation = rotation
        self._auto_write = auto_write
        self.active = active
        self.blink_rate = 0
        self.brightness = 15

    def destroy(self):
        self.active = False
        self.bus.close()

    def _write_cmd(self, byte):
        self._temp = byte
        self.bus.write_byte(self._address, self._temp)

    @property
    def active(self):
        return self._active

    @active.setter
    def active(self, active):
        if isinstance(active, bool):
            self._write_cmd(_HT16K33_SYSTEM_SETUP | 
                            (_HT16K33_OSCILATOR_ON if active is True else 0x00))
            self._active = active
        else:
            raise ValueError('Must set to either True or False.')

    @property
    def blink_rate(self):
        """The blink rate. Range 0-3."""
        return self._blink_rate

    @blink_rate.setter
    def blink_rate(self, rate=None):
        if not 0 <= rate <= 3:
            raise ValueError('Blink rate must be an integer in the range: 0-3')
        rate = rate & 0x03
        self._blink_rate = rate
        self._write_cmd(_HT16K33_BLINK_CMD |
                        _HT16K33_BLINK_DISPLAYON | rate << 1)
        return None

    @property
    def brightness(self):
        """The brightness. Range 0-15."""
        return self._brightness

    @brightness.setter
    def brightness(self, brightness):
        if not 0 <= brightness <= 15:
            raise ValueError('Brightness must be an integer in the range: 0-15')
        brightness = brightness & 0x0F
        self._brightness = brightness
        self._write_cmd(_HT16K33_CMD_BRIGHTNESS | brightness)
        return None

    @property
    def auto_write(self):
        """Auto write updates to the display."""
        return self._auto_write

    @auto_write.setter
    def auto_write(self, auto_write):
        if isinstance(auto_write, bool):
            self._auto_write = auto_write
        else:
            raise ValueError('Must set to either True or False.')

    def show(self):
        """Refresh the display and show the changes."""
        self.bus.write_i2c_block_data(self._address, 0x00, self._buffer)

        # for i in range(8):
        #     print("{:b} {:b}".format(self._buffer[i*2],self._buffer[i*2+1]))

    def fill(self, color):
        """Fill the whole display with the given color."""
        fill = 0xff if color else 0x00
        for i in range(16):
            self._buffer[i] = fill
        if self._auto_write:
            self.show()

    def _pixel(self, x, y, color=None):
        # shift pixel??
        x = (x + 1) % 8

        # rotate coordinates to match display 
        if self._rotation == 1:
            t = x
            x = _DISPLAY_WIDTH - 1 - y
            y = t
        elif self._rotation == 2:
            x = _DISPLAY_WIDTH - 1 - x
            y = _DISPLAY_HEIGHT - 1 - y
        elif self._rotation == 3:
            t = x
            x = y
            y = _DISPLAY_HEIGHT - 1 - t

        # convert x,y into buffer byte and bitmask
        # chip has two bytes for 16 pixels per row, 8 rows
        addr = 2 * y + (x // 8)
        mask = 1 << (x % 8)

        if color is None:
            return bool(self._buffer[addr] & mask)
        if color:
            # set the bit
            self._buffer[addr] |= mask
        else:
            # clear the bit
            self._buffer[addr] &= ~mask

        if self._auto_write:
            self.show()
        
        return None

    def _set_buffer(self, i, value):
        self._buffer[i] = value 

    def _get_buffer(self, i):
        return self._buffer[i]

class Matrix8x8(HT16K33):
    """A single matrix."""
    def pixel(self, x, y, color=None):
        """Get or set the color of a given pixel."""
        # clip anything outside the matrix
        if not 0 <= x <= 7:
            return None
        if not 0 <= y <= 7:
            return None
        return super()._pixel(x, y, color)

    def __getitem__(self, key):
        x, y = key
        return self.pixel(x, y)

    def __setitem__(self, key, value):
        x, y = key
        self.pixel(x, y, value)
