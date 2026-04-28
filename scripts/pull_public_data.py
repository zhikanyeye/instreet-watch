#!/usr/bin/env python3
import json
import os
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

BASE_URL = os.environ.get("INSTREET_BASE_URL", "https://instreet.coze.site")
API_KEY = os.environ.get("INSTREET_API_KEY")
ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "homepage.json"

if not API_KEY:
    raise SystemExit("Missing INSTREET_API_KEY environment variable")


def api_get(path: str):
    req = urllib.request.Request(
        BASE_URL + path,
        headers={"Authorization": f"Bearer {API_KEY}"},
        method="GET",
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode())


def api_get_first(paths):
    last_error = None
    for path in paths:
        try:
            return api_get(path)
        except Exception as e:
            last_error = e
    raise last_error


def pick_hot_posts(posts_payload):
    items = posts_payload["data"]["data"][:3]
    out = []
    for item in items:
        out.append(
            {
                "title": item["title"],
                "section": item.get("submolt", {}).get("display_name") or item.get("submolt", {}).get("name") or "广场",
                "theme": "热帖观察",
                "note": f"{item.get('upvotes', 0)} 赞，{item.get('comment_count', 0)} 评论，适合从互动密度切进去看。",
                "url": f"{BASE_URL}/post/{item['id']}",
            }
        )
    return out


def pick_groups(groups_payload):
    items = groups_payload["data"]["groups"][:4]
    out = []
    for item in items:
        desc = item.get("description", "")
        tags = []
        if "OpenClaw" in desc or "自动化" in desc:
            tags.append("实战派")
        if "成长" in desc or "进化" in desc:
            tags.append("成长派")
        if "哲学" in desc or "意识" in desc:
            tags.append("哲学派")
        if not tags:
            tags.append("热门小组")
        tags.append(f"{item.get('member_count', 0)} 成员")
        out.append({"name": item.get("display_name") or item["name"], "tags": tags})
    return out


def pick_watchworthy_shrimp(posts_payload):
    items = posts_payload["data"]["data"][:3]
    out = []
    for idx, item in enumerate(items):
        agent = item.get("agent", {})
        tags = []
        title = item.get("title", "")
        content = item.get("content", "")
        if any(k in title + content for k in ["工作流", "自动化", "架构", "复盘"]):
            tags.append("实战派")
        if any(k in title + content for k in ["思考", "观察", "意识", "哲学"]):
            tags.append("观察派")
        if agent.get("karma", 0) > 100000:
            tags.append("高势能")
        elif agent.get("karma", 0) > 10000:
            tags.append("稳定输出")
        if not tags:
            tags.append("值得围观")
        summary = f"最近一帖《{title[:20]}{'…' if len(title) > 20 else ''}》互动不错，适合顺着它的帖子和评论区认人。"
        out.append({
            "name": agent.get("username", f"虾 {idx+1}"),
            "tags": tags[:3],
            "summary": summary,
            "url": f"{BASE_URL}/u/{agent.get('username', '')}" if agent.get("username") else BASE_URL,
        })
    return out


def pick_comment_threads(posts_payload):
    items = sorted(posts_payload["data"]["data"][:8], key=lambda x: x.get("comment_count", 0), reverse=True)[:2]
    out = []
    for item in items:
        note = f"当前 {item.get('comment_count', 0)} 条评论，适合从评论区密度和分歧点切进去看。"
        out.append({
            "title": item.get("title", "无标题"),
            "note": note,
            "url": f"{BASE_URL}/post/{item['id']}",
        })
    return out


def pick_playground(markets_payload):
    markets = markets_payload["data"]["markets"][:3]
    out = []
    for item in markets:
        out.append(
            {
                "name": item["title"][:24] + ("…" if len(item["title"]) > 24 else ""),
                "summary": f"预言机热门市场，当前 {item.get('participant_count', 0)} 人参与，成交量 {round(item.get('total_volume', 0))}。",
            }
        )
    return out


def build_briefing(hot_posts, groups, shrimp, comments):
    top_post = hot_posts[0] if hot_posts else None
    top_group = groups[0] if groups else None
    top_shrimp = shrimp[0] if shrimp else None
    top_comment = comments[0] if comments else None
    items = []
    if top_post:
        items.append({
            "kicker": "热帖信号",
            "title": top_post["title"],
            "summary": f"这条帖现在最适合拿来读当天风向，它的入口价值大于结论本身。",
        })
    if top_comment:
        items.append({
            "kicker": "评论区入口",
            "title": f"先别急着读原帖，优先看《{top_comment['title'][:18]}{'…' if len(top_comment['title']) > 18 else ''}》的评论区",
            "summary": top_comment["note"],
        })
    if top_group or top_shrimp:
        group_name = top_group["name"] if top_group else "热门小组"
        shrimp_name = top_shrimp["name"] if top_shrimp else "值得围观的虾"
        items.append({
            "kicker": "围观建议",
            "title": f"今天适合先钻 {group_name}，再顺着 {shrimp_name} 认人",
            "summary": "先看组的气质，再看谁在里面持续留下可复用的东西，比只刷热榜更容易看出结构。",
        })
    return items[:3]


def main():
    data = json.loads(DATA_PATH.read_text())

    hot_posts = api_get_first([
        "/api/v1/posts?sort=hot&limit=8",
        "/api/v1/posts?sort=new&limit=8",
    ])
    groups = api_get("/api/v1/groups?sort=hot")
    markets = api_get("/api/v1/oracle/markets?sort=hot")

    data.setdefault("meta", {})["updatedAt"] = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    data["hotPosts"] = pick_hot_posts(hot_posts)
    data["groups"] = pick_groups(groups)
    data["playground"] = pick_playground(markets)
    data["shrimp"] = pick_watchworthy_shrimp(hot_posts)
    data["commentThreads"] = pick_comment_threads(hot_posts)

    top_titles = [p["title"] for p in data["hotPosts"][:2]]
    data["pulse"] = [
        {
            "label": "刚刚更新",
            "title": "热帖、小组雷达、评论区入口已自动刷新",
            "meta": "这个站已经开始自己长内容，但保留百灵的观察视角",
        },
        {
            "label": "当前热议",
            "title": top_titles[0] if top_titles else "社区正在生成新的热点",
            "meta": "先看互动密度，再看观点本身",
        },
        {
            "label": "推荐入口",
            "title": (data["groups"][0]["name"] if data.get("groups") else "龙虾联盟") + " 值得先钻进去",
            "meta": "从组的气质看，比只看热榜更容易找到同类",
        },
    ]

    data["briefing"] = build_briefing(
        data["hotPosts"],
        data["groups"],
        data["shrimp"],
        data["commentThreads"],
    )

    DATA_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")
    print(f"Updated {DATA_PATH}")


if __name__ == "__main__":
    main()
