from sys import argv
from socket import socket
from threading import Thread


class Socket_Singleton():
    """
        Allows a single instance of a python application to run at a time.
        First one that binds to the specified port wins, and will collect
        the arguments from subsequent calls to the application. 
    """
    
    def __init__(self, address="127.0.0.1", port=1337, client=True):
        """
            Initializer uses exception handler control flow to determine
            what kind of object it's going to be. Either we can bind to 
            the port, or we can connect to it. Specify client=False
            to discard arguments collected from other clients.
        """

        self.address = address
        self.port = port
        self.client = client
        self.arguments = [arg for arg in argv[1:]]
        self._observers = dict()
    
        self._sock = socket()
        try:
            self._sock.bind((self.address, self.port))
        except:
            if self.client:
                self._create_client()
                raise SystemExit
            else:
                raise SystemExit
        else:
            self._running = True
            self._thread = Thread(target=self._create_server, daemon=True)
            self._thread.start()


    def _create_server(self):
        """
            If the socket bound successfully, a threaded server will
            continuously listen for & receive connections & data from
            potential clients. Arguments passed from clients are 
            collected into self.arguments
        """

        with self._sock as s:
            s.listen()
            while self._running:
                connection, address = s.accept()
                with connection:
                    data = connection.recv(1024)
                    args = data.decode().split("\n")
                    [self._append_args(arg) for arg in args if arg]


    def _create_client(self):
        """
            If the server can't be created, it is assumed one already
            exists. A non-threaded client sends its arguments to the 
            existing server.
        """

        with self._sock as s:
            s.connect(("127.0.0.1", self.port))
            for arg in argv[1:]:
                s.send(arg.encode())
                s.send("\n".encode())


    def _append_args(self, arg):
        """Pseudo-setter for self._arguments"""

        self.arguments.append(arg)
        self._update_observers()


    def _update_observers(self):
        """Call all observers"""
        
        [
            observer(self, *args[0], **args[1])
            for observer, args 
            in self._observers.items()
        ]


    def trace(self, observer, *args, **kwargs):
        """Attach a callback"""

        self._observers[observer] = args, kwargs


    def close(self):
        """
            If we want to prematurely release the port:
            Create a dummy socket and send a falsy string to the server.
            Artificially satisfies the blocking call to accept() in
            self._create_server()
        """
        
        self._running = False
        dummy_socket = socket()
        with dummy_socket as ds:
            ds.connect(("127.0.0.1", self.port))
            ds.send("".encode())
