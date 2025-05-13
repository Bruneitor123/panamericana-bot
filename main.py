import os
import discord
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
RADIO_STATIONS = {
    "Panamericana": os.getenv("RADIO_PANAMERICANA"),
    "Machete": os.getenv("RADIO_MACHETE"),
    "Latina": os.getenv("RADIO_LATINA"),
    "Bolivia": os.getenv("RADIO_BOLIVIA"),
}

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Logged in as {bot.user}")

@bot.tree.command(name="join", description="Join your voice channel")
async def join(interaction: discord.Interaction):
    if interaction.user.voice:
        channel = interaction.user.voice.channel
        await channel.connect()
        await interaction.response.send_message(f"Joined {channel.name}")
    else:
        await interaction.response.send_message("You're not in a voice channel.", ephemeral=True)

@bot.tree.command(name="leave", description="Leave the voice channel")
async def leave(interaction: discord.Interaction):
    if interaction.guild.voice_client:
        await interaction.guild.voice_client.disconnect()
        await interaction.response.send_message("Disconnected.")
    else:
        await interaction.response.send_message("I'm not in a voice channel.", ephemeral=True)

@bot.tree.command(name="radio", description="Play a radio station")
@app_commands.describe(station="Choose a radio station to play")
@app_commands.choices(station=[
    app_commands.Choice(name=key, value=key) for key in RADIO_STATIONS.keys()
])
async def radio(interaction: discord.Interaction, station: app_commands.Choice[str]):
    url = RADIO_STATIONS.get(station.value)
    if not url:
        await interaction.response.send_message("Invalid station selected.", ephemeral=True)
        return

    voice_client = interaction.guild.voice_client
    if not voice_client:
        if interaction.user.voice:
            channel = interaction.user.voice.channel
            voice_client = await channel.connect()
        else:
            await interaction.response.send_message("You're not in a voice channel.", ephemeral=True)
            return

    if voice_client.is_playing():
        voice_client.stop()

    source = discord.FFmpegPCMAudio(url)
    voice_client.play(source)
    await interaction.response.send_message(f"Now playing: {station.value}")

bot.run(TOKEN)
