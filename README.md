# Blog

大约是2023年的下半年，开始陆陆续续写一些零碎的感悟和心得，有的是技术上的，有的是生活上的。

---

## 如何新增博客文章

### 1. 文件命名

在 `_posts/` 目录下新建一个 Markdown 文件，文件名格式为：

```
YYYY-MM-DD-文章英文标识.md
```

例如：`2026-01-15-my-new-post.md`

### 2. 填写 Front Matter（文章头部信息）

每篇文章必须以 YAML front matter 开头，基本格式如下：

```yaml
---
title: 文章标题
date: 2026-01-15 12:00:00 +0800
categories: [一级分类, 二级分类]   # 例如 [Tech, Database] 或 [Music, Guitar]
tags: [标签1, 标签2]
description: 文章摘要
author: Payne
---
```

**可选字段说明：**

| 字段 | 说明 | 示例 |
|------|------|------|
| `pin: true` | 文章置顶（首页最前面显示） | `pin: true` |
| `math: true` | 启用 KaTeX 数学公式渲染 | `math: true` |
| `mermaid: true` | 启用 Mermaid 流程图/时序图 | `mermaid: true` |
| `toc: false` | 关闭右侧目录（默认开启） | `toc: false` |
| `comments: false` | 关闭评论（默认开启） | `comments: false` |
| `image` | 文章封面图 | 见下方示例 |

封面图用法：

```yaml
image:
  path: /assets/img/posts/2026-01-15-my-new-post/cover.png
  alt: 图片说明文字
```

### 3. 文章图片

将图片存放在 `assets/img/posts/<文章日期-文章名>/` 目录下，然后在文章中引用：

```markdown
![图片说明](/assets/img/posts/2026-01-15-my-new-post/example.png)
```

### 4. 草稿（可选）

不想立即发布的文章，可先放在 `_drafts/` 目录下（文件名不需要日期前缀）。
本地预览草稿时使用命令：`bundle exec jekyll serve --drafts`

`_drafts/post-template.md` 提供了包含所有可用 front matter 选项和常用 Markdown 语法的完整模板，可直接复制使用。

### 5. 本地预览

```bash
bundle exec jekyll serve
# 含草稿预览
bundle exec jekyll serve --drafts
```

---

## 如何修改博客样式

本博客使用 [jekyll-theme-chirpy](https://github.com/cotes2020/jekyll-theme-chirpy) 主题，样式定制方式如下：

### 1. 自定义 CSS

编辑 `assets/css/jekyll-theme-chirpy.scss` 文件，在该文件中添加 CSS 规则即可覆盖主题默认样式。该文件中已提供常用的样式覆盖示例（均被注释），按需取消注释并修改即可。

常用示例：

```scss
/* 修改正文字体 */
body {
  font-family: "PingFang SC", "Microsoft YaHei", sans-serif;
}

/* 自定义链接颜色 */
[data-mode=light] {
  --link-color: #0056b3;
}

/* 自定义暗色模式链接颜色 */
[data-mode=dark] {
  --link-color: #6ab4f5;
}
```

### 2. 主题配置

大部分主题配置在 `_config.yml` 中，包括：

- `theme_mode: light/dark` — 默认颜色模式（留空跟随系统）
- `toc: true/false` — 全局目录开关
- `paginate: 10` — 首页每页显示的文章数量
- `comments.provider` — 评论系统（当前使用 utterances）
- `avatar` — 侧边栏头像路径

### 3. 侧边栏导航

导航菜单对应 `_tabs/` 目录下的各个 `.md` 文件，每个文件的 front matter 控制图标和排序：

```yaml
---
icon: fas fa-info-circle   # Font Awesome 图标
order: 4                    # 菜单排序（数字越小越靠前）
---
```

---

## Contribute

翻译的读书笔记/文章欢迎指正和勘误，可以通过Blog下方的评论留言，或者直接给[本项目](https://github.com/Paynezheng/Paynezheng.github.io)提issue。如果想要发表文章或者直接在文章上修改，可以直接在此项目下提PR。

提PR需要在 `_data/authors.yml` 下添加作者信息，然后在 `_posts` 下找到对应的文章或者新增对应的文章，文章开头添加自己的 `author` 就可以新增文章或者修改文章啦！