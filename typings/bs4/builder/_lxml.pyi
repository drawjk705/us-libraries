"""
This type stub file was generated by pyright.
"""

from bs4.builder import HTMLTreeBuilder, TreeBuilder

__license__ = "MIT"
LXML = 'lxml'
class LXMLTreeBuilderForXML(TreeBuilder):
    DEFAULT_PARSER_CLASS = ...
    is_xml = ...
    processing_instruction_class = ...
    NAME = ...
    ALTERNATE_NAMES = ...
    features = ...
    CHUNK_SIZE = ...
    DEFAULT_NSMAPS = ...
    DEFAULT_NSMAPS_INVERTED = ...
    def initialize_soup(self, soup):
        """Let the BeautifulSoup object know about the standard namespace
        mapping.

        :param soup: A `BeautifulSoup`.
        """
        ...
    
    def default_parser(self, encoding):
        """Find the default parser for the given encoding.

        :param encoding: A string.
        :return: Either a parser object or a class, which
          will be instantiated with default arguments.
        """
        ...
    
    def parser_for(self, encoding):
        """Instantiate an appropriate parser for the given encoding.

        :param encoding: A string.
        :return: A parser object such as an `etree.XMLParser`.
        """
        ...
    
    def __init__(self, parser=..., empty_element_tags=..., **kwargs) -> None:
        ...
    
    def prepare_markup(self, markup, user_specified_encoding=..., exclude_encodings=..., document_declared_encoding=...):
        """Run any preliminary steps necessary to make incoming markup
        acceptable to the parser.

        lxml really wants to get a bytestring and convert it to
        Unicode itself. So instead of using UnicodeDammit to convert
        the bytestring to Unicode using different encodings, this
        implementation uses EncodingDetector to iterate over the
        encodings, and tell lxml to try to parse the document as each
        one in turn.

        :param markup: Some markup -- hopefully a bytestring.
        :param user_specified_encoding: The user asked to try this encoding.
        :param document_declared_encoding: The markup itself claims to be
            in this encoding.
        :param exclude_encodings: The user asked _not_ to try any of
            these encodings.

        :yield: A series of 4-tuples:
         (markup, encoding, declared encoding,
          has undergone character replacement)

         Each 4-tuple represents a strategy for converting the
         document to Unicode and parsing it. Each strategy will be tried 
         in turn.
        """
        ...
    
    def feed(self, markup):
        ...
    
    def close(self):
        ...
    
    def start(self, name, attrs, nsmap=...):
        ...
    
    def end(self, name):
        ...
    
    def pi(self, target, data):
        ...
    
    def data(self, content):
        ...
    
    def doctype(self, name, pubid, system):
        ...
    
    def comment(self, content):
        "Handle comments as Comment objects."
        ...
    
    def test_fragment_to_document(self, fragment):
        """See `TreeBuilder`."""
        ...
    


class LXMLTreeBuilder(HTMLTreeBuilder, LXMLTreeBuilderForXML):
    NAME = ...
    ALTERNATE_NAMES = ...
    features = ...
    is_xml = ...
    processing_instruction_class = ...
    def default_parser(self, encoding):
        ...
    
    def feed(self, markup):
        ...
    
    def test_fragment_to_document(self, fragment):
        """See `TreeBuilder`."""
        ...
    


