"""
This type stub file was generated by pyright.
"""

def align32(x):
    ...

class BMPWriter:
    def __init__(self, fp, bits, width, height) -> None:
        ...
    
    def write_line(self, y, data):
        ...
    


class ImageWriter:
    """Write image to a file

    Supports various image types: JPEG, JBIG2 and bitmaps
    """
    def __init__(self, outdir) -> None:
        ...
    
    def export_image(self, image):
        ...
    
    @staticmethod
    def is_jbig2_image(image):
        ...
    


