# Soundboard

**Free, offline soundboard with global hotkeys. No ads, no account, no subscription.**

![Soundboard: a board of sound buttons with stickers and hotkeys, two of them playing](docs/soundboard.png)

Make boards of sound buttons and play them with a click or a hotkey, even while you're in a game or
Discord. Sounds go into the device you choose (for example a virtual cable that Discord or OBS
listens to) and to your own speakers or headphones at the same time, with your microphone mixed in
if you like. Your sounds never leave your computer. Works on Windows and macOS.

## Download
Get the latest version from the [Releases page](https://github.com/collinb0607/soundboard/releases/latest).
Nothing else to install.

| Your computer | Download | First launch |
|---|---|---|
| Windows 10/11 | `Soundboard-Windows.exe` | Windows may show "Windows protected your PC" because the app isn't signed. Click **More info**, then **Run anyway**. The first start takes a few seconds. |
| Mac with Apple Silicon (M1 or newer) | `Soundboard-macOS.zip` | Unzip, then open **Soundboard**. macOS blocks it the first time because the app isn't notarized: open **System Settings → Privacy & Security**, scroll down and click **Open Anyway**. For hotkeys, allow Soundboard under **Accessibility** and **Input Monitoring** there too. |

On an Intel Mac, or any other system, run it from source with Python (below).

## How it works
- **Boards.** Keep sounds for different things on their own boards (say *Reactions*, *Game Night*
  and *Voice Clips*). Click **+** to add one; click the pencil on the open board to rename it, or
  right-click a board for more.
- **Buttons your way.** Each sound has a name, a color (12 presets or any color you pick), a volume
  and a hotkey. Give it one of the 180 built-in stickers, or your own picture (you crop it square).
  A button is either **wide** (icon and name) or **square** (just the icon).
- **Arrange freely.** Click **Arrange** and drag buttons to any spot on the grid, gaps and all.
  Drop one on another to swap them. Click **Done** when you're finished.
- **Hotkeys everywhere.** Any key or combination (F1, Ctrl+Shift+A, Num 5...) plays its sound
  from any app. The key still reaches the game you're in. Only the open board's hotkeys are
  active, so every board can use F1–F12. **Stop all** can have its own hotkey.
- **Sounds overlap.** Play several at once; pressing a playing sound again starts it over.
  Each button shows how far along it is, and **Stop all** silences everything.
- **Safe copies.** Added sounds and pictures are copied into the app's own library, so a board
  keeps working if you move or delete the originals.

## Sharing
| File | What's in it |
|---|---|
| `Name.sound` | One sound: its audio, name, color, button shape and sticker or picture. Hotkey and volume stay with you. **Import sounds** adds them to the open board; **Import…** next to the audio file loads one into the sound you're editing. |
| `Name.soundboard` | A whole board: every sound, where it sits on the grid, and its hotkey and volume. **Import board** adds it as a new board. |

You can also drag sound files, `.sound` or `.soundboard` files onto the window.

## Using it with Discord, OBS or a game
Apps hear the soundboard through a **virtual audio cable**, a free driver that acts like a pair of
speakers and a microphone wired together. On Windows, install
[VB-CABLE](https://vb-audio.com/Cable/). On a Mac, [BlackHole](https://existential.audio/blackhole/).

1. In **Configure**, set **Output device** to the cable's input (VB-CABLE: *CABLE Input*).
2. Tick **Also play on** and pick your headphones or speakers, so you hear the sounds too.
3. Tick **Mix in my microphone** and pick your mic, so people still hear you.
4. In Discord (or OBS, or the game), set the input / microphone to the cable's output
   (VB-CABLE: *CABLE Output*).

Plugged something in after starting the app? Click **Refresh devices**.

## Sound files
WAV, MP3, OGG and FLAC. Any sample rate, mono or stereo.

## Run from source (Python)
### Setup (one time)
1. Install **Python 3.8+** from https://python.org. On Windows, tick **"Add Python to PATH"** during install.
2. Run the app (see below). The first time, it offers to install what it needs (`numpy`,
   `sounddevice`, `soundfile`, `Pillow`, `pynput` and `tkinterdnd2`, about 40 MB). Click **Yes**.
   You won't be asked again.

### Run
```
python soundboard.py        # Windows
python3 soundboard.py       # macOS
```

## Troubleshooting
- **Hotkeys do nothing on a Mac:** allow Soundboard (or Terminal / Python, when running from
  source) in **System Settings → Privacy & Security → Accessibility** and **Input Monitoring**,
  then restart the app.
- **A hotkey doesn't play while typing in the app:** that's on purpose. Hotkeys are ignored while
  you're typing in one of the app's text boxes.
- **Discord doesn't hear the sounds:** check that Discord's input device is the cable's *output*,
  and the soundboard's output device is the cable's *input*.
- **Your boards** are kept in `%APPDATA%\Soundboard` on Windows and
  `~/Library/Application Support/Soundboard` on a Mac.
- **Something fails with no message:** errors are also written to `soundboard_errors.log` in your
  temp folder. On Windows, paste `%TEMP%\soundboard_errors.log` into File Explorer's address bar.
  On Mac, run `open $TMPDIR/soundboard_errors.log`.

## For developers
- `tools/slice_stickers.py` cuts the sticker sheets in `assets/sticker-sheets/` into `stickers/`
  (one PNG each, plus `index.json` with their names and search words).
- `tools/build_assets.py` draws the app icon and the extra UI icons.

## Credits
The UI icons are from [Lucide](https://lucide.dev) (ISC license, see [assets/LUCIDE-LICENSE.txt](assets/LUCIDE-LICENSE.txt)).

## Support this project
This app is free, with no ads, accounts or limits. If it saved you time or a subscription, you can
support its development on Ko-fi:

[![Support me on Ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/collinbrooksdev)

## Part of the Offline Toolkit
Also by me: [Audio Converter](https://github.com/collinb0607/audio-converter), which turns videos
or audio into MP3 or WAV (handy for making sound clips), and
[Video Compressor](https://github.com/collinb0607/video-compressor), which shrinks a video to fit
Discord's upload limit.
