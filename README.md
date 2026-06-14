# Homer

Homer 是一个面向单本长篇网文项目的 Codex skill 集。

它的核心不是“帮你写一点文字”，而是维护一套适合连载小说的知识机制：作者可以拥有完整设定，但 AI 写作时默认只参考读者已经知道的内容，以及当前连载需要延续的状态。也就是用“公开设定 + 追踪”来支持部分揭露，避免 AI 把还没揭开的真相、未来伏笔、幕后规则提前写漏。

## 核心机制：部分揭露

长篇连载里，作者脑中通常有完整真相，但正文只能逐步揭露。Homer 把知识分成三层：

- `author-lore`：作者侧完整设定，来源于 `设定/`。这里可以包含隐藏真相、未来反转、世界真实规则、角色秘密和私有计划。
- `public-lore`：读者已经知道的公开设定，来源于所有 `accepted` 正文章节。默认写作只使用这层，避免提前泄露。
- `tracking`：连载追踪状态，来源于所有 `accepted` 正文章节。记录时间线、角色当前位置、关系状态、未回收伏笔、后续需要修补的问题。

默认写作上下文是：

```text
当前用户指令
+ 相关大纲
+ public-lore
+ tracking
+ 必要时的前文/相关 accepted 正文
```

默认不读完整 `设定/`，也不读完整 `author-lore`。只有当任务明确需要隐藏设定时，才读取相关切片。例如某章要揭露角色真实身份，就只读取这个角色和相关组织的作者设定，而不是把整本书的隐藏真相都塞进上下文。

这套机制的目标是让 AI 像一个知道连载边界的助手：它知道读者现在知道什么，也知道当前故事状态推进到哪里，但不会默认把作者手里的底牌摊出来。

## 三条业务流

Homer MVP 只保留三条线：

- `homer-setup`：初始化或修复单本书项目，扫描已有章节，建立 `.homer/state/chapters.json`。
- `homer-write`：写作、续写、扩写、打磨合一，直接修改 `正文/` 下的 draft 文件。
- `homer-sync`：采纳章节进入 canon，并从所有 accepted 章节全量重建 `public-lore` 和 `tracking`。

另有 Codex 启动辅助：

- `homer-start`：在重启会话、hooks 不可用或需要重新加载状态时使用。

## 项目模型

一个工作目录就是一本书。

作者目录完全自由：

```text
设定/     # 作者侧完整设定、隐藏真相、未来揭露
大纲/     # 卷纲、章纲、临时规划
正文/     # 章节正文
```

Homer 结构化目录：

```text
.homer/
  workflow.md
  spec/
  state/
    chapters.json
  knowledge/
    author-lore/
    public-lore/
    tracking/
  cache/
  scripts/
  adapters/
```

Codex / agent 适配层：

```text
.agents/skills/    # 共享 skill
.codex/            # Codex 专用 skill、hook、配置
```

`.homer/` 是权威源。`.agents/` 和 `.codex/` 是从 `.homer/adapters/` 生成出来的适配层。

## 章节状态

章节状态保存在 `.homer/state/chapters.json`。

只保留三种状态：

- `planned`：已规划，但还不是可编辑正文。
- `draft`：可编辑工作稿。
- `accepted`：已采纳为 canon，默认不再修改。

知识状态：

- `none`：不进入长期知识，通常用于 `planned` 或 `draft`。
- `current`：accepted 章节的 hash 与已生成知识一致。
- `stale`：accepted 章节被改过，需要重新 sync。

核心规则：

- `draft` 可以直接改。
- `accepted` 是 canon，默认不改。
- 修改 accepted 属于 canon revision，必须让生成知识变 stale，直到下一次 sync。
- draft 不进入 `public-lore` 和 `tracking`。

## public-lore：公开设定

`public-lore` 只从 accepted 章节重建，表示读者已经知道或可以合理感知到的内容。

它需要区分：

- `shown_fact`：正文明确展示或确认的事实。
- `reader_inference`：读者可以推断，但正文尚未确认。
- `character_claim`：角色说过或相信的内容。
- `rumor`：流言、传闻、公众说法。
- `misdirection`：有意误导的信息。

每条内容都应保留证据和来源章节。这样写新章时，AI 使用的是“读者视角可见世界”，不是作者完整真相。

## tracking：连载追踪

`tracking` 同样只从 accepted 章节重建，但它不是 public-lore 的摘要，而是直接从正文抽取当前连续性状态。

推荐文件：

```text
.homer/knowledge/tracking/context.json
.homer/knowledge/tracking/timeline.json
.homer/knowledge/tracking/character-state.json
.homer/knowledge/tracking/foreshadowing.json
.homer/knowledge/tracking/patches.json
```

它用于回答这些问题：

- 当前剧情推进到哪里？
- 各角色在哪里、知道什么、状态如何？
- 哪些伏笔已经埋下但还没回收？
- 哪些 accepted 正文里的问题不能回头改，只能后文修补？

## author-lore：作者侧设定索引

`author-lore` 来源于 `设定/`，用于索引作者自由写下的完整设定。

规则：

- `设定/` 是作者自由编辑的源文件。
- Homer 默认不修改 `设定/`。
- `author-lore` 只作为 AI 可读 JSON 索引。
- 显式事实、推断、候选想法、冲突项、过期设定必须分开。

## 基本命令

初始化或修复项目：

```bash
python3 .homer/scripts/homer.py init --scan
```

查看状态：

```bash
python3 .homer/scripts/homer.py status
```

从 `.homer/adapters/` 重新生成 `.agents/` 和 `.codex/`：

```bash
python3 .homer/scripts/homer.py generate-adapters
```

修改 draft 章节后更新 hash：

```bash
python3 .homer/scripts/homer.py check
```

机械采纳章节：

```bash
python3 .homer/scripts/homer.py accept 1
```

`homer-sync` 完成 public-lore / tracking 重建后标记知识为最新：

```bash
python3 .homer/scripts/homer.py mark-current
```

## Codex 使用方式

常用 skill：

- `$homer-start`：开始会话或上下文丢失后加载状态。
- `$homer-setup`：初始化、扫描、修复项目。
- `$homer-write`：写作、续写、扩写、打磨 draft。
- `$homer-sync`：采纳章节并重建知识。

`.codex/hooks/inject-homer-state.py` 会在 hooks 启用时注入简短状态，但 hooks 不是硬依赖；skill 和脚本可以独立工作。

## 不做什么

MVP 不做：

- 榜单扫描。
- 市场题材分析。
- 拆书分析产品。
- 封面生成。
- 短篇/长篇双工作流。
- 多书切换。
- 发布平台集成。
- 单独的 review 工作流。
- 每次写作任务创建独立任务目录。

## 仓库内容

- `HOMER_MVP_SPEC.md`：MVP 规格文档。
- `.homer/`：Homer 权威源，包括 workflow、spec、state、knowledge、script、adapter 模板。
- `.agents/skills/`：生成的共享 skill。
- `.codex/`：生成的 Codex 专用 skill、hook、配置。

## 致谢

Homer 的设计参考了两个项目：

- [Trellis](https://github.com/tophtab/Trellis)：参考其“权威源 + 多平台适配生成层”的组织方式。
- [oh-story-claudecode](https://github.com/tophtab/oh-story-claudecode)：参考其小说写作工作流、长篇写作辅助和 Claude/Codex skill 组织经验。

Homer 会有意收敛范围：它不是全链路网文工具箱，而是单本书项目里的知识、写作和同步助手。
