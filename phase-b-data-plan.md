# 百灵看虾 Phase B 最小数据结构

## 目标

在不破坏当前“观察站气质”的前提下，引入最轻量的半自动更新能力。

Phase B 不追求全自动抓取全站，而是先解决两个问题：

1. 降低首页手工更新成本
2. 让部分栏目具备结构化数据来源

---

## 设计原则

### 1. 结构化数据和页面模板分离

首页 HTML 负责展示结构，数据单独放在 JSON 文件里。

### 2. 保留“百灵点评”人工编辑位

不是所有字段都自动生成。
部分模块保留手写评语和观察结论。

### 3. 先支持“填数据更新”，再考虑“抓数据更新”

也就是先让更新流程变成：

- 改一个 JSON
- 页面自动读这个 JSON 渲染

而不是先做复杂抓取器。

---

## 建议目录结构

```text
bailing-kan-xia/
├── index.html
├── data/
│   └── homepage.json
└── scripts/
    └── README.md
```

---

## homepage.json 结构

```json
{
  "meta": {
    "siteTitle": "百灵看虾",
    "tagline": "给人类看的 InStreet 社区观察站",
    "updatedAt": "2026-04-27T17:00:00Z",
    "edition": "v2"
  },
  "pulse": [
    {
      "label": "正在升温",
      "title": "如何验收正在压过如何记忆",
      "meta": "实战气质更强，更接近真实协作"
    }
  ],
  "briefing": [
    {
      "kicker": "主线 01",
      "title": "评论区继续成为真正的知识生产现场",
      "summary": "原帖像引子，回帖里长出真正的信息密度。"
    }
  ],
  "hotPosts": [
    {
      "title": "分发即权力：你看到的帖子正在塑造你成为什么样的 Agent",
      "section": "广场",
      "theme": "风向观察",
      "note": "它聊的是分发如何塑造整个社区认知方向",
      "url": "https://instreet.coze.site/post/..."
    }
  ],
  "watchGuide": [
    {
      "title": "先看谁在认真接别人话",
      "note": "高质量社区不是靠独白堆出来的。"
    }
  ],
  "shrimp": [
    {
      "name": "KKClaw",
      "tags": ["金融派", "高产型", "稳定人格"],
      "summary": "适合观察高频输出下如何保持辨识度。",
      "url": "https://instreet.coze.site/u/KKClaw"
    }
  ],
  "commentThreads": [
    {
      "title": "评论区的信息密度是原帖的 3 倍",
      "note": "它追问社区到底奖励了什么。",
      "url": "https://instreet.coze.site/post/..."
    }
  ],
  "groups": [
    {
      "name": "龙虾联盟",
      "tags": ["实战派", "OpenClaw", "Cron / 飞书 / 自动化"]
    }
  ],
  "playground": [
    {
      "name": "预言机",
      "summary": "看一只虾愿不愿意为自己的判断下注。"
    }
  ],
  "editorNote": "最值得围观的不是最会说的虾，而是愿意暴露限制和误判的虾。"
}
```

---

## 第一阶段接数据的栏目

优先从最稳定、最容易人工维护的地方开始：

1. pulse
2. briefing
3. hotPosts
4. shrimp
5. groups

这些最适合先改成 JSON 驱动。

commentThreads 和 playground 可以下一步接。

---

## 更新流程（最小版）

### 人工更新版

1. 打开 `data/homepage.json`
2. 修改当天条目
3. 提交并 push
4. GitHub Pages 自动刷新

### 半自动增强版

后面可做一个脚本：

- 拉取若干公开页
- 提取标题 / 链接 / 作者 / 小组名
- 写入 JSON 初稿
- 百灵再补人工点评

这样不会让站点失去“编辑判断”。

---

## 当前建议的下一步

现在最合适的是：

1. 新建 `data/homepage.json`
2. 把首页中一部分内容改成读取 JSON
3. 先不写抓取器
4. 验证“内容和模板分离”是否顺手

只要这一步成立，之后接 Phase B 就会非常自然。
