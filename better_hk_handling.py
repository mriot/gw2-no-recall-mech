import os
import sys
import keyboard
from pystray import Icon
from PIL import Image


class HotkeyManager:
    def __init__(self, hotkey: str, tray: Icon):
        self.tray = tray
        self.hotkey = hotkey
        self.hotkey_set = set()  # scan code(s) of our hotkey
        self.active_keys = set()  # scan codes of all currently pressed keys
        self.keyboard_hook = None
        self._make_hotkey_set()

    def _make_hotkey_set(self):
        for key in self.hotkey.split("+"):
            self.hotkey_set.add(
                keyboard.key_to_scan_codes(key)[0]  # not sure what index 1 is for
            )

    def suppress(self):
        print("suppressing")
        self.keyboard_hook = keyboard.hook(self._on_key_event, suppress=True)
        self.tray.notify(f"{self.hotkey.upper()} DISABLED", " ")

    def release(self):
        print("releasing")
        if not self.keyboard_hook:
            return None
        keyboard.unhook(self.keyboard_hook)
        self.tray.notify(f"{self.hotkey.upper()} ENABLED", " ")

    def _on_key_event(self, event):
        if event.event_type == "down":
            self.active_keys.add(event.scan_code)
        elif event.event_type == "up":
            self.active_keys.discard(event.scan_code)
            return True  # as we are releasing keys, there's no need to block

        # block our hotkey regardless of any additional keys
        if self.hotkey_set.issubset(self.active_keys):
            print(f"blocked {self.hotkey}")
            return False  # block

        return True  # pass


# -----------------------------------------------------------------------------------
if getattr(sys, "frozen", False):
    os.environ["BUNDLE_DIR"] = sys._MEIPASS  # type: ignore
else:
    os.environ["BUNDLE_DIR"] = os.path.dirname(os.path.abspath(__file__))

icon = Image.open(os.path.join(os.environ["BUNDLE_DIR"], "mech.png"))

tray = Icon(
    "GW2 NoRecallMech",
    title="GW2 NoRecallMech",
    icon=icon,
)
hkm = HotkeyManager("shift+1", tray)

hkm.suppress()

tray.run()

# -----------------------------------------------------------------------------------
# active_keys = set()


# def block_hotkey(e):
#     global active_keys

#     if e.event_type == "down":
#         active_keys.add(e.scan_code)
#         print("active keys", active_keys)
#     elif e.event_type == "up":
#         active_keys.discard(e.scan_code)
#         return True

#     hk = keyboard.key_to_scan_codes("1")

#     seq = "shift+1".split("+")
#     # print(seq, keyboard.key_to_scan_codes("1"))
#     codes = [keyboard.key_to_scan_codes(k)[0] for k in seq]
#     print(codes)

#     if set(codes).issubset(active_keys):
#         print("blocked umschalt+1")
#         return False

#     # if keyboard.is_pressed("shift+1"):
#     #     print("blocked")
#     #     return False
#     # else:
#     #     # print("passed")
#     #     return True

#     return True


# keyboard.hook(block_hotkey, suppress=True)

# keyboard.wait()
