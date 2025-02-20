import discord
from discord.ext import commands
import asyncio
import romkan
import os
import subprocess
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.voice_states = True
intents.messages = True
bot = commands.Bot(command_prefix='-', intents=intents)

voice_clients = {}
text_channels = {}

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

@bot.command()
async def join_voice_channel(ctx, channel_id: int = None):
    if ctx.guild.id in voice_clients:
        await ctx.send("すでに別のチャンネルで動作しています。`-vcstop` で停止してください。")
        return
    if ctx.author.voice is None:
        embed = discord.Embed(title="VCに入っていません", description="`-join channelid` で指定するかVCに参加してください。", color=discord.Color.red())
        await ctx.send(embed=embed)
        return
    channel = ctx.author.voice.channel if channel_id is None else bot.get_channel(channel_id)
    if channel is None or not isinstance(channel, discord.VoiceChannel):
        embed = discord.Embed(title="VCに入っていません", description="`-join channelid` で指定するかVCに参加してください。", color=discord.Color.red())
        await ctx.send(embed=embed)
        return
    voice_client = await channel.connect()
    voice_clients[ctx.guild.id] = voice_client
    text_channels[ctx.guild.id] = ctx.channel.id

    embed = discord.Embed(title="接続完了！", description="バグがあったら以下にお願いいたします\n@.m0ai.（discord）", color=discord.Color.green())
    await ctx.send(embed=embed)

@bot.command()
async def stop_voice_connection(ctx):
    if ctx.guild.id in voice_clients:
        await voice_clients[ctx.guild.id].disconnect()
        del voice_clients[ctx.guild.id]
        del text_channels[ctx.guild.id]
        await ctx.send("VC接続を停止しました。")
    else:
        await ctx.send("現在VCに接続していません。")

@bot.event
async def on_message(message):
    if message.author.bot:
        return
    voice_client = voice_clients.get(message.guild.id)
    if voice_client and text_channels.get(message.guild.id) == message.channel.id:
        if message.author.voice and message.author.voice.channel == voice_client.channel:
            text = message.content
            romaji_text = romkan.to_roma(text)
            file_path = "/home/hukikomi/temp.wav"

            subprocess.run(["espeak-ng", "-v", "ja", "-w", file_path, romaji_text])

            if os.path.exists(file_path):
                audio_source = discord.FFmpegPCMAudio(file_path)
                voice_client.play(audio_source)
                while voice_client.is_playing():
                    await asyncio.sleep(0.5)
                os.remove(file_path)

    await bot.process_commands(message)

bot.run(TOKEN)
