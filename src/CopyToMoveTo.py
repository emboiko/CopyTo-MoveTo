from tkinter import(
    PhotoImage,
    BooleanVar,
    Menu,
    Label,
    Listbox,
    Toplevel,
    Scrollbar,
    Message,
    Text,
    messagebox,
)
from tkinter.ttk import Treeview
from posixpath import join
from os.path import exists, isdir, split
from os import getcwd
from platform import system
from sys import argv
from json import dumps
from re import split as re_split
from subprocess import run
from utils import (
    flip_slashes,
    init_settings,
    get_disks,
    toplevel_close,
    copy,
    move,
    cleanup,
    name_dupe
)


class CopyToMoveTo:
    """
        Still in beta, use at your own risk.

        Various tweaks and additions are still to come for the UI,
        along with code cleanup / thorough documentation.

        shutil wasn't used on purpose, and is most likely an all around
        better (and more performant) choice for the task. 

        File paths are built and passed around with the "/" forward slash
        delimeter (posixpath.join()), unless being passed as shell arguments, 
        in which case the delimeters are swapped on the fly using flip_slashes()

        This entire program will probably end up getting wrapped or 
        called by a context menu handler that aggregates arguments, in order to 
        deal with multiple instances of the program being instantiated.
        This is triggered by default Windows behavior. Ideally, a context 
        menu entry for Copyto-Moveto will be implemented, so an end-user 
        can multiselect items within windows explorer, and "open with"
        CopyTo-MoveTo.exe. The goal is to mimic the behavior of VSCode and 
        other applications that employ a single instance mode. This will most
        likely be implemented with a lockfile + IPC.
    """

    def __init__(self, root):
        self.master = root
        self.master.title("CopyTo-MoveTo")

        if system() != "Windows":
            self.master.withdraw()
            messagebox.showwarning(
                "Incompatible platform",
                "CopyTo-MoveTo currently supports Windows platforms only."
            )
            quit()

        self.master.geometry("600x400")
        self.master.minsize(width=400, height=200)
        self.master.update()
        (width_offset, height_offset)=self.get_offsets()
        self.master.geometry(f"+{width_offset}+{height_offset}")
        self.master.update()

        self.cwd=flip_slashes(getcwd(), "forward")

        self.file_icon=PhotoImage(file=f"{self.cwd}/src/img/file.gif").subsample(50)
        self.folder_icon=PhotoImage(file=f"{self.cwd}/src/img/folder.gif").subsample(15)
        self.disk_icon=PhotoImage(file=f"{self.cwd}/src/img/disk.gif").subsample(15)

        self.master.iconbitmap(f"{self.cwd}/src/img/main_icon.ico")

        self.settings_show_hidden_files=BooleanVar()
        self.settings_include_files_in_tree=BooleanVar()
        self.settings_tree_xscroll=BooleanVar()
        self.settings_ask_overwrite=BooleanVar()
        self.settings_ask_overwrite.trace("w", self.settings_exclusives)
        self.settings_rename_dupes=BooleanVar()
        self.settings_rename_dupes.trace("w", self.settings_exclusives)

        self.settings=init_settings()

        if self.settings:
            self.settings_show_hidden_files.set(self.settings["show_hidden_files"])
            self.settings_include_files_in_tree.set(self.settings["include_files_in_tree"])
            self.settings_tree_xscroll.set(self.settings["tree_xscroll"])
            self.settings_ask_overwrite.set(self.settings["ask_overwrite"])
            self.settings_rename_dupes.set(self.settings["rename_dupes"])

        self.file_dialog_showing=BooleanVar()
        self.help_showing=BooleanVar()
        self.about_showing=BooleanVar()

        self.master.protocol("WM_DELETE_WINDOW", self.master_close)

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
            command=lambda: self.show_add_items(source=True)
        )
        self.master.bind(
            "<Control-o>",
            lambda event: self.show_add_items(source=True)
        )

        self.file_menu.add_command(
            label="Open Destination(s)",
            accelerator="Ctrl+K+O",
            command=lambda: self.show_add_items(source=False)
        )
        self.master.bind(
            "<Control-k>o",
            lambda event: self.show_add_items(source=False)
        )

        self.file_menu.add_separator()
        self.file_menu.add_command(label="Help / Commands", command=self.show_help)
        self.file_menu.add_command(label="About", command=self.show_about)

        #Settings:
        self.settings_menu.add_checkbutton(
            label="Show Hidden Files & Folders",
            variable=self.settings_show_hidden_files,
            onvalue=True,
            offvalue=False
        )

        self.settings_menu.add_checkbutton(
            label="Include Files in Tree",
            variable=self.settings_include_files_in_tree,
            onvalue=True,
            offvalue=False
        )

        self.settings_menu.add_checkbutton(
            label="Treeview Horizontal Scroll",
            variable=self.settings_tree_xscroll,
            onvalue=True,
            offvalue=False
        )

        self.settings_menu.add_checkbutton(
            label="Ask-Overwrite",
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

        self.main_menu.add_separator()

        self.main_menu.add_command(
            label="Clear Selected",
            accelerator="Ctrl+P",
            command=self.clear_selected
        )
        self.master.bind("<Control-p>", lambda event: self.clear_selected())

        self.main_menu.add_command(
            label="Clear All",
            command=self.clear_all
        )
        self.master.bind("<Control-l>", lambda event: self.clear_all())

        self.main_menu.add_separator()

        self.main_menu.add_command(
            label="COPY",
            command=self.copy_load
        )
        self.master.bind(
            "<Control-Shift-Return>",
            lambda event: self.copy_load()
        )

        self.main_menu.add_command(
            label="MOVE",
            command=self.move_load
        )
        self.master.bind(
            "<Control-Return>",
            lambda event: self.move_load()
        )

        # Body:
        self.label_to = Label(self.master, text="Destination(s):")
        self.label_from = Label(self.master, text="Source(s):")

        self.y_scrollbar_from=Scrollbar(self.master, orient="vertical")
        self.y_scrollbar_to=Scrollbar(self.master, orient="vertical")
        self.x_scrollbar_from=Scrollbar(self.master, orient="horizontal")
        self.x_scrollbar_to=Scrollbar(self.master, orient="horizontal")

        self.list_box_from=Listbox(
            self.master,
            selectmode="extended",
            yscrollcommand=self.y_scrollbar_from.set,
            xscrollcommand=self.x_scrollbar_from.set
        )

        self.list_box_to=Listbox(
            self.master,
            selectmode="extended",
            yscrollcommand=self.y_scrollbar_to.set,
            xscrollcommand=self.x_scrollbar_to.set
        )

        self.x_scrollbar_from.config(command=self.list_box_from.xview)
        self.y_scrollbar_from.config(command=self.list_box_from.yview)
        self.x_scrollbar_to.config(command=self.list_box_to.xview)
        self.y_scrollbar_to.config(command=self.list_box_to.yview)

        # Layout:
        self.master.grid_rowconfigure(1, weight=1)
        self.master.grid_rowconfigure(4, weight=1)
        self.master.grid_columnconfigure(0, weight=1)

        self.label_from.grid(row=0, column=0, sticky="w", columnspan=2)
        self.list_box_from.grid(row=1, column=0, sticky="nsew")
        self.y_scrollbar_from.grid(row=1, column=1, sticky="ns")
        self.x_scrollbar_from.grid(row=2, column=0, sticky="ew")
        self.label_to.grid(row=3, column=0, sticky="w", columnspan=2)
        self.list_box_to.grid(row=4, column=0, sticky="nsew")
        self.y_scrollbar_to.grid(row=4, column=1, sticky="ns")
        self.x_scrollbar_to.grid(row=5, column=0, sticky="ew")

        self.parse_args()


    def parse_args(self):
        """
            Called with what's returned from get_args(), and inserts any 
            existing arguments into the list specified (Currently hardcoded 
            to only populate the origin list).
        """
        
        if argv[1:]:
            for arg in argv[1:]:
                self.list_box_from.insert("end", arg)



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


    def master_close(self):
        """
            Similar to toplevel_close, but writes settings to the disk as json.
        """
        
        settings={
            "show_hidden_files" : self.settings_show_hidden_files.get(),
            "include_files_in_tree" : self.settings_include_files_in_tree.get(),
            "tree_xscroll" : self.settings_tree_xscroll.get(),
            "ask_overwrite" : self.settings_ask_overwrite.get(),
            "rename_dupes" : self.settings_rename_dupes.get()
        }

        settings_json=dumps(settings)

        with open("src/settings.json", "w") as settings_file:
            settings_file.write(settings_json)

        self.master.destroy()


    def get_offsets(self, tk_window=None):
        """
            Returns an appropriate offset for a given tkinter toplevel,
            such that it always is created center screen on the primary display.
        """

        if tk_window:
            width_offset = int(
                (self.master.winfo_screenwidth() / 2) - (tk_window.winfo_width() / 2)
            )

            height_offset = int(
                (self.master.winfo_screenheight() / 2) - (tk_window.winfo_height() / 2)
            )

        else:
            width_offset = int(
                (self.master.winfo_screenwidth() / 2) - (self.master.winfo_width() / 2)
            )

            height_offset = int(
                (self.master.winfo_screenheight() / 2) - (self.master.winfo_height() / 2)
            )

        return (width_offset, height_offset)


    def tear_off(self, menu, top_level):
        """
            Callback for the settings tearoff- specifies basic geometry and behavior.

            Documentation for TEAROFFCOMMAND in tcl is limited. This function
            calls a few basic root-level Tk commands on the tearoff, so that 
            it's configured dynamically.

            Arguments are automatically passed from Menu
        """

        tear_off_width=self.master.tk.call("winfo", "reqwidth", top_level)
        tear_off_height=self.master.tk.call("winfo", "reqheight", top_level)

        (tear_off_width_offset, tear_off_height_offset)=self.get_offsets(
            top_level
        )

        master.tk.call(
            "wm",
            "resizable",
            top_level,
            "0",
            "0"
        )
        
        master.tk.call(
            "wm",
            "geometry",
            top_level,
            f"{tear_off_width}"\
            f"x{tear_off_height}"\
            f"+{tear_off_width_offset-100}"\
            f"+{tear_off_height_offset-200}"
        )


    def clear_selected(self):
        """
            Removes selected (highlighted) item(s) from a 
            given listbox on the main UI in reverse, to avoid
            indexing errors at runtime.
        """

        selected_1=list(self.list_box_from.curselection())
        selected_2=list(self.list_box_to.curselection())
        selected_1.reverse()
        selected_2.reverse()
        for i in selected_1:
            self.list_box_from.delete(i)
        for i in selected_2:
            self.list_box_to.delete(i)


    def clear_all(self):
        """
            Clears both listboxes in the main UI, resetting the form.
        """
        
        while self.list_box_from.size():
            self.list_box_from.delete(0)
        while self.list_box_to.size():
            self.list_box_to.delete(0)


    def copy_load(self):
        """
            Copies each item in the origin list to each path in the destination list.

            The behavior of this function is subject to the state of global booleans 
            responsible for program settings. Ask-Overwrite and Rename Dupes will alter
            the way the program handles existing data standing in its way. By default, 
            all data is overwritten.
        """

        skipped=[]

        while self.list_box_to.size():
            destination=self.list_box_to.get(0)
            
            for i in range(self.list_box_from.size()):
                list_item=self.list_box_from.get(i)
                (_, filename)=split(list_item)
                future_destination=join(destination, filename)

                if exists(future_destination):

                    if (self.settings_ask_overwrite.get() == 0) \
                    and (self.settings_rename_dupes.get() == 0):
                        try:
                            cleanup(future_destination)
                        except Exception as err:
                            messagebox.showerror(
                                "Error",
                                err
                            )

                    elif self.settings_ask_overwrite.get() == 1:
                        behavior_overwrite=messagebox.askyesno(
                            title="Path Conflict",
                            message=f"Overwrite {future_destination}?\n" \
                            f"YES - Overwrite\n NO - Skip"
                        )

                        if behavior_overwrite:
                            try:
                                cleanup(future_destination)
                            except Exception as err:
                                messagebox.showerror(
                                    "Error",
                                    err
                                )
                    
                        else:
                            skipped.append(
                                f"{self.list_box_from.get(0)}"\
                                f" => " \
                                f"{destination}"
                            )
                            self.list_box_from.delete(0)
                            continue

                    elif self.settings_rename_dupes.get() == 1:
                        dupe=name_dupe(future_destination)
                            
                        run([
                            "move",
                            flip_slashes(list_item, "back"),
                            flip_slashes(dupe, "back")
                        ], shell=True)

                        list_item=dupe

                try:
                    copy(
                        flip_slashes(list_item, "back"),
                        flip_slashes(destination, "back")
                    )
                except Exception as err:
                    messagebox.showerror(
                        "Error | Cancelled.",
                        err
                    )
                    return

            self.list_box_to.delete(0)

        self.clear_all()

        if skipped:    
            messagebox.showinfo(
                title="Skipped",
                message="\n".join(skipped)
            )


    def move_load(self):
        """
            Moves each item in the origin list to the path in the destination list.

            The behavior of this function is subject to the state of global booleans 
            responsible for program settings. Ask-Overwrite and Rename Dupes will alter
            the way the program handles existing data standing in its way. By default, 
            all data is overwritten. Supports only a single destination directory.
        """

        if self.list_box_to.size() > 1:
            messagebox.showwarning(
                "Invalid Operation",
                "Move operation only supports a single destination directory."
            )
            return

        destination=self.list_box_to.get(0)
        skipped=[]
        
        while self.list_box_from.size():  
            list_item=self.list_box_from.get(0)
            (_, filename)=split(list_item)
            future_destination=join(destination, filename)

            if exists(future_destination):

                if (self.settings_ask_overwrite.get() == 0) \
                and (self.settings_rename_dupes.get() == 0):
                    try:
                        cleanup(future_destination)
                    except Exception as err:
                        messagebox.showerror(
                            "Error",
                            err
                        )

                elif self.settings_ask_overwrite.get() == 1:
                    behavior_overwrite=messagebox.askyesno(
                        title="Path Conflict",
                        message=f"Overwrite {future_destination}?\n" \
                        f"YES - Overwrite\n NO - Skip"
                    )

                    if behavior_overwrite:
                        try:
                            cleanup(future_destination)
                        except Exception as err:
                            messagebox.showerror(
                                "Error",
                                err
                            )
                    
                    else:
                        skipped.append(self.list_box_from.get(0))
                        self.list_box_from.delete(0)
                        continue

                elif self.settings_rename_dupes.get() == 1:
                    dupe=name_dupe(future_destination)
                        
                    run([
                        "move",
                        flip_slashes(list_item, "back"),
                        flip_slashes(dupe, "back")
                    ], shell=True)

                    list_item=dupe

            try:
                move(
                    flip_slashes(list_item, "back"),
                    flip_slashes(destination, "back")
                )
            except Exception as err:
                messagebox.showerror(
                    "Error | Cancelled.",
                    err
                )
                return

            self.list_box_from.delete(0)

        self.list_box_to.delete(0)

        if skipped:    
            messagebox.showinfo(
                title="Skipped",
                message="\n".join(skipped)
            )


    def show_add_items(self, source):
        """
            Displays the Add Items dialog and doesn't allow any additional
            instances of itself to be created while it's showing.

            Add items is a minimalist filedialog comprised of a tkinter
            treeview and listbox, both with some bindings attatched.
        """

        if self.file_dialog_showing.get() == 0:
            self.file_dialog_showing.set(1)

            self.add_items=Toplevel()
            self.add_items.grab_set()
            self.add_items.geometry("500x300")
            self.add_items.minsize(width=300, height=200)
            self.add_items.update()

            (add_items_width_offset, add_items_height_offset)=self.get_offsets(
                self.add_items
            )
            
            self.add_items.geometry(f"+{add_items_width_offset}+{add_items_height_offset}")

            self.add_items.grid_rowconfigure(0, weight=1)
            self.add_items.grid_columnconfigure(0, weight=1)
            self.add_items.grid_columnconfigure(2, weight=1)

            self.add_items.title("Add Items")
            self.add_items.iconbitmap(f"{self.cwd}/src/img/main_icon.ico")

            # Tkinter x_scroll is broken for treeview
            # https://stackoverflow.com/questions/49715456
            # https://stackoverflow.com/questions/14359906
            self.tree_x_scrollbar=Scrollbar(self.add_items, orient="horizontal")
            self.tree_y_scrollbar=Scrollbar(self.add_items, orient="vertical")
            self.file_list_x_scrollbar=Scrollbar(self.add_items, orient="horizontal")
            self.file_list_y_scrollbar=Scrollbar(self.add_items, orient="vertical")
            
            self.tree=Treeview(
                self.add_items,
                xscrollcommand=self.tree_x_scrollbar.set,
                yscrollcommand=self.tree_y_scrollbar.set,
                show="tree",
                selectmode="browse"
            )

            self.file_list=Listbox(
                self.add_items,
                xscrollcommand=self.file_list_x_scrollbar.set,
                yscrollcommand=self.file_list_y_scrollbar.set,
                selectmode="extended",
                width=34,
                highlightthickness=0,
                bd=2,
                relief="ridge"
            )

            self.tree_x_scrollbar.config(command=self.tree.xview)
            self.tree_y_scrollbar.config(command=self.tree.yview)
            self.file_list_x_scrollbar.config(command=self.file_list.xview)
            self.file_list_y_scrollbar.config(command=self.file_list.yview)
            
            self.tree.grid(row=0, column=0, sticky="nsew")
            self.tree_y_scrollbar.grid(row=0, column=1, sticky="ns")
            self.file_list.grid(row=0, column=2, sticky="nsew")
            self.file_list_y_scrollbar.grid(row=0, column=3, sticky="ns")
            self.tree_x_scrollbar.grid(row=1, column=0, sticky="ew")
            self.file_list_x_scrollbar.grid(row=1, column=2, sticky="ew")

            self.tree.bind("<Double-Button-1>", self.dialog_populate)
            self.tree.bind("<Return>", self.dialog_populate)
            self.tree.bind("<Right>", self.dialog_populate)
            self.file_list.bind("<<ListboxSelect>>", self.selection_populate)
            self.file_list.bind("<Return>", lambda event: self.add_paths(source))

            self.add_items.protocol(
                "WM_DELETE_WINDOW",
                lambda: toplevel_close(self.add_items, self.file_dialog_showing)
            )

            if self.settings_tree_xscroll.get() == 1:
                # This is an ugly bandaid.
                # Minwidth is arbitrary.
                self.tree.column("#0", minwidth=1000)

            self.init_dialog_populate()
            self.dialog_selection=[]
            self.add_items.focus()


    def init_dialog_populate(self):
        """
            Called each time show_add_items() is called, to initialize the dialog.

            This function populates the treeview in the Add Items dialog with
            data returned from get disks. The path in its entirety is loaded into
            an array called "values". The disk, or directory "name" is displayed
            without the delimeter, as the treeview is only intended to show the 
            name of the file or directory without a path, root, or delimeters.
        """

        disks=get_disks()

        for disk in disks:
            self.tree.insert(
                "",
                index="end",
                text=disk[0:-1],
                image=self.disk_icon,
                value=disk
            )
        

    def dialog_populate(self,*args):
        """
            Dynamically populates & updates the treeview and listbox in Add Items

            Spaces in paths act as a delimeter for the values array to split on.
            tree_item_name is just the result of building the pathname back together,
            and could also be done by overwriting the same variable. 

            The treeview is populated with the data for the full path, 
            and the file or directory name is displayed as text + an icon.

            The listbox is more verbose, including the full absolute paths 
            inside of what's been selected in the treeview.
        """

        error=False

        children = self.tree.get_children(self.tree.focus())
        if children:
            for child in children:
                self.tree.delete(child)

        tree_item_name=self.tree.item(self.tree.focus())["values"]
        tree_item_name = [str(piece) for piece in tree_item_name]
        tree_item_name = " ".join(tree_item_name)

        if isdir(tree_item_name):
            try:
                if self.settings_show_hidden_files.get() == 1:
                    items=self.list_dir(tree_item_name, force=True)
                else:
                    items=self.list_dir(tree_item_name, force=False)
                    
            except Exception as err:
                messagebox.showerror(
                "Error.",
                err
                )

                items=[]
                error=True
                self.tree.master.lift()

            for item in items:
                full_path=join(tree_item_name, item)

                if isdir(full_path): 
                    self.tree.insert(
                        self.tree.focus(),
                        index="end",
                        text=item,
                        value=full_path,
                        image=self.folder_icon
                    )

                elif self.settings_include_files_in_tree.get() == 1:
                    self.tree.insert(
                        self.tree.focus(),
                        index="end",
                        text=item,
                        value=full_path,
                        image=self.file_icon
                    )

        while self.file_list.size():
            self.file_list.delete(0)

        if not error:
            if isdir(tree_item_name):
                for item in items:
                    full_path=join(tree_item_name, item)
                    self.file_list.insert("end", full_path)
            else:
                self.file_list.insert("end", tree_item_name)


    def selection_populate(self, event=None):
        """
            Dynamically refreshes the array of selected items in the
            Add Items listbox (Callback for <<ListboxSelect>>).
        """

        self.dialog_selection.clear()
        selection_index_arr=self.file_list.curselection()

        for i in selection_index_arr:
            self.dialog_selection.append(self.file_list.get(i))


    def list_dir(self, full_path, force):
        """
            Reads a directory with a system call to dir, 
            returning contents based on the boolean FORCE

            This function spawns a child process which 
            then sends 'dir' or 'dir PATH /b /a', similar to 'dir -force'. 
            Python parses the output, parses it a little more with a 
            regular expression, and returns it.
        """

        full_path=flip_slashes(full_path, "back")

        if force:
            dir_listing=run([
                "dir",
                full_path,
                "/b",
                "/a"
            ], shell=True, capture_output=True)

        else:
            dir_listing=run([
                "dir",
                full_path,
                "/b"
            ], shell=True, capture_output=True)

        output=dir_listing.stdout
        err=dir_listing.stderr

        if not output:
            return []

        if err:
            err=err.decode("utf-8")
            raise Exception(err)

        str_output=output.decode("utf-8")
        list_output=re_split("\r\n", str_output)
        
        return sorted([item for item in list_output if item])


    def add_paths(self, source, event=None):
        """
            Populates the given listbox (source/destination) with the
            selection array from the Add Items listbox, then destroys
            the dialog.
        """

        if source:
            for item in self.dialog_selection:
                self.list_box_from.insert("end", item)
        else:
            for item in self.dialog_selection:
                self.list_box_to.insert("end", item)

        self.file_dialog_showing.set(0)
        self.add_items.destroy()


    def show_about(self):
        """
            Displays a small dialog and doesn't allow any additional
            instances of itself to be created while it's showing.
        """

        if self.about_showing.get() == 0:
            self.about_showing.set(1)
            
            self.about=Toplevel()
            self.about.resizable(0,0)
            self.about.geometry("600x400")
            self.about.update()

            (width_offset, height_offset)=self.get_offsets(self.about)
            self.about.geometry(f"+{width_offset-75}+{height_offset-75}")
            self.about.update()

            self.about.title("About")
            self.about.iconbitmap(f"{self.cwd}/src/img/main_icon.ico")

            with open("src/about.txt", "r") as infofile:
                about_info=infofile.read()

            self.about_message=Message(
                self.about,
                text=about_info,
                width=(self.about.winfo_width() - 25)
            )

            self.about_message.grid(sticky="nsew")

            self.about.protocol(
                "WM_DELETE_WINDOW",
                lambda: toplevel_close(self.about, self.about_showing)
            )


    def show_help(self):
        """
            Displays a small scrollable help dialog and doesn't allow any additional
            instances of itself to be created while it's showing.
        """

        if self.help_showing.get() == 0:
            self.help_showing.set(1)

            self.help_window=Toplevel()
            self.help_window.resizable(0,0)
            self.help_window.geometry("500x300")
            self.help_window.update()

            (width_offset, height_offset)=self.get_offsets(self.help_window)
            self.help_window.geometry(f"+{width_offset+75}+{height_offset-75}")
            self.help_window.update()

            self.help_window.rowconfigure(0, weight=1)
            self.help_window.columnconfigure(0, weight=1)
            self.help_window.columnconfigure(1, weight=1)

            self.help_window.title("Help")
            self.help_window.iconbitmap(f"{self.cwd}/src/img/main_icon.ico")

            with open("src/help.txt", "r") as helpfile:
                help_info=helpfile.read()

            self.message_y_scrollbar=Scrollbar(self.help_window, orient="vertical")

            self.help_text=Text(
                self.help_window,
                width=60,
                wrap="word",
                yscrollcommand=self.message_y_scrollbar.set
            )

            self.help_text.insert("end", help_info)
            self.help_text.config(state="disabled")
            self.help_text.grid(row=0, column=0)

            self.message_y_scrollbar.grid(row=0, column=1, sticky="ns")
            self.message_y_scrollbar.config(command=self.help_text.yview)

            self.help_window.protocol(
                "WM_DELETE_WINDOW",
                lambda: toplevel_close(self.help_window, self.help_showing)
            )
