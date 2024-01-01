# import keyboard

# while True:
#     event = keyboard.read_event()
#     if keyboard.is_pressed("shift+1"):
#         print(event)
#         # print("key was pressed")


import keyboard

active_keys = set()


#
def block_hotkey(e):
    global active_keys

    if e.event_type == "down":
        active_keys.add(e.scan_code)
        print("active keys", active_keys)
    elif e.event_type == "up":
        active_keys.discard(e.scan_code)
        return True

    hk = keyboard.key_to_scan_codes("1")

    seq = "shift+1".split("+")
    # print(seq, keyboard.key_to_scan_codes("1"))
    codes = [keyboard.key_to_scan_codes(k)[0] for k in seq]
    print(codes)

    if set(codes).issubset(active_keys):
        print("blocked umschalt+1")
        return False

    # if keyboard.is_pressed("shift+1"):
    #     print("blocked")
    #     return False
    # else:
    #     # print("passed")
    #     return True

    return True


keyboard.hook(block_hotkey, suppress=True)

keyboard.wait()
