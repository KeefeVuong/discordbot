import discord
from discord.ext import commands
import youtube_dl
import os

client = commands.Bot(command_prefix="!")
song_id_count = 0

queue = {}
channel = None
def add_to_queue(guild, song):
    if guild.id not in queue:
        queue[guild.id] = []
    queue[guild.id].append(song)

@client.event
async def on_ready():
    print("I am online as {0.user}!".format(client))

# @client.event
# async def on_message(message):
#     if message.author == client.user:
#         return
    
#     if message.content.startswith("!hello"):
#         await message.author.voice.channel.connect()
#         await message.channel.send("Hi there!")

@client.command()
async def play(ctx, url):
    global song_id_count
    global channel
    song_path = os.path.isfile("song.webm")
    add_to_queue(ctx.message.guild, url)

    # try:
    #     if song_path:
    #         #os.remove("./song.webm")
    #         song = True
        
    # except PermissionError:
    #     await ctx.send("Wait for the current song to end or use '!stop' to stop the current song")
    #     return
    
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)

    if not voice:
    #     await ctx.send("Already connected to a voice channel.")
    #     song_urls.append(url)
        if ctx.message.author.voice:
            channel = ctx.message.author.voice.channel
            voice = await channel.connect()
        else:
            await ctx.send("You are not connected to any voice channels.")
            return
    
    ydl_opts = {
        "format": "249/250/251",
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        song = queue[channel.guild.id][0]
        if song == None:
            return
        queue[channel.guild.id].remove(song)
        ydl.download([song])
        song_id_count += 1

    for file in os.listdir("./"):
        if file.endswith(".webm"):
            os.rename(file, f"song{song_id_count}.webm")
    
    await voice.play(discord.FFmpegOpusAudio(f"song{song_id_count}.webm"))

@client.command()
async def leave(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if voice:
        await voice.disconnect()
    else:
        await ctx.send("Keefe bot is not connected to any voice channel.")

@client.command()
async def stop(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    voice.stop()

@client.command()
async def pause(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if voice.is_playing():
        voice.pause()
        await ctx.send("Pausing the song.")
    else:
        await ctx.send("No song is currently being played.")

@client.command()
async def resume(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if not voice.is_playing():
        voice.resume()
        await ctx.send("Resuming the song.")
    else:
        await ctx.send("No song has been paused.")

client.run("OTE4MTEzNDEzMjcwNDgyOTg1.YbChvw.Uibb10W8PKIMlK_NB4awV2rZluQ")