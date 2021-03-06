import asyncio
import discord
import os
from dotenv import load_dotenv
from discord import FFmpegPCMAudio
from discord.ext import commands
from youtube_dl import YoutubeDL
from discord.utils import get
from random import randint

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
intents = discord.Intents.default()
intents.members = True
songs = asyncio.Queue()
play_next_music = asyncio.Event()
client = discord.Client()
client = commands.Bot(command_prefix='#', intents=intents)


@client.event
async def on_ready():
    print(client.user.id)
    print(client.user.name)
    print('---------------------')


@client.event
async def on_member_join(member):
    await member.send('Добро пожаловать на сервер!')


@client.command()
async def roll(ctx):
    a = randint(0, 100)
    await ctx.send(f"Тебе выпало: {a}")


queue = []


@client.command(aliases=['p'])
async def play(ctx, url):
    if not ctx.message.author.voice:
        await ctx.send("Дурак что-ли. зайди сначала в гс")
    else:
        voice_client = get(client.voice_clients, guild=ctx.guild)
        YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist': 'True'}
        FFMPEG_OPTIONS = {
            'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
        if voice_client is None or not voice_client.is_connected():
            await ctx.message.author.voice.channel.connect()
            voice = get(client.voice_clients, guild=ctx.guild)
            if not voice.is_playing():
                with YoutubeDL(YDL_OPTIONS) as ydl:
                    info = ydl.extract_info(url, download=False)
                    URL = info['url']
                    TITLE = info['title']
                    THUMBNAIL = info['thumbnail']
                    voice.play(FFmpegPCMAudio(URL, **FFMPEG_OPTIONS))
                    voice.is_playing()
                    embed = discord.Embed(title=TITLE, url=url, color=discord.Color.from_rgb(255, 255, 255))
                    embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
                    embed.set_thumbnail(url=THUMBNAIL)
                    await ctx.send(embed=embed)
        elif voice_client.is_playing():
            queue.append(url)
            if queue:
                s = 0
                for i in queue:
                    with YoutubeDL(YDL_OPTIONS) as ydl:
                        info = ydl.extract_info(queue[s], download=False)
                        TITLE = info['title']
                        THUMBNAIL = info['thumbnail']
                        s += 1
                embed = discord.Embed(title=TITLE, url=queue[s - 1], color=discord.Color.from_rgb(255, 255, 255))
                embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
                embed.set_thumbnail(url=THUMBNAIL)
                embed.set_footer(text="Песня добавлена в очередь")
                await ctx.send(embed=embed)


@client.command()
async def stop(ctx):
    voice = get(client.voice_clients, guild=ctx.guild)
    if voice.is_playing():
        voice.stop()
        await ctx.voice_client.disconnect()
        await ctx.send('Останавливаюсь!')


if __name__ == "__main__":
    client.run(TOKEN)
