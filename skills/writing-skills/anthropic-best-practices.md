# Skill 编写最佳实践

> 本文整理 Anthropic 官方关于编写可发现、可执行 skill 的建议，并保留其关键结构、例子和检查项。

优秀 skill 应简洁、结构清楚，并经真实使用验证。概念背景见 [Skills overview](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview)。

## 核心原则

### 简洁最重要

context window 是公共资源。skill 会与 system prompt、对话历史、其它 skill metadata 和用户请求竞争空间。启动时通常只预加载 `name` 与 `description`，正文和 supporting file 按需读取，但入口一旦加载，每个 token 都有成本。

默认假设 agent 已经很聪明。对每段内容追问：agent 是否真的需要？能否合理假定它已知道？这段解释是否值得其 token 成本？

```markdown
## 提取 PDF 文本

使用 pdfplumber：

```python
import pdfplumber

with pdfplumber.open("file.pdf") as pdf:
    text = pdf.pages[0].extract_text()
```
```

无需解释 PDF 是什么、为什么需要 library 或如何安装每个常见工具，除非这些信息对目标环境并非显而易见。

### 设置合适的自由度

指导强度要匹配任务的脆弱性和变化范围：

- **高自由度：** 多种方法都有效、决策依赖上下文、适合 heuristic 时，用文字原则。
- **中自由度：** 有首选模式但允许变化，或配置影响行为时，用 pseudocode 或带参数脚本。
- **低自由度：** 操作脆弱、错误成本高、顺序必须一致时，给精确脚本和极少参数。

数据库 migration 像两侧悬崖的窄桥，需要明确 guardrail；code review 更像开阔地，可以依上下文选择路径。

### 在实际使用的每种模型上测试

skill 是底层模型的增量，因此效果依赖模型。若同时使用 Haiku、Sonnet、Opus、Claude Code 或 Codex，要分别确认较弱模型得到足够指导，平衡模型能高效执行，强推理模型不会被过度解释束缚。

## Skill 结构

`SKILL.md` frontmatter 需要：

- `name`：不超过 64 字符。
- `description`：不超过 1024 字符，说明 skill 的能力和使用时机。

本仓库另有更严格的本地规则：description 只写触发条件，防止模型把流程摘要当捷径；以本仓库 `writing-skills/SKILL.md` 为准。

### 命名

使用一致、可描述活动的名称。官方建议 gerund/动名词形式，如 Processing PDFs、Analyzing spreadsheets、Managing databases。也可用明确名词短语或动作短语。避免 Helper、Utils、Tools、Documents、Data 等含糊或过度宽泛名称，并保持整个 skill 集合一致。

### 有效 Description

description 会注入 system prompt，必须使用第三人称，包含 agent 选择该 skill 所需的具体关键词和上下文。不要写“我可以帮你……”或“你可以用它……”。

```yaml
# 具体
description: 处理 PDF 文本、表格、form 与 document extraction 任务时使用

# 含糊
description: 帮助处理文档
```

### 渐进披露

把 `SKILL.md` 当作概览和导航，目标正文少于 500 行；接近上限时拆出 reference、example 和 script。

```text
pdf/
├── SKILL.md
├── FORMS.md
├── reference.md
├── examples.md
└── scripts/
    ├── analyze_form.py
    ├── fill_form.py
    └── validate.py
```

常见模式：

1. **入口加直接 references：** quick start 留在入口，form、API、example 分别直接链接。
2. **按领域拆分：** `reference/finance.md`、`sales.md`、`product.md`、`marketing.md`，只加载当前问题需要的领域。
3. **按条件导航：** 普通编辑放入口；tracked changes 指向 `REDLINING.md`；OOXML 细节指向 `OOXML.md`。

reference 与入口只保持一层关系。不要让 `SKILL.md -> advanced.md -> details.md` 多层跳转，因为 agent 可能只 preview 前 100 行而漏掉真实规则。超过 100 行的 reference 应在顶部提供目录。

## Workflow 与反馈循环

