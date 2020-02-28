from tkinter import Tk
from CopyToMoveTo import CopyToMoveTo
from Socket_Singleton.Socket_Singleton import Socket_Singleton

class Ct_Mt:
    """
        Wrapper class for GUI & Socket_Singleton
    """

    def __init__(self):
        self.app = Socket_Singleton()
        self.root = Tk()
        self.gui = CopyToMoveTo(self.root)

        for arg in self.app.arguments:
            self.gui.list_box_from.insert("end", arg)
        self.app.arguments.clear()

        self.app.trace(self.arg_handler)
        self.root.mainloop()

    
    def __str__(self):
        return f"CopyTo-MoveTo wrapper @{hex(id(self))}"


    def arg_handler(self, args):
        """
            Observer calls back once for each argument, which we pass to the
            GUI & remove from the collection. 
        """
        
        self.gui.list_box_from.insert("end", args.pop())


def main():
    Ct_Mt()


if __name__ == "__main__":
    main()
