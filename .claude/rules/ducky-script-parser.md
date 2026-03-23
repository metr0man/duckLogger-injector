# Ducky Script Parser Rules

## Supported Command Subset

Only the following Ducky Script commands are supported. Do not implement or silently ignore unsupported commands — raise a descriptive parse error instead.

| Command | Syntax | Description |
|---|---|---|
| `STRING` | `STRING <text>` | Type a string of characters |
| `DELAY` | `DELAY <ms>` | Wait for a number of milliseconds |
| `ENTER` | `ENTER` | Press and release Enter |
| `GUI` | `GUI <key>` | Win/Super key + optional key (e.g. `GUI r`) |
| `SHIFT` | `SHIFT <key>` | Shift + a key (e.g. `SHIFT TAB`) |
| `CTRL` | `CTRL <key>` | Ctrl + a key (e.g. `CTRL c`) |
| `ALT` | `ALT <key>` | Alt + a key (e.g. `ALT F4`) |

Modifier combos (e.g. `CTRL SHIFT <key>`) are not supported in this subset.

## Frame Format Contract

Every keystroke produced by the parser **must** be expressed as an 11-byte CH9350 UART frame:

```
[0x57, 0xAB, 0x01, mod_byte, 0x00, key1, key2, key3, key4, key5, key6]
```

| Byte(s) | Value | Meaning |
|---|---|---|
| 0–2 | `0x57 0xAB 0x01` | Fixed magic header |
| 3 | `mod_byte` | Modifier bitmask (see below) |
| 4 | `0x00` | Reserved, always zero |
| 5–10 | `key1..key6` | Up to 6 simultaneous HID keycodes; pad unused slots with `0x00` |

### Modifier Bitmask

| Bit | Mask | Key |
|---|---|---|
| 0 | `0x01` | Left Ctrl |
| 1 | `0x02` | Left Shift |
| 2 | `0x04` | Left Alt |
| 3 | `0x08` | Left GUI (Win/Super) |
| 4 | `0x10` | Right Ctrl |
| 5 | `0x20` | Right Shift |
| 6 | `0x40` | Right Alt |
| 7 | `0x80` | Right GUI |

Use left-hand modifier bits by default. Only set right-hand bits if the source explicitly requires it.

### Key Press / Release Cycle

Each logical keypress must be two frames sent back-to-back:
1. **Press frame** — `mod_byte` and `key` slots populated.
2. **Release frame** — all bytes `0x00` except the fixed header: `[0x57, 0xAB, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]`.

Skipping the release frame will cause keys to appear held on the target.

### `STRING` Expansion

Each character in a `STRING` argument must be looked up in `logger.py`'s `key_map` / `key_map_shift` to obtain its HID keycode. Characters requiring Shift must set bit `0x02` in `mod_byte`. Characters not present in either keymap must raise a parse error — do not silently drop them.

### `DELAY` Handling

`DELAY` does not produce a UART frame. It produces an `asyncio.sleep(ms / 1000)` await point in the injection coroutine. See `opsec-guidelines.md` for the no-blocking rule.
