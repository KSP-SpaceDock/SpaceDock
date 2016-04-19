from markdown.inlinepatterns import Pattern
from markdown.extensions import Extension
from markdown.util import etree

from urllib.parse import parse_qs, urlparse

EMBED_RE = r'\[\[(?P<url>.+?)\]\]'

def embed_youtube(link):
    q = parse_qs(link.query)
    v = q['v'][0]
    el = etree.Element('iframe')
    el.set('width', '100%')
    el.set('height', '600')
    el.set('frameborder', '0')
    el.set('allowfullscreen', '')
    el.set('src', '//www.youtube-nocookie.com/embed/' + v + '?rel=0')
    return el

def embed_imgur(link):
    a = link.path.split('/')[2]
    el = etree.Element('iframe')
    el.set('width', '100%')
    el.set('height', '550')
    el.set('frameborder', '0')
    el.set('allowfullscreen', '')
    el.set('src', '//imgur.com/a/' + a + '/embed')
    return el

class EmbedPattern(Pattern):
    def __init__(self, pattern, m, configs):
        super(EmbedPattern, self).__init__(pattern, m)
        self.config = configs

    def handleMatch(self, m):
        d = m.groupdict()
        url = d.get('url')
        if not url:
            el = etree.Element('span')
            el.text = "[[" + url + "]]"
            return el
        host = None
        link = None
        try:
            link = urlparse(url)
            host = link.hostname
        except:
            el = etree.Element('span')
            el.text = "[[" + url + "]]"
            return el
        el = None
        try:
            if host == 'youtube.com' or host == 'www.youtube.com':
                el = embed_youtube(link)
            if host == 'imgur.com' or host == 'www.imgur.com':
                el = embed_imgur(link)
        except:
            pass
        if el == None:
            el = etree.Element('span')
            el.text = "[[" + url + "]]"
            return el
        return el

class KerbDown(Extension):
    def __init__(self):
        self.config = {}

    def extendMarkdown(self, md, md_globals):
        md.inlinePatterns['embeds'] = EmbedPattern(EMBED_RE, md, self.config)
        md.registerExtension(self)
