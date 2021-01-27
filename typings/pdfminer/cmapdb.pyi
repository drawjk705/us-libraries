"""
This type stub file was generated by pyright.
"""

import logging
from .psparser import PSStackParser

""" Adobe character mapping (CMap) support.

CMaps provide the mapping between character codes and Unicode
code-points to character ids (CIDs).

More information is available on the Adobe website:

  http://opensource.adobe.com/wiki/display/cmap/CMap+Resources

"""
log = logging.getLogger(__name__)
class CMapError(Exception):
    ...


class CMapBase:
    debug = ...
    def __init__(self, **kwargs) -> None:
        ...
    
    def is_vertical(self):
        ...
    
    def set_attr(self, k, v):
        ...
    
    def add_code2cid(self, code, cid):
        ...
    
    def add_cid2unichr(self, cid, code):
        ...
    
    def use_cmap(self, cmap):
        ...
    


class CMap(CMapBase):
    def __init__(self, **kwargs) -> None:
        ...
    
    def __repr__(self):
        ...
    
    def use_cmap(self, cmap):
        ...
    
    def decode(self, code):
        ...
    
    def dump(self, out=..., code2cid=..., code=...):
        ...
    


class IdentityCMap(CMapBase):
    def decode(self, code):
        ...
    


class IdentityCMapByte(IdentityCMap):
    def decode(self, code):
        ...
    


class UnicodeMap(CMapBase):
    def __init__(self, **kwargs) -> None:
        ...
    
    def __repr__(self):
        ...
    
    def get_unichr(self, cid):
        ...
    
    def dump(self, out=...):
        ...
    


class FileCMap(CMap):
    def add_code2cid(self, code, cid):
        ...
    


class FileUnicodeMap(UnicodeMap):
    def add_cid2unichr(self, cid, code):
        ...
    


class PyCMap(CMap):
    def __init__(self, name, module) -> None:
        ...
    


class PyUnicodeMap(UnicodeMap):
    def __init__(self, name, module, vertical) -> None:
        ...
    


class CMapDB:
    _cmap_cache = ...
    _umap_cache = ...
    class CMapNotFound(CMapError):
        ...
    
    
    @classmethod
    def get_cmap(cls, name):
        ...
    
    @classmethod
    def get_unicode_map(cls, name, vertical=...):
        ...
    


class CMapParser(PSStackParser):
    def __init__(self, cmap, fp) -> None:
        ...
    
    def run(self):
        ...
    
    KEYWORD_BEGINCMAP = ...
    KEYWORD_ENDCMAP = ...
    KEYWORD_USECMAP = ...
    KEYWORD_DEF = ...
    KEYWORD_BEGINCODESPACERANGE = ...
    KEYWORD_ENDCODESPACERANGE = ...
    KEYWORD_BEGINCIDRANGE = ...
    KEYWORD_ENDCIDRANGE = ...
    KEYWORD_BEGINCIDCHAR = ...
    KEYWORD_ENDCIDCHAR = ...
    KEYWORD_BEGINBFRANGE = ...
    KEYWORD_ENDBFRANGE = ...
    KEYWORD_BEGINBFCHAR = ...
    KEYWORD_ENDBFCHAR = ...
    KEYWORD_BEGINNOTDEFRANGE = ...
    KEYWORD_ENDNOTDEFRANGE = ...
    def do_keyword(self, pos, token):
        ...
    


def main(argv):
    ...

if __name__ == '__main__':
    ...
