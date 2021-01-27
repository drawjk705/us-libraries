"""
This type stub file was generated by pyright.
"""

import logging

logger = logging.getLogger(__name__)
class CorruptDataError(Exception):
    ...


class LZWDecoder:
    def __init__(self, fp) -> None:
        ...
    
    def readbits(self, bits):
        ...
    
    def feed(self, code):
        ...
    
    def run(self):
        ...
    


def lzwdecode(data):
    ...

