# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

DuckLogger is a MicroPython firmware for ESP32-S3 SuperMini that acts as a USB keystroke logger with pass-through injection. A CH9350 HID module sits between the victim keyboard and the ESP32, converting USB HID data to UART serial. The ESP32 simultaneously logs keystrokes to `log.txt`, re-emits them as USB HID (transparent pass-through), and hosts a Wi-Fi AP + HTTP server for log retrieval.

## Development Workflow

All deployment targets the ESP32-S3 board via `mpremote`.

```bash
# List connected boards
mpremote connect list

# Copy all library files to /lib on device
mpremote cp lib/*.py :/lib/

# Copy main entrypoint
mpremote cp main.py :

# Reboot the board
mpremote reset

# Run a file directly (without copying) for quick testing
mpremote run main.py
```

MicroPython packages installed on the board (not in this repo):
```bash
mpremote mip install usb-device
mpremote mip install usb-device-keyboard
```

## Architecture

### Data Flow

```
USB Keyboard → CH9350 HID Module → UART (115200 baud, TX=GP2, RX=GP1)
                                        ↓
                               UARTBuffer.get_frame()
                                  (11-byte frame)
                                        ↓
                    ┌───────────────────┼───────────────────┐
                    ↓                   ↓                   ↓
             KeyboardLED         Keyboard.emulate()     Log.add()
          (LED state tracking,   (USB HID pass-through   (decode keycodes,
           send LED cmd frame     via usb.device)         buffer → log.txt)
           back to CH9350)
```

### CH9350 Frame Format

Frames are 11 bytes: `[0x57, 0xAB, 0x01, mod_byte, 0x00, key1..key6]`

- `frame[3]`: modifier bitmask (LCtrl=0x01, LShift=0x02, LAlt=0x04, LWin=0x08, RCtrl=0x10, RShift=0x20, RAlt=0x40, RWin=0x80)
- `frame[5:11]`: up to 6 simultaneous HID keycodes (0x00 = no key)

### Module Responsibilities

| File | Role |
|---|---|
| `main.py` | Entry point: blink LED, init UART/objects, run asyncio loop |
| `lib/uart_buffer.py` | Async UART reader; syncs to `0x57 0xAB 0x01` magic header |
| `lib/keyboard.py` | Parses frames, exposes modifier/key lists, emulates USB HID |
| `lib/logger.py` | Translates HID keycodes → chars (two keymaps: normal + shifted), buffers writes, flushes to `log.txt` |
| `lib/key_led.py` | Tracks caps/num/scroll lock state; sends LED control frames (Cmd `0x12`) back over UART to CH9350 |
| `lib/access_point.py` | Starts `network.WLAN` AP (`192.168.4.1`, password `duckPass1234`) |
| `lib/api.py` | Microdot routes: `GET /` returns HTML page, `GET /log` streams `log.txt` |
| `lib/microdot.py` | Vendored copy of [Microdot](https://github.com/miguelgrinberg/microdot) web framework |

### Key Design Details

- `Log` buffers up to 20,000 chars before flushing; also force-flushes every 10 seconds of inactivity from the main loop.
- `KeyboardLED` maintains lock-key state required by `Log._get_press()` to correctly apply shift/caps logic.
- `Keyboard.emulate()` re-emits every intercepted frame as USB HID, making the device transparent to the host PC.
- Modifier keycodes are stored as negative integers (e.g., `-0x01` for LCtrl) to avoid collision with normal HID keycodes in the key maps.
- The asyncio event loop runs a single `main()` coroutine with `app.start_server` as a background task.
