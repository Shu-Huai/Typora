from html.parser import HTMLParser
from pathlib import Path
import re, sys

src, dst, title = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3]

class P(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.active=False; self.depth=0; self.lines=[]; self.buf=''; self.link=None
        self.in_pre=False; self.in_code=False; self.pre_buf=''; self.pre_lang=''; self.lang_capture=False
    def flush(self):
        s=self.buf.strip()
        if s: self.lines.append(s)
        self.buf=''
    def handle_starttag(self, tag, attrs):
        a=dict(attrs); cls=a.get('class','')
        if tag=='div' and 'markdown-body' in cls.split(): self.active=True; self.depth=1; return
        if not self.active: return
        if self.in_pre:
            if tag=='code': self.in_code=True
            elif 'code-block-extension-lang' in cls.split(): self.lang_capture=True
            elif tag=='br' and self.in_code: self.pre_buf+='\n'
            return
        if tag=='div': self.depth+=1
        if tag in ('h1','h2','h3','h4','h5','h6'): self.flush(); self.buf='#'*int(tag[1])+' '
        elif tag=='p': self.flush()
        elif tag=='br': self.buf+='\n'
        elif tag in ('strong','b'): self.buf+='**'
        elif tag=='code': self.buf+='`'
        elif tag=='pre': self.flush(); self.in_pre=True; self.in_code=False; self.pre_buf=''; self.pre_lang=''
        elif tag=='a': self.link=a.get('href'); self.buf+='['
        elif tag=='img': self.flush(); self.lines.append(f"![{a.get('alt','image')}]({a.get('src','')})")
        elif tag=='li': self.flush(); self.buf='- '
    def handle_endtag(self, tag):
        if not self.active: return
        if self.in_pre:
            if tag=='code': self.in_code=False
            elif tag=='pre':
                self.lines.append('```'+self.pre_lang+'\n'+self.pre_buf.strip('\n')+'\n```'); self.in_pre=False
            return
        if tag in ('h1','h2','h3','h4','h5','h6','p','li'): self.flush()
        elif tag in ('strong','b'): self.buf+='**'
        elif tag=='code': self.buf+='`'
        elif tag=='a':
            if self.link: self.buf += ']('+self.link+')'
            self.link=None
        elif tag=='div':
            self.depth-=1
            if self.depth==0: self.flush(); self.active=False
    def handle_data(self, data):
        if not self.active: return
        if self.in_pre:
            if self.lang_capture: self.pre_lang += data.strip(); self.lang_capture=False
            elif self.in_code: self.pre_buf += data
        else:
            self.buf += re.sub(r'\s+', ' ', data)

p=P(); p.feed(src.read_text(encoding='utf-8')); p.flush()
text='# '+title+'\n\n'+'\n\n'.join(x for x in p.lines if x.strip())
text=re.sub(r'(?m)^(\s*\d+)[）)]\s*',r'\1. ',text)
text=re.sub(r'(?:\.\.\.|……)\s*$','',text).rstrip()+'\n'
dst.write_text(text,encoding='utf-8')
print(dst, len(text), 'bytes')
