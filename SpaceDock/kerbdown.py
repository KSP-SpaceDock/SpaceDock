import urllib.parse
from urllib.parse import parse_qs, urlparse
from typing import List, Dict, Any, Match, Tuple, Optional

from flask import url_for
from markdown import Markdown
from markdown.extensions import Extension
from markdown.extensions.tables import TableProcessor
from markdown.inlinepatterns import InlineProcessor
from xml.etree import ElementTree
from markdown.util import AtomicString

from .objects import User


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


class AtUsernameProcessor(InlineProcessor):
    # Don't worry about re.compiling this, markdown.inlinepatterns.Pattern.__init__ does that for us
    # Same as blueprints.accounts._username_re
    USER_RE = r'@(?P<username>[A-Za-z0-9_]+)'

    def __init__(self, md: Markdown, configs: Dict[str, Any]) -> None:
        super().__init__(self.USER_RE, md)
        self.configs = configs

    def handleMatch(self, match: Match[str], data: str) -> Tuple[Optional[ElementTree.Element], Optional[int], Optional[int]]:  # type: ignore[override]
        username = match.groupdict().get('username')
        # Case insensitive lookup
        user = User.query.filter(User.username.ilike(username)).first()
        return ((self._profileLink(user), match.start(0), match.end(0))
                # Keep original text if user not found
                if user and user.public else (None, None, None))

    @classmethod
    def _profileLink(cls, user: User) -> ElementTree.Element:
        # Make a link to the user's profile
        elt = ElementTree.Element('a', href=url_for('profile.view_profile',
                                                    username=user.username),
                                       # Summarize user's profile in tooltip
                                       title='\n'.join((f'{user.username}\'s profile',
                                                        f'{cls._profileModCount(user)} mods',
                                                        f'Joined {user.created.strftime("%Y-%m-%d")}')))
        # Make it bold
        strong = ElementTree.SubElement(elt, 'strong')
        # AtomicString prevents Markdown from entering an infinite loop by processing the subelement's text again
        strong.text = AtomicString(f'@{user.username}')
        return elt

    @staticmethod
    def _profileModCount(user: User) -> int:
        return len([m for m in user.mods + [sa.mod for sa in user.shared_authors
                                            if sa.accepted]
                    if m is not None and m.published])


class StyledTableProcessor(TableProcessor):
    def run(self, parent: ElementTree.Element, blocks: List[str]) -> None:
        super().run(parent, blocks)
        for table in parent.findall('table'):
            table.attrib['class'] = 'table-condensed table-bordered'


class KerbDown(Extension):
    def __init__(self, **kwargs: str) -> None:
        super().__init__(**kwargs) # type: ignore[arg-type]
        self.config: Dict[str, Any] = {}

    # noinspection PyMethodOverriding
    def extendMarkdown(self, md: Markdown) -> None:
        # BUG: the base method signature is INVALID, it's a bug in flask-markdown
        md.inlinePatterns.register(EmbedInlineProcessor(md, self.config), 'embed', 200)
        md.inlinePatterns.register(AtUsernameProcessor(md, self.config), 'atuser', 200)
        md.parser.blockprocessors.register(StyledTableProcessor(md.parser,
                                                                {'use_align_attribute': False}),
                                           'styled_table', 75)
        md.registerExtension(self)
