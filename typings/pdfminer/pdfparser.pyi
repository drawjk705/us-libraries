"""
This type stub file was generated by pyright.
"""

import logging
from .psparser import PSStackParser
from .pdftypes import PDFException

log = logging.getLogger(__name__)
class PDFSyntaxError(PDFException):
    ...


class PDFParser(PSStackParser):
    """
    PDFParser fetch PDF objects from a file stream.
    It can handle indirect references by referring to
    a PDF document set by set_document method.
    It also reads XRefs at the end of every PDF file.

    Typical usage:
      parser = PDFParser(fp)
      parser.read_xref()
      parser.read_xref(fallback=True) # optional
      parser.set_document(doc)
      parser.seek(offset)
      parser.nextobject()

    """
    def __init__(self, fp) -> None:
        ...
    
    def set_document(self, doc):
        """Associates the parser with a PDFDocument object."""
        ...
    
    KEYWORD_R = ...
    KEYWORD_NULL = ...
    KEYWORD_ENDOBJ = ...
    KEYWORD_STREAM = ...
    KEYWORD_XREF = ...
    KEYWORD_STARTXREF = ...
    def do_keyword(self, pos, token):
        """Handles PDF-related keywords."""
        ...
    


class PDFStreamParser(PDFParser):
    """
    PDFStreamParser is used to parse PDF content streams
    that is contained in each page and has instructions
    for rendering the page. A reference to a PDF document is
    needed because a PDF content stream can also have
    indirect references to other objects in the same document.
    """
    def __init__(self, data) -> None:
        ...
    
    def flush(self):
        ...
    
    KEYWORD_OBJ = ...
    def do_keyword(self, pos, token):
        ...
    