### 复杂任务使用顺序明确的 Workflow

长分析和无代码任务同样适用 checklist：

```text
研究进度：
- [ ] 读取全部 source
- [ ] 识别关键主题
- [ ] 交叉核对主张
- [ ] 生成结构化摘要
- [ ] 验证引用
```

每步必须说明输入、动作和完成条件。代码任务也可以使用：分析 form -> 生成 field mapping -> 验证 mapping -> 填写 -> 验证输出。若验证失败，应回到产生该 artifact 的步骤，而不是继续。

### 实施反馈循环

核心模式是：运行 validator -> 修复错误 -> 再次运行，直到通过。

无代码内容可把 `STYLE_GUIDE.md` 作为 validator：起草、逐项对照术语/示例/必需 section、记录问题、修订、再次对照。代码 artifact 应在修改后立即执行确定性 validator，通过后才能 pack 或发布。

## 内容规则

### 避免易过期信息

不要用“2025 年 8 月之前用旧 API，之后用新 API”污染主路径。正文只写当前方法；确有历史价值时放在折叠的“旧模式”部分，并标注 deprecated 时间和状态。

### 术语保持一致

全文固定使用一个术语，如始终使用 “API endpoint”“field”“extract”，不要在 URL/API route/path 或 field/box/control 之间随意切换。

## 常用模式

### 模板

输出格式严格时明确说“必须使用以下精确结构”；允许适配时明确说这是默认结构，并允许按分析内容调整。不要让 agent 猜测格式约束强度。

### Input/Output 示例

输出质量依赖风格时，给少量完整 input/output pair。例如 commit message 示例应同时体现 subject 和 body，而不是只描述 conventional commit 概念。例子通常比抽象说明更容易让模型匹配目标形状。

### 条件 Workflow

先让 agent 判断任务类型，再路由到对应步骤。例如创建 DOCX 使用 `docx-js` 从零构建；编辑已有 DOCX 则 unpack、修改 XML、逐次 validate、最后 repack。流程太大时拆入独立文件，并在入口明确何时读取哪一个。

## 评估与迭代

### 先建立 Evaluation

写大量文档前先运行无 skill baseline：

1. 在代表性任务中识别具体信息缺口或失败。
2. 建立至少三个覆盖这些缺口的场景。
3. 记录无 skill 表现。
4. 只写足以处理失败的最小指导。
5. 与 baseline 比较并迭代。

```json
{
  "skills": ["pdf-processing"],
  "query": "Extract all text from this PDF file and save it to output.txt",
  "files": ["test-files/document.pdf"],
  "expected_behavior": [
    "Reads every page with an appropriate PDF tool",
    "Extracts all text without missing pages",
    "Writes readable output.txt"
  ]
}
```

evaluation 是测量 skill 效果的 authority。平台没有统一内建 runner 时，可以自行建立只读 harness。

### 用创建者和使用者两个新鲜上下文迭代

一个 agent 帮助整理 domain knowledge 和改进 skill，另一个 fresh-context agent 用 skill 执行真实任务。观察后者遗漏了什么、文件读取顺序是否异常、哪些 reference 从未访问、哪些规则被忽略，再把原始行为反馈给前者调整。

重要的是传递任务 artifact 和可观察行为，不泄露预期答案或先前结论。测试 agent 不应编辑 skill 或代替主 agent 实施修改。

### 观察 Agent 如何导航

注意意外的探索路径、未跟随的重要链接、对某一 section 的过度依赖以及从不访问的 bundled file。常访问的内容可能应移回入口；从不访问的内容可能无用或入口提示不足。`name` 与 `description` 对是否触发尤其关键。

## 应避免的反模式

### Windows 风格路径

始终使用 `/`：`scripts/helper.py`、`reference/guide.md`。不要使用 `scripts\helper.py`。

### 提供过多选项

除非必要，不要同时列 pypdf、pdfplumber、PyMuPDF、pdf2image 等一堆平行选项。给一个默认方案，再为明确例外提供 escape hatch，例如普通文本用 pdfplumber，扫描件 OCR 才用 pdf2image + pytesseract。

