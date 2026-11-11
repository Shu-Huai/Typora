from pathlib import Path
import re

root = Path(r'D:\Typora\八股文')
names = ['key','value','size','index','id','result','entry','map','list','queue','n','m','i','x','y','z']
for path in root.rglob('*.md'):
    lines = path.read_text(encoding='utf-8').splitlines()
    out=[]; fence=False
    for line in lines:
        if line.lstrip().startswith(('```','~~~')):
            fence=not fence; out.append(line); continue
        if fence: out.append(line); continue
        parts=line.split('`')
        for i in range(0,len(parts),2):
            s=parts[i]
            saved=[]
            def hold(m): saved.append(m.group(0)); return f'\x00{len(saved)-1}\x00'
            s=re.sub(r'\$[^$\n]+\$',hold,s)
            s=re.sub(r'(?<![\w/])((?:[A-Za-z_]\w*\.)+[A-Za-z_]\w*\([^()\n]*\))(?![\w])',lambda m:'`'+m.group(1)+'`',s)
            for name in names:
                s=re.sub(r'(?<![\w`])'+re.escape(name)+r'(?![\w`])','`'+name+'`',s)
            s=re.sub(r'`([A-Za-z_]\w*)`\(\)',r'`\1()`',s)
            s=re.sub(r'\x00(\d+)\x00',lambda m:saved[int(m.group(1))],s)
            parts[i]=s
        out.append('`'.join(parts))
    path.write_text('\n'.join(out)+'\n',encoding='utf-8')
