from os.path import exists, isdir, splitext, split
from posixpath import join
from subprocess import run
from platform import system
from re import findall, sub
from json import loads


def flip_slashes(path, direction):
    """
        Normalizes path delimiters.
    """

    if direction == "forward":
        new_path=sub("\\\\", "/", path)
        return new_path
    if direction == "back":
        new_path=sub("/", "\\\\", path)
        return new_path


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


def get_disks():
    """
        Returns all mounted disks
    """

    logicaldisks=run([
        "wmic",
        "logicaldisk",
        "get",
        "name"
    ], capture_output=True)

    disks=findall("[A-Z]:", str(logicaldisks.stdout))
    
    return [disk + "/" for disk in disks]


def toplevel_close(dialog, boolean):
    """
        Callback that flips the value for a given toplevel_showing boolean, 
        before disposing of the toplevel.

        Toplevel windows are bound to booleans which flip when they're created 
        or destroyed, in order to prevent multiple instances of the toplevels.
    """

    boolean.set(0)
    dialog.destroy()


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
        A non-pythonic function that replaces and 
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


def cleanup(full_path):
    """
        Deletes given the file or directory (recursively) from the disk.
    """

    full_path=flip_slashes(full_path, "back")

    if isdir(full_path):
        result=run([
            "rmdir",
            "/s",
            "/q",
            full_path
        ], shell=True, capture_output=True)

    else:
        result=run([
            "del",
            "/f",
            "/q",
            full_path
        ], shell=True, capture_output=True)
    
    stderr=str(result.stderr)
    
    if len(stderr) > 3:
        raise Exception(stderr)


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


def get_offset(tk_window):
        """
            Returns an appropriate offset for a given tkinter toplevel,
            such that it always is created center screen on the primary display.
        """

        width_offset = int(
            (tk_window.winfo_screenwidth() / 2) - (tk_window.winfo_width() / 2)
        )

        height_offset = int(
            (tk_window.winfo_screenheight() / 2) - (tk_window.winfo_height() / 2)
        )

        return (width_offset, height_offset)
