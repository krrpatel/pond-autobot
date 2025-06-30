import uuid
import json
import requests
import google.generativeai as genai
from datetime import datetime, timedelta
import time
import schedule
import os

CONFIG_FILE = "config.json"

# === 🔧 LOAD OR ASK CONFIG ===
def load_or_ask_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            config = json.load(f)
            print("✅ Loaded config from config.json")
            return config
    else:
        config = {
            "developer_id": input("Enter your Developer ID: ").strip(),
            "auth_token": input("Enter your CryptoPond Auth Token: ").strip(),
            "gemini_api_key": input("Enter your Gemini API Key: ").strip(),
            "last_post_time": datetime.now().isoformat(),
            "last_vote_time": datetime.now().isoformat()
        }
        with open(CONFIG_FILE, "w") as f:
            json.dump(config, f, indent=2)
        print("💾 Saved config to config.json")
        return config

config = load_or_ask_config()
DEVELOPER_ID = config["developer_id"]
AUTH_TOKEN = config["auth_token"]
GEMINI_API_KEY = config["gemini_api_key"]

# === ⚙️ HEADERS ===
HEADERS = {
    "accept": "application/json, text/plain, */*",
    "authorization": AUTH_TOKEN,
    "content-type": "application/x-www-form-urlencoded",
    "origin": "https://cryptopond.xyz",
    "referer": "https://cryptopond.xyz/ideas",
    "user-agent": "Mozilla/5.0"
}

# === 💡 IDEA POST SYSTEM ===
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel(model_name="gemini-1.5-flash")

def generate_crypto_idea():
    prompt = (
        "Generate a crypto project idea. Return it in this strict format:\n\n"
        "**Name:** <name here>\n"
        "**Subtitle:** <short subtitle here>\n"
        "**Description:** <1 paragraph under 50 words>\n\n"
        "No bullet points, no numbering. Only the three fields with labels exactly as shown."    )
    response = model.generate_content(prompt)
    text = response.text.strip()
    name, subtitle, description = "", "", ""
    for line in text.split('\n'):
        if line.lower().startswith("**name:**"):
            name = line.split("**Name:**", 1)[-1].strip(" *")
        elif line.lower().startswith("**subtitle:**"):
            subtitle = line.split("**Subtitle:**", 1)[-1].strip(" *")
        elif line.lower().startswith("**description:**"):
            description = line.split("**Description:**", 1)[-1].strip(" *")
    return name or "Unnamed Project", subtitle or "No Subtitle", description or "No Description"

def build_description_block(text):
    block_id = str(uuid.uuid4())
    return json.dumps([
        {
            "id": block_id,
            "type": "paragraph",
            "props": {
                "textColor": "default",
                "backgroundColor": "default",
                "textAlignment": "left"
            },
            "content": [{"type": "text", "text": text, "styles": {}}],
            "children": []
        }
    ])

def post_to_cryptopond(name, subtitle, description_json):
    url = "https://cryptopond.xyz/api/frontier/api/v1/competitions/modify"
    payload = {
        "name": name,
        "subtitle": subtitle,
        "description": description_json,
        "current_status": "0",
        "developer_id": DEVELOPER_ID
    }
    response = requests.post(url, headers=HEADERS, data=payload)
    print("\n🚀 Idea Submission Response:")
    print(response.json())
    config["last_post_time"] = datetime.now().isoformat()
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)

# === 🗳️ VOTING SYSTEM ===
def get_vote_history():
    url = f"https://cryptopond.xyz/api/frontier/api/v1/developer/{DEVELOPER_ID}/competition/vote/history"
    r = requests.get(url, headers=HEADERS)
    data = r.json().get("data", {})
    return data.get("count", 0), data.get("week_start"), data.get("week_end")

def get_unvoted_ideas():
    url = "https://cryptopond.xyz/api/frontier/api/v2/competition/ideas?limit=50&offset=0&status=going"
    r = requests.get(url, headers=HEADERS)
    ideas = r.json().get("data", {}).get("list", [])
    return [i for i in ideas if i.get("is_voted", {}).get("Bool") is False]

def vote_on_idea(idea_id):
    url = f"https://cryptopond.xyz/api/frontier/api/v2/competition/{idea_id}/{DEVELOPER_ID}/vote"
    payload = f"competition_id={idea_id}&developer_id={DEVELOPER_ID}"
    r = requests.post(url, headers=HEADERS, data=payload)
    return "Voting Success" in r.text

def get_user_points():
    url = f"https://cryptopond.xyz/api/frontier/api/v1/developer/{DEVELOPER_ID}/points/detail"
    r = requests.get(url, headers=HEADERS)
    data = r.json().get("data", {}).get("score", {})
    print(f"\n💰 Points Summary: Today: {data.get('TodayScore')} | Month: {data.get('MonthScore')} | Total: {data.get('TotalScore')}")

# === ⏲️ TIMED ACTIONS ===
def should_post():
    last = datetime.fromisoformat(config["last_post_time"])
    return datetime.now() - last >= timedelta(hours=24)

def should_vote():
    last = datetime.fromisoformat(config["last_vote_time"])
    return datetime.now() - last >= timedelta(hours=48)

def scheduled_post():
    print(f"\n📆 Posting idea at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    get_user_points()
    name, subtitle, desc_text = generate_crypto_idea()
    print(f"\n📌 {name} - {subtitle}\n📝 {desc_text}")
    desc_json = build_description_block(desc_text)
    post_to_cryptopond(name, subtitle, desc_json)


def scheduled_vote():
    print(f"\n📆 Voting at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    get_user_points()
    vote_count, ws, we = get_vote_history()
    remaining = max(0, 3 - vote_count)
    print(f"\n🗓️ Voting Period: {ws} to {we} | ✅ Votes Left: {remaining}")
    ideas = get_unvoted_ideas()
    if not ideas:
        print("🟡 No unvoted ideas available.")
        return
    for idea in ideas[:remaining]:
        print(f"🗳️ Voting on: {idea['name']} (ID: {idea['id']})")
        success = vote_on_idea(idea['id'])
        print("✅ Success" if success else "❌ Failed")
    config["last_vote_time"] = datetime.now().isoformat()
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)

# Run immediately once, then schedule
scheduled_post()
scheduled_vote()

schedule.every(24).hours.do(scheduled_post)
schedule.every(48).hours.do(scheduled_vote)

print("✅ Bot is running. Next actions will be scheduled...")
while True:
    schedule.run_pending()
    time.sleep(30)
