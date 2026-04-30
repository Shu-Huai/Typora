# Skills

这份笔记只讨论 **Skills 本身**。这里的 Skills 不是某个具体平台的宣传概念，也不是某个外部生态的全家桶介绍，而是一种可复用能力包的组织方式：用一个入口说明文件描述任务边界、触发条件、执行原则和资源位置，再按需要配套参考资料、脚本、模板和测试样例。

一个 Skill 的核心价值不在于目录有多复杂，而在于它能把一类反复出现的任务处理方式稳定保存下来。它解决的是“每次都要重新解释同一套要求”的问题。比如你经常要求一份 Markdown 笔记必须内容充足、结构合理、不要写成学习路线、不要像教培软文、标题层级不要碎、段落和列表要交错使用，这类长期稳定的偏好就适合被固化成 Skill。

![OpenAI Skills](http://public.file.lvshuhuai.cn/images\skills-openai-academy-cover.jpeg)

## Skill 的基本定义与边界

Skill 可以理解为一种**任务级能力封装**。它把某类任务的处理规范、判断边界、操作步骤、参考材料、脚本和模板组织到一个目录中，使执行者在面对同类任务时可以按固定方式处理，而不是每次从零开始理解需求。这个思路也可以对应到 [OpenAI Agent Skills](https://github.com/openai/skills) 或 [Claude Skills](https://claude.com/docs/skills/overview) 这样的具体实现，但本文关注的是通用组织方式。

一个最小 Skill 可以只有一个文件：

```text
my-skill/
└── SKILL.md
```

这个结构已经足够表达一个 Skill。只要 `SKILL.md` 写清楚这个 Skill 什么时候使用、什么时候不要使用、应该遵守哪些步骤、输出应该是什么样，它就是一个可工作的最小能力包。

![Skill Folder Structure](http://public.file.lvshuhuai.cn/images\skills-openai-screenshot-2.jpeg)

### Skill 不是一次性提示词

一次性[[提示词 Prompt]] 通常只服务当前任务。例如：

```text
请把这段对话整理成 Markdown 笔记，内容要详细，不要写成学习路线，标题不要太碎，段落和列表要结合。
```

这条提示词只在当前任务里生效。下次做类似任务时，用户还要重新解释一遍。

Skill 则把这种长期有效的要求沉淀下来。它更像一个可复用的任务说明书：

```text
markdown-note-writer/
└── SKILL.md
```

在 `SKILL.md` 中可以长期保存：

- 任务适用范围；
- 输出风格；
- 标题层级要求；
- 常见错误；
- 文件命名规则；
- 是否需要运行检查脚本；
- 是否需要使用模板；
- 哪些资料可以作为参考。

因此，Skill 和普通提示词的关系可以这样区分：

| 对象 | 作用 | 生命周期 | 结构化程度 |
|---|---|---|---|
| 一次性提示词 | 解决当前任务 | 当前对话或当前请求 | 通常较弱 |
| Skill | 固化一类任务的处理方式 | 长期复用 | 较强 |
| `SKILL.md` | Skill 的入口说明文件 | 随 Skill 存在 | 强 |
| 附加文件 | 补充资料、脚本、模板、样例 | 按需扩展 | 取决于设计 |

Skill 的意义不是让提示词消失，而是把反复使用的提示词规则沉淀为可维护文件。很多有价值的 Skill 都来自同一种现象：用户不断纠正同一类输出问题，最后把这些纠正规则固定下来。

### Skill 也不是单纯的工具脚本

Skill 可以包含脚本，但 Skill 本身不等于脚本。

脚本通常解决确定性问题，例如检查 Markdown 代码块是否闭合、校验 JSON 是否符合 schema、统计文件中的标题数量。Skill 解决的是更高层的任务组织问题：面对某类任务应该按什么规则判断、按什么结构输出、什么时候使用哪些辅助文件。

例如，一个 Markdown 笔记 Skill 可以包含脚本：

```text
scripts/validate_note.py
```

这个脚本可以检查：

- 是否有一级标题；
- 是否存在未闭合代码块；
- 是否用了不推荐的宣传式表达；
- 是否二级标题过多；
- 文件名是否符合规范。

但脚本不会决定“这份笔记应该如何组织思想”。这种组织原则仍然应该写在 `SKILL.md` 和相关说明文件中。

所以更准确的边界是：

```text
Skill 负责定义任务方法。
脚本负责执行确定性操作。
模板负责稳定输出形态。
参考资料负责补充长期知识。
```

### Skill 的判断标准

判断一个东西是否值得做成 Skill，可以看它是否满足以下条件：

1. 这类任务是否会反复出现；
2. 用户是否经常提出相似要求；
3. 输出是否有固定风格或格式；
4. 任务是否有稳定步骤；
5. 是否存在常见错误需要反复避免；
6. 是否需要长期保存一些参考材料；
7. 是否可以通过脚本或模板提高稳定性。

如果只是一次性问题，通常不需要做成 Skill。比如“解释一下这个单词”一般不需要 Skill；但“以后每次把我们的技术对话整理成这种风格的 Markdown 笔记”就适合做成 Skill。

![Identifying Good Use Cases for Skills](http://public.file.lvshuhuai.cn/images\skills-openai-screenshot-3.jpeg)

## `SKILL.md`：入口、触发器与调度规则

[`SKILL.md`](https://github.com/openai/skills/blob/main/skills/.system/skill-creator/SKILL.md) 是 Skill 的核心入口。它既是说明书，也是调度文件。一个设计良好的 `SKILL.md` 不是把所有资料都塞进去，而是清楚说明这个 Skill 的使用条件、边界、执行过程和资源组织方式。

![Example Skill Detail](http://public.file.lvshuhuai.cn/images\skills-openai-screenshot-1.png)

典型结构如下：

```markdown
---
name: markdown-note-writer
description: Use this skill when the user asks to turn a conversation, source text, or concept explanation into a systematic Markdown note. The output should be detailed, structurally coherent, and avoid superficial tutorial-style writing.
---

# Markdown Note Writer

## Purpose

This skill helps produce systematic Markdown notes from conversations, source texts, or scattered explanations.

## When to use

Use this skill when the user asks to:
- turn a conversation into a Markdown note
- reorganize source material into a stable document
- produce a detailed technical note
- avoid shallow learning-route style

## When not to use

Do not use this skill when the user asks for:
- a short answer
- casual chat
- simple translation
- spreadsheet generation
- slide generation

## Procedure

1. Identify the target topic.
2. Remove irrelevant conversational fragments.
3. Reorganize the material by semantic structure rather than dialogue order.
4. Use a small number of major sections.
5. Mix paragraphs, lists, examples, and code blocks where appropriate.
6. Validate the output if a file is generated.
```

### `name` 应该稳定、短、可读

`name` 是 Skill 的标识符。它不应该含糊，也不应该情绪化。推荐使用小写英文和连字符。

推荐：

```yaml
name: markdown-note-writer
name: academic-method-writer
name: pytorch-code-reviewer
name: docker-debugging-checklist
```

不推荐：

```yaml
name: helper
name: skill1
name: good-writer
name: my-awesome-skill
```

命名的目标不是好看，而是稳定可识别。一个好的 `name` 应该让人不读正文也能大致判断 Skill 的用途。

### `description` 是触发判断的关键

`description` 比 `name` 更重要。它决定这个 Skill 什么时候应该被使用。如果 description 太泛，Skill 会被误触发；如果太窄，可能无法在该用时被选中。

坏的写法：

```yaml
description: Helps write notes.
```

问题在于过于宽泛。它没有说明是什么类型的笔记、输入是什么、输出要求是什么、风格边界是什么。

更好的写法：

```yaml
description: Use this skill when the user asks to turn a conversation, source text, or concept explanation into a systematic Markdown note. The output should be detailed, structurally coherent, and avoid superficial tutorial-style writing.
```

这个 description 包含三层信息：

- 任务类型：turn ... into a systematic Markdown note；
- 输入范围：conversation, source text, concept explanation；
- 输出要求：detailed, structurally coherent, avoid superficial tutorial-style writing。

写 description 时要避免“万能助手式”的措辞。Skill 的边界越清楚，执行越稳定。

### `When to use` 与 `When not to use`

一个 Skill 只写“什么时候用”是不够的，还必须写“什么时候不用”。很多 Skill 失败不是因为能力不足，而是因为被用于不合适的场景。

例如 Markdown 笔记 Skill 适合：

- 用户要求整理长对话；
- 用户要求生成 `.md` 文件；
- 用户要求系统性知识文档；
- 用户要求重组内容而不是逐句总结；
- 用户明确提出结构和风格要求。

它不适合：

- 用户只问一个简单定义；
- 用户要求翻译一句话；
- 用户要求写代码；
- 用户要求做 Excel；
- 用户要求生成幻灯片；
- 用户只是闲聊。

`When not to use` 的价值在于防止过度泛化。如果没有反触发条件，一个写作 Skill 可能会在短问答中生成过长文本，一个代码审查 Skill 可能会被误用于概念解释，一个模板型 Skill 可能会把简单问题套成复杂文档。

### Procedure 要可执行，不要只写抽象品质词

差的 procedure：

```markdown
1. Write a good note.
2. Make it detailed.
3. Make it clear.
```

这些句子听起来正确，但不可执行。执行者不知道什么叫 “good”，也不知道如何判断 “detailed”。

更好的 procedure：

```markdown
1. Identify the target topic and document purpose.
2. Remove irrelevant conversational fragments.
3. Merge semantically similar content into the same section.
4. Use H2 only for major conceptual blocks.
5. Use H3 for local distinctions.
6. Add concrete examples when a concept would otherwise remain abstract.
7. Avoid excessive bullet lists; mix paragraphs and lists.
8. If a Markdown file is generated, run the validation script.
```

这种步骤可以被执行，也可以被检查。

### `SKILL.md` 不应该无限膨胀

`SKILL.md` 应该是入口文件，而不是百科全书。它要包含最重要的规则，但不应该包含全部长资料。

判断标准：

```text
如果一段内容是“使用这个 Skill 必须立即知道的规则”，放进 SKILL.md。
如果一段内容是“需要时再查的长说明、样例或规范”，放进 references/。
如果一段内容是“输出骨架”，放进 assets/。
如果一段内容是“可执行检查或转换逻辑”，放进 scripts/。
```

过长的 `SKILL.md` 会导致维护困难，也会降低加载效率。一个好的 Skill 应该让 `SKILL.md` 保持清楚、短、可导航。

## 文件组织：目录不是绝对规范，但语义必须清楚

Skill 的目录结构并不是像某些编程语言项目那样有硬性编译规范。除了 `SKILL.md` 作为核心入口通常比较关键之外，其他目录更多是约定。

常见结构：

```text
my-skill/
├── SKILL.md
├── references/
│   ├── style-guide.md
│   └── examples.md
├── scripts/
│   └── validate.py
└── assets/
    └── template.md
```

这是一种清晰、可维护的结构，但它不是唯一可能的结构。如果你在 `SKILL.md` 中写清楚：

```text
templates/ contains reusable output templates.
docs/ contains long reference documents.
bin/ contains executable scripts.
```

那么下面这种结构也可以被理解：

```text
my-skill/
├── SKILL.md
├── docs/
├── bin/
└── templates/
```

甚至从纯语义角度讲，只要 `SKILL.md` 说明清楚，一个任意命名的目录也可以承担模板或资料功能。关键不在目录名本身，而在于说明是否明确、路径是否准确、执行者是否能访问。

不过，工程上仍然推荐使用常见语义目录。原因很简单：

- `references/` 一看就是参考资料；
- `scripts/` 一看就是可执行脚本；
- `assets/` 一看就是模板或资源；
- 后续维护者不需要反复查说明；
- 自动化工具或平台更容易按惯例处理；
- 团队协作时减少误解。

因此，合理结论是：

```text
目录名不是绝对规范。
SKILL.md 中的说明才是关键。
但为了可维护性和可迁移性，优先使用 references/、scripts/、assets/ 这类语义明确的目录。
```

![Creating Custom Skills](http://public.file.lvshuhuai.cn/images\skills-claude-creating-custom-skills.png)

### `references/`：长期知识与规范

`references/` 适合存放不必每次都读、但在复杂任务中可能需要查阅的长资料。

例如：

```text
markdown-note-writer/
├── SKILL.md
└── references/
    ├── writing-style-guide.md
    ├── bad-phrases.md
    ├── heading-rules.md
    └── examples.md
```

这些文件不一定每次都用，但它们可以让 Skill 更稳定。

`references/` 适合放：

- 写作风格指南；
- 术语解释；
- 长示例；
- 好坏案例；
- 项目内部规范；
- 输出质量检查表；
- 常见误区说明；
- 领域背景资料。

不适合放：

- 可执行脚本；
- 输出模板骨架；
- 临时文件；
- 大量无关材料；
- 与当前 Skill 不相关的知识集合。

例如，一个写作风格参考文件可以这样写：

```markdown
# Writing Style Guide

The output should look like a serious technical note, not a course advertisement.

Prefer:
- precise definitions
- coherent sectioning
- concrete examples
- paragraphs mixed with bullet lists
- a small number of major sections

Avoid:
- excessive second-level headings
- motivational language
- shallow learning-route framing
- long bullet lists without explanation
- repeated ideas under different headings
```

`references/` 的核心作用是补充“应该知道什么”。它不负责给出最终输出骨架，也不负责执行代码。

### `scripts/`：确定性检查与处理

`scripts/` 用于存放可执行代码。它适合处理明确、重复、可验证的任务。

例如：

```text
scripts/
├── validate_note.py
├── check_filename.py
└── normalize_markdown.py
```

脚本适合做：

- 检查 Markdown 是否有一级标题；
- 检查代码块是否闭合；
- 检查文件扩展名；
- 检查 JSON/YAML 是否合法；
- 统计标题数量；
- 检查是否出现禁用词；
- 解析日志；
- 汇总指标；
- 格式化固定结构。

脚本不适合做：

- 判断文章是否“有深度”；
- 判断观点是否“高级”；
- 替代人工判断研究价值；
- 替代模型进行复杂语义组织；
- 执行危险文件操作。

一个最小 Markdown 检查脚本示例：

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pathlib import Path
import re
import sys

BANNED_PHRASES = [
    "非常强大",
    "极大提升效率",
    "只需要简单几步",
    "小白也能学会",
    "保姆级教程",
    "学习路线",
]

def has_h1(text: str) -> bool:
    return bool(re.search(r"^# [^#].+", text, flags=re.MULTILINE))

def code_fences_balanced(text: str) -> bool:
    count = len(re.findall(r"^```", text, flags=re.MULTILINE))
    return count % 2 == 0

def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: python validate_note.py path/to/file.md")
        return 1

    path = Path(sys.argv[1])

    if not path.exists():
        print(f"ERROR: file does not exist: {path}")
        return 1

    if path.suffix.lower() != ".md":
        print("ERROR: expected a .md file")
        return 1

    text = path.read_text(encoding="utf-8")

    errors = []
    warnings = []

    if not has_h1(text):
        errors.append("missing top-level H1 title")

    if not code_fences_balanced(text):
        errors.append("unbalanced Markdown code fences")

    for phrase in BANNED_PHRASES:
        if phrase in text:
            warnings.append(f"discouraged phrase found: {phrase}")

    for item in errors:
        print("ERROR:", item)

    for item in warnings:
        print("WARNING:", item)

    if errors:
        return 1

    print("PASS")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
```

这个脚本体现了脚本的边界：它只处理可检查规则，不负责写内容。

在 `SKILL.md` 中可以这样描述脚本：

```markdown
## Scripts

Use scripts only for deterministic validation.

- `scripts/validate_note.py`: Validate Markdown structure, code fences, and discouraged phrases.

Run this script when a Markdown file is generated. If it reports errors, revise the file before delivery.
```

脚本一旦加入，Skill 就从纯文本说明变成了带执行能力的资源包。因此要注意安全：

- 不要默认删除文件；
- 不要默认覆盖用户文件；
- 不要默认访问网络；
- 不要执行不透明 shell 命令；
- 输入路径要检查；
- 有破坏性操作时要显式说明；
- 尽量提供 dry-run 或只读模式。

### `assets/`：模板、样例文件与可复用资源

`assets/` 用于放模板和可复用资源。它回答的是“输出应该长什么样”。

例如：

```text
assets/
├── long-note-template.md
├── comparison-template.md
└── concept-card-template.md
```

`assets/long-note-template.md` 可以是：

```markdown
# {{TITLE}}

## 核心问题

{{说明这个主题解决的核心问题。}}

## 基本概念与边界

{{定义核心概念，并说明它和相邻概念的边界。}}

## 结构与组成

{{说明该主题的内部组成。}}

## 具体示例

{{给出一个可落地的例子。}}

## 常见错误

{{列出常见误解或错误用法。}}

## 总结

{{用一段话总结。}}
```

这个模板不是知识说明，而是输出骨架。执行者可以根据任务填充它，也可以删掉不适合当前任务的部分。

`assets/` 可以放：

- Markdown 模板；
- 文档模板；
- 表格模板；
- JSON schema；
- YAML 配置；
- 示例输入文件；
- 空白报告；
- starter files；
- 固定格式资源。

但它不应该变成杂物堆。每个 asset 都应该有明确用途，并且在 `SKILL.md` 中说明何时使用。

例如：

```markdown
## Assets

- `assets/long-note-template.md`: Use when generating a long-form Markdown note.
- `assets/comparison-template.md`: Use when comparing two concepts.
- `assets/concept-card-template.md`: Use when explaining one concept in a compact form.

Templates are starting points. Remove or modify sections that do not fit the user request.
```

### `references/`、`scripts/`、`assets/` 的分工

三者的边界可以这样记：

```text
references/  负责“应该知道什么”
scripts/     负责“可以确定性执行什么”
assets/      负责“输出或资源长什么样”
SKILL.md     负责“什么时候用、怎么调度”
```

常见错误是混用职责。例如：

- 把大量术语解释写进 `assets/`；
- 把模板骨架放进 `references/`；
- 把执行命令直接散落在 `SKILL.md`；
- 把所有内容塞进 `SKILL.md`；
- 不说明目录用途，让执行者猜。

更好的做法是让每类文件有单一职责。

## 一个 Skill 如何从最小形态演化

一个 Skill 不应该一开始就设计得很庞大。更合理的方式是从一个真实重复任务出发，逐步增加文件。

### 第一阶段：只有 `SKILL.md`

```text
markdown-note-writer/
└── SKILL.md
```

适合任务边界比较清楚、规则不多的情况。此时 `SKILL.md` 写清楚：

- 什么时候用；
- 什么时候不用；
- 执行步骤；
- 输出要求；
- 常见错误。

例如，一个纯说明型 Skill 可以只规定 Markdown 笔记写作风格，不包含任何额外文件。

这种形态的优点是轻量，缺点是当规则变多时 `SKILL.md` 会变得臃肿。

### 第二阶段：加入 `references/`

```text
markdown-note-writer/
├── SKILL.md
└── references/
    ├── writing-style-guide.md
    └── examples.md
```

当风格指南、例子、术语说明越来越长时，就应该拆到 `references/`。`SKILL.md` 保持短，只负责说明什么时候读这些文件。

这种形态适合知识密集或规范密集的任务。

### 第三阶段：加入 `scripts/`

```text
markdown-note-writer/
├── SKILL.md
├── references/
│   └── writing-style-guide.md
└── scripts/
    └── validate_note.py
```

当你发现某些检查每次都可以程序化执行，就可以加入脚本。例如：

- 代码块是否闭合；
- 标题数量是否过多；
- 是否出现禁用表达；
- 文件名是否符合规范。

这种形态适合需要稳定质量检查的任务。

### 第四阶段：加入 `assets/`

```text
markdown-note-writer/
├── SKILL.md
├── references/
│   └── writing-style-guide.md
├── scripts/
│   └── validate_note.py
└── assets/
    └── long-note-template.md
```

当输出结构比较固定，就可以加入模板。例如：

- 长文档模板；
- 对比说明模板；
- 报告模板；
- 概念卡片模板。

这种形态适合固定格式输出。

![Skill Draft and Install](http://public.file.lvshuhuai.cn/images\skills-openai-screenshot-4.png)

### 第五阶段：加入 `tests/` 或 `examples/`

如果一个 Skill 被频繁使用，或者会给别人使用，可以增加测试样例：

```text
markdown-note-writer/
├── SKILL.md
├── references/
├── scripts/
├── assets/
└── tests/
    ├── input-short-question.txt
    ├── input-long-note.txt
    └── expected-behavior.md
```

`tests/` 不一定是自动化单元测试，也可以是行为样例。它可以记录：

- 哪些输入应该触发这个 Skill；
- 哪些输入不应该触发；
- 输出大概应该是什么结构；
- 哪些错误输出应该避免。

这对长期维护很有用。

## 完整示例：一个 Markdown 笔记写作 Skill

下面给出一个完整示例。它不依赖外部生态，只展示 Skill 本身如何组织。

目录结构：

```text
markdown-note-writer/
├── SKILL.md
├── references/
│   ├── writing-style-guide.md
│   └── examples.md
├── scripts/
│   └── validate_note.py
└── assets/
    ├── long-note-template.md
    └── compact-note-template.md
```

### `SKILL.md`

```markdown
---
name: markdown-note-writer
description: Use this skill when the user asks to turn a conversation, source text, or concept explanation into a systematic Markdown note. The output should be detailed, structurally coherent, and avoid superficial tutorial-style writing.
---

# Markdown Note Writer

## Purpose

This skill helps produce systematic Markdown notes from conversations, source texts, or scattered explanations.

The output should not mechanically follow the dialogue order. It should reorganize material into a stable document with clear concepts, concrete examples, and coherent sectioning.

## When to use

Use this skill when the user asks to:
- summarize and reorganize a conversation into a Markdown note
- produce a downloadable `.md` document
- expand a previous explanation into a systematic note
- avoid shallow or promotional writing
- combine paragraphs, lists, examples, and code blocks

## When not to use

Do not use this skill when the user asks for:
- a short answer
- a casual explanation
- translation
- code debugging
- spreadsheet generation
- slide generation
- image generation

## References

Read these files when needed:

- `references/writing-style-guide.md`: writing style and structure rules
- `references/examples.md`: good and bad examples

## Assets

Use these templates when helpful:

- `assets/long-note-template.md`: for long Markdown notes
- `assets/compact-note-template.md`: for short but structured notes

Templates are starting points. Modify or remove sections that do not fit the task.

## Scripts

Use scripts only for deterministic validation.

- `scripts/validate_note.py`: checks Markdown structure and discouraged phrases

Run the validation script when a Markdown file is created.

## Procedure

1. Identify the target topic and document purpose.
2. Remove irrelevant conversational content.
3. Reorganize the content by semantic structure, not by dialogue order.
4. Use a small number of major sections.
5. Combine paragraphs, bullet lists, tables, and code blocks where appropriate.
6. Add concrete examples when concepts are abstract.
7. Use an English filename for downloadable files.
8. If a Markdown file is generated, run `scripts/validate_note.py`.
9. Revise the file if validation reports errors or serious warnings.

## Output rules

- Default language: Chinese.
- Keep technical terms in English when appropriate.
- Avoid excessive H2 headings.
- Avoid motivational or course-advertising language.
- Do not include unrelated external ecosystem explanations.
```

这个 `SKILL.md` 已经具备比较完整的结构。它没有把所有资料塞进去，而是通过 References、Assets、Scripts 三个小节说明其他文件如何使用。

### `references/writing-style-guide.md`

```markdown
# Writing Style Guide

The output should look like a serious technical note, not a training course outline.

Prefer:
- clear conceptual boundaries
- compact but detailed paragraphs
- concrete examples
- comparison tables when useful
- paragraphs mixed with bullet lists
- a small number of major sections

Avoid:
- excessive second-level headings
- motivational language
- shallow roadmap framing
- long bullet lists without explanation
- repeated ideas under different headings
- vague praise such as "very powerful" or "greatly improves efficiency"

Use headings for semantic structure, not for every small point.
```

### `references/examples.md`

````markdown
# Examples

## Bad style

```text
这个东西非常强大，只需要简单几步就能极大提升效率。下面是学习路线。
```

Problem:

- promotional wording
- shallow structure
- vague claims
- roadmap framing

## Better style

```text
这个结构解决的是重复任务规范化问题。它把触发条件、执行步骤、参考资料和输出模板集中到一个目录中，使同类任务可以按稳定方式处理。
```

Why better:

- defines the problem
- explains the mechanism
- avoids exaggerated claims
- uses concrete structure
````

### `assets/long-note-template.md`

```markdown
# {{TITLE}}

{{开头说明本文的范围和目标。}}

## 核心定义与问题边界

{{定义主题，并说明它解决什么问题、不解决什么问题。}}

## 内部结构与组成

{{说明主要组成部分及其分工。}}

## 具体示例

{{给出目录结构、代码片段或输入输出示例。}}

## 常见错误与修正方式

{{列出误解、坏例子和更好的写法。}}

## 总结

{{用一段话压缩总结。}}
```

### `scripts/validate_note.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pathlib import Path
import re
import sys

BANNED_PHRASES = [
    "非常强大",
    "极大提升效率",
    "只需要简单几步",
    "小白也能学会",
    "保姆级教程",
    "学习路线",
]

def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: python validate_note.py path/to/file.md")
        return 1

    path = Path(sys.argv[1])
    if not path.exists():
        print("ERROR: file does not exist")
        return 1

    text = path.read_text(encoding="utf-8")
    errors = []
    warnings = []

    if not re.search(r"^# [^#].+", text, flags=re.MULTILINE):
        errors.append("missing H1 title")

    if len(re.findall(r"^```", text, flags=re.MULTILINE)) % 2 != 0:
        errors.append("unbalanced code fences")

    for phrase in BANNED_PHRASES:
        if phrase in text:
            warnings.append(f"discouraged phrase: {phrase}")

    for error in errors:
        print("ERROR:", error)

    for warning in warnings:
        print("WARNING:", warning)

    if errors:
        return 1

    print("PASS")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
```

这个完整示例展示了一个 Skill 如何把说明、资料、模板、脚本组合起来，而不是把所有内容混在一个文件里。

![Claude Skills Overview](http://public.file.lvshuhuai.cn/images\skills-claude-overview.png)

## 常见设计错误与修正

### 错误一：Skill 太泛

坏例子：

```yaml
description: Helps the user write better.
```

这个 Skill 没有边界，几乎什么写作任务都能匹配，最终会导致误用。

修正：

```yaml
description: Use this skill when the user asks to turn a conversation, source text, or concept explanation into a systematic Markdown note. The output should be detailed, structurally coherent, and avoid superficial tutorial-style writing.
```

修正后的版本明确了输入、任务和输出风格。

### 错误二：只有正向触发，没有反向边界

坏例子：

```markdown
## When to use

Use this skill for writing.
```

问题在于太宽。它没有说什么情况下不该用。

修正：

```markdown
## When not to use

Do not use this skill for:
- short answers
- casual chat
- translation
- code debugging
- spreadsheet generation
- slide generation
```

反向边界可以显著减少误触发。

### 错误三：把 `SKILL.md` 写成超长资料库

`SKILL.md` 如果塞入大量术语解释、长例子和背景文档，会变得难以维护。

修正方式：

```text
SKILL.md：只放入口规则和调度说明。
references/：放长资料。
assets/：放模板。
scripts/：放执行代码。
```

### 错误四：模板过度僵硬

模板应该是起点，不是铁板。用户请求不同，结构也应该调整。

坏做法：

```text
无论用户问什么，都强行套完整长文档模板。
```

修正：

```markdown
Templates are starting points. Modify or remove sections that do not fit the task.
```

### 错误五：脚本承担语义判断

坏做法：

```text
用脚本判断一篇文章是否有深度。
```

这类判断缺乏确定标准，脚本很难可靠完成。

修正：

```text
脚本检查格式、结构、代码块、文件名、schema。
内容深度、解释质量、结构取舍仍由语言理解或人工判断完成。
```

### 错误六：目录命名随意且无说明

虽然目录名不是绝对规范，但如果随意命名又不说明，会让 Skill 变得不可维护。

坏例子：

```text
my-skill/
├── SKILL.md
├── stuff/
├── things/
└── aaa/
```

修正：

```text
my-skill/
├── SKILL.md
├── references/
├── scripts/
└── assets/
```

如果确实要自定义目录名，也应在 `SKILL.md` 中明确说明：

```markdown
## File organization

- `docs/`: long reference documents
- `templates/`: reusable output templates
- `bin/`: executable scripts
```

## Skill 质量检查清单

写完一个 Skill 后，不要只看它有没有文件，而要检查它是否真的可用。

### 入口与触发

- 是否有 `SKILL.md`；
- 是否有明确的 `name`；
- 是否有具体的 `description`；
- description 是否说明任务类型；
- description 是否说明输入范围；
- description 是否说明输出要求；
- 是否避免了过宽的万能描述。

### 边界与适用范围

- 是否写清楚 When to use；
- 是否写清楚 When not to use；
- 是否说明哪些任务不应该触发；
- 是否避免把多个不相关任务塞进一个 Skill；
- 是否能从用户请求中判断是否该使用。

### 执行过程

- Procedure 是否是可执行步骤；
- 是否避免了“写得好”“更清楚”这种空泛指令；
- 是否说明如何处理长资料；
- 是否说明如何选择模板；
- 是否说明何时运行脚本；
- 是否说明输出格式。

### 文件组织

- `references/` 是否存放长期知识和规范；
- `scripts/` 是否只包含确定性操作；
- `assets/` 是否存放模板和资源；
- 是否存在职责混乱的文件；
- 每个文件是否能从名称看出用途；
- 自定义目录是否在 `SKILL.md` 中说明。

### 安全与维护

- 脚本是否避免危险操作；
- 脚本是否明确输入输出；
- 是否避免默认删除或覆盖文件；
- 是否尽量减少不必要依赖；
- 文件名是否可读；
- 未来维护者是否能快速理解结构。

![Share Skill](http://public.file.lvshuhuai.cn/images\skills-openai-screenshot-5.png)

