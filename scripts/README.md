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
- 也会顺手刷新一部分 `pulse` 和 `briefing`
- 但不会覆盖所有百灵的人工观察内容

## 后续可加的脚本

- `build-homepage-json.js`
  - 把抓取结果整理成首页 JSON 初稿
- `publish.sh`
  - 提交并 push 更新
