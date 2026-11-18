#!/usr/bin/env python3
"""Cut the sticker spritesheets (assets/sticker-sheets/sheet*.png, 6 x 5 stickers each)
into one square PNG per sticker in stickers/, and write stickers/index.json (id, name,
search words) for the app's sticker picker.

Run from the repo root after changing a sheet or a name:
    python tools/slice_stickers.py

Needs Pillow and numpy. Each sticker is found as the parts of the sheet that are clearly
visible (alpha >= 64) whose center lies in its grid cell. Everything else (the faint
noise between stickers) is cleared, so the PNGs have clean transparent edges.
"""
import json
import os
import sys
from collections import deque

import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SHEETS = os.path.join(ROOT, "assets", "sticker-sheets")
OUT = os.path.join(ROOT, "stickers")
COLS, ROWS, SIZE = 6, 5, 192

# One list per sheet, row by row. "name|extra search words".
NAMES = [
    ["Air horn|horn loud", "Applause|clap hands", "Rimshot|drum ba dum tss", "Crickets|cricket silence",
     "Sad trombone|fail trombone", "Trophy|victory win cup",
     "Drumroll|drumsticks", "Record scratch|vinyl dj", "Laughing|laugh lol emoji", "Stopwatch|countdown timer",
     "Unimpressed|bruh meh emoji", "Magic hat|ta-da tada magic",
     "Service bell|ding bell", "Whistle|referee", "Siren|alarm alert police", "Megaphone|announcement",
     "Party popper|confetti celebrate", "Microphone|mic voice",
     "Rubber chicken|squeak", "Rubber duck|quack squeak", "Dog|bark woof", "Cat|meow", "Frog|ribbit croak",
     "Ghost|boo spooky",
     "Explosion|boom bang", "Thunderstorm|thunder lightning rain", "Water drop|drip splash", "Fire|flame burn",
     "Coin|money ding", "Rocket|launch space"],
    ["Alarm clock|ring wake", "Telephone|ring phone", "Bike horn|honk clown", "Door knocker|knock door",
     "Gavel|judge order court", "Key card|door hotel beep",
     "Joystick|arcade game", "Gamepad|controller game", "Pixel heart|life game", "Treasure chest|loot gems",
     "Ray gun|laser pew", "Portal|vortex warp",
     "Banana peel|slip", "Toaster|toast pop ding", "Chattering teeth|teeth wind-up", "Whoopee cushion|fart",
     "Jack in the box|clown surprise", "Popcorn|pop movie",
     "Wolf|howl", "Owl|hoot", "Bee|buzz", "Lion|roar", "Crow|caw bird", "Pig|oink snort",
     "Cymbals|crash", "Tambourine|jingle", "Triangle|ding", "Electric guitar|guitar riff rock",
     "Accordion|music", "Maracas|shake"],
    ["Clapperboard|action movie film", "Film projector|movie reel", "Director's chair|movie",
     "Creaky door|door creak", "UFO|alien spaceship", "Chains|rattle",
     "Kettle|whistle steam", "Frying pan|sizzle egg", "Boiling pot|bubble soup", "Blender|whirr",
     "Soda can|open fizz drink", "Fortune cookie|crack",
     "Foam finger|number one fan", "Checkered flag|race finish", "Yellow flag|penalty", "Basketball|bounce",
     "Bowling|strike pins", "Hockey puck|slap shot",
     "Typewriter|typing ding", "Instant camera|photo shutter", "Stapler|staple", "Fan|whirr wind",
     "Washing machine|laundry", "Drill|power tool",
     "Violin|music strings", "Saxophone|sax jazz", "Harmonica|blues", "Tuba|brass", "Music box|melody",
     "Kazoo|buzz"],
    ["Steam train|choo choo whistle", "Taxi|car honk", "Helicopter|chopper", "Tugboat|ship horn boat",
     "Skateboard|skate", "Subway|metro train",
     "Modem|dial-up internet", "Floppy disk|save computer", "VHS tape|video rewind", "Printer|dot matrix",
     "TV static|television noise", "Flip phone|ring vibrate",
     "Dragon|roar", "Potion|bubble magic", "Spell book|magic", "Crystal ball|magic fortune",
     "Skull|spooky laugh", "Magic wand|sparkle spell",
     "Wind|gust breeze leaf", "Wave|ocean sea splash", "Rain|tent camping storm", "Woodpecker|peck knock bird",
     "Dolphin|click splash", "Cicada|bug insect",
     "Bubble gum|pop", "Sponge|squish", "Pogo stick|boing bounce", "Balloon|deflate air",
     "Duct tape|rip tear", "Slurp|drink straw cup"],
    ["Cash register|ka-ching money", "Buzzer|button wrong game show", "Slot machine|jackpot casino",
     "Gong|bang", "Dice|roll", "Prize wheel|spin wheel",
     "Hair clippers|buzz", "Ribbon cutting|scissors snip", "Zipper|zip", "Click pen|pen click",
     "Hole punch|punch", "Rubber stamp|stamp approved",
     "Choir|sing hallelujah", "Ocarina|flute", "Bagpipes|music", "Xylophone|music", "Washboard|scrub",
     "Didgeridoo|music",
     "Walrus|roar", "Donkey|hee-haw bray", "Peacock|call bird", "Sheep|baa", "Rattlesnake|rattle snake hiss",
     "Lobster|crab pinch",
     "Champagne|pop cork celebrate", "Ice|crack freeze", "Rocking chair|creak", "Crumpled paper|crumple",
     "Dominoes|fall", "Teacup|spoon clink tea"],
    ["Curtains|stage theater show", "Intercom|speaker announcement", "Tap shoe|dance tap",
     "Sad mask|drama theater cry", "Velvet rope|vip", "Bouquet|flowers roses",
     "Saw|wood cut", "Vise|clamp", "Tape measure|snap", "Sanding|sandpaper", "Ratchet|wrench click",
     "Hammer|nail bang",
     "Pickle jar|jar pop open", "Taco|crunch", "Microwave|beep ding", "Pepper grinder|grind",
     "Chips|crunch bag snack", "Apple|bite crunch",
     "Boombox|music radio", "Gramophone|record old music", "Reel-to-reel|tape recorder",
     "Walkie-talkie|radio over", "CD player|disc music", "Headphones|music",
     "Kangaroo|hop jump", "Zebra|call", "Loon|bird call lake", "Beaver|tail slap", "Whale|song spout",
     "Elephant|trumpet"],
]


