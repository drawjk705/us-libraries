"""
This type stub file was generated by pyright.
"""

import os
import re
import sys
import traceback
import warnings
from collections import Counter

from .builder import ParserRejectedMarkup, builder_registry
from .dammit import UnicodeDammit
from .element import (
    DEFAULT_OUTPUT_ENCODING,
    PYTHON_SPECIFIC_ENCODINGS,
    CData,
    Comment,
    Declaration,
    Doctype,
    NavigableString,
    PageElement,
    ProcessingInstruction,
    ResultSet,
    Script,
    SoupStrainer,
    Stylesheet,
    Tag,
    TemplateString,
)

"""Beautiful Soup Elixir and Tonic - "The Screen-Scraper's Friend".

http://www.crummy.com/software/BeautifulSoup/

Beautiful Soup uses a pluggable XML or HTML parser to parse a
(possibly invalid) document into a tree representation. Beautiful Soup
provides methods and Pythonic idioms that make it easy to navigate,
search, and modify the parse tree.

Beautiful Soup works with Python 2.7 and up. It works better if lxml
and/or html5lib is installed.

For more than you ever wanted to know about Beautiful Soup, see the
documentation: http://www.crummy.com/software/BeautifulSoup/bs4/doc/
"""
__author__ = "Leonard Richardson (leonardr@segfault.org)"
__version__ = "4.9.3"
__copyright__ = "Copyright (c) 2004-2020 Leonard Richardson"
__license__ = "MIT"

class GuessedAtParserWarning(UserWarning):
    """The warning issued when BeautifulSoup has to guess what parser to
    use -- probably because no parser was specified in the constructor.
    """

    ...

class MarkupResemblesLocatorWarning(UserWarning):
    """The warning issued when BeautifulSoup is given 'markup' that
    actually looks like a resource locator -- a URL or a path to a file
    on disk.
    """

    ...

