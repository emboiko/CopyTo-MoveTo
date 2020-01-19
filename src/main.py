from tkinter import Tk
from CopyToMoveTo import CopyToMoveTo
from Socket_Singleton.Socket_Singleton import Socket_Singleton


def arg_handler(args, gui):
    gui.list_box_from.insert("end", args[0])
    args.pop()


def main():
    app = Socket_Singleton()
    root = Tk()
    gui = CopyToMoveTo(root)
    for arg in app.arguments:
        gui.list_box_from.insert("end", arg)
    app.arguments.clear()
    app.trace(arg_handler, gui)
    root.mainloop()


if __name__ == "__main__":
    main()
