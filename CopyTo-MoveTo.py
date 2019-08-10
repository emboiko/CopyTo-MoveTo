from tkinter import(
    Tk,
    Toplevel, 
    BooleanVar,
    PhotoImage, 
    Menu, 
    Text,
    Message,
    Listbox,
    Scrollbar,
    messagebox,
)

from tkinter.ttk import Treeview

from os.path import(
    exists, isdir, splitext, split
)

from posixpath import join

from os import getcwd

from re import findall, sub, split as re_split

from json import loads, dumps

#Popen might slowly replace calls to run
from subprocess import run

from sys import argv

from platform import system


def get_offset(window_width, window_height):
    """
        Returns an appropriate offset for a given tkinter toplevel,
        such that it always is created center screen on the primary display.
    """

    width_offset=int(
        (master.winfo_screenwidth() / 2) - (window_width / 2)
    )
    height_offset=int(
        (master.winfo_screenheight() / 2) - (window_height / 2)
    )
    return (width_offset, height_offset)


def tear_off(menu, top_level):
    """
        Callback for the settings tearoff- specifies basic geometry and behavior.

        Documentation for TEAROFFCOMMAND in tcl is limited. This function
        calls a few basic root-level Tk commands on the tearoff, so that 
        it's configured dynamically.

        Arguments are automatically passed from Menu
    """

    tear_off_width=master.tk.call("winfo", "reqwidth", top_level)
    tear_off_height=master.tk.call("winfo", "reqheight", top_level)

    (tear_off_width_offset, tear_off_height_offset)=get_offset(
        tear_off_height, tear_off_width
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


def toplevel_close(dialog, boolean):
    """
        Callback that flips the value for a given toplevel_showing boolean, 
        before disposing of the toplevel.

        Toplevel windows are bound to booleans which flip when they're created 
        or destroyed, in order to prevent multiple instances of the toplevels.
    """

    boolean.set(0)
    dialog.destroy()


def master_close(master):
    """
        Similar to toplevel_close, but writes settings to the disk as json.
    """
    
    settings={
        "show_hidden_files" : settings_show_hidden_files.get(),
        "include_files_in_tree" : settings_include_files_in_tree.get(),
        "tree_xscroll" : settings_tree_xscroll.get(),
        "ask_overwrite" : settings_ask_overwrite.get(),
        "rename_dupes" : settings_rename_dupes.get()
    }

    settings_json=dumps(settings)

    with open("settings.json", "w") as settings_file:
        settings_file.write(settings_json)

    master.destroy()


def get_args():
    """
        Gathers all arguments into an array and returns them if they exist
    """
    args = None
    if len(argv) > 1:
        args = argv[1:]
        return args
    return args


def insert_args(args, list_box):
    """
        Called with what's returned from get_args(), and inserts any 
        existing arguments into the list specified (Currently hardcoded 
        to only populate the origin list).
    """
    
    if args:
        for arg in args:
            list_box.insert("end", arg)


def init_settings():
    """
        Called on startup, loads, parses, and returns json settings.
    """

    if exists("settings.json"):
        with open("settings.json", "r") as settings_file:
            settings_json=settings_file.read()

        settings=loads(settings_json)
        return settings
    else:
        return None


def settings_exclusives(*args):
    """
        Callback assigned to settings that are mutually exclusive, 
        to prevent logical/runtime errors or unexpected behavior.
    """

    if args[0] == "PY_VAR3":
        if settings_ask_overwrite.get() == 1:
            settings_rename_dupes.set(0)
            return 

    elif args[0] == "PY_VAR4":        
        if settings_rename_dupes.get() == 1:
            settings_ask_overwrite.set(0)
            return 


def flip_slashes(path, direction):
    """
        A really simple utility that changes path delimiters.
    """

    if direction == "forward":
        new_path=sub("\\\\", "/", path)
        return new_path
    if direction == "back":
        new_path=sub("/", "\\\\", path)
        return new_path


def get_disks():
    """
        Simple utility that returns all disks mounted to the system,
        with a forward slash delimeter attatched at the end.

        Additional disks not mounted between A-Z in windows are
        otherwise mounted at elsewhere within the filesystem, 
        somewhere between A-Z. This function spawns a child process which 
        then sends 'wmic logicaldisk get name'. Python parses the output, 
        parses it a little more with a regular expression, and returns it.
    """

    logicaldisks=run([
        "wmic",
        "logicaldisk",
        "get",
        "name"
    ], capture_output=True)

    disks=findall("[A-Z]:", str(logicaldisks.stdout))
    
    return [disk+"/" for disk in disks]


def list_dir(full_path, force):
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


def init_dialog_populate(tree):
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
        tree.insert(
            "",
            index="end",
            text=disk[0:-1],
            image=disk_icon,
            values=disk
        )


def dialog_populate(event, tree, list_box):
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

    #this if statement sucks, and doesn't implement a dynamic behavior.
    #it should refresh that branch of the tree with a new call to
    #list_dir + populate
    if not tree.get_children(tree.focus()):
        tree_item_name_values=tree.item(tree.focus())["values"]
        tree_item_name_arr=[str(val) for val in tree_item_name_values]
        tree_item_name=" ".join(tree_item_name_arr)

        if isdir(tree_item_name):
            try:
                if settings_show_hidden_files.get() == 1:
                    items=list_dir(tree_item_name, force=True)
                else:
                    items=list_dir(tree_item_name, force=False)

            except Exception as err:
                messagebox.showerror(
                "Error.",
                err
                )

                items=[]
                error=True
                tree.master.lift()

            for item in items:
                full_path=join(tree_item_name, item)

                if isdir(full_path): 
                    tree.insert(
                        tree.focus(),
                        index="end",
                        text=item,
                        values=full_path,
                        image=folder_icon
                    )

                elif settings_include_files_in_tree.get() == 1:
                    tree.insert(
                        tree.focus(),
                        index="end",
                        text=item,
                        values=full_path,
                        image=file_icon
                    )

    while list_box.size():
        list_box.delete(0)

    if not error:

        tree_item_name_values=tree.item(tree.focus())["values"]
        tree_item_name_arr=[str(val) for val in tree_item_name_values]
        tree_item_name=" ".join(tree_item_name_arr)

        if isdir(tree_item_name):
            if settings_show_hidden_files.get():
                items=list_dir(tree_item_name, force=True)
            else:
                items=list_dir(tree_item_name, force=False)

            for item in items:
                full_path=join(tree_item_name, item)
                list_box.insert("end", full_path)
        
        else:
            list_box.insert("end", tree_item_name)


def selection_populate(event, list_box, dialog_selection):
    """
        Dynamically refreshes the array of selected items in the
        Add Items listbox (Callback for <<ListboxSelect>>).
    """

    dialog_selection.clear()
    selection_index_arr=list_box.curselection()

    for i in selection_index_arr:
        dialog_selection.append(list_box.get(i))


def add_paths(handler, top_level, dialog_selection, source):
    """
        Populates the given listbox (source/destination) with the
        selection array from the Add Items listbox, then destroys
        the dialog.
    """

    if source:
        for item in dialog_selection:
            list_box_from.insert("end", item)
    else:
        for item in dialog_selection:
            list_box_to.insert("end", item)

    file_dialog_showing.set(0)
    top_level.destroy()


def cleanup(full_path):
    """
        Deletes given the file or directory (recursively) from the disk.
    """

    full_path=flip_slashes(full_path, "back")

    if isdir(full_path):
        dir_result=run([
            "rmdir",
            "/s",
            "/q",
            full_path
        ], shell=True, capture_output=True)
        
        stderr=str(dir_result.stderr)
        
        if len(stderr) > 3:
            raise Exception(stderr)

    else:
        file_result=run([
            "del",
            "/f",
            "/q",
            full_path
        ], shell=True, capture_output=True)
        
        stderr=str(file_result.stderr)
        
        if len(stderr) > 3:
            raise Exception(stderr)


def name_dupe(future_destination):
    """
        Renames the file or directory (by reference) until it doesn't exist
        in the destination with that name anymore, by appending
        the filename with an index wrapped in parenthesis.
    """

    if isdir(future_destination):
        (root, filename)=split(future_destination)
        new_title=filename

        filecount=0
        while exists(future_destination):
            filecount += 1
            new_title=filename + " (" + str(filecount) + ")"
            future_destination=join(root, new_title)
        
        return new_title

    else:
        (root, filename)=split(future_destination)
        (title, ext)=splitext(filename)
        new_title=title

        filecount=0
        while exists(future_destination):
            filecount += 1
            new_title=title + " (" + str(filecount) + ")"
            future_destination=join(root, new_title + ext)
        
        return new_title + ext


def move(source, destination):
    """
        A somewhat non-pythonic function that replaces shutil.move() 
        in the context of this application.
    """

    if exists(source) and exists(destination):
        result=run([
            "move",
            "/Y",
            source,
            destination
        ], shell=True, capture_output=True)

        stderr=str(result.stderr)
        if len(stderr) > 3:
            raise Exception(stderr)


def copy(source, destination):
    """
        A somewhat non-pythonic function that replaces and 
        combines shutil.copy2() and shutil.copytree()
    """

    if exists(source) and exists(destination):

        if isdir(source):
            (_, filename)=split(source)
            future_destination=join(destination, filename)

            run([
                "mkdir",
                future_destination
            ], shell=True)

            result=run([
                "robocopy",
                "/E",
                source,
                future_destination
            ], shell=True, capture_output=True)

            stderr=str(result.stderr)
            if len(stderr) > 3:
                raise Exception(stderr)

        else:    
            result=run([
                "copy",
                "/Y",
                source,
                destination
            ], shell=True, capture_output=True)

            stderr=str(result.stderr)
            if len(stderr) > 3:
                raise Exception(stderr)


def show_about(cwd):
    """
        Displays a small dialog and doesn't allow any additional
        instances of itself to be created while it's showing.
    """

    if about_showing.get() == 0:
        about_showing.set(1)
        
        about=Toplevel()
        about.resizable(0,0)
        about_width=600
        about_height=400

        (about_width_offset, about_height_offset)=get_offset(
            about_width, about_height
        )

        about.geometry(
            f"{about_width}"\
            f"x{about_height}"\
            f"+{about_width_offset-75}"\
            f"+{about_height_offset+75}"
        )

        about.title("About")
        about.iconbitmap(f"{cwd}/img/main_icon.ico")

        with open("about.txt", "r") as infofile:
            about_info=infofile.read()

        about_message=Message(
            about,
            text=about_info,
            width=(about.winfo_width() - 25)
        )

        about_message.grid(sticky="nsew")

        about.protocol(
            "WM_DELETE_WINDOW",
            lambda: toplevel_close(about, about_showing)
        )


def show_help(cwd, event=None):
    """
        Displays a small scrollable help dialog and doesn't allow any additional
        instances of itself to be created while it's showing.
    """

    if help_showing.get() == 0:
        help_showing.set(1)

        help_window=Toplevel()
        help_window.resizable(0,0)
        help_window_width=500
        help_window_height=300

        (help_width_offset, help_height_offset)=get_offset(
            help_window_width, help_window_height
        )

        help_window.geometry(
            f"{help_window_width}"\
            f"x{help_window_height}"\
            f"+{help_width_offset}"\
            f"+{help_height_offset}"
        )

        help_window.rowconfigure(0, weight=1)
        help_window.columnconfigure(0, weight=1)
        help_window.columnconfigure(1, weight=1)

        help_window.title("Help")
        help_window.iconbitmap(f"{cwd}/img/main_icon.ico")

        with open("help.txt", "r") as helpfile:
            help_info=helpfile.read()

        message_y_scrollbar=Scrollbar(help_window, orient="vertical")

        help_text=Text(
            help_window,
            width=60,
            wrap="word",
            yscrollcommand=message_y_scrollbar.set
        )

        help_text.insert("end", help_info)
        help_text.config(state="disabled")
        help_text.grid(row=0, column=0)

        message_y_scrollbar.grid(row=0, column=1, sticky="ns")
        message_y_scrollbar.config(command=help_text.yview)

        help_window.protocol(
            "WM_DELETE_WINDOW",
            lambda: toplevel_close(help_window, help_showing)
        )


def show_add_items(cwd, event=None, source=True):
    """
        Displays the Add Items dialog and doesn't allow any additional
        instances of itself to be created while it's showing.

        Add items is a minimalist filedialog comprised of a tkinter
        treeview and listbox, both with some bindings attatched.
    """

    if file_dialog_showing.get() == 0:
        file_dialog_showing.set(1)

        add_items=Toplevel()
        add_items.grab_set()
        add_items_width=500
        add_items_height=300
        add_items.minsize(width=300, height=200)

        (add_items_width_offset, add_items_height_offset)=get_offset(
            add_items_width, add_items_height
        )
        
        add_items.geometry(
            f"{add_items_width}"\
            f"x{add_items_height}"\
            f"+{add_items_width_offset}"\
            f"+{add_items_height_offset}"
        )

        add_items.grid_rowconfigure(0, weight=1)
        add_items.grid_columnconfigure(0, weight=1)
        add_items.grid_columnconfigure(2, weight=1)

        add_items.title("Add Items")
        add_items.iconbitmap(f"{cwd}/img/main_icon.ico")

        # Tkinter x_scroll is broken for treeview.
        # https://stackoverflow.com/questions/49715456
        # https://stackoverflow.com/questions/14359906
        tree_x_scrollbar=Scrollbar(add_items, orient="horizontal")
        tree_y_scrollbar=Scrollbar(add_items, orient="vertical")
        file_list_x_scrollbar=Scrollbar(add_items, orient="horizontal")
        file_list_y_scrollbar=Scrollbar(add_items, orient="vertical")
        
        tree=Treeview(
            add_items,
            xscrollcommand=tree_x_scrollbar.set,
            yscrollcommand=tree_y_scrollbar.set,
            show="tree",
            selectmode="browse"
        )

        file_list=Listbox(
            add_items,
            xscrollcommand=file_list_x_scrollbar.set,
            yscrollcommand=file_list_y_scrollbar.set,
            selectmode="extended",
            width=34,
            highlightthickness=0,
            bd=2,
            relief="ridge"
        )
        
        tree.grid(
            row=0,
            column=0,
            sticky="nsew",
        )

        file_list.grid(
            row=0,
            column=2,
            sticky="nsew"
        )
        
        tree_x_scrollbar.grid(
            row=1,
            column=0,
            sticky="ew",
        )
        
        tree_y_scrollbar.grid(
            row=0,
            column=1,
            sticky="ns",
        )

        file_list_x_scrollbar.grid(
            row=1,
            column=2,
            sticky="ew",
        )
        
        file_list_y_scrollbar.grid(
            row=0,
            column=3,
            sticky="ns",
        )
        
        #See above
        tree_x_scrollbar.config(command=tree.xview)
        tree_y_scrollbar.config(command=tree.yview)
        file_list_x_scrollbar.config(command=file_list.xview)
        file_list_y_scrollbar.config(command=file_list.yview)

        if settings_tree_xscroll.get() == 1:
            # This is an ugly bandaid.
            # Minwidth is arbitrary.
            tree.column("#0", minwidth=1000)
        
        init_dialog_populate(tree)

        dialog_selection=[]

        tree.bind(
            sequence="<Double-Button-1>",
            func=lambda handler: dialog_populate(
                handler,
                tree,
                file_list
            )
        )

        tree.bind(
            sequence="<Return>",
            func=lambda handler: dialog_populate(
                handler,
                tree,
                file_list
            )
        )

        tree.bind(
            sequence="<Right>",
            func=lambda handler: dialog_populate(
                handler,
                tree,
                file_list
            )
        )

        file_list.bind(
            sequence="<<ListboxSelect>>",
            func=lambda handler: selection_populate(
                handler,
                file_list,
                dialog_selection
            )
        )

        file_list.bind(
            sequence="<Return>",
            func=lambda handler: add_paths(
                handler,
                add_items,
                dialog_selection,
                source
            )
        )

        add_items.protocol(
            "WM_DELETE_WINDOW",
            lambda: toplevel_close(add_items, file_dialog_showing)
        )


def clear_selected(event=None):
    """
        Removes selected (highlighted) item(s) from a 
        given listbox on the main UI in reverse, to avoid
        indexing errors at runtime.
    """

    selected_1=list(list_box_from.curselection())
    selected_2=list(list_box_to.curselection())
    selected_1.reverse()
    selected_2.reverse()
    for i in selected_1:
        list_box_from.delete(i)
    for i in selected_2:
        list_box_to.delete(i)


def clear(event=None):
    """
        Clears both listboxes in the main UI, resetting the form.
    """
    
    while list_box_from.size():
        list_box_from.delete(0)
    while list_box_to.size():
        list_box_to.delete(0)


def copy_load(event=None):
    """
        Copies each item in the origin list to each path in the destination list.

        The behavior of this function is subject to the state of global booleans 
        responsible for program settings. Ask-Overwrite and Rename Dupes will alter
        the way the program handles existing data standing in its way. By default, 
        all data is overwritten.
    """

    skipped=[]

    while list_box_to.size():
        destination=list_box_to.get(0)
        
        for i in range(list_box_from.size()):
            list_item=list_box_from.get(i)
            (_, filename)=split(list_item)
            future_destination=join(destination, filename)

            if exists(future_destination):

                if (settings_ask_overwrite.get() == 0) \
                and (settings_rename_dupes.get() == 0):
                    try:
                        cleanup(future_destination)
                    except Exception as err:
                        messagebox.showerror(
                            "Error",
                            err
                        )

                elif settings_ask_overwrite.get() == 1:
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
                            f"{list_box_from.get(0)}"\
                            f" => " \
                            f"{destination}"
                        )
                        list_box_from.delete(0)
                        continue

                elif settings_rename_dupes.get() == 1:
                    dupe=name_dupe(future_destination)
                        
                    run([
                        "move",
                        flip_slashes(list_item, "back"),
                        flip_slashes(dupe, "back")
                    ], shell=True)

                    list_item=dupe

            try:
                # shutil_copy2(list_item, destination)
                # -or- 
                # shutil_copytree(list_item, destination)
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

        list_box_to.delete(0)

    clear(event=None)

    [print(f"Skipped {item}") for item in skipped]


