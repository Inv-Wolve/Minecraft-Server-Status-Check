import discord
import os
from discord.ext import commands, tasks
from mcstatus import MinecraftServer
from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')
SERVER_IP = os.getenv('SERVER_IP')
ROLE_ID = 12345567890 # replace with role to ping
CHANNEL_ID = 1345676543 # replace with the channel ID you want to send the messages to 

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

server_was_online = False

@bot.listen("on_ready")
async def on_ready():
    print(f'Logged in as {bot.user}')
    if not check_server_status.is_running():
        check_server_status.start()

@tasks.loop(minutes=5)
async def check_server_status():
    global server_was_online
    channel = bot.get_channel(CHANNEL_ID)
    role = discord.utils.get(channel.guild.roles, id=ROLE_ID)

    try:
        server = MinecraftServer.lookup(SERVER_IP)
        status = server.status()
        
        if not server_was_online:
            response = (
                f"🟢 **The Server `{SERVER_IP}` is now online!**\n"
                f"**Players Online**: {status.players.online}/{status.players.max}\n"
                f"**Ping**: {status.latency} ms\n"
                f"{role.mention}"
            )
            await channel.send(response)
            server_was_online = True
        else:
            response = (
                f"🟢 **The Server `{SERVER_IP}` is still online.**\n"
                f"**Players Online**: {status.players.online}/{status.players.max}\n"
                f"**Ping**: {status.latency} ms"
            )
            await channel.send(response)

    except Exception as e:
        if server_was_online:
            await channel.send(f"🔴 **The Server `{SERVER_IP}` is now offline.**")
            server_was_online = False
        else:
            print(f"Could not reach server {SERVER_IP}: {e}")

@bot.command()
async def mcstatus(ctx):
    await check_server_status()

bot.run(BOT_TOKEN)