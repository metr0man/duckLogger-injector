from logger import key_map, key_map_shift

# --- Constants -----------------------------------------------------------

_RELEASE = bytearray([0x57, 0xAB, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])

_MOD = {
    'CTRL':  0x01,
    'SHIFT': 0x02,
    'ALT':   0x04,
    'GUI':   0x08,
}

# Named keys accepted as the argument to GUI/SHIFT/CTRL/ALT and ENTER.
_NAMED_KEY = {
    'ENTER':     40,
    'ESC':       41,
    'ESCAPE':    41,
    'BACKSPACE': 42,
    'TAB':       43,
    'SPACE':     44,
    'DELETE':    76,
    'DEL':       76,
    'INSERT':    73,
    'INS':       73,
    'HOME':      74,
    'END':       77,
    'PAGEUP':    75,
    'PAGEDOWN':  78,
    'UP':        82,
    'DOWN':      81,
    'LEFT':      80,
    'RIGHT':     79,
    'F1':  58, 'F2':  59, 'F3':  60, 'F4':  61,
    'F5':  62, 'F6':  63, 'F7':  64, 'F8':  65,
    'F9':  66, 'F10': 67, 'F11': 68, 'F12': 69,
    # Single letter keys for combos like GUI r, CTRL c
    'A':  4, 'B':  5, 'C':  6, 'D':  7, 'E':  8, 'F':  9, 'G': 10,
    'H': 11, 'I': 12, 'J': 13, 'K': 14, 'L': 15, 'M': 16,
    'N': 17, 'O': 18, 'P': 19, 'Q': 20, 'R': 21, 'S': 22,
    'T': 23, 'U': 24, 'V': 25, 'W': 26, 'X': 27, 'Y': 28, 'Z': 29,
}

_LETTER_KEYCODES = frozenset(range(4, 30))  # a–z

# --- Reverse keymap (built once at import) --------------------------------
#
# Maps a single printable character to (keycode, needs_shift).
# Priority: key_map (no-shift) is loaded first, then key_map_shift fills
# in chars not yet seen (uppercase letters, shifted symbols).
# Negative keycodes (modifier pseudo-entries) and multi-char labels
# (e.g. "[ENTER]\n") are skipped.

_char_to_key = {}

for _kc, _ch in key_map.items():
    if _kc >= 0 and len(_ch) == 1:
        _char_to_key[_ch] = (_kc, False)

for _kc, _ch in key_map_shift.items():
    if _kc >= 0 and len(_ch) == 1 and _ch not in _char_to_key:
        _char_to_key[_ch] = (_kc, True)

# --- Helpers --------------------------------------------------------------

def _frame(mod_byte, keycode):
    f = bytearray(11)
    f[0] = 0x57; f[1] = 0xAB; f[2] = 0x01
    f[3] = mod_byte
    f[5] = keycode
    return f


def _lookup_named(cmd, token):
    key = token.upper()
    if key not in _NAMED_KEY:
        raise ValueError("{}: unsupported key {!r}".format(cmd, token))
    return _NAMED_KEY[key]


# --- Public API -----------------------------------------------------------

class Delay:
    """Yielded by parse() in place of a frame when a DELAY command is seen."""
    __slots__ = ('ms',)

    def __init__(self, ms):
        self.ms = ms


def parse(script, caps_lock=False):
    """Generator that translates a Ducky Script string into CH9350 frames.

    Yields:
        bytearray (11 bytes) — press or release frame, or
        Delay                — caller must ``await asyncio.sleep(d.ms / 1000)``.

    Each logical keypress produces exactly two consecutive bytearrays:
    a press frame followed by a release frame.

    Args:
        script:    Raw Ducky Script text (newline-separated commands).
        caps_lock: Current KeyboardLED.caps_lock state. Must be supplied
                   so that STRING injection produces the correct case
                   without toggling caps lock on the target.

    Raises:
        ValueError: On any unsupported command or unmappable character.
    """
    for line in script.split('\n'):
        line = line.strip()
        if not line:
            continue

        # ---- STRING ----
        if line.startswith('STRING '):
            for ch in line[7:]:
                if ch not in _char_to_key:
                    raise ValueError("STRING: unsupported character {!r}".format(ch))
                keycode, needs_shift = _char_to_key[ch]
                if keycode in _LETTER_KEYCODES:
                    # XOR with caps_lock: if caps is on, invert the shift
                    # decision so the emitted character matches the intent.
                    shift = needs_shift ^ caps_lock
                else:
                    shift = needs_shift
                yield _frame(0x02 if shift else 0x00, keycode)
                yield bytearray(_RELEASE)

        # ---- DELAY ----
        elif line.startswith('DELAY '):
            raw = line[6:]
            try:
                ms = int(raw)
            except ValueError:
                raise ValueError("DELAY: expected integer milliseconds, got {!r}".format(raw))
            yield Delay(ms)

        # ---- ENTER ----
        elif line == 'ENTER':
            yield _frame(0x00, 40)
            yield bytearray(_RELEASE)

        # ---- GUI <key> ----
        elif line.startswith('GUI '):
            yield _frame(_MOD['GUI'], _lookup_named('GUI', line[4:]))
            yield bytearray(_RELEASE)

        # ---- SHIFT <key> ----
        elif line.startswith('SHIFT '):
            yield _frame(_MOD['SHIFT'], _lookup_named('SHIFT', line[6:]))
            yield bytearray(_RELEASE)

        # ---- CTRL <key> ----
        elif line.startswith('CTRL '):
            yield _frame(_MOD['CTRL'], _lookup_named('CTRL', line[5:]))
            yield bytearray(_RELEASE)

        # ---- ALT <key> ----
        elif line.startswith('ALT '):
            yield _frame(_MOD['ALT'], _lookup_named('ALT', line[4:]))
            yield bytearray(_RELEASE)

        else:
            raise ValueError("Unsupported Ducky Script command: {!r}".format(line))
