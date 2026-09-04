# Obsidian 使用指南:如何用 Obsidian 打开并管理本知识库

本知识库是纯 Markdown(MkDocs 构建),**Obsidian 可以直接作为 vault 打开**,无需转换。

## 一、安装 Obsidian

```bash
# 方式 1:Homebrew(若已安装)
brew install --cask obsidian

# 方式 2:直接下载(浏览器打开下面链接,选 macOS 的 .dmg)
#   https://obsidian.md/download
# 或命令行下载(Universal 包,含 Apple Silicon):
curl -L -o ~/Downloads/Obsidian.dmg \
  "https://github.com/obsidianmd/obsidian-releases/releases/download/v1.13.4/Obsidian-1.13.4.dmg"

# 安装 dmg:双击打开 → 把 Obsidian 拖进 Applications 即可
```

## 二、打开本知识库作为 vault(推荐用 docs/)

两种方式二选一(推荐第 1 种):

1. **只管理知识内容**:Obsidian → "Open folder as vault" → 选择本仓库的 **`docs/`** 目录
   - 好处:只看知识文章,不含 MkDocs 构建文件与参考资料;
   - 目录结构:01-ai-basics / 02-llm / … / 10-harmonyos / inbox / _template.md。
2. **管理全仓库**:选择仓库**根目录**
   - 可同时看 `references/`(原始资料存档)与 `docs/`,但导航里会混入非知识文件。

## 三、链接与语法兼容说明

| 本站写法 | Obsidian 表现 | 说明 |
| --- | --- | --- |
| `[标题](../02-llm/rag.md)` | ✅ 原生支持相对路径 Markdown 链接,点击跳转 | 无需修改 |
| `[[wikilink]]` | 未启用(本站用相对路径风格) | 若想用,设置 → Files & Links → 开启 |
| `!!! note 提示块` | 显示为普通引用块 | MkDocs admonition 语法,Obsidian 不渲染为卡片,但不影响阅读 |
| YAML frontmatter | ✅ 原生识别 | 可用于标签/属性 |

!!! tip "建议设置(可选)**
    - 设置 → Files & Links → **New link format: Relative path to file**(与本站一致);
    - 设置 → Editor → 关闭严格 Markdown 换行(便于看本站长文);
    - 把 `inbox/` 加入 Excluded files(可选,避免未整理素材干扰图谱)。

## 四、在 Obsidian 里能做什么

- **浏览**:左侧文件树直接看全部章节文章;
- **关系图谱**:Graph view 看站内互链(文章间引用自动成图);
- **检索**:全局搜索(Cmd/Ctrl+Shift+F),可搜全站;
- **编辑**:直接改 Markdown,改完运行 `.venv/bin/mkdocs build` 即可重新构建站点;
- **收件箱**:新素材丢进 `docs/inbox/`,按本站 AGENTS.md 流程整理。

## 五、注意事项

- **不要改动** `mkdocs.yml`、`docs/index.md` 的学习地图结构(它们控制站点导航);
- 文章链接用相对路径(与 MkDocs 一致),**不要用 `[[wikilink]]` 替代**(会破坏站点构建);
- 新增文章后按 AGENTS.md 的"联动更新"流程更新章节 index 与 nav。
