# No Recall Mech (Guild Wars 2 Tool)

This tool disables your keybind for <img src="https://github.com/mriot/mriot/assets/24588573/48ea15fe-030f-4d2b-951b-c0029d58aa5c" align="top" height="30" alt="recall mech skill icon"> [Recall Mech](https://wiki.guildwars2.com/wiki/Recall_Mech)  while you are playing as mechanist.

**Why?**  
"Recall Mech" sends your Mech into oblivion which can be quite annoying if you are in the middle of a fight and accidentally press the hotkey (default <kbd>F4</kbd>).

Your keybind is only disabled while you are playing as an engineer with the Mechanist spec active.  
If you tab out of the game or change your build to another spec, the keybind will be immediately restored.

## Usage

Download `NoRecallMech.exe` from the [latest release](https://github.com/mriot/gw2-no-recall-mech/releases) and place it anywhere you want.  
[Is this a virus?](#is-it-a-virus) <small>(spoiler: no)</small>

You can start the tool before launching GW2 or after, it will detect the game either way.  
While it runs a little Mechanist icon <img src="./mech.png" align="top" height="22" alt="mech"> will show in your system tray. Right click it to exit.

### Keybind

You can customize which keybind will be disabled by providing it as a command line argument.

Supported modifier keys are: `ctrl`, `alt`, `shift` and `windows`.

#### Examples

<kbd>F4</kbd> (default)  
`NoRecallMech.exe --hotkey=f4`

<kbd>Shift</kbd> + <kbd>4</kbd>  
`NoRecallMech.exe --hotkey=shift+4`

<kbd>Control</kbd>+<kbd>Shift</kbd>+<kbd>1</kbd>  
`NoRecallMech.exe --hotkey=ctrl+shift+1`

<kbd>Alt</kbd> + <kbd>Shift</kbd> + <kbd>S</kbd>  
`NoRecallMech.exe --hotkey=alt+shift+s`

#### 💡 Tip: Create a shortcut

You can create a shortcut to this tool and add the command line argument to the target field.  
Like this: `"C:\path\to\NoRecallMech.exe" --hotkey=f4`

## Limitations

### Notifications

Sometimes if you start the tool and then immediately tab into the game, the **first** notification may fail to show but the keybind will still be suppressed.

### Keybind blocking

In GW2, keybinds function even when other keys are pressed simultaneously, allowing you to walk while casting a skill.  
This, however, makes it a bit challenging to suppress specific keybinds. To address this, the tool identifies all simultaneously pressed keys and checks if your hotkey is among them.  
If that's the case, the keypress event will be suppressed.

As a result, if you continuously hold your hotkey down, subsequent keypresses will not be detected by the game.

However, in my tests, this wasn't really an issue. In fact I didn't even notice it at all as you typically tap the hotkey briefly by accident rather than holding it down for extended periods.

#### Chat, search and other text inputs

While GW2 does provide a way to detect if _certain_ text input fields are focused, not all are covered.  
This means, your keybinds will not work while those fields are focused.  

However, the most common ones like the chat, inventory, LFG, bank, hero panel, squad broadcast, mail, etc work just fine.  

What's not covered are the search fields in the trading post and the party menu <kbd>p</kbd>.  

## FAQ

### How does it work? Is it safe?

Yes, pretty safe I'd say. It uses the offical [Mumble Link API](https://wiki.guildwars2.com/wiki/API:MumbleLink) to detect if you are playing as an engineer with a Mechanist build active.  
Your hotkey for "Recall Mech" gets caught and suppressed before it reaches the game.  
The tool does not interact with the game at all.

### Is it a virus?

No of course not. Review the code and pack it yourself to be extra safe. 🙂  
It might get detected as a keylogger by your antivirus software. This is because it hooks keyboard events in order to suppress them.

## Setup for development

> Python 3.12

Create a virtual environment and install the dependencies:

```bash
pip install pyinstaller -r requirements.txt
```

Build the .exe with pyinstaller. See [build.bat](./build.bat)

## Credits

- Gw2 Wiki Contributors for the [MumbleLink example code](https://wiki.guildwars2.com/wiki/API:MumbleLink/Example_implementation_(Python))
- App icon "Mechanist" by ArenaNet

---

## Disclaimer

This project is independent and not affiliated with ArenaNet, Guild Wars 2, or any of their partners. All copyrights are reserved to their respective owners. The use of any trademarks, logos, or other intellectual property of ArenaNet, Guild Wars 2, or their partners is purely for descriptive and informational purposes.

This tool's purpose is to enhance user experience within the context of Guild Wars 2. While we strive for accuracy and reliability, we cannot guarantee the tool's compatibility with all systems or the accuracy of the information presented. Users should exercise their own discretion and adhere to the terms of service and policies of Guild Wars 2.

By using this tool, you acknowledge that any reliance on the tool or its information is at your own risk. We disclaim any liability for damages or losses incurred, directly or indirectly, as a result of the use or reliance on this project.

This disclaimer is subject to change without notice, and it is advisable to review periodically for any updates. If you do not agree with any part of this disclaimer, we recommend refraining from using the tool.
