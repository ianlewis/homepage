#:coding=utf-8:

import re
import logging
import html2text
import HTMLParser

from django.template import Library
from django.utils.safestring import mark_safe

from docutils import nodes
from docutils.writers import html4css1
from docutils.core import publish_parts
from docutils.parsers.rst import directives

from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name, TextLexer

register = Library()

logger = logging.getLogger(__name__)

VARIANTS = {}

def pygments_directive(name, arguments, options, content, lineno,
                       content_offset, block_text, state, state_machine):
    try:
        lexer = get_lexer_by_name(arguments[0])
    except (ValueError, IndexError):
        # no lexer found - use the text one instead of an exception
        lexer = TextLexer()
    parsed = highlight(u"\n".join(content), lexer, HtmlFormatter(cssclass="highlight notranslate"))
    return [nodes.raw("", parsed, format="html")]
pygments_directive.arguments = (0, 1, False)
pygments_directive.content = 1
pygments_directive.options = dict([(key, directives.flag) for key in VARIANTS])

directives.register_directive("sourcecode", pygments_directive)
directives.register_directive("code-block", pygments_directive)

def lightbox_directive(name, arguments, options, content, lineno,
        content_offset, block_text, state, state_machine):
    """
    lightbox image directive

    usage:

    .. lightbox:: thumb_url img_url

        Title
    """
    thumb_href = arguments[0]
    img_href = arguments[1]
    title = u" ".join(content)

    html = '<div class="lightbox-img"><a title="%(title)s" rel="lightbox" href="%(img_href)s"><img src="%(thumb_href)s" title="%(title)s" alt=""/></a></div>' % {
        "title": title, 
        "img_href": img_href,
        "thumb_href": thumb_href,
    }
    return [nodes.raw("", html, format="html")]
lightbox_directive.arguments = (2, 2, False)
lightbox_directive.content = 1
lightbox_directive.options = dict([(key, directives.flag) for key in VARIANTS])

directives.register_directive("lightbox", lightbox_directive)

class HTMLWriter(html4css1.Writer):
    def __init__(self):
        html4css1.Writer.__init__(self)
        self.translator_class = HTMLTranslator

class HTMLTranslator(html4css1.HTMLTranslator):
    named_tags = []
    
    def visit_literal(self, node):
        # TODO: wrapping fixes.
        self.body.append("<code>%s</code>" % node.astext())
        raise nodes.SkipNode


def rst_to_html(value):
    parts = publish_parts(source=value, writer=HTMLWriter(),
        settings_overrides={"initial_header_level": 2})
    return parts["fragment"]
    

def to_html(obj):
    if obj.markup_type == "html":
        html = obj.content
    elif obj.markup_type == "rst":
        html = rst_to_html(obj.content)
    return mark_safe(html)
register.filter("to_html", to_html)

def show_post_brief(context, post):
    return {
        "post": post,
        "last": context["forloop"]["last"],
        "can_edit": context["user"].is_staff,
    }
register.inclusion_tag("blog/post_brief.html", takes_context=True)(show_post_brief)

@register.filter
def date_microformat(d):
    '''
        Microformat version of a date.
        2009-02-10T02:58:00+00:00 (ideal)
        2009-02-09T17:54:41.181868-08:00 (mine)
    '''
    return d.isoformat()

STRIKE_REPL_RE = re.compile("< *strike *>[^<]*</ *strike *>", re.IGNORECASE)
def html_to_text(html):
    """
    HTMLを plain/text に変換する
    """
    h = html2text.HTML2Text()
    h.ignore_links = True
    h.ignore_images = True
    h.ignore_emphasis = True
    h.hide_strikethrough = True
    # <strike>***</strike> テキストを削る 
    text = STRIKE_REPL_RE.sub("", html)
    # html2text を呼び出す
    text = h.handle(text).replace("&nbsp_place_holder;", " ")
    # 先頭と後続の空白を削る
    return text.strip()

def abbrev(s, num=255, end="..."):
    """
    >>> abbrev('spamspamspam', 6)
    'spa...'
    >>> abbrev('spamspamspam', 12)
    'spamspamspam'
    >>> abbrev('blahblahblah', 13)
    'eggseggseg...'
    >>> abbrev('eggseggseggs', 1)
    'e'
    >>> abbrev('eggseggseggs', 2, '.')
    'e.'
    """
    index = num - len(end)
    if len(s) > num:
        s = (s[:index] + end) if index > 0 else s[:num]
    return s

def to_lead(obj, max_len=None):
    if obj.lead:
        lead = obj.lead
    elif obj.content:
        html = to_html(obj)
        try:
            lead = html_to_text(html)
        except HTMLParser.HTMLParseError,e:
            logger.error('HTML Parse error: "%s" for text "%s"' % (
                e,
                html,
            ))
            return ""

    if not max_len:
        max_len = 300 if obj.locale == "jp" else 600
    return abbrev(lead, max_len, "[...]")
         
register.filter("to_lead", to_lead)
