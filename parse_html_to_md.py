from html.parser import HTMLParser
from html import unescape
from pathlib import Path
import re
import sys

src = Path(sys.argv[1])
dst = Path(sys.argv[2])
title = sys.argv[3]

class Parser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.active = False
        self.depth = 0
        self.lines = []
        self.buf = ''
        self.link = None
        self.code = False

    def emit(self, text=''):
        text = re.sub(r'\s+', ' ', text).strip()
        if text:
            self.buf += text

    def flush(self):
        if self.buf.strip():
            self.lines.append(self.buf.strip())
        self.buf = ''

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'div' and 'markdown-body' in a.get('class', '').split():
            self.active = True; self.depth = 1; return
        if not self.active: return
        if tag == 'div': self.depth += 1
        if tag in ('h1','h2','h3','h4','h5','h6'):
            self.flush(); self.buf = '#' * int(tag[1]) + ' '
        elif tag == 'p': self.flush()
        elif tag == 'br': self.buf += '\n'
        elif tag == 'strong' or tag == 'b': self.buf += '**'
        elif tag == 'code': self.buf += '`'; self.code = True
        elif tag == 'pre': self.flush(); self.buf = '```\n'
        elif tag == 'a': self.link = a.get('href')
        elif tag == 'img':
            self.flush(); self.lines.append(f"![{a.get('alt','image')}]({a.get('src','')})")
        elif tag == 'li': self.flush(); self.buf = '- '

    def handle_endtag(self, tag):
        if not self.active: return
        if tag in ('h1','h2','h3','h4','h5','h6','p','li'):
            self.flush()
        elif tag == 'strong' or tag == 'b': self.buf += '**'
        elif tag == 'code': self.buf += '`'; self.code = False
        elif tag == 'pre': self.flush(); self.lines.append('```')
        elif tag == 'a':
            if self.link: self.buf += f' ({self.link})'
            self.link = None
        elif tag == 'div':
            self.depth -= 1
            if self.depth == 0:
                self.flush(); self.active = False

    def handle_data(self, data):
        if self.active: self.emit(data)

p = Parser(); p.feed(src.read_text(encoding='utf-8'))
p.flush()
text = '# ' + title + '\n\n' + '\n\n'.join(x for x in p.lines if x.strip())
text = re.sub(r'(?m)^(\s*\d+)[）)]\s*', r'\1. ', text)
text = re.sub(r'\n{3,}', '\n\n', text).strip() + '\n'
dst.write_text(text, encoding='utf-8')
print(f'{dst}\n{len(text)} bytes\n{len(p.lines)} blocks')
