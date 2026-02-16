import usb.device
from usb.device.keyboard import KeyboardInterface

class Keyboard:
    def __init__(self) -> None:
        self.kbd = KeyboardInterface()
        usb.device.get().init(self.kbd)
    def send_keys(self, keys):
        # keys is a iterable with byte(8 bit int, hex or binary) elements
        self.kbd.send_keys(keys)

    def get_modifiers(self, frame) -> list:
        mod_byte = frame[3]
        mods_keys = []

        # Modifier bits mapping:
        # Bit: 0=LCtrl, 1=LShift, 2=LAlt, 3=LWin, 4=RCtrl, 5=RShift, 6=RAlt, 7=RWin
        if mod_byte & 0x01: mods_keys.append(-0x01) # LEFT_CTRL
        if mod_byte & 0x10: mods_keys.append(-0x10) # RIGHT_CTRL
        if mod_byte & 0x02: mods_keys.append(-0x02) # LEFT_SHIFT
        if mod_byte & 0x20: mods_keys.append(-0x20) # RIGHT_SHIFT
        if mod_byte & 0x04: mods_keys.append(-0x04) # LEFT_ALT
        if mod_byte & 0x40: mods_keys.append(-0x40) # RIGHT_ALT
        if mod_byte & 0x08: mods_keys.append(-0x08) # LEFT_UI
        if mod_byte & 0x80: mods_keys.append(-0x80) # RIGHT_UI

        return mods_keys

    def get_keys(self, frame) -> list:
        # We use a list comprehension to filter out 0x00 (no key pressed)
        return [k for k in frame[5:11] if k != 0x00]

    def _get_all_keys(self, frame) -> list:
        all_keys = self.get_modifiers(frame)
        all_keys.extend(self.get_keys(frame))
        return all_keys

    def emulate(self, frame):
        keys = self._get_all_keys(frame)
        self.send_keys(keys)
