from pathlib import Path
import re

root = Path(r'D:\Typora\八股文\Java后端\1')
files = list(root.glob('*.md'))
for p in files:
    t = p.read_text(encoding='utf-8')
    # Repair list links whose list marker was swallowed into the link label.
    t = re.sub(r'\[\[-\s*\[([^\]]+)\]\]\]\((https?://[^)]+)\)', r'- [\1](\2)', t)
    t = re.sub(r'\[\[-\s*([^\]]+)\]\]\((https?://[^)]+)\)', r'- [\1](\2)', t)
    # Collapse accidental nested link brackets until standard syntax remains.
    old = None
    while old != t:
        old = t
        t = re.sub(r'\[\[([^\[\]]+)\]\]\((https?://[^)]+)\)', r'[\1](\2)', t)
    def flatten(m):
        label = m.group(2).strip()
        label = label.strip('[]').strip()
        if label.startswith('- '):
            return '- [' + label[2:].strip() + '](' + m.group(4) + ')'
        return '[' + label + '](' + m.group(4) + ')'
    t = re.sub(r'(\[+)([^\n]*?)(\]+)\((https?://[^)]+)\)', flatten, t)
    p.write_text(t.rstrip() + '\n', encoding='utf-8')
print('Repaired links in', len(files), 'files')
