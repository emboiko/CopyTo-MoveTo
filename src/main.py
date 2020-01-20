from tkinter import Tk
from CopyToMoveTo import CopyToMoveTo
from Socket_Singleton.Socket_Singleton import Socket_Singleton

############################################################################
# Ed Boiko
# CopyTo-MoveTo (Beta)
# 1/19/2020 
# https://github.com/emboiko/CopyTo-MoveTo

# If you're reading this, consider submitting a pull request on this 
# contrived application or one of its submodules :) Perhaps validate 
# my existence with a star. 

#   Todo:
#########
# - CopyTo-MoveTo.py & Ufd.py can both be dry'd and refactored. I started 
# writing this when I barely knew a thing about Python, and this project
# served double duty as a sandbox/playground and as a semi-legitimate
# project. There are artifacts dotted throughout the code that indicate 
# this very clearly, and there are many things I consciously chose to 
# implement non-Pythonic at the time. This repo is ready to be branched 
# into a much better version of itself, so there should be none, or very 
# few commits remaining for this branch.

# - Assets such as photos & text documents need a better place in my 
# non-existent directory structure, and I'm currently just duplicating them 
# so they ship easily with the x64 binaries that PyInstaller builds for me, 
# and THAT is all becoming very silly very fast. 

# - Path delimiters got a little out of control- There's too many sloc 
# dedicated to finessing backslashes to forward and vice versa with my
# own homebrewed solutions. This is one of a few areas in this project 
# where I want to eliminate reinventing the wheel, when a standard library
# module can do it for me. 

# - Ufd (which is a submodule now) turned out great but there's a fine line 
# between "minimalist" and "lacking features". At the very least, Ufd needs 
# better data structures & MVC pattern. It would be *nice* to adapt Ufd to 
# non-Windows systems. There should be controls to search, create & delete.

# - I have a bit more learning to do before I think about publishing this 
# application (or its submodules, which are probably more interesting than 
# the application itself if I'm honest) to PyPi, but that's the plan. If 
# anyone actually benefits from pip installing something I wrote, that would
# be pretty neat.

#   Some smaller things:
########################
# - the .exe should have a cute little icon.
# - no dark mode in 2020 is a sin, this should be on a toggle
# - An "official" changelog will begin with the new branch complete with a 
# super professional major.minor.revision patch notation 
############################################################################


class Ct_Mt:
    """
        Wrapper class to hook up GUI w/ Socket_Singleton
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
    """
        CopyTo-MoveTo: Single-instance, minimalist file-manager (for Windows).        
    """
    
    Ct_Mt()


if __name__ == "__main__":
    main()
