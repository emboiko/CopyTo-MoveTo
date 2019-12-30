# CopyTo-MoveTo
***
**Basic Installation and Usage:**
`python CopyTo-MoveTo.py`
**-or-**
Run CopyTo-MoveTo.exe from within its source directory using a shortcut.

Edit + execute `regkeys.reg` with a proper path/to/CopyTo-MoveTo.exe and add it to a context menu! Multiselect an arbitrary number of files and/or directories in Windows Explorer, and gather them in CopyTo-MoveTo

about.txt, help.txt, and the img directory all must exist alongside the main program. A settings.json will also be generated on exit. See help & about more information, keybinds, etc.

**Now featuring IPC:** CopyTo-MoveTo should only allow one copy of itself to exist at a time. Additional instances will pass their first (and only their first*) positional argument to the main process, where they will flow into the GUI's "destination" box.

(*Easily hackable in main.py(The Windows verb invoked in this case splits the selection and passes elements individually to a new & separate process.))

***
12/30/2019
**Due for refactor** 
This project has served double duty as a place to experiement & as a semi-useful application. Version 2.0 will cut out a little bit of fluff via better inheritance & a full refactor with object oriented programming in mind.

CopyTo-MoveTo is still very much in beta and various UI tweaks / improvements are still to come. The file dialog or "Add-Items" will also be refactored to be resuable (and expanded upon, most likely with search + filter features), as it was the entire point of writing this program. Calls to internal commands will most likely be tweaked and improved over time.

If you like or use CopyTo-MoveTo, please considering contributing to the source code, or request a new feature.
***
![](https://i.imgur.com/MVXhTZD.png)
![](https://i.imgur.com/1X8c48Y.png)
![](https://i.imgur.com/XLXe8Nc.png)
