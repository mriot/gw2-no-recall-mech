import argparse
import ctypes
import json
import mmap
import os
import sys
import threading
import time

import keyboard
from PIL import Image
from pystray import Icon, Menu, MenuItem


class Link(ctypes.Structure):
    _fields_ = [
        ("uiVersion", ctypes.c_uint32),  # 4 bytes
        ("uiTick", ctypes.c_ulong),  # 4 bytes
        ("fAvatarPosition", ctypes.c_float * 3),  # 3*4 bytes
        ("fAvatarFront", ctypes.c_float * 3),  # 3*4 bytes
        ("fAvatarTop", ctypes.c_float * 3),  # 3*4 bytes
        ("name", ctypes.c_wchar * 256),  # 512 bytes
        ("fCameraPosition", ctypes.c_float * 3),  # 3*4 bytes
        ("fCameraFront", ctypes.c_float * 3),  # 3*4 bytes
        ("fCameraTop", ctypes.c_float * 3),  # 3*4 bytes
        ("identity", ctypes.c_wchar * 256),  # 512 bytes
        ("context_len", ctypes.c_uint32),  # 4 bytes
        # ("context", ctypes.c_ubyte * 256),      # 256 bytes, see below
        # ("description", ctypes.c_wchar * 2048), # 4096 bytes, always empty
    ]


class Context(ctypes.Structure):
    _fields_ = [
        ("serverAddress", ctypes.c_ubyte * 28),  # 28 bytes
        ("mapId", ctypes.c_uint32),  # 4 bytes
        ("mapType", ctypes.c_uint32),  # 4 bytes
        ("shardId", ctypes.c_uint32),  # 4 bytes
        ("instance", ctypes.c_uint32),  # 4 bytes
        ("buildId", ctypes.c_uint32),  # 4 bytes
        ("uiState", ctypes.c_uint32),  # 4 bytes
        ("compassWidth", ctypes.c_uint16),  # 2 bytes
        ("compassHeight", ctypes.c_uint16),  # 2 bytes
        ("compassRotation", ctypes.c_float),  # 4 bytes
        ("playerX", ctypes.c_float),  # 4 bytes
        ("playerY", ctypes.c_float),  # 4 bytes
        ("mapCenterX", ctypes.c_float),  # 4 bytes
        ("mapCenterY", ctypes.c_float),  # 4 bytes
        ("mapScale", ctypes.c_float),  # 4 bytes
        ("processId", ctypes.c_uint32),  # 4 bytes
        ("mountIndex", ctypes.c_uint8),  # 1 byte
    ]


class MumbleLink:
    data = Link
    context = Context

    def __init__(self):
        self.size_link = ctypes.sizeof(Link)
        self.size_context = ctypes.sizeof(Context)
        size_discarded = (
            256 - self.size_context + 4096
        )  # empty areas of context and description

        # GW2 won't start sending data if memfile isn't big enough so we have to add discarded bits too
        memfile_length = self.size_link + self.size_context + size_discarded

        self.memfile = mmap.mmap(fileno=-1, length=memfile_length, tagname="MumbleLink")

    def read(self):
        self.memfile.seek(0)

        self.data = self.unpack(Link, self.memfile.read(self.size_link))
        self.context = self.unpack(Context, self.memfile.read(self.size_context))

    def close(self):
        self.memfile.close()

    @staticmethod
    def unpack(ctype, buf):
        cstring = ctypes.create_string_buffer(buf)
        ctype_instance = ctypes.cast(
            ctypes.pointer(cstring), ctypes.POINTER(ctype)
        ).contents
        return ctype_instance


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
        if self.keyboard_hook:
            return None

        self.keyboard_hook = keyboard.hook(self._on_key_event, suppress=True)
        self.tray.notify(f"{self.hotkey.upper()} DISABLED", " ")

    def release(self):
        if not self.keyboard_hook:
            return None

        keyboard.unhook(self.keyboard_hook)
        self.keyboard_hook = None
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


def getForegroundWindowTitle() -> str:
    user32 = ctypes.windll.user32
    hwnd = user32.GetForegroundWindow()
    title_length = 256
    title_buffer = ctypes.create_unicode_buffer(title_length)
    user32.GetWindowTextW(hwnd, title_buffer, title_length)
    return title_buffer.value


def observer(mumble_link: MumbleLink, hotkey: HotkeyManager, tray: Icon) -> None:
    while True:
        if getForegroundWindowTitle() != "Guild Wars 2":
            hotkey.release()
            print("GW2 not in focus...")
            time.sleep(1)
            continue

        mumble_link.read()

        if not mumble_link.data.uiTick:
            print("Waiting for MumbleLink data...")
            time.sleep(1)
            continue

        # print(mumble_link.data.identity)
        id = json.loads(str(mumble_link.data.identity))

        if id.get("profession") == 3 and id.get("spec") == 70:
            print("Mech detected!")
            hotkey.suppress()
        else:
            print("Not a mech...")
            hotkey.release()

        time.sleep(1)


def main():
    if getattr(sys, "frozen", False):
        os.environ["BUNDLE_DIR"] = sys._MEIPASS  # type: ignore
    else:
        os.environ["BUNDLE_DIR"] = os.path.dirname(os.path.abspath(__file__))

    icon = Image.open(os.path.join(os.environ["BUNDLE_DIR"], "mech.png"))
    tray = Icon(
        "GW2 NoRecallMech",
        title="GW2 NoRecallMech",
        icon=icon,
        menu=Menu(MenuItem("Exit", lambda: tray.stop())),
    )

    try:
        parser = argparse.ArgumentParser(description="GW2 NoRecallMech")
        parser.add_argument(
            "--hotkey",
            help="Specify the hotkey that should be deactivated while playing as machanist.\n\nUse the format: ctrl+shift+k.",
            default="f4",
        )
        args = parser.parse_args()
        hkm = HotkeyManager(args.hotkey, tray)
    except argparse.ArgumentError as e:
        tray.notify("❌ Error with hotkey", str(e))
        sys.exit(1)

    try:
        ml = MumbleLink()
        threading.Thread(target=observer, args=(ml, hkm, tray), daemon=True).start()
    except Exception as e:
        tray.notify("❌ Error with MumbleLink", str(e))
        sys.exit(1)

    tray.run()
    ml.close()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(e)
