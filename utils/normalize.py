# coding: utf-8
import re
import sys
import unicodedata
from HTMLParser import HTMLParser

DEL_ZERO_WIDTH_SPACE = re.compile(ur'(?u)[\u200B \u200E\uFEFF\u2060]+')
DEL_STRANGE_SEPARATOR_SPACE = re.compile(ur'(?u)\{0\}|\{/0\}|\{0/\}|\{1\}|\{/1\}')
DEL_SLASH_T = re.compile(ur'(?u)\\t|\\\\n')
DEL_SLASH_QUOTE = re.compile(ur"(?u)\\'")

UNESCAPE_FACTOR_SEPARATOR = re.compile(r'&#124;'), r'|'
UNESCAPE_LEFT_ANGLE_BRACKET = re.compile(r'&lt;'), r'<'
UNESCAPE_RIGHT_ANGLE_BRACKET = re.compile(r'&gt;'), r'>'
UNESCAPE_DOUBLE_QUOTE = re.compile(r'&quot;'), r'"'
UNESCAPE_SINGLE_QUOTE = re.compile(r"&apos;"), r"'"
UNESCAPE_SYNTAX_NONTERMINAL_LEFT = re.compile(r'&#91;'), r'['
UNESCAPE_SYNTAX_NONTERMINAL_RIGHT = re.compile(r'&#93;'), r']'
UNESCAPE_AMPERSAND = re.compile(r'&amp;'), r'&'
# The legacy regexes are used to support outputs from older Moses versions.
UNESCAPE_FACTOR_SEPARATOR_LEGACY = re.compile(r'&bar;'), r'|'
UNESCAPE_SYNTAX_NONTERMINAL_LEFT_LEGACY = re.compile(r'&bra;'), r'['
UNESCAPE_SYNTAX_NONTERMINAL_RIGHT_LEGACY = re.compile(r'&ket;'), r']'


MOSES_UNESCAPE_XML_REGEXES = [UNESCAPE_FACTOR_SEPARATOR_LEGACY,
                              UNESCAPE_FACTOR_SEPARATOR, UNESCAPE_LEFT_ANGLE_BRACKET,
                              UNESCAPE_RIGHT_ANGLE_BRACKET,
                              UNESCAPE_SYNTAX_NONTERMINAL_LEFT_LEGACY,
                              UNESCAPE_SYNTAX_NONTERMINAL_RIGHT_LEGACY,
                              UNESCAPE_DOUBLE_QUOTE, UNESCAPE_SINGLE_QUOTE,
                              UNESCAPE_SYNTAX_NONTERMINAL_LEFT,
                              UNESCAPE_SYNTAX_NONTERMINAL_RIGHT, UNESCAPE_AMPERSAND]

HTML_PARSER = HTMLParser()


def unescape_xml(text):
    for regexp, substitution in MOSES_UNESCAPE_XML_REGEXES:
        text = regexp.sub(substitution, text)
    return text

def normalize(text):
    text = DEL_SLASH_T.sub(u' ', DEL_STRANGE_SEPARATOR_SPACE.sub(u'', DEL_ZERO_WIDTH_SPACE.sub(u' ', text)))
    text = DEL_SLASH_QUOTE.sub(u"'", text)
    return unicodedata.normalize('NFKC', HTML_PARSER.unescape(unescape_xml(text)))


def remove_control_characters(s):
    return "".join(ch for ch in s if unicodedata.category(ch)[0]!="C")

def main():
    for l in sys.stdin:
        snts = l.decode('utf-8').strip(u'\n').replace(u'\t', u' ').replace(u'\\r', u'').replace(u'\\n', u'\n').split(u'\n')
        for s in snts:
            s = remove_control_characters(normalize(s))
            if s and len(s) > 1:
                print s.encode('utf-8')

if __name__ == '__main__':
    main()