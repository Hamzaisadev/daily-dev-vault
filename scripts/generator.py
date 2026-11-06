#!/usr/bin/env python3
import json
import os
import sys
import subprocess
from datetime import datetime, timezone

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CATALOG_PATH = os.path.join(ROOT_DIR, "scripts", "catalog.json")
VAULT_DIR = os.path.join(ROOT_DIR, "vault")
METADATA_PATH = os.path.join(VAULT_DIR, "metadata.json")
README_PATH = os.path.join(ROOT_DIR, "README.md")

def load_json(path, default=None):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return default or []

def save_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def build_entry_markdown(topic, date_str):
    category_title = topic['category'].replace("-", " ").title()
    tags_formatted = " ".join([f"`#{tag}`" for tag in topic.get("tags", [])])
    
    return f"""# ⚡ {topic['title']}

> **Category**: {category_title} &nbsp;·&nbsp; **Difficulty**: `{topic['difficulty']}` &nbsp;·&nbsp; **Published**: {date_str}  
> **Tags**: {tags_formatted}

---

## 📌 Executive Summary
{topic['summary']}

---

## 🧠 Architectural Deep-Dive & Core Concept
{topic['concept']}

---

## 💻 Production Implementation ({topic['code_language'].title()})

```{topic['code_language']}
{topic['code_snippet'].strip()}
```

---

## 🔬 Benchmark & Engineering Trade-offs
{topic['deep_dive']}

---

## 🚀 Key Takeaways for Senior Engineers
- **Production Safety**: Ensure error boundaries and proper retry logic handle edge cases gracefully.
- **Observability**: Expose telemetry counters and latency histograms for all critical operations.
- **Resource Footprint**: Keep memory allocations and network roundtrips minimized under high concurrency.

---
*Authored by [Hamza Ishaq (@Hamzaisadev)](https://github.com/Hamzaisadev) · Part of the [Daily Dev Vault](https://github.com/Hamzaisadev/daily-dev-vault).*
"""

def generate_readme(published_entries):
    total = len(published_entries)
    last_updated = datetime.now(timezone.utc).strftime("%B %d, %Y")
    
    rows = []
    for entry in published_entries:
        date_str = entry.get("published_date", "")
        title = entry["title"]
        category = entry["category"].replace("-", " ").title()
        diff = entry["difficulty"]
        rel_path = f"vault/{entry['category']}/{entry['id']}.md"
        rows.append(f"| `{date_str}` | **[{title}]({rel_path})** | `{category}` | `{diff}` |")
        
    table_str = "\n".join(rows) if rows else "| *Pending initial entries* | | | |"
    
    latest_entry = published_entries[-1] if published_entries else None
    latest_feature = ""
    if latest_entry:
        latest_feature = f"""### 🔥 Latest Entry: [{latest_entry['title']}](vault/{latest_entry['category']}/{latest_entry['id']}.md)
> *{latest_entry['summary']}*
"""

    return f"""<div align="center">

# 🏛️ Daily Dev Vault
### *Production-Grade Engineering Deep Dives, Systems Architecture & High-Performance Patterns*

[![Daily Automated Ship](https://github.com/Hamzaisadev/daily-dev-vault/actions/workflows/daily-entry.yml/badge.svg)](https://github.com/Hamzaisadev/daily-dev-vault/actions)
[![Total Topics Shipped](https://img.shields.io/badge/Topics%20Shipped-{total}-34D399?style=for-the-badge&logo=git&logoColor=white)](https://github.com/Hamzaisadev/daily-dev-vault)
[![License: MIT](https://img.shields.io/badge/License-MIT-38BDF8?style=for-the-badge)](LICENSE)
[![GitHub Stars](https://img.shields.io/github/stars/Hamzaisadev/daily-dev-vault?style=for-the-badge&color=FBBF24&logo=github)](https://github.com/Hamzaisadev/daily-dev-vault/stargazers)
[![Follow @Hamzaisadev](https://img.shields.io/github/followers/Hamzaisadev?style=for-the-badge&color=0B111E&logo=github&label=Follow%20%40Hamzaisadev)](https://github.com/Hamzaisadev)

<p align="center">
  A curated, daily engineering repository containing verified, battle-tested solutions for distributed systems, high-concurrency backends, database internals, and modern full-stack performance.
</p>

[Browse Vault](#-topic-directory) &nbsp;·&nbsp; [Suggest a Topic](https://github.com/Hamzaisadev/daily-dev-vault/issues/new) &nbsp;·&nbsp; [Author Profile](https://github.com/Hamzaisadev)

</div>

---

## ⚡ What is the Daily Dev Vault?

Most developer tutorials show toy examples. The **Daily Dev Vault** is different:
- **No Fluff**: Pure architectural rationale, mathematical proofs, and production code.
- **Enterprise-Grade**: Handles concurrency races, network partitions, memory limits, and failover scenarios.
- **Automated Delivery**: Shipped daily via GitHub Actions with automated verification.

{latest_feature}

---

## 📚 Topic Directory

| Date | Title | Category | Difficulty |
| :--- | :--- | :--- | :--- |
{table_str}

---

## 🛠️ Repository Structure

```text
daily-dev-vault/
├── .github/workflows/   # Automated daily ship pipeline (GitHub Actions)
├── vault/               # Deep-dive Markdown entries grouped by domain
│   ├── algorithms/
│   ├── backend/
│   ├── performance/
│   ├── security/
│   └── system-design/
└── scripts/             # Topic generator, validation, and auto-indexer
```

---

## 🤝 Contributing & Star Support

1. ⭐ **Star this repository** if you find these architecture deep dives helpful!
2. 🍴 **Fork & Clone** to test the code recipes locally.
3. 💬 Open an issue if you'd like an architectural breakdown of a specific technology or protocol.

---

<div align="center">
  <sub>Maintained by <b><a href="https://github.com/Hamzaisadev">Hamza Ishaq (@Hamzaisadev)</a></b> · Software Architect & Full-Stack Systems Engineer</sub>
</div>
"""

