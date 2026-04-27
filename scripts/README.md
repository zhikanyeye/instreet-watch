# scripts/

这里先不放抓取器，先放约定。

## Phase B 原则

- 先让 `index.html` 读取 `data/homepage.json`
- 再考虑写脚本生成 JSON 初稿
- 抓取器只负责“收集公开信息”，不负责写最终观察结论
- 百灵点评和结构判断继续保留人工编辑位

## 后续可加的脚本

- `pull-public-pages.js`
  - 拉取公开页标题、链接、小组名等
- `build-homepage-json.js`
  - 把抓取结果整理成首页 JSON 初稿
- `publish.sh`
  - 提交并 push 更新
