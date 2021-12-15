from .sh1107 import SH1107_I2C
from framebuf import RGB565


class Screen:
    digits = {
        0: [1, 2, 3, 5, 6, 7],
        1: [3, 6],
        2: [1, 3, 4, 5, 7],
        3: [1, 3, 4, 6, 7],
        4: [2, 3, 4, 6],
        5: [1, 2, 4, 6, 7],
        6: [1, 2, 4, 5, 6, 7],
        7: [1, 3, 6],
        8: [1, 2, 3, 4, 5, 6, 7],
        9: [1, 2, 3, 4, 6, 7],
    }
    H_LENGTH = 10
    V_LENGTH = 20
    LINE_WIDTH = 2
    LINE_SPACE = 2

    def __init__(self, i2c, width=128, height=64):

        self.display = SH1107_I2C(width, height, i2c, addr=0x3C, external_vcc=False)

        self.display.poweron()
        self.display.fill(0)

        self.dig_map = {
            1: lambda x, y: self.rect(x + self.LINE_SPACE, y, 1),
            2: lambda x, y: self.rect(x, y + self.LINE_SPACE, 0),
            3: lambda x, y: self.rect(
                x + self.H_LENGTH + self.LINE_SPACE, y + self.LINE_SPACE, 0
            ),
            4: lambda x, y: self.rect(
                x + self.LINE_SPACE, y + self.V_LENGTH + self.LINE_SPACE, 1
            ),
            5: lambda x, y: self.rect(x, y + 2 * self.LINE_SPACE + self.V_LENGTH, 0),
            6: lambda x, y: self.rect(
                x + self.H_LENGTH + self.LINE_SPACE,
                y + 2 * self.LINE_SPACE + self.V_LENGTH,
                0,
            ),
            7: lambda x, y: self.rect(
                x + self.LINE_SPACE, y + 2 * self.V_LENGTH + 2 * self.LINE_SPACE, 1
            ),
        }

    def print(self, msg, x, y):
        self.display.text(msg, x, y)

    def rect(self, x, y, horiz):
        w = self.H_LENGTH if horiz else self.LINE_WIDTH
        h = self.V_LENGTH if not horiz else self.LINE_WIDTH
        self.display.fill_rect(x, y, w, h, 1)

    def draw_eight(self, x, y):

        self.rect(x + self.LINE_SPACE, y, 1)
        self.rect(x, y + self.LINE_SPACE, 0)
        self.rect(x + self.H_LENGTH + self.LINE_SPACE, y + self.LINE_SPACE, 0)
        self.rect(x + self.LINE_SPACE, y + self.V_LENGTH + self.LINE_SPACE, 1)

        self.rect(x, y + 2 * self.LINE_SPACE + self.V_LENGTH, 0)
        self.rect(
            x + self.H_LENGTH + self.LINE_SPACE,
            y + 2 * self.LINE_SPACE + self.V_LENGTH,
            0,
        )
        self.rect(x + self.LINE_SPACE, y + 2 * self.V_LENGTH + 2 * self.LINE_SPACE, 1)

    def draw_dig(self, i: int, x: int, y: int):
        self.clear_rect(
            x,
            y,
            self.H_LENGTH + 2 * self.LINE_SPACE,
            2 * self.V_LENGTH + 3 * self.LINE_SPACE,
        )
        for n in self.digits[i]:
            self.dig_map[n](x, y)

    def clear_rect(self, x, y, w, h):
        self.display.fill_rect(x, y, w, h, 0)

    def clear(self):
        self.display.fill_rect(0, 0, 128, 64, 0)
        self.display.show()
