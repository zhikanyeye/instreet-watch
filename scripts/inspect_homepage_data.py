#!/usr/bin/env python3
import json
from pathlib import Path

p = Path('/root/.openclaw/workspace/bailing-kan-xia/data/homepage.json')
data = json.loads(p.read_text())
print(data['meta']['updatedAt'])
print(data['hotPosts'][0]['title'])
print(data['groups'][0]['name'])
print(data['playground'][0]['name'])
