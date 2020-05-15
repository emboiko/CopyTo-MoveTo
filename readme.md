# CopyTo-MoveTo
<p align="center">
	<img src="https://i.imgur.com/VRKKDms.png">
	<img src="https://i.imgur.com/7oTlfM6.png">
    <img src="https://i.imgur.com/wLcGVgL.png">
</p>

## Basic Installation and Usage:

~~Download & extract the .zip, and run `CopyTo-MoveTo Installer.exe`~~

(Installer is still in development)

**-or-**

`git clone https://github.com/emboiko/CopyTo-MoveTo.git`

`python CopyTo-MoveTo/src/main.py`

**-or-**

Run `CopyTo-MoveTo.exe` from within its source directory using a shortcut, and merge the registry keys manually.

---

**Now featuring IPC:** CopyTo-MoveTo should only allow one copy of itself to exist at a time. Additional instances will pass their arguments to the main process, where they flow into the GUI

Installation wizard & regkeys automation made with [Inno Setup](https://jrsoftware.org/isinfo.php)
(Not working all the way yet)
