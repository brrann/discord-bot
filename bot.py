import discord
from discord.ext import tasks
import json
import os
from datetime import datetime, timedelta

# ============================================================
#  SETTINGS - Only edit things in this section
# ============================================================

TOKEN = os.getenv("TOKEN")

ROLE_NAME = "ROBUX"  # Exact name of the role in your server

FIRST_DM = "**Groups to Join:**\n\n🔗 https://www.roblox.com/communities/33289887/Urban-Shift#!/about\n\n🔗 https://www.roblox.com/communities/152867095/URBAN-SHIFT-UGC#!/about\n\n🔗 https://www.roblox.com/communities/313721528/for-tha-guys#!/about\n\n🔗 https://www.roblox.com/communities/504790841/URBAN-SHlFT\n\nI'll notify you **14 days from today** to remind you that you're now payout eligible for Robux!

FOLLOWUP_DM = "Hey, this is your reminder to DM **Bran** that you're payout eligible in the **ROBLOX communities** and can now buy Robux!"

# ============================================================
#  BOT CODE - Do not edit below this line
# ============================================================

DATA_FILE = "pending_dms.json"

intents = discord.Intents.default()
intents.members = True
intents.guilds = True

client = discord.Client(intents=intents)

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

@client.event
async def on_ready():
    print(f"✅ Bot is online as {client.user}")
    check_pending_dms.start()

@client.event
async def on_member_update(before, after):
    before_roles = set(r.name for r in before.roles)
    after_roles = set(r.name for r in after.roles)

    # Check if the ROBUX role was just added
    if ROLE_NAME in after_roles and ROLE_NAME not in before_roles:
        try:
            await after.send(FIRST_DM)

            data = load_data()
            data[str(after.id)] = {
                "username": str(after),
                "role_given_at": datetime.utcnow().isoformat()
            }
            save_data(data)
            print(f"📨 Sent first DM to {after} — 14-day reminder scheduled")

        except discord.Forbidden:
            print(f"⚠️ Could not DM {after} — they may have DMs disabled")

@tasks.loop(hours=1)
async def check_pending_dms():
    data = load_data()
    now = datetime.utcnow()
    to_remove = []

    for user_id, info in data.items():
        role_given_at = datetime.fromisoformat(info["role_given_at"])
        if now >= role_given_at + timedelta(days=14):
            try:
                user = await client.fetch_user(int(user_id))
                await user.send(FOLLOWUP_DM)
                print(f"✅ Sent 14-day payout DM to {user}")
            except Exception as e:
                print(f"⚠️ Could not send followup to {user_id}: {e}")
            to_remove.append(user_id)

    for user_id in to_remove:
        del data[user_id]

    if to_remove:
        save_data(data)

client.run(TOKEN)
