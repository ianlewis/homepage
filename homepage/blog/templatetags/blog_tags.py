#:coding=utf-8:

import re
import logging
import html2text
import HTMLParser

from django.template import Library
from django.utils.safestring import mark_safe

from docutils.parsers.rst import directives, states
from docutils.parsers.rst import DirectiveError
from docutils import nodes

from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name, TextLexer

from homepage.core.templatetags.utility_tags import (
    rst_to_html,
    md_to_html,
) 

register = Library()

logger = logging.getLogger(__name__)


def flag(argument):
    if argument and argument.strip():
        raise ValueError('no argument is allowed; "%s" supplied' % argument)
    else:
        return True

def pygments_directive(name, arguments, options, content, lineno,
                       content_offset, block_text, state, state_machine):
    try:
        lexer = get_lexer_by_name(arguments[0], **options)
    except (ValueError, IndexError):
        # no lexer found - use the text one instead of an exception
        lexer = TextLexer()
    parsed = highlight(u"\n".join(content), lexer,
                       HtmlFormatter(cssclass="highlight notranslate"))
    return [nodes.raw("", parsed, format="html")]
pygments_directive.arguments = (0, 1, False)
pygments_directive.content = 1
pygments_directive.options = OPTIONS = {
    'startinline': flag,  # For PHP
}

directives.register_directive("sourcecode", pygments_directive)
directives.register_directive("code-block", pygments_directive)

align_h_values = ('left', 'center', 'right')
align_v_values = ('top', 'middle', 'bottom')
align_values = align_v_values + align_h_values


def lightbox_directive(name, arguments, options, content, lineno,
                       content_offset, block_text, state, state_machine):
    """
    lightbox image directive

    usage:

    .. lightbox:: thumb_url img_url

        Title
    """
    classes = ["lightbox-img"]
    if 'align' in options:
        directives.choice(options['align'], align_values)

        if isinstance(state, states.SubstitutionDef):
            # Check for align_v_values.
            if options['align'] not in align_v_values:
                raise DirectiveError(3,
                    'Error in "%s" directive: "%s" is not a valid value '
                    'for the "align" option within a substitution '
                    'definition.  Valid values for "align" are: "%s".'
                    % (name, options['align'],
                       '", "'.join(align_v_values)))
        elif options['align'] not in align_h_values:
            raise DirectiveError(3,
                'Error in "%s" directive: "%s" is not a valid value for '
                'the "align" option.  Valid values for "align" are: "%s".'
                % (name, options['align'],
                   '", "'.join(align_h_values)))

        classes.append('align-%s' % options['align'])

    thumb_href = arguments[0]
    img_href = arguments[1]
    title = u" ".join(content)
    alt = options.get('alt', '')

    html = '<a title="%(title)s" rel="lightbox" href="%(img_href)s"><img %(classes)s src="%(thumb_href)s" title="%(title)s" alt="%(alt)s"/></a>' % {
        "classes": 'class="%s"' % " ".join(classes) if classes else "",
        "title": title,
        "img_href": img_href,
        "thumb_href": thumb_href,
        "alt": alt,
    }
    return [nodes.raw("", html, format="html")]
lightbox_directive.arguments = (2, 0, False)
lightbox_directive.content = 1
lightbox_directive.options = {
    'alt': directives.unchanged,
    'height': directives.length_or_unitless,
    'width': directives.length_or_percentage_or_unitless,
    'scale': directives.percentage,

    'align': lambda argument: directives.choice(argument, align_values),
    'name': directives.unchanged,
    'target': directives.unchanged_required,
    'class': directives.class_option,
}


directives.register_directive("lightbox", lightbox_directive)


def to_html(obj):
    if obj.markup_type == "md":
        html = md_to_html(obj.content)
    elif obj.markup_type == "rst":
        html = rst_to_html(obj.content)
    else:
        html = mark_safe(obj.content)

    return html
register.filter("to_html", to_html)


def show_post_brief(context, post):
    return {
        "post": post,
        "last": context["forloop"]["last"],
        "can_edit": context["user"].is_staff,
    }

register.inclusion_tag("blog/post_brief.html",
                       takes_context=True)(show_post_brief)


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
    Convert HTML to plain/text
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
        except HTMLParser.HTMLParseError, e:
            logger.error('HTML Parse error: "%s" for text "%s"' % (
                e,
                html,
            ))
            return ""

    if not max_len:
        max_len = 300 if obj.locale == "jp" else 600
    return abbrev(lead, max_len, "[...]")

register.filter("to_lead", to_lead)

class AnchorParser(HTMLParser.HTMLParser):
    def __init__(self):
        HTMLParser.HTMLParser.__init__(self)
        self.img = None

    def handle_starttag(self, tag, attrs):
        if not self.img and tag == 'img':
            for name, val in attrs:
                if name == 'src':
                    self.img = val

def first_image(html):
    """
    Parses out the first image from the given
    html.
    """
    parser = AnchorParser()
    parser.feed(html)
    return parser.img

register.filter("first_image", first_image)
