import urllib.parse
from urllib.parse import parse_qs, urlparse
from typing import Dict, Any, Match, Tuple, Optional

from markdown import Markdown
from markdown.extensions import Extension
from markdown.inlinepatterns import InlineProcessor
from xml.etree import ElementTree


class EmbedInlineProcessor(InlineProcessor):
    # Don't worry about re.compiling this, markdown.inlinepatterns.Pattern.__init__ does that for us
    EMBED_RE = r'\[\[(?P<url>.+?)\]\]'

    # Prefixes of the iframe src attributes we generate
    YOUTUBE_SRC_PREFIX = '//www.youtube-nocookie.com/embed/'
    IFRAME_SRC_PREFIXES = [YOUTUBE_SRC_PREFIX]

    # Other iframe attributes we generate
    IFRAME_ATTRIBS = ['width', 'height', 'frameborder', 'allowfullscreen']

    def __init__(self, md: Markdown, configs: Dict[str, Any]) -> None:
        super().__init__(self.EMBED_RE, md)
        self.config = configs

    def handleMatch(self, m: Match[str], data: str) -> Tuple[ElementTree.Element, int, int]:  # type: ignore[override]
        d = m.groupdict()
        url = d.get('url')
        el: Optional[ElementTree.Element]
        if not url:
            el = ElementTree.Element('span')
            el.text = "[[]]"
            return el, m.start(0), m.end(0)
        try:
            link = urlparse(url)
            host = link.hostname
        except:
            el = ElementTree.Element('span')
            el.text = "[[" + url + "]]"
            return el, m.start(0), m.end(0)
        el = None
        try:
            if host == 'youtube.com' or host == 'www.youtube.com' or host == 'youtu.be':
                el = self._embed_youtube(self._get_youtube_id(link))
        except:
            pass
        if el is None:
            el = ElementTree.Element('span')
            el.text = "[[" + url + "]]"
        return el, m.start(0), m.end(0)

    def _get_youtube_id(self, link: urllib.parse.ParseResult) -> str:
        return (link.path if link.netloc == 'youtu.be'
                else parse_qs(link.query)['v'][0])

    def _embed_youtube(self, vid_id: str) -> ElementTree.Element:
        el = ElementTree.Element('iframe')
        el.set('width', '100%')
        el.set('height', '600')
        el.set('frameborder', '0')
        el.set('allowfullscreen', '')
        el.set('src', self.YOUTUBE_SRC_PREFIX + vid_id + '?rel=0')
        return el


class KerbDown(Extension):
    def __init__(self, **kwargs: str) -> None:
        super().__init__(**kwargs) # type: ignore[arg-type]
        self.config: Dict[str, Any] = {}

    # noinspection PyMethodOverriding
    def extendMarkdown(self, md: Markdown) -> None:
        # BUG: the base method signature is INVALID, it's a bug in flask-markdown
        md.inlinePatterns.register(EmbedInlineProcessor(md, self.config), 'embed', 200)
        md.registerExtension(self)
