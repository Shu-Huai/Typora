from pathlib import Path
import re, subprocess, sys, urllib.request

root=Path(r'D:\Typora\八股文\Java后端\1'); desktop=Path(r'C:\Users\lvzhi\Desktop'); imgdir=Path(r'Z:\Public\images')
htmls=list(desktop.rglob('*.html'))
norm=lambda s: re.sub(r'[^\w\u4e00-\u9fff]','',s).lower()
jobs=[]
for md in root.glob('*.md'):
    t=md.read_text(encoding='utf-8',errors='ignore'); m=re.search(r'^#\s+(.+)$',t,re.M)
    if not m: continue
    title=m.group(1).strip(); key=norm(title.rstrip('？?'))
    src=next((h for h in htmls if norm(h.stem.split(' - 面试鸭')[0].rstrip('？?'))==key),None)
    if src: jobs.append((src,md,title))
for src,md,title in jobs:
    subprocess.run([sys.executable,'reparse_html.py',str(src),str(md),title],check=True)
    text=md.read_text(encoding='utf-8')
    def dl(m):
        url=m.group(1); name=Path(url.split('?')[0]).name; out=imgdir/name
        if not out.exists(): urllib.request.urlretrieve(url,out)
        return m.group(0).replace(url,'Z:/Public/images/'+name)
    text=re.sub(r'!\[[^\]]*\]\((https?://[^)]+)\)',dl,text)
    md.write_text(text.rstrip()+'\n',encoding='utf-8')
print('Reparsed',len(jobs),'Markdown files with matching HTML sources')