def move_load(event=None):
    """
        Moves each item in the origin list to the path in the destination list.

        The behavior of this function is subject to the state of global booleans 
        responsible for program settings. Ask-Overwrite and Rename Dupes will alter
        the way the program handles existing data standing in its way. By default, 
        all data is overwritten. Supports only a single destination directory.
    """

    if list_box_to.size() > 1:
        messagebox.showwarning(
            "Invalid Operation",
            "Move operation only supports a single destination directory."
        )
        return

    destination=list_box_to.get(0)
    skipped=[]
    
    while list_box_from.size():  
        list_item=list_box_from.get(0)
        (_, filename)=split(list_item)
        future_destination=join(destination, filename)

        if exists(future_destination):

            if (settings_ask_overwrite.get() == 0) \
            and (settings_rename_dupes.get() == 0):
                try:
                    cleanup(future_destination)
                except Exception as err:
                    messagebox.showerror(
                        "Error",
                        err
                    )

            elif settings_ask_overwrite.get() == 1:
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
                    skipped.append(list_box_from.get(0))
                    list_box_from.delete(0)
                    continue

            elif settings_rename_dupes.get() == 1:
                dupe=name_dupe(future_destination)
                    
                run([
                    "move",
                    flip_slashes(list_item, "back"),
                    flip_slashes(dupe, "back")
                ], shell=True)

                list_item=dupe

        try:
            # shutil_move(list_item, destination)
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

        list_box_from.delete(0)

    list_box_to.delete(0)

    [print(f"Skipped {item}") for item in skipped]


