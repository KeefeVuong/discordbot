import discord
from discord.ext import commands
import pafy
import os
import urllib.request
import re

intents = discord.Intents.all()
client = commands.Bot(command_prefix="!", intents=intents)
song_id_count = 0
channel = None
global queues
queues = {}
repeat_status = False

@client.event
async def on_ready():
    print("I am online as {0.user}!".format(client))

def check_queue(ctx, id):
    global repeat_status
    global song_id_count
    if len(queues) > 0 and queues[id] != []:
        voice = ctx.guild.voice_client
        if (repeat_status): 
            source = queues[id][song_id_count]
            song_id_count += 1
            if (song_id_count == len(queues)):
                print("hello")
                song_id_count = 0
        else:
            source = queues[id].pop(0)
        voice.play(source["url"], after=lambda x=0: check_queue(ctx, ctx.message.guild.id))

@client.command()
async def repeat(ctx):
    global repeat_status
    if repeat_status is False:
        await ctx.send("Repeat mode is turned on.")
        repeat_status = True
    else:
        await ctx.send("Repeat mode is turned off.")
        repeat_status = False

@client.command()
async def remove(ctx, n):
    if len(queues) <= 0 or queues[ctx.message.guild.id] == []:
        await ctx.send("There are no songs in the queue.")
        return
    else:
        for i, item in enumerate(queues[ctx.message.guild.id]):
            if i == int(n):
                name = item["title"]
                await ctx.send(f"{name} has been removed from the queue.")
                queues[ctx.message.guild.id].remove(item)
                return

        await ctx.send(f"Invalid number. Please enter a number between 0 and {i}")
        return

@client.command()
async def queue(ctx):
    if len(queues) <= 0 or queues[ctx.message.guild.id] == []:
        await ctx.send("There are no songs in the queue.")
        return
    else:
        string = "```"
        for i, item in enumerate(queues[ctx.message.guild.id]):
            string += str(i) + ": " + item["title"] + "\n"

        string += "```"
        await ctx.send(string)
        return


@client.command()
async def clear(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    queues.clear()
    voice.stop()
    await ctx.send("Music is stopped and the queue is cleared.")

@client.command()
async def play(ctx, url):
    global song_id_count
    global channel
    
    if ("https://" not in url or "http://" not in url):
        html = urllib.request.urlopen("https://www.youtube.com/results?search_query=" + url)
        video_ids = re.findall(r"watch\?v=(\S{11})", html.read().decode())
        url = 'https://www.youtube.com/watch?v=' + video_ids[0]


    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)

    if not voice:
        if ctx.message.author.voice:
            channel = ctx.message.author.voice.channel
            voice = await channel.connect()
        else:
            await ctx.send("You are not connected to any voice channels.")
            return

    song = pafy.new(url)

    FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}


    audio = song.getbestaudio()

    source = {
        "url": discord.FFmpegOpusAudio(audio.url, **FFMPEG_OPTIONS),
        "title": song.title
    }

    guild_id = ctx.message.guild.id
    if guild_id in queues:
        queues[guild_id].append(source)
    else:
        queues[guild_id] = [source]

    await ctx.send(f'{song.title} was added to the queue')

    # ctx.voice_client.stop()
    # voice.play(discord.FFmpegOpusAudio(audio.url, **FFMPEG_OPTIONS))
    if (not voice.is_playing()):
        check_queue(ctx, guild_id)
        voice.is_playing()
        await ctx.send('Playing: '+ song.title)

@client.command()
async def skip(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if len(queues) <= 0 or queues[ctx.message.guild.id] == []:
        if voice.is_playing():
            ctx.voice_client.stop()
            voice.is_playing()
            await ctx.send("Skipped.")
        else:
            await ctx.send("There are no songs in the queue.")
            return
    else:
        voice.stop()
        check_queue(ctx, ctx.message.guild.id)
        await ctx.send('Skipped.')

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