def main():
    catalog = load_json(CATALOG_PATH, [])
    metadata = load_json(METADATA_PATH, {"published": [], "last_index": -1})
    published_ids = {item["id"] for item in metadata.get("published", [])}
    
    # Pick next unpublished topic
    next_topic = None
    for topic in catalog:
        if topic["id"] not in published_ids:
            next_topic = topic
            break
            
    if not next_topic:
        print("All catalog topics published! Recycling with updated deep-dives...")
        next_topic = catalog[0]
        
    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    category_dir = os.path.join(VAULT_DIR, next_topic["category"])
    os.makedirs(category_dir, exist_ok=True)
    
    entry_path = os.path.join(category_dir, f"{next_topic['id']}.md")
    content = build_entry_markdown(next_topic, date_str)
    
    with open(entry_path, "w", encoding="utf-8") as f:
        f.write(content)
        
    print(f"Generated entry: {entry_path}")
    
    # Record metadata
    entry_record = {
        "id": next_topic["id"],
        "title": next_topic["title"],
        "category": next_topic["category"],
        "difficulty": next_topic["difficulty"],
        "published_date": date_str,
        "summary": next_topic["summary"]
    }
    
    metadata["published"].append(entry_record)
    metadata["last_updated"] = date_str
    save_json(METADATA_PATH, metadata)
    
    # Update README
    readme_content = generate_readme(metadata["published"])
    with open(README_PATH, "w", encoding="utf-8") as f:
        f.write(readme_content)
        
    print("Updated README.md with latest directory index.")
    
    # Git actions if requested
    if "--push" in sys.argv or "--commit" in sys.argv:
        print("Staging and committing changes...")
        subprocess.run(["git", "add", "."], cwd=ROOT_DIR, check=True)
        commit_msg = f"feat(vault): publish '{next_topic['title']}' ({date_str})"
        subprocess.run(["git", "commit", "-m", commit_msg], cwd=ROOT_DIR, check=False)
        
        if "--push" in sys.argv:
            print("Pushing to remote origin...")
            subprocess.run(["git", "push", "origin", "main"], cwd=ROOT_DIR, check=True)
            print("Successfully pushed to GitHub! 🚀")

if __name__ == "__main__":
    main()
