from flask import Flask, render_template, request, redirect
import os
import requests
import re

app = Flask(__name__)

FILE = "subreddits.txt"

# ---------- LOAD ----------
def load_subreddits():
    if not os.path.exists(FILE):
        return []

    with open(FILE, "r", encoding="utf-8") as f:
        return [line.strip() for line in f.readlines() if line.strip()]

# ---------- SAVE ----------
def save_subreddit(link):
    with open(FILE, "a", encoding="utf-8") as f:
        f.write(link + "\n")

# ---------- ICON FETCH ----------
def get_icon(sub_name):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        url = f"https://www.reddit.com/r/{sub_name}/about.json"
        r = requests.get(url, headers=headers, timeout=5)

        if r.status_code == 200:
            data = r.json()["data"]

            icon = (
                data.get("icon_img")
                or data.get("community_icon")
                or data.get("header_img")
            )

            if icon:
                return icon.split("?")[0]

    except:
        pass

    return "https://www.redditstatic.com/desktop2x/img/favicon/favicon-96x96.png"

# ---------- HOME ----------
@app.route("/", methods=["GET"])
def home():
    subs = load_subreddits()
    query = request.args.get("search", "").lower()

    processed = []
    seen = set()

    for s in subs:
        if query and query not in s.lower():
            continue

        name = s.rstrip("/").split("/r/")[-1]

        # remove duplicates in memory too
        if name in seen:
            continue
        seen.add(name)

        processed.append({
            "name": name,
            "url": s,
            "icon": get_icon(name)
        })

    return render_template("index.html", subreddits=processed, search=query)

# ---------- ADD (FIXED MULTI-INPUT PARSER) ----------
@app.route("/add", methods=["POST"])
def add():
    raw = request.form["url"]

    # 🔥 extract ALL r/subreddit anywhere in text
    subs = re.findall(r"r/[A-Za-z0-9_]+", raw)

    existing = load_subreddits()
    existing_set = set(existing)

    for sub in subs:
        full_link = f"https://www.reddit.com/{sub}/"

        # avoid duplicates in file
        if full_link in existing_set:
            continue

        save_subreddit(full_link)
        existing_set.add(full_link)

    return redirect("/")

# ---------- RUN ----------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
