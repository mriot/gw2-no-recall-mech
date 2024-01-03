# No Recall Mech (Guild Wars 2 Tool)

This little tool disables your keybind for <img src="https://github.com/mriot/mriot/assets/24588573/48ea15fe-030f-4d2b-951b-c0029d58aa5c" height="16" alt="recall mech skill icon">[Recall Mech](https://wiki.guildwars2.com/wiki/Recall_Mech)  while you are playing as mechanist.

**Why?**  
"Recall Mech" sends your Mech into oblivion which can be quite annoying if you are in the middle of a fight and accidentally press the hotkey (default <kbd>F4</kbd>).

Your keybind is only managed while Guild Wars 2 is running and you are playing as an engineer with the Mechanist spec equipped.  
If you tab out of the game, the keybind will be immediately restored.

## Usage

Download `NoRecallMech.exe` from the [latest release](/) and place it anywhere you want.

While it runs a little Mechanist icon <img src="./mech.png" height="20" alt="mech"> will show in your system tray.  
Right click the icon to exit.

### Keybind

You can customize which hotkey will be disabled by providing it as a command line argument.

Supported modifier keys are: `ctrl`, `alt`, `shift` and `windows`.

For example, if you want to disable the hotkey <kbd>Control</kbd>+<kbd>Shift</kbd>+<kbd>1</kbd> you would start the program like this:

`NoRecallMech.exe --hotkey=ctrl+shift+1`

For <kbd>F5</kbd>  
`NoRecallMech.exe --hotkey=f5`

For <kbd>Alt</kbd> + <kbd>Shift</kbd> + <kbd>S</kbd>  
`NoRecallMech.exe --hotkey=alt+shift+s`

#### Tip: Create a shortcut

You can create a shortcut to this tool and add the command line argument to the target field.  
Like this: `"C:\path\to\NoRecallMech.exe" --hotkey=f4`

## Limitations

### Notifications

Sometimes if you start the tool and then immediately tab into the game, the first notification will fail to show but the keybind should still be suppressed (if you are playing as a mechanist).

### Keybinds

Keybinds in GW2 function even when additional keys are pressed simultaneously, enabling you to walk while casting a skill.  
However, suppressing specific keybinds can be a bit challenging. This tool identifies all simultaneously pressed keys and checks if your hotkey is among them.  
If so, the keypress event will be suppressed.
As a result, if you continuously hold your hotkey down, subsequent keypresses will not be detected by the game.

In my tests, this wasn't really an issue. In fact I barely noticed it at all as you typically tap the hotkey briefly by accident rather than holding it down for extended periods.

## FAQ

### How does it work? Is it safe?

Yes, pretty safe I'd say. It uses the offical [Mumble Link API](https://wiki.guildwars2.com/wiki/API:MumbleLink) to detect if you are playing as an engineer with a Mechanist build active.  
Your hotkey for "Recall Mech" gets caught and suppressed before it reaches the game.  
The tool does not interact with the game at all.

### Why not use class specific keybinds?

I play about 6 builds on the engineer and I don't want to unbind <kbd>F4</kbd> every time I switch to a mech build.

### Is it a virus?

No. You can check the code and pack it yourself if you don't trust me. :)  
It might get detected as a keylogger by your antivirus software since it hooks keyboard events.

## Setup for development

> Python 3.12

Create a virtual environment and install the dependencies:

```bash
python -m venv .venv; .venv\Scripts\activate; pip install pyinstaller -r requirements.txt
```

Build using pyinstaller: See [build.bat](./build.bat)

## Credits

- Gw2 Wiki Contributors for the [MumbleLink example code](https://wiki.guildwars2.com/wiki/API:MumbleLink/Example_implementation_(Python))
- App icon: "Mechanist" icon by ArenaNet

---

## Disclaimer

This project is independent and not affiliated with ArenaNet, Guild Wars 2, or any of their partners. All copyrights are reserved to their respective owners. The use of any trademarks, logos, or other intellectual property of ArenaNet, Guild Wars 2, or their partners is purely for descriptive and informational purposes.

This tool's purpose is to enhance user experience within the context of Guild Wars 2. While we strive for accuracy and reliability, we cannot guarantee the tool's compatibility with all systems or the accuracy of the information presented. Users should exercise their own discretion and adhere to the terms of service and policies of Guild Wars 2.

By using this tool, you acknowledge that any reliance on the tool or its information is at your own risk. We disclaim any liability for damages or losses incurred, directly or indirectly, as a result of the use or reliance on this project.

This disclaimer is subject to change without notice, and it is advisable to review periodically for any updates. If you do not agree with any part of this disclaimer, we recommend refraining from using the tool.
