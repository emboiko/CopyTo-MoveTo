from tkinter import Tk
from CopyToMoveTo import CopyToMoveTo
from socket_singleton import Socket_Singleton


def arg_handler(app, gui):
    gui.list_box_from.insert("end", app.arguments[0])
    app.arguments.pop()


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
