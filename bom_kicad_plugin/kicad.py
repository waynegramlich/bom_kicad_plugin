# MIT License
# 
# Copyright (c) 2019 Wayne C. Gramlich
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from bom_manager import bom

class Kicad(bom.Cad):
    def __init__(self, tracing=None):
        # Verify argument types:
        assert isinstance(tracing, str) or tracing is None

        # Perform any requested *tracing*:
        next_tracing = None if tracing is None else tracing + " "
        if tracing is not None:
            print(f"{tracing}=>Kicad.__init__()")

        # Initialize the super class of the *FindChips* object (i.e. *self*):
        super().__init__("KiCAD", tracing=next_tracing)

        # Perform any requested *tracing*:
        if tracing is not None:
            print(f"{tracing}<=Kicad.__init__()")

    def load(self, file_name, tracing=None):
        # Verify argument types:
        assert isinstance(file_name, str)
        assert isinstance(tracing, str) or tracing is None

        # Perform any requested *tracing*:
        next_tracing = None if tracing is None else tracing + " "
        if tracing is not None:
            print(f"{tracing}=>Kicad.load(*, '{file_name}')")

        # Wrap up any requested *tracing* and return the *matches_list*
        foo = list()
        if tracing is not None:
            print(f"{tracing}<=Kicad.load(*, '{file_name}')=>[...]")
        return foo


def cad_get(tracing=None):
    # Verify argument types:
    assert isinstance(tracing, str) or tracing is None

    # Perform any requested *tracing*:
    next_tracing = None if tracing is None else tracing + " "
    if tracing is not None:
        print(f"{tracing}=>findchips.py:panda_get()")

    # Create the *find_chips* object:
    kicad = Kicad(tracing=next_tracing)

    # Wrap up any requested *tracing* and return *kicad*:
    if tracing is not None:
        print(f"{tracing}<=findchips.py:panda_get()=>*")
    return kicad

