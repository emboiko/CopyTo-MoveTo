from tkinter import (
    Tk,
    Toplevel,
    Listbox,
    Scrollbar,
    PhotoImage,
    messagebox
)
from tkinter.ttk import Treeview
from os import getcwd
from os.path import isdir
from posixpath import join
from re import split as re_split
from subprocess import run
from utils import get_disks, flip_slashes, get_offset


class Ufd:
    """
        Universal File Dialog - "UFD"
        
        Unopinionated, minimalist, reusable, slightly configurable,
        general-purpose file-dialog.
    """
    def __init__(
        self,
        show_hidden=False,
        include_files=False,
        tree_xscroll=False
    ):
        """
            Displays the Add Items dialog and doesn't allow any additional
            instances of itself to be created while it's showing.

            Add items is a minimalist filedialog comprised of a tkinter
            treeview and listbox, both with some bindings attatched.
        """

        root = Tk()
        root.withdraw()

        if show_hidden:
            self.show_hidden_files = True
        else:
            self.show_hidden_files = False

        if include_files:
            self.include_files = True
        else:
            self.include_files = False

        if tree_xscroll:
            self.tree_xscroll = True
        else:
            self.tree_xscroll = False

        self.cwd=flip_slashes(getcwd(), "forward")

        self.file_icon=PhotoImage(file=f"{self.cwd}/img/file.gif").subsample(50)
        self.folder_icon=PhotoImage(file=f"{self.cwd}/img/folder.gif").subsample(15)
        self.disk_icon=PhotoImage(file=f"{self.cwd}/img/disk.gif").subsample(15)


    def __call__(self):
        """
            Display dialog & return selection
        """
        self.dialog=Toplevel()
        self.dialog.grab_set()
        self.dialog.geometry("500x300")
        self.dialog.minsize(width=300, height=200)
        self.dialog.update()
        (width_offset, height_offset)=get_offset(self.dialog)
        self.dialog.geometry(f"+{width_offset}+{height_offset}")

        self.dialog.title("Universal File Dialog")
        self.dialog.iconbitmap(f"{self.cwd}/img/main_icon.ico")

        # Tkinter x_scroll is broken for treeview
        # https://stackoverflow.com/questions/49715456
        # https://stackoverflow.com/questions/14359906
        self.tree_x_scrollbar=Scrollbar(self.dialog, orient="horizontal")
        self.tree_y_scrollbar=Scrollbar(self.dialog, orient="vertical")
        self.file_list_x_scrollbar=Scrollbar(self.dialog, orient="horizontal")
        self.file_list_y_scrollbar=Scrollbar(self.dialog, orient="vertical")
        
        self.tree=Treeview(
            self.dialog,
            xscrollcommand=self.tree_x_scrollbar.set,
            yscrollcommand=self.tree_y_scrollbar.set,
            show="tree",
            selectmode="browse"
        )

        self.file_list=Listbox(
            self.dialog,
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
        
        self.dialog.grid_rowconfigure(0, weight=1)
        self.dialog.grid_columnconfigure(0, weight=1)
        self.dialog.grid_columnconfigure(2, weight=1)

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
        self.file_list.bind("<Return>", self.destroy_dialog)

        if self.tree_xscroll:
            self.tree.column("#0", minwidth=1000)

        self.init_dialog_populate()
        self.dialog_selection=[]
        self.dialog.focus()
        
        self.dialog.wait_window()
        return self.dialog_selection


    def init_dialog_populate(self):
        """
            Called each time show_dialog() is called, to initialize the dialog.

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


    def dialog_populate(self, event=None):
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
                if self.show_hidden_files:
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

                elif self.include_files:
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
            listbox (Callback for <<ListboxSelect>>).
        """

        self.dialog_selection.clear()
        selection_index_arr=self.file_list.curselection()

        for i in selection_index_arr:
            self.dialog_selection.append(self.file_list.get(i))


    def destroy_dialog(self, event=None):
        """
            Callback for <Return> on the file listbox.
        """

        self.dialog.destroy()
