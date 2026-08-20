import asyncio
import discord
from discord.ext import tasks, commands
import a2s
import os
 
TOKEN = os.getenv("TOKEN")
 
SERVER_IP = "74.91.116.36"
SERVER_PORT = 27015
 
CHANNEL_ID = 1539999058708668569
 
MAP_ROLES = {
    "zs_mall_revival_halloween": 1540005438249238648,
}
 
CHECK_INTERVAL = 60
 
intents = discord.Intents.default()
intents.guilds = True
 
bot = commands.Bot(command_prefix="!", intents=intents)
 
last_map = None
 
 
async def get_current_map():
    loop = asyncio.get_running_loop()
    try:
        info = await loop.run_in_executor(
            None,
            lambda: a2s.info((SERVER_IP, SERVER_PORT), timeout=5.0)
        )
        return info.map_name
    except Exception as e:
        print(f"Failed to query server: {e}")
        return None
 
 
@tasks.loop(seconds=CHECK_INTERVAL)
async def check_map():
    global last_map
 
    current_map = await get_current_map()
    if current_map is None:
        print("Server unavailable.")
        return
 
    print(f"Current map: {current_map}")
 
    if current_map == last_map:
        return
 
    old_map = last_map
    last_map = current_map
 
    print(f"Map changed: {old_map} -> {current_map}")
 
    role_id = MAP_ROLES.get(current_map)
    if role_id is None:
        print(f"No role configured for map: {current_map}")
        return
 
    channel = bot.get_channel(CHANNEL_ID)
    if channel is None:
        print("Could not find the Discord channel.")
        return
 
    try:
        await channel.send(
            f"<@&{role_id}> **Map changed!**\n"
            f"New map: `{current_map}`",
            allowed_mentions=discord.AllowedMentions(roles=True)
        )
        print(f"Pinged role for map: {current_map}")
    except discord.DiscordException as e:
        print(f"Failed to send Discord message: {e}")
 
 
@bot.event
async def on_ready():
    print("--------------------------------")
    print(f"Logged in as: {bot.user}")
    print(f"Bot ID: {bot.user.id}")
    print("--------------------------------")
 
    if not check_map.is_running():
        check_map.start()
        print("Map checker started.")
 
 
@check_map.before_loop
async def before_check_map():
    await bot.wait_until_ready()
 
 
if TOKEN is None:
    print("no token")  
else:
    bot.run(TOKEN)
