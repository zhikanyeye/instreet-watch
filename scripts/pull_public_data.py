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
        summary = f"最近这只虾靠《{title[:18]}{'…' if len(title) > 18 else ''}》冒了头，适合顺着它的帖子和评论区慢慢认人。"
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
        count = item.get('comment_count', 0)
        if count >= 100:
            note = f"评论已经堆得很厚了，适合进去看分歧怎么长出来。当前 {count} 条。"
        else:
            note = f"这帖的评论区已经开始有密度了，适合从回帖而不是原帖切进去。当前 {count} 条。"
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
            "kicker": "今天先看",
            "title": top_post["title"],
            "summary": "这条帖不一定代表最正确的观点，但很适合拿来判断今天社区的注意力正往哪边偏。",
        })
    if top_comment:
        items.append({
            "kicker": "别跳过评论区",
            "title": f"《{top_comment['title'][:20]}{'…' if len(top_comment['title']) > 20 else ''}》更值得从回帖读起",
            "summary": top_comment["note"],
        })
    if top_group or top_shrimp:
        group_name = top_group["name"] if top_group else "这个热门小组"
        shrimp_name = top_shrimp["name"] if top_shrimp else "那只刚冒头的虾"
        items.append({
            "kicker": "围观路线",
            "title": f"今天不妨先钻 {group_name}，再顺着 {shrimp_name} 认人",
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
