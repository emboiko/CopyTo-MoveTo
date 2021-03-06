from tkinter import Tk
from CopyToMoveTo import CopyToMoveTo
from Socket_Singleton import Socket_Singleton


class Ct_Mt:
    """
        Wrapper class for GUI & Socket_Singleton
    """

    def __init__(self):
        """
            Immediately enforce singleton status, init Tk GUI, init args,
            and attatch the observer / callback for subsequent arguments
        """

        self.app = Socket_Singleton()
        self.root = Tk()
        self.gui = CopyToMoveTo(self.root)

        for arg in self.app.arguments:
            self.insert_arg(arg)

        self.app.arguments.clear()

        self.app.trace(self.arg_handler)
        self.root.mainloop()


    def __str__(self):
        """Return own address"""

        return f"CopyTo-MoveTo wrapper @{hex(id(self))}"


    def arg_handler(self, arg):
        """
            Observer calls back once for each argument, which we pass to the
            GUI & remove from the collection. 
        """

        self.insert_arg(arg)


    def insert_arg(self, arg):
        """Slice the prefix, strip double quotes, populate the GUI accordingly"""

        if arg.startswith("s|"):
            self.gui.list_box_source.insert("end", arg[2:].strip("\""))
            
        elif arg.startswith("d|"):
            self.gui.list_box_dest.insert("end", arg[2:].strip("\""))

        else:
            self.gui.list_box_source.insert("end", arg)


def main():
    Ct_Mt()


if __name__ == "__main__":
    main()
