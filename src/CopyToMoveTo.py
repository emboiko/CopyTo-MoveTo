from tkinter import(
    PanedWindow,
    BooleanVar,
    Menu,
    Label,
    Listbox,
    Scrollbar,
    Toplevel,
    Text,
    messagebox,
)
from shutil import copy2, move, rmtree, copytree
from os.path import dirname, join, split, splitext, exists, isfile, isdir
from os import mkdir, sep, remove, getenv
from platform import system
from json import dumps, loads
from functools import wraps
from threading import Thread

from Ufd.Ufd import Ufd


class CopyToMoveTo:
    """
        Minimalist file manager intended to be used independently
        or alongside Windows Explorer
    """

    def __init__(self, root):
        """
            Setup window geometry, init settings, define widgets + layout
        """
        self.master = root
        self.master.title("CopyTo-MoveTo")
        self.master.iconbitmap(f"{dirname(__file__)}/icon.ico")

        if system() != "Windows":
            self.master.withdraw()
            messagebox.showwarning(
                "Incompatible platform",
                "CopyTo-MoveTo currently supports Windows platforms only."
            )
            raise SystemExit

        #Settings:
        self.settings_show_hidden=BooleanVar()
        self.settings_include_files=BooleanVar(value=True)
        self.settings_ask_overwrite=BooleanVar()
        self.settings_ask_overwrite.trace("w", self.settings_exclusives)
        self.settings_rename_dupes=BooleanVar(value=True)
        self.settings_rename_dupes.trace("w", self.settings_exclusives)
        self.settings_multiselect=BooleanVar(value=True)
        self.settings_select_dirs=BooleanVar(value=True)
        self.settings_select_dirs.trace("w", self.settings_mutuals)
        self.settings_select_files=BooleanVar(value=True)
        self.settings_select_files.trace("w", self.settings_mutuals)
        self.settings_geometry = None

        self.appdata_dir = getenv("APPDATA") + "/CopyTo-MoveTo"
        self.appdata_path = self.appdata_dir + "/settings.json"
        self.settings=self.init_settings()

        if self.settings:
            self.settings_geometry = self.settings["geometry"]
            self.settings_show_hidden.set(self.settings["show_hidden"])
            self.settings_include_files.set(self.settings["include_files"])
            self.settings_ask_overwrite.set(self.settings["ask_overwrite"])
            self.settings_rename_dupes.set(self.settings["rename_dupes"])
            self.settings_multiselect.set(self.settings["multiselect"])
            self.settings_select_dirs.set(self.settings["select_dirs"])
            self.settings_select_files.set(self.settings["select_files"])

        self.dialog_showing=BooleanVar()
        self.help_showing=BooleanVar()
        self.about_showing=BooleanVar()

        self.master.protocol("WM_DELETE_WINDOW", self.master_close)
        self.master.bind("<Control-w>", self.master_close)

        #Geometry:
        self.master.minsize(width=450, height=200)

        if self.settings_geometry:
            self.master.geometry(self.settings_geometry)
            self.master.update()
        else:
            self.master.geometry("600x400")
            self.master.update_idletasks()
            (width_offset, height_offset)=Ufd.get_offset(self.master)
            self.master.geometry(f"+{width_offset}+{height_offset}")
            self.master.update_idletasks()


        # Menu:
        self.main_menu=Menu(self.master)
        self.master.config(menu=self.main_menu)

        self.file_menu=Menu(self.main_menu, tearoff=0)
        self.settings_menu=Menu(self.main_menu, tearoff=0)
        self.main_menu.add_cascade(label="File", menu=self.file_menu)
        self.main_menu.add_cascade(label="Settings", menu=self.settings_menu)

        self.file_menu.add_command(
            label="Open Source(s)",
            accelerator="Ctrl+O",
            command=lambda: self.show_ufd(source=True)
        )
        self.master.bind(
            "<Control-o>",
            lambda event: self.show_ufd(source=True)
        )

        self.file_menu.add_command(
            label="Open Destination(s)",
            accelerator="Ctrl+K+O",
            command=lambda: self.show_ufd(source=False)
        )
        self.master.bind(
            "<Control-k>o",
            lambda event: self.show_ufd(source=False)
        )

        self.file_menu.add_separator()
        self.file_menu.add_command(label="Help / Commands", command=self.show_help)
        self.file_menu.add_command(label="About", command=self.show_about)

        #Settings menu:
        self.settings_menu.add_checkbutton(
            label="Show Hidden Files & Folders",
            variable=self.settings_show_hidden,
            onvalue=True,
            offvalue=False
        )

        self.settings_menu.add_checkbutton(
            label="Include Files in Tree",
            variable=self.settings_include_files,
            onvalue=True,
            offvalue=False
        )

        self.settings_menu.add_separator()

        self.settings_menu.add_checkbutton(
            label="Ask Overwrite",
            variable=self.settings_ask_overwrite,
            onvalue=True,
            offvalue=False
        )

        self.settings_menu.add_checkbutton(
            label="Rename Duplicates",
            variable=self.settings_rename_dupes,
            onvalue=True,
            offvalue=False
        )

        self.settings_menu.add_separator()

        self.settings_menu.add_checkbutton(
            label="Multiselect",
            variable=self.settings_multiselect,
            onvalue=True,
            offvalue=False
        )

        self.settings_menu.add_checkbutton(
            label="Select Folders",
            variable=self.settings_select_dirs,
            onvalue=True,
            offvalue=False
        )

        self.settings_menu.add_checkbutton(
            label="Select Files",
            variable=self.settings_select_files,
            onvalue=True,
            offvalue=False
        )
        
        self.main_menu.add_separator()

        #Menu commands:
        self.main_menu.add_command(
            label="Swap Selected",
            command=self.swap_selected
        )
        self.master.bind("<Control-s>", lambda event: self.swap_selected())
        
        self.main_menu.add_command(
            label="Clear Selected",
            command=self.clear_selected
        )
        self.master.bind("<Control-x>", lambda event: self.clear_selected())

        self.main_menu.add_command(
            label="Clear All",
            command=self.clear_all
        )
        self.master.bind("<Control-Shift-X>", lambda event: self.clear_all())

        self.main_menu.add_separator()

        self.main_menu.add_command(
            label="COPY",
            command=lambda: self._submit(copy=True)
        )
        self.master.bind(
            "<Control-Shift-Return>",
            lambda event: self._submit(copy=True)
        )

        self.main_menu.add_command(
            label="MOVE",
            command=lambda: self._submit(copy=False)
        )
        self.master.bind(
            "<Control-Return>",
            lambda event: self._submit(copy=False)
        )

        # Body:
        self.paneview = PanedWindow(
            self.master,
            sashwidth=7,
            bg="#cccccc",
            bd=0,
            orient="vertical"
        )

        self.top_pane = PanedWindow(self.paneview)
        self.bottom_pane = PanedWindow(self.paneview)
        self.paneview.add(self.top_pane)
        self.paneview.add(self.bottom_pane)

        self.label_source = Label(self.top_pane, text="Source(s):")
        self.label_dest = Label(self.bottom_pane, text="Destination(s):")

        self.y_scrollbar_source=Scrollbar(self.top_pane, orient="vertical")
        self.x_scrollbar_source=Scrollbar(self.top_pane, orient="horizontal")
        self.y_scrollbar_dest=Scrollbar(self.bottom_pane, orient="vertical")
        self.x_scrollbar_dest=Scrollbar(self.bottom_pane, orient="horizontal")

        self.list_box_source=Listbox(
            self.top_pane,
            selectmode="extended",
            yscrollcommand=self.y_scrollbar_source.set,
            xscrollcommand=self.x_scrollbar_source.set
        )

        self.list_box_dest=Listbox(
            self.bottom_pane,
            selectmode="extended",
            yscrollcommand=self.y_scrollbar_dest.set,
            xscrollcommand=self.x_scrollbar_dest.set
        )

        self.x_scrollbar_source.config(command=self.list_box_source.xview)
        self.y_scrollbar_source.config(command=self.list_box_source.yview)
        self.x_scrollbar_dest.config(command=self.list_box_dest.xview)
        self.y_scrollbar_dest.config(command=self.list_box_dest.yview)

        # Layout:
        self.master.rowconfigure(0, weight=1)
        self.master.columnconfigure(0, weight=1)

        self.top_pane.rowconfigure(1, weight=1)
        self.top_pane.columnconfigure(0, weight=1)
        self.bottom_pane.rowconfigure(1, weight=1)
        self.bottom_pane.columnconfigure(0, weight=1)

        self.paneview.paneconfigure(self.top_pane, minsize=100)
        self.paneview.paneconfigure(self.bottom_pane, minsize=100)

        self.paneview.grid(row=0, column=0, sticky="nsew")

        self.label_source.grid(row=0, column=0, sticky="w")
        self.list_box_source.grid(row=1, column=0, sticky="nsew")
        self.y_scrollbar_source.grid(row=1, column=1, sticky="ns")
        self.x_scrollbar_source.grid(row=2, column=0, sticky="ew")

        self.label_dest.grid(row=0, column=0, sticky="w", columnspan=2)
        self.list_box_dest.grid(row=1, column=0, sticky="nsew")
        self.y_scrollbar_dest.grid(row=1, column=1, sticky="ns")
        self.x_scrollbar_dest.grid(row=2, column=0, sticky="ew")


    def __str__(self):
        """Return own address"""

        return f"CopyTo-MoveTo @ {hex(id(self))}"


    def init_settings(self):
        """Called on startup, loads, parses, and returns json settings."""


        if exists(self.appdata_path):
            with open(self.appdata_path, "r") as settings_file:
                settings_json=settings_file.read()

            settings=loads(settings_json)
            return settings
        else:
            return None


    def settings_exclusives(self, *args):
        """
            Callback assigned to settings that are mutually exclusive, 
            to prevent logical/runtime errors or unexpected behavior.
        """

        if args[0] == "PY_VAR3":
            if self.settings_ask_overwrite.get() == 1:
                self.settings_rename_dupes.set(0)
                return 

        elif args[0] == "PY_VAR4":        
            if self.settings_rename_dupes.get() == 1:
                self.settings_ask_overwrite.set(0)
                return 


    def settings_mutuals(self, *args):
        """
            Prevent select folders & select files from being disabled concurrently

            If both are unselected, reselect the one we didn't just deselect on.
        """

        if self.settings_select_dirs.get() == 0 \
        and self.settings_select_files.get() == 0:

            if args[0] == "PY_VAR7":
                self.settings_select_files.set(1)
        
            elif args[0] == "PY_VAR8":
                self.settings_select_dirs.set(1)


    def master_close(self, event=None):
        """
            Similar to utils.toplevel_close().
            writes settings to the disk as json.
        """

        settings={
            "geometry" : self.master.geometry(),
            "show_hidden" : self.settings_show_hidden.get(),
            "include_files" : self.settings_include_files.get(),
            "ask_overwrite" : self.settings_ask_overwrite.get(),
            "rename_dupes" : self.settings_rename_dupes.get(),
            "multiselect" : self.settings_multiselect.get(),
            "select_dirs" : self.settings_select_dirs.get(),
            "select_files" : self.settings_select_files.get(),
        }

        settings_json=dumps(settings)

        if not exists(self.appdata_dir):
            mkdir(self.appdata_dir)

        with open(self.appdata_path, "w+") as settings_file:
            settings_file.write(settings_json)

        if self.dialog_showing.get() == 1:
            self.ufd.cancel()

        self.master.destroy()


    def toplevel_close(self, dialog, boolean):
        """
            This callback flips the value for a given toplevel_showing boolean
            to false, before disposing of the toplevel.
        """

        boolean.set(0)
        dialog.destroy()


    def swap_selected(self):
        """Swap list entries between source & destination"""

        source_selection = list(self.list_box_source.curselection())
        dest_selection = list(self.list_box_dest.curselection())

        for i in reversed(source_selection):
            item = self.list_box_source.get(i)
            self.list_box_source.delete(i)
            self.list_box_dest.insert("0", item)


        for i in reversed(dest_selection):
            item = self.list_box_dest.get(i)
            self.list_box_dest.delete(i)
            self.list_box_source.insert("0", item)


    def clear_selected(self):
        """Removes selected (highlighted) item(s) from a given listbox"""

        source_selection = list(self.list_box_source.curselection())
        dest_selection = list(self.list_box_dest.curselection())

        if source_selection:
            for i in reversed(source_selection):
                self.list_box_source.delete(i)

            self.list_box_source.selection_set(source_selection[0])

        if dest_selection:
            for i in reversed(dest_selection):
                self.list_box_dest.delete(i)

            self.list_box_dest.selection_set(dest_selection[0])

    def clear_all(self):
        """Clears both listboxes in the main UI, resetting the form."""

        self.list_box_source.delete(0, "end")
        self.list_box_dest.delete(0, "end")


    def handled(fn):
        """Filesystem operations are wrapped here for error handling"""

        @wraps(fn)
        def inner(self, *args, **kwargs):
            try:
                fn(self, *args, **kwargs)
                return True
            except (PermissionError, FileNotFoundError) as err:
                self.skipped_err.append(
                    f"{err.args[1]}:\n" + (" => ".join(args))
                )
                return False

        return inner


    @handled
    def _copy(self, path, destination):
        """Wrapper for shutil.copy2() || shutil.copytree()"""

        if isfile(path):
            copy2(path, destination)
        else:
            copytree(path, destination)


    @handled
    def _move(self, path, destination):
        """Wrapper for shutil.move()"""

        move(path, destination)


    @handled
    def _delete(self, path):
        """Wrapper for os.remove() || shutil.rmtree()"""

        if isfile(path):
            remove(path)
        elif isdir(path):
            rmtree(path)


    def disabled_ui(fn):
        """Menubar is disabled during operations"""

        @wraps(fn)
        def inner(self, *args, **kwargs):
            self.main_menu.entryconfig("File", state="disabled")
            self.main_menu.entryconfig("Settings", state="disabled")
            self.main_menu.entryconfig("Clear Selected", state="disabled")
            self.main_menu.entryconfig("Clear All", state="disabled")
            self.main_menu.entryconfig("COPY", state="disabled")
            self.main_menu.entryconfig("MOVE", state="disabled")

            fn(self, *args, **kwargs)

            self.main_menu.entryconfig("File", state="normal")
            self.main_menu.entryconfig("Settings", state="normal")
            self.main_menu.entryconfig("Clear Selected", state="normal")
            self.main_menu.entryconfig("Clear All", state="normal")
            self.main_menu.entryconfig("COPY", state="normal")
            self.main_menu.entryconfig("MOVE", state="normal")

        return inner


    def _submit(self, copy):
        """Thread/wrapper for submit() so we don't block the UI during operations"""

        self.thread = Thread(target=self.submit, args=(copy,), daemon=True)
        self.thread.start()


    @disabled_ui
    def submit(self, copy):
        """
            Move or copy each item in the origin list to the path in the
            destination list. Supports no more than one destination directory
            where copy == False.

            Ask Overwrite and Rename Dupes will alter the way we handle 
            existing data standing in the way. By default, duplicates are 
            renamed with an index. A messagebox can complain to the user
            if shutil raises a PermissionError, and the operation is skipped.
        """

        if (self.list_box_dest.size() > 1) and not copy:
            messagebox.showwarning(
                "Invalid Operation",
                "Move operation only supports a single destination directory."
            )
            return

        sources = self.list_box_source.get(0,"end")
        destinations =  self.list_box_dest.get(0,"end")

        self.skipped_err = []

        for j, destination in enumerate(destinations):

            if isfile(destination):
                self.skipped_err.append(f"Invalid destination: {destination}")
                continue

            for i, source in enumerate(sources):
                self.progress(i, j)

                (_, filename) = split(source)
                future_destination = join(destination + sep, filename)

                if exists(future_destination):
                    if not self.settings_ask_overwrite.get() \
                    and not self.settings_rename_dupes.get():

                        if not self._delete(future_destination):
                            continue

                    if self.settings_ask_overwrite.get():

                        if self.ask_overwrite(future_destination):    
                            if not self._delete(future_destination):
                                continue

                        else:
                            continue

                    if self.settings_rename_dupes.get():
                        future_destination = self.name_dupe(future_destination)
                        
                if copy:
                    if not self._copy(source, future_destination):
                        continue
                else:
                    if not self._move(source, future_destination):
                        continue

        self.list_box_source.delete(0, "end")
        self.list_box_dest.delete(0, "end")

        if self.skipped_err:
                messagebox.showerror(
                    title="Error(s)",
                    message="\n\n".join(self.skipped_err)
                )


    @staticmethod
    def name_dupe(path):
        """
            Renames the file or directory until it doesn't exist
            in the destination with that name anymore, by appending
            the filename with an index wrapped in parenthesis.
            (Windows platforms)
            file.txt => file (1).txt => file (2).txt
        """

        if system() != "Windows":
            raise OSError("For use with Windows filesystems.")

        path_ = path
        (root, filename) = split(path_)

        if isdir(path_):
            title=filename
            ext = None
        else:
            (title, ext)=splitext(filename)

        filecount=0
        while exists(path_):
            filecount += 1
            new_title=title + " (" + str(filecount) + ")"
            if ext:
                new_title = new_title + ext
            path_ = join(root, new_title)

        return path_


    def ask_overwrite(self, future_destination):
        """Messagebox result returned as truth value"""

        return messagebox.askyesno(
            title="Path Conflict",
            message=f"Overwrite:\n\n{future_destination}?\n\n" \
            f"YES - Overwrite\nNO - Skip"
        )


    def progress(self, i, j):
        """
            Visualize operands in GUI during operations

            i = current source operand index
            j = current destination operand index
        """

        for y, _ in enumerate(self.list_box_source.get(0, "end")):
            if y != i:
                self.list_box_source.itemconfigure(y, bg="#FFFFFF", fg="#000000")
            else:
                self.list_box_source.itemconfigure(y, bg="#cccccc", fg="#000000")

        for x, _ in enumerate(self.list_box_dest.get(0, "end")):
            if x != j:
                self.list_box_dest.itemconfigure(x, bg="#FFFFFF", fg="#000000")
            else:
                self.list_box_dest.itemconfigure(x, bg="#cccccc", fg="#000000")

        self.master.update()


    #Toplevels:
    def show_about(self):
        """
            Displays a static dialog that doesn't allow additional
            instances of itself to be created while showing.
        """

        if self.about_showing.get() == 0:
            self.about_showing.set(1)

            try:
                with open(f"{dirname(__file__)}/about.txt", "r") as aboutfile:
                    about_info=aboutfile.read()
            except FileNotFoundError:
                messagebox.showerror("Error", "File not found")
                self.about_showing.set(0)
                return

            else:
                self.about=Toplevel()
                self.about.title("About")
                self.about.iconbitmap(f"{dirname(__file__)}/icon.ico")

                self.about.geometry("600x400")
                self.about.resizable(0,0)
                self.about.update_idletasks()
                (width_offset, height_offset)=Ufd.get_offset(self.about)
                self.about.geometry(f"+{width_offset-75}+{height_offset-75}")
                self.about.update_idletasks()

                self.about_message=Label(
                    self.about,
                    text=about_info,
                    justify="left",
                    wraplength=(self.about.winfo_width() - 25)
                )

                self.about_message.grid(sticky="nsew")

                self.about.protocol(
                    "WM_DELETE_WINDOW",
                    lambda: self.toplevel_close(self.about, self.about_showing)
                )


    def show_help(self):
        """
            Displays a scrollable dialog that doesn't allow additional
            instances of itself to be created while showing.
        """

        if self.help_showing.get() == 0:
            self.help_showing.set(1)

            try:
                with open(f"{dirname(__file__)}/help.txt", "r") as helpfile:
                    help_info=helpfile.read()
            except FileNotFoundError:
                messagebox.showerror("Error", "File not found")
                self.help_showing.set(0)
                return

            else:
                self.help_window=Toplevel()
                self.help_window.title("Help")
                self.help_window.iconbitmap(f"{dirname(__file__)}/icon.ico")

                self.help_window.geometry("500x300")
                self.help_window.update_idletasks()
                (width_offset, height_offset)=Ufd.get_offset(self.help_window)
                self.help_window.geometry(f"+{width_offset+75}+{height_offset-75}")
                self.help_window.update_idletasks()

                self.message_y_scrollbar=Scrollbar(self.help_window, orient="vertical")

                self.help_text=Text(
                    self.help_window,
                    wrap="word",
                    yscrollcommand=self.message_y_scrollbar.set
                )

                self.help_window.rowconfigure(0, weight=1)
                self.help_window.columnconfigure(0, weight=1)

                self.help_text.grid(row=0, column=0, sticky="nsew")
                self.message_y_scrollbar.grid(row=0, column=1, sticky="nse")

                self.message_y_scrollbar.config(command=self.help_text.yview)

                self.help_text.insert("end", help_info)
                self.help_text.config(state="disabled")

                self.help_window.protocol(
                    "WM_DELETE_WINDOW",
                    lambda: self.toplevel_close(self.help_window, self.help_showing)
                )


    def show_ufd(self, source=True):
        """ Display Ufd w/ appropriate kwargs => Populate GUI w/ result"""

        if self.dialog_showing.get() == 0:
            self.dialog_showing.set(1)

            self.ufd = Ufd(
                title="Add Items",
                show_hidden=self.settings_show_hidden.get(),
                include_files=self.settings_include_files.get(),
                multiselect=self.settings_multiselect.get(),
                select_dirs=self.settings_select_dirs.get(),
                select_files=self.settings_select_files.get(),
                unix_delimiter=False,
                stdout=False
            )

            for result in self.ufd():
                if source:
                    self.list_box_source.insert("end",result)
                else:
                    self.list_box_dest.insert("end",result)

            self.dialog_showing.set(0)
