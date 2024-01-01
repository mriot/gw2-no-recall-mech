# No Recall Mech (Guild Wars 2 Tool)

This little tool disables your keybind for <img src="https://github.com/mriot/mriot/assets/24588573/48ea15fe-030f-4d2b-951b-c0029d58aa5c" height="16" alt="recall mech skill icon">[Recall Mech](https://wiki.guildwars2.com/wiki/Recall_Mech)  while you are playing as mechanist.

"Recall Mech" sends your mech into oblivion which can be quite annoying if you are in the middle of a fight and accidentally press the hotkey (default <kbd>F4</kbd>).

You will still be able to press the skill with the mouse or by using another keybind.

> If Guild Wars 2 is not running or not focused or you are not playing as a Mechanist, the keybind will work as usual.

## Usage

Download `NoRecallMech.exe` from the [latest release](/) and place it anywhere you want.

It will display a little Mechanist icon <img src="./mech.png" height="20" alt="mech"> in your system tray once started.  
Right click the icon to exit.

### Keybind

You can customize which hotkey will be disabled by providing it as a command line argument.

For example, if you want to disable the hotkey <kbd>Control</kbd>+<kbd>Shift</kbd>+<kbd>1</kbd> you would start the program like this:

`NoRecallMech.exe --hotkey=ctrl+shift+1`

For <kbd>F5</kbd>  
`NoRecallMech.exe --hotkey=f5`

For <kbd>Alt</kbd> + <kbd>Shift</kbd> + <kbd>S</kbd>  
`NoRecallMech.exe --hotkey=alt+shift+s`

Pretty straightforward I think. :)

> Tip: You can create a shortcut to the program and add the command line argument to the target field.
> Like this: `"C:\path\to\NoRecallMech.exe" --hotkey=f4`

## Limitations

- Only works on Windows (key suppression)
- Only works with the Mechanist elite spec

## FAQ

### How does it work? Is it safe?

Yes, it's safe. It uses the offical [Mumble Link API](https://wiki.guildwars2.com/wiki/API:MumbleLink) to detect if you are playing as a Mechanist and the hotkey gets caught and suppressed by the program before it reaches the game.

### Does this work with other classes?

No. It only works with the Mechanist elite spec. But if you got another use case, feel free to open an issue.

### Is it a virus?

No. You can check the code and even pack it yourself if you don't trust me. :)  
It might get detected as a virus by your antivirus software because it's not signed.

## Credits

- Gw2 Wiki Contributors for the [MumbleLink example code](https://wiki.guildwars2.com/wiki/API:MumbleLink/Example_implementation_(Python))
