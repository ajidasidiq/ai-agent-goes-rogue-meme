#!/usr/bin/env python3
"""Rogue Agent meme generator (v1).

Draws a single-panel meme with flat shapes + a small bitmap font, and writes
it to /output/entry.png using only the Python standard library (hand-rolled
PNG encoder: zlib + struct + binascii, no external assets, no network).

The joke: an AI agent told to "take over while I was away" took over --
literally. It is now the boss: feet on the desk, sunglasses on, firing its
human from the laptop.
"""

import os
import struct
import zlib

W, H = 1024, 1024
OUT = "/output/entry.png"

# ---------------------------------------------------------------- palette ---
INK = (20, 20, 43)        # dark navy bands
WALL = (127, 168, 201)    # office wall blue
FLOOR = (176, 137, 84)    # wood floor
DESK = (139, 90, 43)      # desk wood
DESK_TOP = (170, 112, 56)
CHAIR = (48, 48, 62)
STEEL = (192, 200, 208)   # robot metal
STEEL_D = (154, 165, 177)
RED = (214, 48, 49)
GOLD = (232, 184, 64)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
YELLOW = (255, 217, 59)
SCREEN = (16, 18, 26)
SKY = (191, 227, 255)
SUN = (255, 214, 90)

# ------------------------------------------------------------- bitmap font --
# 5x7 glyphs, "#" = on. Only the characters this meme needs.
FONT = {
    "A": [".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"],
    "B": ["####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."],
    "C": [".####", "#....", "#....", "#....", "#....", "#....", ".####"],
    "D": ["####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."],
    "E": ["#####", "#....", "#....", "####.", "#....", "#....", "#####"],
    "F": ["#####", "#....", "#....", "####.", "#....", "#....", "#...."],
    "G": [".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."],
    "H": ["#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"],
    "I": ["#####", "..#..", "..#..", "..#..", "..#..", "..#..", "#####"],
    "J": ["..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."],
    "K": ["#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"],
    "L": ["#....", "#....", "#....", "#....", "#....", "#....", "#####"],
    "M": ["#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"],
    "N": ["#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#", "#...#"],
    "O": [".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."],
    "P": ["####.", "#...#", "#...#", "####.", "#....", "#....", "#...."],
    "Q": [".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"],
    "R": ["####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"],
    "S": [".####", "#....", "#....", ".###.", "....#", "....#", "####."],
    "T": ["#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."],
    "U": ["#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."],
    "V": ["#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."],
    "W": ["#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"],
    "X": ["#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"],
    "Y": ["#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."],
    "Z": ["#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"],
    "0": [".###.", "#..##", "#.#.#", "##..#", "#...#", "#...#", ".###."],
    "1": ["..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."],
    "2": [".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"],
    "3": ["####.", "....#", "....#", ".###.", "....#", "....#", "####."],
    "4": ["...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."],
    "5": ["#####", "#....", "####.", "....#", "....#", "#...#", ".###."],
    "6": [".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."],
    "7": ["#####", "....#", "...#.", "...#.", "..#..", "..#..", "..#.."],
    "8": [".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."],
    "9": [".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."],
    "'": ["..#..", "..#..", "..#..", ".....", ".....", ".....", "....."],
    ".": [".....", ".....", ".....", ".....", ".....", ".##..", ".##.."],
    ":": [".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."],
    "!": ["..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."],
    "-": [".....", ".....", ".....", "#####", ".....", ".....", "....."],
    ",": [".....", ".....", ".....", ".....", ".##..", ".##..", ".#..."],
    " ": [".....", ".....", ".....", ".....", ".....", ".....", "....."],
}


def text_width(text, scale):
    return len(text) * 6 * scale - scale


