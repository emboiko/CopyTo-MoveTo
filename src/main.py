from sys import argv
from socket import socket
from threading import Thread
from tkinter import Tk
from CopyToMoveTo import CopyToMoveTo


class Handler():
    def __init__(self):
        self.root = Tk()
        self.gui = CopyToMoveTo(self.root)
        self.root.withdraw()
        self.arguments = [arg for arg in argv[1:]]
        self.gui.list_box_from.insert("end", *self.arguments)
        self.sock = socket()
        self.socket_handler()


    def __str__(self):
        return "Wrapper & argument handler for CopyTo-MoveTo"\
        f" @ {hex(id(self))}"


    def socket_handler(self):
        try:
            self.sock.bind(("127.0.0.1", 9001))
        except:
            self.create_client()
        else:
            self.thread = Thread(target=self.create_server, daemon=True)
            self.thread.start()


    def create_server(self):
        with self.sock as s:
            s.listen()
            while True:
                connection, address = s.accept()
                with connection:
                    data = connection.recv(1024)
                    self.gui.list_box_from.insert("end",data.decode())


    def create_client(self):
        with self.sock as s:
            s.connect(("127.0.0.1", 9001))
            if len(argv) > 1:
                s.send(argv[1].encode())


def main():
    app = Handler()
    if hasattr(app, "thread"):
        app.root.deiconify()
        app.root.mainloop()
    

if __name__ == "__main__":
    main()
