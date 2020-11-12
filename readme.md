# CopyTo-MoveTo

CopyTo-MoveTo is a GUI utility for making the process of copying and moving files and/or directories more explicit, and is intended to be used alongside Windows Explorer or by itself. It is built with Python + Tkinter, made for Windows platforms, and is dependency free. The modules listed in `requirements.txt`, [Ufd](https://pypi.org/project/Ufd/) and [Socket_Singleton](https://pypi.org/project/Socket-Singleton/), are former submodules of this repo, and have been packaged on [PyPi](https://pypi.org/). 

<p align="center">
    <img src="https://i.imgur.com/7oTlfM6.png">
	<img src="https://i.imgur.com/VRKKDms.png">
</p>

## Basic Installation and Usage:

Download & extract the .zip, and run `Install CopyTo-MoveTo.exe`

**-or-**

``` 
git clone https://github.com/emboiko/CopyTo-MoveTo.git CopyTo-MoveTo
cd CopyTo-MoveTo/src
python CopyTo-MoveTo/src/main.py 
```

**-or-**

Run `CopyTo-MoveTo.exe` from within its source directory using a shortcut, and merge the registry keys manually.

<img src="https://i.imgur.com/wLcGVgL.png">

- **Now featuring IPC:** CopyTo-MoveTo should only allow one copy of itself to exist at a time. Additional instances will pass their arguments to the main process, where they flow into the GUI

- A `settings.json` will be created in %APPDATA/CopyTo-MoveTo when the program exits for the first time. 

- Installation wizard & regkeys automation made with [Inno Setup](https://jrsoftware.org/isinfo.php)


Shortcuts:
----------

COPY:
- Supports multiple destination directories. 
- Copies the entirety of the origin list, for each item in the destination list
- <Ctrl+Shift+Enter>

MOVE:
- Supports no more/less than a single destination directory. 
- Moves the entirety of the origin list to the path specified in the destination list
- <Ctrl+Enter>

Clear All: 
- Clear entire form
- <Ctrl+Shift+X>

Clear Selection:
- Clear only selected items in a given list
- <Ctrl+X>

Swap Selection:
- Swap selected items in a given list
- <Ctrl+S>

Open Origin(s):
- Show the file-dialog, insert into origin list (top)
- <Ctrl+O>

Open Destination(s):
- Show the file-dialog, insert into destination list (bottom)
- <Ctrl+K+O>

Exit:
- Quit the application
- <Ctrl+W>

Settings:
---

- Show Hidden Files and Folders:
Show system & hidden files in directory listings.

- Include Files in Tree:
Include files alongside directories, with a unique icon.

- Ask Overwrite:
Prompts the user for further action if the program encounters existing files/directories during operation. (Mutually exclusive with Rename Duplicates)

- Rename Duplicates:
Renames the file until a given path conflic is resolved, by appending an index to the filename. (Mutually exclusive with Ask Overwrite)

- Multiselect:
Enable / Disable multiselect in the dialog's list-selection area. 

- Select Folders:
Enable / Disable directory entries in the dialog's list-selection area.

- Select Files:
Enable / Disable file entries in the dialog's list-selection area.

Tips & Tricks:
---

- One instance of the application is allowed to run at a time.

- Run as administrator to avoid permission errors in most situations. Permission errors thrown from a move operation may still result in a copy.

- To enable a context menu entry or entries in Windows Explorer, edit regkeys.reg with a proper path to the application. This makes using CopyTo-MoveTo alongside windows explorer much more streamlined.

- Drill through the treeview with Doubleclick, Enter, or ArrowKeys. Directories are lazy loaded, and only read once.

- Navigate the listbox on the right with the mouse or arrow keys. Multiselect is supported with the Shift, Ctrl, or by dragging the mouse. Select all with <Ctrl+A> as expected. Confirm selection in the filedialog with Enter. 

- Drag + drop files/directories to CopyTo-MoveTo.exe's shortcut to run the application with those paths as arguments. Currently hardcoded to populate to origin listbox.


