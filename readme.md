# CopyTo-MoveTo

CopyTo-MoveTo is a GUI utility for making the process of copying and moving files and/or directories more explicit, and is intended to be used alongside Windows Explorer or by itself. It is built with Python + Tkinter, made for Windows platforms, and is dependency free.

<p align="center">
    <img src="https://i.imgur.com/7oTlfM6.png">
	<img src="https://i.imgur.com/VRKKDms.png">
</p>

## Basic Installation and Usage:

Download & extract the .zip, then install with `CopyTo-MoveTo Installer.exe`

**-or-**

`git clone https://github.com/emboiko/CopyTo-MoveTo.git`

`python CopyTo-MoveTo/src/main.py`

**-or-**

Run `CopyTo-MoveTo.exe` from within its source directory using a shortcut, and merge the registry keys manually.

---

**Now featuring IPC:** CopyTo-MoveTo should only allow one copy of itself to exist at a time. Additional instances will pass their arguments to the main process, where they flow into the GUI

<img src="https://i.imgur.com/wLcGVgL.png">

Installation wizard & regkeys automation made with [Inno Setup](https://jrsoftware.org/isinfo.php)