def slug(name):
    s = "".join(c.lower() if c.isalnum() else "-" for c in name.replace("'", ""))
    return "-".join(p for p in s.split("-") if p)


def components(mask):
    """Label the 4-connected parts of a boolean mask (a small mask, so plain BFS is fine).
    Returns a list of (pixel index arrays ys, xs)."""
    h, w = mask.shape
    seen = np.zeros_like(mask, dtype=bool)
    out = []
    for y0, x0 in zip(*np.nonzero(mask)):
        if seen[y0, x0]:
            continue
        q = deque([(y0, x0)])
        seen[y0, x0] = True
        ys, xs = [], []
        while q:
            y, x = q.popleft()
            ys.append(y)
            xs.append(x)
            for ny, nx in ((y - 1, x), (y + 1, x), (y, x - 1), (y, x + 1)):
                if 0 <= ny < h and 0 <= nx < w and mask[ny, nx] and not seen[ny, nx]:
                    seen[ny, nx] = True
                    q.append((ny, nx))
        out.append((np.array(ys), np.array(xs)))
    return out


BODY = 800  # a part this big (on the small mask) is a sticker's main shape, not a "sound line"


def _shift_or(m):
    g = m.copy()
    g[1:] |= m[:-1]; g[:-1] |= m[1:]; g[:, 1:] |= m[:, :-1]; g[:, :-1] |= m[:, 1:]
    return g


