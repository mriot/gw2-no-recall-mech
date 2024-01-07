import argparse
import ctypes
import json
import mmap
import os
import sys
from socket import socket
from threading import Thread
from time import sleep

import keyboard
from PIL import Image
from psutil import pid_exists
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


class KeybindManager:
    def __init__(self, keybinds: str, tray: Icon):
        self.tray = tray
        self.keybinds = keybinds
        self.keybind_sets = self._make_keybind_sets()  # scan codes of user keybinds
        self.pressed_keys = set()  # scan codes of all currently pressed keys
        self.keyboard_hook = None

    def _make_keybind_sets(self):
        keybind_sets = []
        for keybind_string in self.keybinds.split(";"):
            keybind_set = set()
            for key in keybind_string.split("+"):
                keybind_set.add(keyboard.key_to_scan_codes(key)[0])
            keybind_sets.append(keybind_set)
        return keybind_sets

    def suppress(self, silent=False):
        if self.keyboard_hook:
            return None

        self.keyboard_hook = keyboard.hook(self._on_key_event, suppress=True)
        if not silent:
            self.tray.notify(f"{" and ".join(self.keybinds.upper().split(";"))} DISABLED", " ")

    def release(self, silent=False):
        if not self.keyboard_hook:
            return None

        keyboard.unhook(self.keyboard_hook)
        self.keyboard_hook = None
        if not silent:
            self.tray.notify("KEYBINDS RELEASED", " ")

    def _on_key_event(self, event):
        if event.event_type == "down":
            self.pressed_keys.add(event.scan_code)
        elif event.event_type == "up":
            self.pressed_keys.discard(event.scan_code)
            return True  # as we are releasing keys, there's no need to go further

        # block our keybind regardless of any additional keys
        for keybind_set in self.keybind_sets:
            if keybind_set.issubset(self.pressed_keys):
                print(f"blocked {self.keybinds}")
                return False  # block

        return True  # pass


def observer(mumble_link: MumbleLink, keybinds: KeybindManager) -> None:
    silenced = False
    while not mumble_link.memfile.closed:
        mumble_link.read()

        # uiState bitmask: 1=MapOpen, 2=CompassTopRight, 3=CompassRotation,
        # 4=GameFocus, 5=Competitive, 6=TextboxFocus, 7=Combat

        # release if GW2 is not running
        if not pid_exists(mumble_link.context.processId):  # type: ignore
            keybinds.release()
            sleep(5) # dont check too often
            continue

        # release if bit 4 is not set (game is not focused)
        if not (int(mumble_link.context.uiState) & 0b0001000):  # type: ignore
            keybinds.release(silent=True)
            silenced = True
            sleep(1)
            continue

        # release if bit 6 is set (textbox is focused)
        if int(mumble_link.context.uiState) & 0b0100000:  # type: ignore
            keybinds.release(silent=True)
            silenced = True
            sleep(0.25) # react faster
            continue

        # print(mumble_link.data.identity)
        id = json.loads(str(mumble_link.data.identity))

        # engineer with mechanist spec
        if id.get("profession") == 3 and id.get("spec") == 70:
            keybinds.suppress(silent=silenced)
        else:
            keybinds.release()

        silenced = False
        sleep(0.5)


def main():
    # mutex to prevent multiple instances of the app
    s = socket()
    s.bind(("127.0.0.1", 57827))
    s.listen(1)

    # get path to unpacked files
    if getattr(sys, "frozen", False):
        unpack_dir = sys._MEIPASS  # type: ignore
    else:
        unpack_dir = os.path.dirname(os.path.abspath(__file__))

    # create tray icon
    icon = Image.open(os.path.join(unpack_dir, "mech.png"))
    tray = Icon(
        "GW2 NoRecallMech",
        title="GW2 NoRecallMech v1.3",
        icon=icon,
        menu=Menu(MenuItem("Exit", lambda: tray.stop())),
    )

    try:
        parser = argparse.ArgumentParser(description="GW2 NoRecallMech")
        parser.add_argument("--keybinds", default="f4")
        args = parser.parse_args()
        hkm = KeybindManager(args.keybinds, tray)
    except argparse.ArgumentError as e:
        tray.notify("❌ Error with keybinds", str(e))
        sys.exit(1)

    try:
        ml = MumbleLink()
        Thread(target=observer, args=(ml, hkm), daemon=True).start()
    except Exception as e:
        tray.notify("❌ Error with MumbleLink", str(e))
        sys.exit(1)

    tray.run()  # blocks until tray.stop() is called
    ml.close()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(e)
