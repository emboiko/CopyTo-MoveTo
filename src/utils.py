from os.path import exists, isdir, splitext, split
from re import findall, sub
from subprocess import run
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
