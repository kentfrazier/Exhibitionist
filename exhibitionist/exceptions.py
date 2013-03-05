# -*- coding: utf-8 -*-
from __future__ import print_function

class ExhibitionistError(Exception):
    def __init__(self, value,errno=None):
        self.value = value
        self.errno=errno

    def __str__(self):
        return repr(self.value)