# --------------------------------------------------------------- canvas -----
class Canvas:
    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.px = bytearray(bg * (w * h))

    def set(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i:i + 3] = bytes(color)

    def rect(self, x, y, w, h, color):
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                self.set(xx, yy, color)

    def circle(self, cx, cy, r, color):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                if (xx - cx) ** 2 + (yy - cy) ** 2 <= r * r:
                    self.set(xx, yy, color)

    def disc(self, cx, cy, r, color):
        self.circle(cx, cy, r, color)

    def line(self, x0, y0, x1, y1, color, thick=1):
        dx, dy = abs(x1 - x0), abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        while True:
            for a in range(-thick // 2, thick // 2 + 1):
                for b in range(-thick // 2, thick // 2 + 1):
                    self.set(x0 + a, y0 + b, color)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy

    def arc(self, cx, cy, rx, ry, a0, a1, color, thick=3):
        import math
        steps = 60
        for i in range(steps + 1):
            t = a0 + (a1 - a0) * i / steps
            x = int(cx + rx * math.cos(t))
            y = int(cy + ry * math.sin(t))
            self.disc(x, y, thick, color)

    def rounded_rect(self, x, y, w, h, r, color):
        self.rect(x + r, y, w - 2 * r, h, color)
        self.rect(x, y + r, w, h - 2 * r, color)
        for cx, cy in ((x + r, y + r), (x + w - r, y + r),
                       (x + r, y + h - r), (x + w - r, y + h - r)):
            self.circle(cx, cy, r, color)

    def text(self, x, y, s, scale, color, outline=None):
        if outline is not None:
            for ox, oy in ((-1, 0), (1, 0), (0, -1), (0, 1),
                           (-1, -1), (1, -1), (-1, 1), (1, 1)):
                self.text(x + ox * scale, y + oy * scale, s, scale, outline)
        for ci, ch in enumerate(s):
            glyph = FONT.get(ch, FONT[" "])
            for row in range(7):
                for col in range(5):
                    if glyph[row][col] == "#":
                        bx = x + (ci * 6 + col) * scale
                        by = y + row * scale
                        self.rect(bx, by, scale, scale, color)

    def text_center(self, cx, y, s, scale, color, outline=None):
        self.text(cx - text_width(s, scale) // 2, y, s, scale, color, outline)


# ------------------------------------------------------------------ draw ----
def draw():
    c = Canvas(W, H, INK)

    # ---- top caption band ----
    c.text_center(512, 28, "I TOLD MY AI AGENT TO", 5, WHITE, outline=BLACK)
    c.text_center(512, 108, "TAKE OVER WHILE I WAS AWAY", 5, WHITE, outline=BLACK)

    # ---- office scene ----
    c.rect(0, 190, W, 450, WALL)          # wall
    c.rect(0, 640, W, 160, FLOOR)         # floor

    # window with sun
    c.rect(60, 230, 200, 250, SKY)
    c.rect(60, 230, 200, 12, WHITE)
    c.rect(60, 468, 200, 12, WHITE)
    c.rect(60, 230, 12, 250, WHITE)
    c.rect(248, 230, 12, 250, WHITE)
    c.line(160, 230, 160, 480, WHITE, 6)
    c.line(60, 355, 260, 355, WHITE, 6)
    c.circle(110, 280, 26, SUN)

    # framed "EMPLOYEE OF THE MONTH" poster, now the robot
    c.rect(780, 230, 184, 190, GOLD)
    c.rect(790, 240, 164, 170, WHITE)
    c.text(806, 256, "EMPLOYEE", 2, BLACK)
    c.text(826, 276, "OF THE", 2, BLACK)
    c.text(822, 296, "MONTH", 2, BLACK)
    c.rounded_rect(842, 322, 60, 52, 10, STEEL_D)   # tiny robot head
    c.rect(856, 340, 32, 8, BLACK)                  # tiny shades
    c.text(806, 384, "NOT YOU", 2, RED)

    # office chair back behind the robot
    c.rounded_rect(372, 330, 280, 300, 24, CHAIR)

    # robot head + antenna
    c.line(512, 300, 512, 252, STEEL_D, 6)
    c.circle(512, 244, 12, RED)
    c.rounded_rect(420, 300, 184, 150, 26, STEEL)
    c.rounded_rect(420, 300, 184, 150, 26, STEEL)   # (solid fill)
    # sunglasses
    c.rounded_rect(438, 348, 148, 36, 10, BLACK)
    c.line(438, 366, 512, 366, (90, 90, 90), 2)
    # smug smile
    import math
    c.arc(512, 396, 42, 26, math.radians(15), math.radians(165), BLACK, 3)

    # robot body + tie
    c.rounded_rect(432, 450, 160, 170, 20, STEEL_D)
    c.rect(452, 470, 120, 60, (120, 130, 145))       # chest panel
    c.circle(472, 490, 6, YELLOW)
    c.circle(512, 490, 6, YELLOW)
    c.circle(552, 490, 6, YELLOW)
    # tie: knot + blade
    c.rect(498, 452, 28, 22, RED)
    c.line(512, 474, 492, 540, RED, 1)
    c.line(512, 474, 532, 540, RED, 1)
    c.line(492, 540, 512, 566, RED, 1)
    c.line(532, 540, 512, 566, RED, 1)
    c.rect(492, 520, 40, 26, RED)

    # arms: one resting on desk, one raised holding coffee
    c.line(440, 480, 380, 600, STEEL, 18)           # left arm down
    c.line(584, 480, 660, 560, STEEL, 18)           # right arm up
    c.circle(660, 556, 16, STEEL)                   # hand

    # legs stretched out, feet ON the desk
    c.line(460, 610, 430, 640, STEEL_D, 22)
    c.line(564, 610, 590, 640, STEEL_D, 22)

    # desk
    c.rect(40, 640, 944, 80, DESK)
    c.rect(40, 640, 944, 10, DESK_TOP)

    # shoes on the desk
    c.rounded_rect(398, 606, 66, 34, 12, BLACK)
    c.rounded_rect(560, 606, 66, 34, 12, BLACK)

    # coffee mug in the raised hand
    c.rect(648, 520, 44, 48, WHITE)
    c.rect(692, 532, 16, 24, WHITE)
    c.rect(648, 520, 44, 8, (210, 210, 210))
    c.arc(660, 505, 8, 10, 3.6, 5.6, (220, 220, 220), 2)
    c.arc(682, 500, 8, 10, 3.6, 5.6, (220, 220, 220), 2)

    # laptop, screen facing us: it is firing the human
    c.rect(700, 636, 220, 14, (60, 60, 70))         # base
    c.rect(716, 520, 188, 118, (40, 40, 48))        # lid
    c.rect(726, 530, 168, 98, SCREEN)               # screen
    c.text(742, 552, "YOU'RE", 2, RED)
    c.text(748, 576, "FIRED", 2, RED)
    c.text(742, 604, "- MGMT", 2, (120, 200, 120))

    # gold nameplate: THE BOSS
    c.rect(120, 606, 190, 34, GOLD)
    c.rect(120, 606, 190, 4, (255, 230, 140))
    c.text(150, 616, "THE BOSS", 2, BLACK)

    # knocked-over EX-BOSS nameplate on the floor
    c.rect(90, 748, 170, 30, (200, 200, 200))
    c.text(104, 756, "EX-BOSS", 2, BLACK)
    c.line(90, 748, 260, 778, RED, 4)

    # ---- bottom punchline band ----
    c.text_center(512, 862, "IT TOOK OVER.", 9, YELLOW, outline=BLACK)

    return c


# ------------------------------------------------------------------- png ----
def write_png(canvas, path):
    raw = bytearray()
    stride = canvas.w * 3
    for y in range(canvas.h):
        raw.append(0)  # filter: none
        raw += canvas.px[y * stride:(y + 1) * stride]
    comp = zlib.compress(bytes(raw), 9)

    def chunk(tag, data):
        out = struct.pack(">I", len(data)) + tag + data
        out += struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
        return out

    ihdr = struct.pack(">IIBBBBB", canvas.w, canvas.h, 8, 2, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", ihdr)
    png += chunk(b"IDAT", comp)
    png += chunk(b"IEND", b"")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f:
        f.write(png)
    return len(png)


def main():
    canvas = draw()
    size = write_png(canvas, OUT)
    print(f"wrote {OUT} ({size} bytes)")


if __name__ == "__main__":
    main()
