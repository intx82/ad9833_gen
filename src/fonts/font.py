
class glyph:
    def __init__(self, bo=0, width=0, height=0, xAdvance=0, xOffset=0, yOffset=0) -> None:
        self.bitmapOffset = bo       # Pointer into GFXfont->bitmap
        self.width = width           # Bitmap dimensions in pixels
        self.height = height         # Bitmap dimensions in pixels
        self.xAdvance = xAdvance     # Distance to advance cursor (x axis)
        self.xOffset = xOffset       # X dist from cursor pos to UL corner
        self.yOffset = yOffset       # Y dist from cursor pos to UL corner


class font:
    def __init__(self, display) -> None:
        self.display = display
        self.cursor_x = 0
        self.cursor_y = self.y_advance()
        self.wrap = False

    def bitmap(self) -> bytes:
        return bytes()

    def glyph(self, _chr: int) -> glyph:
        return None

    def first(self) -> int:
        return 0

    def last(self) -> int:
        return 0

    def y_advance(self) -> int:
        return 0

    def _draw_chr(self, x: int, y: int, _chr: int) -> None:
        _chr = ord(_chr) - self.first()
        _glyph = self.glyph(_chr)
        if _glyph is None:
            return

        bits = bit = 0
        bo = _glyph.bitmapOffset
        xo = _glyph.xOffset
        yo = _glyph.yOffset

        for yy in range(_glyph.height):
            for xx in range(_glyph.width):
                if not (bit & 7):
                    bits = self.bitmap()[bo]
                    bo += 1
                bit += 1

                if bits & 0x80:
                    self.display.pixel(x + xx + xo, y + yy + yo, 1)
                bits <<= 1


    def draw_chr(self, c: int):
        if c == '\n':
            self.cursor_x = 0
            self.cursor_y += self.y_advance()
        elif c != '\r':
            if ord(c) >= self.first() and ord(c) <= self.last():
                _glyph = self.glyph(ord(c) - self.first())
                if _glyph is None:
                    return

                w = _glyph.width
                h = _glyph.height
                
                if (w > 0) and (h > 0):
                    xo = _glyph.xOffset
                
                if self.wrap and self.cursor_x + (xo + w) > self._width:
                    self.cursor_x = 0
                    self.cursor_y += self.y_advance()
                
                self._draw_chr(self.cursor_x, self.cursor_y, c)
                self.cursor_x +=_glyph.xAdvance 

    def text(self, _str, x_offset = 0, y_offset = 0):
        self.cursor_x = x_offset
        self.cursor_y = self.y_advance() + y_offset
        for s in _str:
            self.draw_chr(s)

if __name__ == '__main__':
    from fonts.disp_mock import disp_mock
    from fonts.TitilliumWeb_Regular11 import TitilliumWeb_Regular11
    fnt = TitilliumWeb_Regular11(disp_mock())
    fnt.draw_chr('.')