## 含可执行代码的高级 Skill

纯 Markdown skill 可直接跳到最终 checklist。

### 解决问题，不把错误甩回 Agent

script 应明确处理 `FileNotFoundError`、`PermissionError` 等错误，给有用信息或安全 fallback，而不是裸 `open(path).read()` 后让 agent 自己猜。

配置值必须解释依据，避免 voodoo constant：

```python
# 普通 HTTP 请求通常 30 秒内完成；该值也容纳慢连接
REQUEST_TIMEOUT = 30

# 三次 retry 在可靠性与速度之间平衡，多数间歇失败会在第二次前恢复
MAX_RETRIES = 3
```

### 提供 Utility Script

预置 script 比每次生成更可靠、更省 token、更快，也能保持一致。说明 agent 应该**执行**还是**阅读**：

- “运行 `analyze_form.py` 提取 fields”表示执行。
- “阅读 `analyze_form.py` 理解 extraction algorithm”表示作为 reference。

大多数 utility script 应直接执行；输出格式和错误行为必须记录。

### 视觉分析

输入可渲染成图像时，可以提供 `pdf_to_images.py` 等确定性转换脚本，再让 agent 查看每页图像识别 layout 和 field。必须实际包含并测试所引用脚本。

### 可验证的中间产物

批量、破坏性、复杂规则或高风险任务应先产生 machine-readable preview，例如 `changes.json`，在触碰原始文件前由 script 验证：分析 -> 输出 change set -> 验证 -> 执行 -> 验证结果。

validator 要给具体错误，例如指出不存在的 `signature_date` 并列出可用 field，而不是只说 invalid。

### 依赖与 Runtime

列出必需 package，并按目标平台验证可用性。claude.ai 可能允许从 npm/PyPI/GitHub 安装；Anthropic API 的 code execution 环境可能无网络和 runtime 安装能力，当前事实应以官方运行时文档为准。

skill runtime 通过 filesystem 按需读取文件并执行 bash/script。大 reference 在未读取前不占 context，因此文件名应描述内容，目录按 domain/feature 组织，确定性操作优先 script。

### MCP 工具名

使用完全限定名 `ServerName:tool_name`，例如 `BigQuery:bigquery_schema`、`GitHub:create_issue`，避免多个 MCP server 下找不到工具。

### 不要假定工具已安装

明确 dependency 和安装方式，或提供环境检测。不要只说“使用 pdf library”。但安装动作本身仍必须符合目标 runtime 的网络和权限约束。

## 技术约束

- `name` 最大 64 字符，`description` 最大 1024 字符。
- `SKILL.md` 正文目标少于 500 行；更多内容通过渐进披露拆分。
- 文件引用保持一层深，并使用 `/`。
- 结构细节以当前 [Skills overview](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview#skill-structure) 为准。

## 有效 Skill Checklist

### 核心质量

- [ ] description 具体，包含关键触发词和使用场景
- [ ] 正文少于 500 行，细节按需拆出
- [ ] 易过期内容不污染当前主路径
- [ ] 术语一致，示例具体
- [ ] reference 只深一层
- [ ] 渐进披露合理，workflow 步骤清晰

### 代码与 Script

- [ ] script 解决错误，而不是把问题甩回 agent
- [ ] 错误信息明确有用
- [ ] 所有参数有依据，没有 magic number
- [ ] 依赖已列出并验证可用
- [ ] 使用 `/` 路径
- [ ] 关键操作有 validation/verification 与反馈循环

### 测试

- [ ] 至少建立三个 evaluation
- [ ] 在实际计划使用的每种模型/runtime 上测试
- [ ] 使用真实任务场景，而不只学术问题
- [ ] 有团队时吸收真实使用反馈

## 后续阅读

- [Agent Skills quickstart](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/quickstart)
- [Claude Code skills](https://code.claude.com/docs/en/skills)
- [Skills API guide](https://platform.claude.com/docs/en/build-with-claude/skills-guide)
