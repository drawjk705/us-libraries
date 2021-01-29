"""
This type stub file was generated by pyright.
"""

SEG_STRUCT = [
    (">L", "number"),
    (">B", "flags"),
    (">B", "retention_flags"),
    (">B", "page_assoc"),
    (">L", "data_length"),
]
HEADER_FLAG_DEFERRED = 128
HEADER_FLAG_PAGE_ASSOC_LONG = 64
SEG_TYPE_MASK = 63
REF_COUNT_SHORT_MASK = 224
REF_COUNT_LONG_MASK = 536870911
REF_COUNT_LONG = 7
DATA_LEN_UNKNOWN = 4294967295
SEG_TYPE_IMMEDIATE_GEN_REGION = 38
SEG_TYPE_END_OF_PAGE = 49
SEG_TYPE_END_OF_FILE = 50
FILE_HEADER_ID = b"\x97\x4A\x42\x32\x0D\x0A\x1A\x0A"
FILE_HEAD_FLAG_SEQUENTIAL = 1
FILE_HEAD_FLAG_PAGES_UNKNOWN = 2

def bit_set(bit_pos, value): ...
def check_flag(flag, value): ...
def masked_value(mask, value): ...
def mask_value(mask, value): ...

class JBIG2StreamReader:
    """Read segments from a JBIG2 byte stream"""

    def __init__(self, stream) -> None: ...
    def get_segments(self): ...
    def is_eof(self): ...
    def parse_flags(self, segment, flags, field): ...
    def parse_retention_flags(self, segment, flags, field): ...
    def parse_page_assoc(self, segment, page, field): ...
    def parse_data_length(self, segment, length, field): ...

class JBIG2StreamWriter:
    """Write JBIG2 segments to a file in JBIG2 format"""

    def __init__(self, stream) -> None: ...
    def write_segments(self, segments, fix_last_page=...): ...
    def write_file(self, segments, fix_last_page=...): ...
    def encode_segment(self, segment): ...
    def encode_flags(self, value, segment): ...
    def encode_retention_flags(self, value, segment): ...
    def encode_data_length(self, value, segment): ...
    def get_eop_segment(self, seg_number, page_number): ...
    def get_eof_segment(self, seg_number): ...
