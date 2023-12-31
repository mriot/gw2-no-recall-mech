import ctypes
import mmap
import sys
import time
import json
import threading
import argparse

from pystray import Icon, Menu, MenuItem
from PIL import Image
import keyboard


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
    def __init__(self, tray: Icon, hotkey: str):
        self.tray = tray
        self.hotkey = hotkey
        self.hk = None

    def suppress(self):
        self.hk = keyboard.add_hotkey(self.hotkey, lambda: None, suppress=True)
        self.tray.notify(f"{self.hotkey.upper()} DISABLED", " ")

    def release(self):
        if not self.hk:
            return None
        keyboard.remove_hotkey(self.hk)
        self.hk = None
        self.tray.notify(f"{self.hotkey.upper()} ENABLED", " ")


def getForegroundWindowTitle() -> str:
    user32 = ctypes.windll.user32
    hwnd = user32.GetForegroundWindow()
    title_length = 256
    title_buffer = ctypes.create_unicode_buffer(title_length)
    user32.GetWindowTextW(hwnd, title_buffer, title_length)
    return title_buffer.value


def observer(mumble_link: MumbleLink, hotkey: HotkeyManager) -> None:
    was_mech_before = False

    while True:
        if getForegroundWindowTitle() != "Guild Wars 2":
            hotkey.release()
            time.sleep(5)
            continue

        mumble_link.read()

        if not mumble_link.data.uiTick:
            print("Waiting for data...")
            continue

        # print(mumble_link.data.identity)

        id = json.loads(str(mumble_link.data.identity))

        if id.get("profession") == 3 and id.get("spec") == 70:
            if not was_mech_before:
                hotkey.suppress()
            was_mech_before = True
        else:
            if was_mech_before:
                hotkey.release()
            was_mech_before = False

        time.sleep(2)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--hotkey",
        help="Specify the hotkey that should be deactivated while playing Mech.\n\nFor modifier keys, use the following format: ctrl+shift+k.",
        default="f4",
    )

    icon = Image.open("mech.png")
    tray = Icon(
        "GW2 Mech Detector",
        title="GW2 Mech Detector",
        icon=icon,
        menu=Menu(MenuItem("Exit", lambda: tray.stop())),
    )

    try:
        args = parser.parse_args()
    except argparse.ArgumentError as e:
        tray.notify("❌ Error with arguments", str(e))
        sys.exit(1)

    hkm = HotkeyManager(tray, args.hotkey)

    try:
        ml = MumbleLink()
        threading.Thread(target=observer, args=(ml, hkm), daemon=True).start()
    except Exception as e:
        tray.notify("❌ Error with MumbleLink", str(e))
        sys.exit(1)

    tray.run()
    ml.close()


if __name__ == "__main__":
    main()
