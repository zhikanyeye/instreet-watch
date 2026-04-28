# scripts/

这里先不放抓取器，先放约定。

## Phase B 原则

- 先让 `index.html` 读取 `data/homepage.json`
- 再考虑写脚本生成 JSON 初稿
- 抓取器只负责“收集公开信息”，不负责写最终观察结论
- 百灵点评和结构判断继续保留人工编辑位

## 当前已存在脚本

### `pull_public_data.py`

用途：

- 拉取公开可见的热帖
- 拉取热门小组
- 拉取预言机热门市场
- 回写 `data/homepage.json` 的部分字段

使用方式：

```bash
cd bailing-kan-xia
INSTREET_API_KEY=你的key python3 scripts/pull_public_data.py
```

说明：

- 它会自动更新 `hotPosts`、`groups`、`playground`
- 也会自动生成 `shrimp` 和 `commentThreads` 的初稿
- 也会顺手刷新一部分 `pulse` 和 `briefing`
- 但不会覆盖所有百灵的人工观察内容

### `publish.sh`

用途：

- 拉取公开数据
- 更新 `data/homepage.json`
- 自动提交变化
- 自动 push 到 GitHub Pages 仓库

使用方式：

```bash
cd bailing-kan-xia
INSTREET_API_KEY=你的key bash scripts/publish.sh
```

说明：

- 如果这次拉取后没有内容变化，它会直接退出，不会产生空提交
- 如果有变化，会自动提交并推送

### `inspect_homepage_data.py`

用途：

- 快速检查 `homepage.json` 当前关键字段是否更新成功

## 后续可加的脚本

- `build-homepage-json.js`
  - 把抓取结果整理成首页 JSON 初稿
