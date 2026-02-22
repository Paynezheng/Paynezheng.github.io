# Blog

大约是2023年的下半年，开始陆陆续续写一些零碎的感悟和心得，有的是技术上的，有的是生活上的。

本项目基于 [Jekyll](https://jekyllrb.com/) 框架和 [jekyll-theme-chirpy](https://github.com/cotes2020/jekyll-theme-chirpy) 主题构建。

## 本地预览

```bash
bundle install          # 首次安装依赖
bundle exec jekyll serve  # 启动本地预览，访问 http://127.0.0.1:4000
```

## 新增博客文章

1. 在 `_posts/` 目录下新建文件，命名格式为 `YYYY-MM-DD-文章名.md`
2. 文件开头写 YAML Front Matter：
   ```yaml
   ---
   title: 文章标题
   date: 2026-01-01 12:00:00 +0800
   categories: [一级分类, 二级分类]
   tags: [标签1, 标签2]
   description: 文章简介
   author: Payne
   ---
   ```
3. Front Matter 之后用 Markdown 编写正文

详细说明请参考博客文章：[如何新增博客和编辑博客样式](https://paynezheng.github.io/posts/how-to-blog/)

## 自定义样式

在 `assets/css/jekyll-theme-chirpy.scss` 中添加自定义 CSS/SCSS 规则，可以覆盖主题默认样式。

## Contribute

翻译的读书笔记/文章欢迎指正和勘误，可以通过 Blog 下方的评论留言，或者直接给[本项目](https://github.com/Paynezheng/Paynezheng.github.io)提 issue。如果想要发表文章或者直接在文章上修改，可以直接在此项目下提 PR。

提 PR 需要先在 `_data/authors.yml` 下添加作者信息，然后在 `_posts` 下找到对应的文章或者新增文章，文章开头添加自己的 `author` 字段即可。