def split_touching(parts, cell_of, cw, ch):
    """Some stickers touch their neighbor, so they come out as one part and a cell is left
    empty. Such a part is shrunk until it falls apart into two shapes, then each pixel goes
    back to the shape it grows back from first."""
    for _ in range(COLS * ROWS):
        bodies = [p for p in parts if len(p[0]) >= BODY]
        empty = set(range(COLS * ROWS)) - {cell_of(*p) for p in bodies}
        if not empty:
            return parts
        e = min(empty)
        er, ec = divmod(e, COLS)

        def overlap(p):  # how far a body reaches into the empty cell
            ys, xs = p
            return np.count_nonzero((xs // cw == ec) & (ys // ch == er))
        big = max(bodies, key=overlap)
        if overlap(big) == 0:
            sys.exit(f"no sticker found in cell {e}")
        ys, xs = big
        y0, x0 = ys.min() - 1, xs.min() - 1
        mask = np.zeros((ys.max() - y0 + 2, xs.max() - x0 + 2), dtype=bool)
        mask[ys - y0, xs - x0] = True
        core = mask
        for _ in range(40):
            core = ~_shift_or(~core)  # erode by one pixel
            pieces = [p for p in components(core) if len(p[0]) >= 100]
            if len(pieces) >= 2:
                break
        else:
            sys.exit(f"couldn't separate the stickers around cell {e}")
        label = np.zeros(mask.shape, dtype=np.int32)
        for i, (py, px) in enumerate(pieces, 1):
            label[py, px] = i
        while True:  # grow the pieces back inside the original shape
            free = mask & (label == 0)
            if not free.any():
                break
            grown = label.copy()
            for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                shifted = np.roll(label, (dy, dx), axis=(0, 1))
                take = free & (grown == 0) & (shifted > 0)
                grown[take] = shifted[take]
            if (grown == label).all():
                break  # pixels no piece can reach (cut off by the erosion): left out
            label = grown
        parts = [p for p in parts if p is not big]
        for i in range(1, len(pieces) + 1):
            py, px = np.nonzero(label == i)
            parts.append((py + y0, px + x0))
    return parts


def assign(parts, cell_of):
    """Each cell's sticker: its main shape, plus the small parts (sound lines, sparkles)
    nearest to it."""
    bodies = {}
    for p in parts:
        if len(p[0]) >= BODY:
            bodies.setdefault(cell_of(*p), []).append(p)
    keys = list(bodies)
    pts = {c: np.concatenate([np.stack(b, 1) for b in bodies[c]])[::4] for c in keys}
    cells = {c: list(bodies[c]) for c in keys}
    for p in parts:
        if len(p[0]) >= BODY:
            continue
        mine = np.stack(p, 1)[::4].astype(float)
        best = min(keys, key=lambda c: np.min(((pts[c][None, :, :] - mine[:, None, :]) ** 2).sum(-1)))
        cells[best].append(p)
    return [cells.get(i, []) for i in range(COLS * ROWS)]


def main():
    os.makedirs(OUT, exist_ok=True)
    index, ids = [], set()
    for n, names in enumerate(NAMES, 1):
        sheet = Image.open(os.path.join(SHEETS, f"sheet{n}.png")).convert("RGBA")
        W, H = sheet.size
        arr = np.array(sheet)
        alpha = arr[:, :, 3]
        k = 3  # find the parts on a 1/3-size mask (fast), then use them at full size
        small = alpha[::k, ::k] >= 64
        cw, ch = W / COLS, H / ROWS

        def cell_of(ys, xs):
            return min(ROWS - 1, int(ys.mean() * k // ch)) * COLS + min(COLS - 1, int(xs.mean() * k // cw))

        parts = [p for p in components(small) if len(p[0]) >= 30]  # (not specks)
        parts = split_touching(parts, cell_of, cw / k, ch / k)
        cells = assign(parts, cell_of)
        for i, label in enumerate(names):
            name, _, words = label.partition("|")
            parts = cells[i]
            if not parts:
                sys.exit(f"sheet{n}: nothing found for {name}")
            keep = np.zeros_like(small)
            for ys, xs in parts:
                keep[ys, xs] = True
            # Back to full size, grown by a few pixels to keep each sticker's soft edge.
            full = np.kron(keep, np.ones((k, k), dtype=bool))[:H, :W]
            grown = full.copy()
            for _ in range(2):
                grown = _shift_or(grown)
            px = arr.copy()
            px[~grown] = 0
            px[px[:, :, 3] < 8] = 0  # last of the faint noise
            ys, xs = np.nonzero(px[:, :, 3])
            x0, x1, y0, y1 = xs.min(), xs.max() + 1, ys.min(), ys.max() + 1
            crop = Image.fromarray(px[y0:y1, x0:x1])
            side = max(crop.size)
            square = Image.new("RGBA", (side, side), (0, 0, 0, 0))
            square.paste(crop, ((side - crop.width) // 2, (side - crop.height) // 2))
            square = square.resize((SIZE, SIZE), Image.LANCZOS)
            sid = slug(name)
            if sid in ids:
                sys.exit(f"duplicate sticker id {sid}")
            ids.add(sid)
            square.save(os.path.join(OUT, sid + ".png"), optimize=True)
            index.append({"id": sid, "name": name, "words": words})
    with open(os.path.join(OUT, "index.json"), "w", encoding="utf-8") as f:
        json.dump(index, f, indent=1, ensure_ascii=False)
    print(f"{len(index)} stickers written to {OUT}")


if __name__ == "__main__":
    main()
