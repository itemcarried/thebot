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
    "zs_laurelmall": 1540019369999081663,
    "gm_flux": 1540025355455303732,
    "gm_underground_parking": 1540025600192946288,
    "gm_flux2": 1540025736608481290,
    "gm_prison": 1540025797690265720,
    "gm_windswept": 1540025852346245311,
    "rp_silenthilldark": 1540025899938742312,
    "gm_port_trajan": 1540025940011253870,
    "gm_bitterbrookwoods": 1540026019849699439,
    "gm_construct_renovation_night": 1540026080944066611,
    "gm_rostok_factory_minecraft": 1540026121276358767,
    "hns_deadcity": 1540026171184386048,
    "gm_ancientegypt_night": 1540026207587008513,
    "gm_mallparking_plus": 1540026249231999026,
    "gm_fazbears_forgotten": 1540026290470658068,
    "gm_occupants": 1540026349685706762,
    "gm_cabin_in_the_woods": 1540026392501288980,
    "gm_russia": 1540026427053711361,
    "hns_sc_asylum": 1540026458498666596,
    "gm_bunker678": 1540026516984037447,
    "hns_bricolage": 1540026552400617483,
    "gm_cfx_upsilon_hotel": 1540026617399869632,
    "rp_area354_orion_v2": 1540026654569537576,
    "cc_new_eden": 1540026697531920516,
    "gm_city17_aftermath": 1540026760089837648,
    "gm_k9": 1540026824073941112,
    "hns_stormwald": 1540026860245618818,
    "gm_cyan_dreampools": 1540026997139574834,
    "gm_silent_apartments": 1540027059521454240,
    "soul_of_cinder": 1540027093587333220,
    "gm_cursed_flat": 1540027140693823598,
    "gm_ratpocalypse": 1540027179113390123,
    "gm_fieldhouse": 1540027216279244931,
    "pvb_outlook_r1": 1540027282175959130,
    "repentance": 1540027361410678814,
    "gm_doomsdale": 1540027390426877992,
    "rp_unioncity": 1540027447674675211,
    "gm_neonpolis": 1540027478750527508,
    "gm_moskva_1942": 1540027521842679939,
    "gm_closedzone-001": 1540027569984774304,
    "rp_wasteland_city_ruins": 1540027610732695713,
    "gm_vacant_industry_revamped": 1540027673831546950,
    "gm_everpine_mall": 1540027706819747980,
    "rp_outtown_v1": 1540027749094391868,
    "gm_operation_grace": 1540027797353926716,
    "gm_subclass": 1540027831638032434,
    "rp_sister_location_night": 1540027864009936926,
    "rp_southside": 1540027913221570622,
    "gm_mc15": 1540027954371760250,
    "rp_vindico_mines": 1540028024538406922
}

CHECK_INTERVAL = 60

GIF_URL = " || https://tenor.com/view/bleach-nel-cutie-yes-yep-gif-18405016442900009995 || "

intents = discord.Intents.default()
intents.guilds = True
intents.message_content = True

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
            f"New map: `{current_map}`\n"
            f"{GIF_URL}",
            allowed_mentions=discord.AllowedMentions(roles=True)
        )
        print(f"Pinged role for map: {current_map}")
    except discord.DiscordException as e:
        print(f"Failed to send Discord message: {e}")


@bot.command()
async def testmap(ctx, *, map_name: str):
    role_id = MAP_ROLES.get(map_name)

    if role_id is None:
        await ctx.send(f"No role configured for map: {map_name}")
        return

    await ctx.send(
        f"<@&{role_id}> **Map changed!**\n"
        f"New map: `{map_name}`\n"
        f"{GIF_URL}",
        allowed_mentions=discord.AllowedMentions(roles=True)
    )


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
    print("ERROR: No TOKEN found.")
    print("Make sure you set the TOKEN variable in Railway.")
else:
    bot.run(TOKEN)
