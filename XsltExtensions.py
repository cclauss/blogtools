##
##  XSLT extension functions.
##

import os, re, time
from PIL import Image

def endswith(text, s):
    return int(bool(text.endswith(s)))

def makeuri(base, u, dpath):
    if ':' in u:
        # Full URI: don't touch.
        uri = u
    else:
        # Relative.  Base+u, but make sure a slash separates them.
        if u.startswith('#'):
            u = dpath + u
        uri = base
        if not base.endswith('/') and not u.startswith('/'):
            uri += '/'
        uri += u
        # Don't link to index.html pages.
        if uri.endswith('/index.html'):
            uri = uri[:-len('/index.html')]
    return uri

def urlquote(u):
    import urllib
    return urllib.quote(urllib.unquote(u.encode('utf-8')))

def phpquote(u):
    return u.replace('"', r'\"').replace("'", r"\'")

def now8601():
    return time.strftime("%Y%m%dT%H%M%S")

def w3cdtf(s8601):
    sTime = time.strftime("%Y-%m-%dT%H:%M:%S", time.strptime(s8601, "%Y%m%dT%H%M%S"))
    if time.daylight:
        zsecs = time.altzone
    else:
        zsecs = time.timezone
    if zsecs < 0:
        zchar = '+'
        zsecs = -zsecs
    else:
        zchar = '-'
    zmins = zsecs/60
    zhours = zmins/60
    zmins = zmins % 60
    return "%s%s%02d:%02d" % (sTime, zchar, zhours, zmins)

def idfromtext(s):
    import urllib
    s = urllib.quote(s.strip().replace(' ', '_').encode('utf-8'))
    return s.replace('%', '_')

def slugfromtext(txt):
    slug = txt.encode('ascii', 'ignore').replace(' ', '_').lower()
    slug = re.sub('[^\w _]', '', slug)
    slug = re.sub('_+', '_', slug).strip('_')
    if not slug:
        import urllib
        slug = urllib.quote(txt.strip().replace(' ', '_').encode('utf-8'))
        slug = slug.replace('%', '_')
    return slug

idfromtext = slugfromtext

def lexcode(code, lang, number=False):
    import pygments, pygments.lexers, pygments.formatters
    # Because we are omitting the <pre> wrapper, we need spaces to become &nbsp;.
    import pygments.formatters.html as pfh
    pfh._escape_html_table.update({ord(' '): u'&#xA0;'})

    class CodeHtmlFormatter(pygments.formatters.HtmlFormatter):

        def wrap(self, source, outfile):
            return self._wrap_code(source)

        def _wrap_code(self, source):
            # yield 0, '<pre>'
            for i, t in source:
                if i == 1:
                    # it's a line of formatted code
                    t += '<br>'
                yield i, t
            # yield 0, '</pre>'

    aliases = {
        "cs": "c#",
        "htaccess": "apacheconf",
        "ps": "postscript",
        "m3u": "text",  # Don't know if this will ever be supported...
        }
    lang = lang.lower()
    lang = aliases.get(lang, lang)
    lexer = pygments.lexers.get_lexer_by_name(lang, stripall=True)
    formatter = CodeHtmlFormatter(linenos='inline' if number else False, cssclass="source")
    result = pygments.highlight(code, lexer, formatter)
    return result

imgsizecache = {}
curdir = os.getcwd()
# Yuk! Hard-coded path!
imgpath = [ curdir, os.path.join(curdir, 'pages') ]

def getImageSize(s):
    if s.startswith('http://') or s.startswith('file://'):
        return
    if not imgsizecache.has_key(s):
        img = None
        for p in imgpath:
            try:
                spath = os.path.join(p, s)
                img = Image.open(spath)
                #print "opened %r" % s
                break
            except IOError, msg:
                pass
        if img:
            imgsizecache[s] = img.size
        else:
            print "Couldn't open image %s" % s
    if imgsizecache.has_key(s):
        return imgsizecache[s]

def imgwidth(s, scale=None):
    return img_dimension(0, s, scale)

def imgheight(s, scale=None):
    return img_dimension(1, s, scale)

def img_dimension(which, s, scale=None):
    scale = scale or 1.0
    size = getImageSize(s)
    if size:
        return str(int(size[which]*float(scale)))
    else:
        return ''
