# CopyTo-MoveTo
<p align="center">
	<img src="https://i.imgur.com/VRKKDms.png">
	<img src="https://i.imgur.com/7oTlfM6.png">
</p>

## Basic Installation and Usage:

`git clone https://github.com/emboiko/CopyTo-MoveTo.git` (or grab the .zip)

`python CopyTo-MoveTo.py`

**-or-**

Run `CopyTo-MoveTo.exe` from within its source directory using a shortcut.

Edit + merge `regkeys.reg` with a proper path/to/CopyTo-MoveTo.exe and add it to a context menu! Multiselect an arbitrary number of files and/or directories in Windows Explorer, and gather them in CopyTo-MoveTo

   <img src="https://i.imgur.com/wLcGVgL.png">

**Now featuring IPC:** CopyTo-MoveTo should only allow one copy of itself to exist at a time. Additional instances will pass their first (and only their first*) positional argument to the main process, where they flow into the GUI