if __name__ == "__main__":
    """
        Still in beta, use at your own risk.

        Various tweaks and additions are still to come for the UI,
        along with code cleanup / thorough documentation.

        shutil wasn't used on purpose, and is most likely an all around
        better (and more performant) choice for the task. 

        This entire program will probably end up getting wrapped or 
        called by a "handler" that aggregates arguments, in order to 
        deal with multiple instances of the program being instantiated.
        This is triggered by default Windows behavior. Ideally, a context 
        menu entry for Copyto-Moveto will be implemented, so an end-user 
        can multiselect items within windows explorer, and "open with"
        Copto-Moveto.exe (Note, the registry key will not live under the 
        actual "open with" keys, but under */shell and directory/shell).
        This idea hasn't been fully formulated quite yet, but the goal
        is to mimic the behavior of VSCode and other applications that
        have their own context menu entry. If a user selects a collection
        of items in windows explorer, and chooses to "Open with code",
        VScode will act accordingly. I have some learning to do with 
        regard to Inter-Process Communication.

    """

    master=Tk()

    master_width=600
    master_height=400
    master.minsize(width=400, height=200)

    (master_width_offset, master_height_offset)=get_offset(
        master_width, master_height
    )
    
    master.geometry(
        f"{master_width}"\
        f"x{master_height}"\
        f"+{master_width_offset}"\
        f"+{master_height_offset}"
    )

    master.grid_rowconfigure(0, weight=1)
    master.grid_rowconfigure(1, weight=0)
    master.grid_rowconfigure(2, weight=1)
    master.grid_rowconfigure(3, weight=0)
    master.grid_columnconfigure(0, weight=1)

    master.title("CopyTo-MoveTo")

    ###############
    # Global Stuff, image references & Settings:
    ###############

    if system() != "Windows":
        master.withdraw()
        messagebox.showwarning(
            "Incompatible platform",
            "CopyTo-MoveTo currently supports Windows platforms only."
        )
        quit()

    cwd=flip_slashes(getcwd(), "forward")

    file_icon=PhotoImage(
        file=f"{cwd}/img/file.gif"
    ).subsample(50)

    folder_icon=PhotoImage(
        file=f"{cwd}/img/folder.gif"
    ).subsample(15)
    
    disk_icon=PhotoImage(
        file=f"{cwd}/img/disk.gif"
    ).subsample(15)

    master.iconbitmap(f"{cwd}/img/main_icon.ico")

    settings_show_hidden_files=BooleanVar()
    settings_include_files_in_tree=BooleanVar()
    settings_tree_xscroll=BooleanVar()
    settings_ask_overwrite=BooleanVar()
    settings_ask_overwrite.trace("w", settings_exclusives)
    settings_rename_dupes=BooleanVar()
    settings_rename_dupes.trace("w", settings_exclusives)

    settings=init_settings()

    if settings:
        settings_show_hidden_files.set(settings["show_hidden_files"])
        settings_include_files_in_tree.set(settings["include_files_in_tree"])
        settings_tree_xscroll.set(settings["tree_xscroll"])
        settings_ask_overwrite.set(settings["ask_overwrite"])
        settings_rename_dupes.set(settings["rename_dupes"])

    file_dialog_showing=BooleanVar()
    help_showing=BooleanVar()
    about_showing=BooleanVar()

    master.protocol(
        "WM_DELETE_WINDOW",
        lambda: master_close(master)
    )

    ###############
    # Menu:
    ###############

    main_menu=Menu(master)
    master.config(menu=main_menu)

    file_menu=Menu(main_menu, tearoff=0)
    settings_menu=Menu(main_menu, tearoff=1, tearoffcommand=tear_off)
    main_menu.add_cascade(label="File", menu=file_menu)
    main_menu.add_cascade(label="Settings", menu=settings_menu)

    file_menu.add_command(
        label="Open Source(s)",
        command=lambda: show_add_items(cwd),
        accelerator="Ctrl+O"
    )

    master.bind(
        sequence="<Control-o>",
        func=lambda handler: show_add_items(cwd, handler)
    )

    file_menu.add_command(
        label="Open Destination(s)",
        command=lambda: show_add_items(cwd, source=False),
        accelerator="Ctrl+K+O"
    )

    master.bind(
        sequence="<Control-k>o",
        func=lambda handler: show_add_items(cwd, handler, source=False)
    )

    file_menu.add_separator()

    file_menu.add_command(
        label="Help / Commands",
        command=lambda: show_help(cwd),
        accelerator="Ctrl+H"
    )

    master.bind(
        sequence="<Control-h>",
        func=lambda handler: show_help(cwd, handler)
    )

    file_menu.add_command(
        label="About",
        command=lambda: show_about(cwd)
    )

    settings_menu.add_checkbutton(
        label="Show Hidden Files & Folders",
        variable=settings_show_hidden_files,
        onvalue=True,
        offvalue=False
    )

    settings_menu.add_checkbutton(
        label="Include Files in Tree",
        variable=settings_include_files_in_tree,
        onvalue=True,
        offvalue=False
    )

    settings_menu.add_checkbutton(
        label="Treeview Horizontal Scroll",
        variable=settings_tree_xscroll,
        onvalue=True,
        offvalue=False
    )

    settings_menu.add_checkbutton(
        label="Ask-Overwrite",
        variable=settings_ask_overwrite,
        onvalue=True,
        offvalue=False
    )

    settings_menu.add_checkbutton(
        label="Rename Duplicates",
        variable=settings_rename_dupes,
        onvalue=True,
        offvalue=False
    )
    
    main_menu.add_separator()

    main_menu.add_command(
        label="Clear Selected",
        command=clear_selected
    )

    master.bind(
        sequence="<Control-p>",
        func=lambda handler: clear_selected(handler)
    )

    main_menu.add_command(
        label="Clear All",
        command=clear
    )

    master.bind(
        sequence="<Control-l>",
        func=lambda handler: clear(handler)
    )

    main_menu.add_separator()

    main_menu.add_command(
        label="COPY",
        command=copy_load
    )

    master.bind(
        sequence="<Control-Shift-Return>",
        func=lambda handler: copy_load(handler)
    )

    main_menu.add_command(
        label="MOVE",
        command=move_load
    )

    master.bind(
        sequence="<Control-Return>",
        func=lambda handler: move_load(handler)
    )

    ###############
    # Body
    ###############

    y_scrollbar_from=Scrollbar(master, orient="vertical")
    y_scrollbar_to=Scrollbar(master, orient="vertical")
    x_scrollbar_from=Scrollbar(master, orient="horizontal")
    x_scrollbar_to=Scrollbar(master, orient="horizontal")

    list_box_from=Listbox(
        master,
        selectmode="extended",
        bg="#000000",
        fg="#FFFFFF",
        yscrollcommand=y_scrollbar_from.set,
        xscrollcommand=x_scrollbar_from.set
    )

    list_box_to=Listbox(
        master,
        selectmode="extended",
        bg="#000000",
        fg="#FFFFFF",
        yscrollcommand=y_scrollbar_to.set,
        xscrollcommand=x_scrollbar_to.set
    )

    y_scrollbar_from.grid(
        row=0,
        column=1,
        sticky="ns"
    )

    y_scrollbar_to.grid(
        row=2,
        column=1,
        sticky="ns"
    )

    x_scrollbar_from.grid(
        row=1,
        column=0,
        sticky="ew"
    )

    x_scrollbar_to.grid(
        row=3,
        column=0,
        sticky="ew"
    )

    list_box_from.grid(
        row=0,
        column=0,
        sticky="nsew"
    )

    list_box_to.grid(
        row=2,
        column=0,
        sticky="nsew"
    )

    x_scrollbar_from.config(command=list_box_from.xview)
    y_scrollbar_from.config(command=list_box_from.yview)
    x_scrollbar_to.config(command=list_box_to.xview)
    y_scrollbar_to.config(command=list_box_to.yview)

    insert_args(get_args(), list_box_from)

    master.mainloop()