class BeautifulSoup(Tag):
    """A data structure representing a parsed HTML or XML document.

    Most of the methods you'll call on a BeautifulSoup object are inherited from
    PageElement or Tag.

    Internally, this class defines the basic interface called by the
    tree builders when converting an HTML/XML document into a data
    structure. The interface abstracts away the differences between
    parsers. To write a new tree builder, you'll need to understand
    these methods as a whole.

    These methods will be called by the BeautifulSoup constructor:
      * reset()
      * feed(markup)

    The tree builder may call these methods from its feed() implementation:
      * handle_starttag(name, attrs) # See note about return value
      * handle_endtag(name)
      * handle_data(data) # Appends to the current data node
      * endData(containerClass) # Ends the current data node

    No matter how complicated the underlying parser is, you should be
    able to build a tree using 'start tag' events, 'end tag' events,
    'data' events, and "done with data" events.

    If you encounter an empty-element tag (aka a self-closing tag,
    like HTML's <br> tag), call handle_starttag and then
    handle_endtag.
    """

    ROOT_TAG_NAME = ...
    DEFAULT_BUILDER_FEATURES = ...
    ASCII_SPACES = ...
    NO_PARSER_SPECIFIED_WARNING = ...
    def __init__(
        self,
        markup=...,
        features=...,
        builder=...,
        parse_only=...,
        from_encoding=...,
        exclude_encodings=...,
        element_classes=...,
        **kwargs
    ) -> None:
        """Constructor.

        :param markup: A string or a file-like object representing
         markup to be parsed.

        :param features: Desirable features of the parser to be
         used. This may be the name of a specific parser ("lxml",
         "lxml-xml", "html.parser", or "html5lib") or it may be the
         type of markup to be used ("html", "html5", "xml"). It's
         recommended that you name a specific parser, so that
         Beautiful Soup gives you the same results across platforms
         and virtual environments.

        :param builder: A TreeBuilder subclass to instantiate (or
         instance to use) instead of looking one up based on
         `features`. You only need to use this if you've implemented a
         custom TreeBuilder.

        :param parse_only: A SoupStrainer. Only parts of the document
         matching the SoupStrainer will be considered. This is useful
         when parsing part of a document that would otherwise be too
         large to fit into memory.

        :param from_encoding: A string indicating the encoding of the
         document to be parsed. Pass this in if Beautiful Soup is
         guessing wrongly about the document's encoding.

        :param exclude_encodings: A list of strings indicating
         encodings known to be wrong. Pass this in if you don't know
         the document's encoding but you know Beautiful Soup's guess is
         wrong.

        :param element_classes: A dictionary mapping BeautifulSoup
         classes like Tag and NavigableString, to other classes you'd
         like to be instantiated instead as the parse tree is
         built. This is useful for subclassing Tag or NavigableString
         to modify default behavior.

        :param kwargs: For backwards compatibility purposes, the
         constructor accepts certain keyword arguments used in
         Beautiful Soup 3. None of these arguments do anything in
         Beautiful Soup 4; they will result in a warning and then be
         ignored.

         Apart from this, any keyword arguments passed into the
         BeautifulSoup constructor are propagated to the TreeBuilder
         constructor. This makes it possible to configure a
         TreeBuilder by passing in arguments, not just by saying which
         one to use.
        """
        ...
    def __copy__(self):
        """Copy a BeautifulSoup object by converting the document to a string and parsing it again."""
        ...
    def __getstate__(self): ...
    def reset(self):
        """Reset this object to a state as though it had never parsed any
        markup.
        """
        ...
    def new_tag(
        self,
        name,
        namespace=...,
        nsprefix=...,
        attrs=...,
        sourceline=...,
        sourcepos=...,
        **kwattrs
    ):
        """Create a new Tag associated with this BeautifulSoup object.

        :param name: The name of the new Tag.
        :param namespace: The URI of the new Tag's XML namespace, if any.
        :param prefix: The prefix for the new Tag's XML namespace, if any.
        :param attrs: A dictionary of this Tag's attribute values; can
            be used instead of `kwattrs` for attributes like 'class'
            that are reserved words in Python.
        :param sourceline: The line number where this tag was
            (purportedly) found in its source document.
        :param sourcepos: The character position within `sourceline` where this
            tag was (purportedly) found.
        :param kwattrs: Keyword arguments for the new Tag's attribute values.

        """
        ...
    def string_container(self, base_class=...): ...
    def new_string(self, s, subclass=...):
        """Create a new NavigableString associated with this BeautifulSoup
        object.
        """
        ...
    def insert_before(self, *args):
        """This method is part of the PageElement API, but `BeautifulSoup` doesn't implement
        it because there is nothing before or after it in the parse tree.
        """
        ...
    def insert_after(self, *args):
        """This method is part of the PageElement API, but `BeautifulSoup` doesn't implement
        it because there is nothing before or after it in the parse tree.
        """
        ...
    def popTag(self):
        """Internal method called by _popToTag when a tag is closed."""
        ...
    def pushTag(self, tag):
        """Internal method called by handle_starttag when a tag is opened."""
        ...
    def endData(self, containerClass=...):
        """Method called by the TreeBuilder when the end of a data segment
        occurs.
        """
        ...
    def object_was_parsed(self, o, parent=..., most_recent_element=...):
        """Method called by the TreeBuilder to integrate an object into the parse tree."""
        ...
    def handle_starttag(
        self, name, namespace, nsprefix, attrs, sourceline=..., sourcepos=...
    ):
        """Called by the tree builder when a new tag is encountered.

        :param name: Name of the tag.
        :param nsprefix: Namespace prefix for the tag.
        :param attrs: A dictionary of attribute values.
        :param sourceline: The line number where this tag was found in its
            source document.
        :param sourcepos: The character position within `sourceline` where this
            tag was found.

        If this method returns None, the tag was rejected by an active
        SoupStrainer. You should proceed as if the tag had not occurred
        in the document. For instance, if this was a self-closing tag,
        don't call handle_endtag.
        """
        ...
    def handle_endtag(self, name, nsprefix=...):
        """Called by the tree builder when an ending tag is encountered.

        :param name: Name of the tag.
        :param nsprefix: Namespace prefix for the tag.
        """
        ...
    def handle_data(self, data):
        """Called by the tree builder when a chunk of textual data is encountered."""
        ...
    def decode(self, pretty_print=..., eventual_encoding=..., formatter=...):
        """Returns a string or Unicode representation of the parse tree
            as an HTML or XML document.

        :param pretty_print: If this is True, indentation will be used to
            make the document more readable.
        :param eventual_encoding: The encoding of the final document.
            If this is None, the document will be a Unicode string.
        """
        ...

_s = BeautifulSoup
_soup = BeautifulSoup

class BeautifulStoneSoup(BeautifulSoup):
    """Deprecated interface to an XML parser."""

    def __init__(self, *args, **kwargs) -> None: ...

class StopParsing(Exception):
    """Exception raised by a TreeBuilder if it's unable to continue parsing."""

    ...

class FeatureNotFound(ValueError):
    """Exception raised by the BeautifulSoup constructor if no parser with the
    requested features is found.
    """

    ...

if __name__ == "__main__":
    soup = BeautifulSoup(sys.stdin)
