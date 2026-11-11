from pathlib import Path
import re

root = Path(r'D:\Typora\八股文\Java后端\1')
files = [p for p in root.glob('*.md') if p.stat().st_mtime >= 0]
# The recent regenerated batch is the 28 files modified today after 13:20.
files = [p for p in files if p.stat().st_mtime >= 1791254400]

def prose_parts(text):
    return re.split(r'(```[\s\S]*?```|`[^`\n]*`|\*\*[^*\n]+\*\*|__[^_\n]+__|!\[[^\]]*\]\([^)]*\)|\[[^\]]+\]\([^)]*\))', text)

for path in files:
    text = path.read_text(encoding='utf-8')
    # Repair the HTML parser's compact code representation.
    text = re.sub(
        r'```\s*\n?\s*▼(java|sql|text)复制代码`([\s\S]*?)`\s*\n?```',
        lambda m: f'```{m.group(1)}\n{m.group(2).strip()}\n```', text)
    # Convert plain link output to standard Markdown links.
    text = re.sub(r'(?m)^(#{1,6})\s+\[([^\]]+)\]\((https?://[^)]+)\)\s*$', r'\1 \2', text)
    text = re.sub(r'([^\n()：:，,。；;]+?)\s*\((https?://[^)]+)\)', r'[\1](\2)', text)
    # Normalize numbered lists even when several items were emitted on one line.
    text = re.sub(r'\s+(\d+)[）)]\s*', r'\n\1. ', text)
    # Normalize prose spacing and Chinese semicolons, while protecting code/links/bold.
    parts = prose_parts(text)
    for i in range(0, len(parts), 2):
        s = parts[i]
        s = re.sub(r'(?<=[\u4e00-\u9fff])(?=[A-Za-z0-9])', ' ', s)
        s = re.sub(r'(?<=[A-Za-z0-9])(?=[\u4e00-\u9fff])', ' ', s)
        if re.search(r'[\u4e00-\u9fff]', s):
            s = s.replace(';', '；')
        parts[i] = s
    text = ''.join(parts)
    def expand_code(m):
        body = m.group(2)
        if len(body) > 120:
            body = re.sub(r';\s+', ';\n', body)
        return '```' + m.group(1) + '\n' + body.strip() + '\n```'
    text = re.sub(r'```(java|sql|text)\n([\s\S]*?)\n```', expand_code, text)
    # Keep exactly one H1 at the beginning; remove duplicate H1 lines.
    lines = text.replace('\r\n', '\n').split('\n')
    h1 = next((x.strip() for x in lines if re.match(r'^#\s+\S', x)), '# ' + path.stem)
    body = [x for x in lines if not re.match(r'^#\s+\S', x)]
    while body and not body[0].strip(): body.pop(0)
    lines = [h1] + body
    # Remove terminal blank lines and standalone ellipses.
    while lines and not lines[-1].strip(): lines.pop()
    while lines and lines[-1].strip() in ('...', '……'):
        lines.pop()
        while lines and not lines[-1].strip(): lines.pop()
    path.write_text('\n'.join(lines).rstrip() + '\n', encoding='utf-8')

print(f'Normalized {len(files)} files')
