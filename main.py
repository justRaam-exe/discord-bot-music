# # main.py
# import discord
# from discord.ext import commands
# import yt_dlp as youtube_dl
# import asyncio

# # Konfigurasi
# TOKEN = 'MTMzODgzNTc2Mzk2OTY1ODkxMw.GeE3VY.L_aWT0vBKPQvT8casBQI89fkRqRBUOXEVTSAIg'  # Ganti dengan token bot Anda
# PREFIX = '!'  # Prefix perintah

# # Inisialisasi bot
# intents = discord.Intents.default()
# intents.message_content = True
# bot = commands.Bot(command_prefix=PREFIX, intents=intents)

# # Konfigurasi untuk yt-dlp
# ydl_opts = {
#     'format': 'bestaudio/best',
#     'postprocessors': [{
#         'key': 'FFmpegExtractAudio',
#         'preferredcodec': 'mp3',
#         'preferredquality': '192',
#     }],
#     'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
# }

# ffmpeg_options = {
#     'options': '-vn'
# }

# # Antrian lagu per server
# queues = {}

# @bot.event
# async def on_ready():
#     print(f'Bot {bot.user.name} telah online!')

# def check_queue(ctx, id):
#     if queues.get(id):
#         player = queues[id].pop(0)
#         ctx.voice_client.play(player, after=lambda x=None: check_queue(ctx, id))

# @bot.command()
# async def play(ctx, url):
#     channel = ctx.author.voice.channel
    
#     if not ctx.voice_client:
#         await channel.connect()
#     elif ctx.voice_client.channel != channel:
#         await ctx.voice_client.move_to(channel)
    
#     with youtube_dl.YoutubeDL(ydl_opts) as ydl:
#         info = ydl.extract_info(url, download=False)
#         url2 = info['formats'][0]['url']
#         title = info['title']
        
#         player = discord.FFmpegPCMAudio(url2, **ffmpeg_options)
#         ctx.voice_client.play(player, after=lambda x=None: check_queue(ctx, ctx.guild.id))
        
#         embed = discord.Embed(
#             title="🎵 Sedang Memutar",
#             description=f"[{title}]({url})",
#             color=discord.Color.green()
#         )
#         await ctx.send(embed=embed)

# @bot.command()
# async def queue(ctx, url):
#     with youtube_dl.YoutubeDL(ydl_opts) as ydl:
#         info = ydl.extract_info(url, download=False)
#         url2 = info['formats'][0]['url']
#         title = info['title']
        
#         player = discord.FFmpegPCMAudio(url2, **ffmpeg_options)
        
#         guild_id = ctx.guild.id
#         if guild_id in queues:
#             queues[guild_id].append(player)
#         else:
#             queues[guild_id] = [player]
        
#         embed = discord.Embed(
#             title="📥 Ditambahkan ke Antrian",
#             description=f"[{title}]({url})",
#             color=discord.Color.blue()
#         )
#         await ctx.send(embed=embed)

# @bot.command()
# async def pause(ctx):
#     ctx.voice_client.pause()
#     await ctx.send("⏸️ Musik dijeda")

# @bot.command()
# async def resume(ctx):
#     ctx.voice_client.resume()
#     await ctx.send("▶️ Musik dilanjutkan")

# @bot.command()
# async def stop(ctx):
#     ctx.voice_client.stop()
#     await ctx.voice_client.disconnect()
#     await ctx.send("⏹️ Musik dihentikan")

# @bot.command()
# async def skip(ctx):
#     ctx.voice_client.stop()
#     await ctx.send("⏭️ Lagu dilewati")
#     check_queue(ctx, ctx.guild.id)

# bot.run(TOKEN)


# main.py
import discord
from discord.ext import commands
import yt_dlp as youtube_dl
import asyncio
import os

# Konfigurasi
TOKEN = 'MTMzODgzNTc2Mzk2OTY1ODkxMw.GeE3VY.L_aWT0vBKPQvT8casBQI89fkRqRBUOXEVTSAIg'  # Ganti dengan token bot Anda
PREFIX = '!'  # Prefix perintah

# Path ke FFmpeg (sesuaikan dengan lokasi Anda)
FFMPEG_PATH = os.path.join(os.getcwd(), 'ffmpeg', 'ffmpeg.exe')

# Inisialisasi bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=PREFIX, intents=intents)

# Konfigurasi untuk yt-dlp
ydl_opts = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'
}

# Konfigurasi FFmpeg
ffmpeg_options = {
    'options': '-vn',
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'executable': FFMPEG_PATH  # Gunakan FFmpeg lokal
}

# Antrian lagu per server
queues = {}

@bot.event
async def on_ready():
    print(f'Bot {bot.user.name} telah online!')
    print(f'FFmpeg path: {FFMPEG_PATH}')
    print(f'FFmpeg exists: {os.path.exists(FFMPEG_PATH)}')

def check_queue(ctx, guild_id):
    if queues.get(guild_id) and len(queues[guild_id]) > 0:
        player = queues[guild_id].pop(0)
        ctx.voice_client.play(player, after=lambda x=None: check_queue(ctx, guild_id))
    else:
        asyncio.run_coroutine_threadsafe(ctx.voice_client.disconnect(), bot.loop)

@bot.command()
async def play(ctx, *, url):
    # Cek apakah user ada di voice channel
    if not ctx.author.voice:
        await ctx.send("🚫 Anda harus berada di voice channel terlebih dahulu!")
        return

    channel = ctx.author.voice.channel
    
    # Cek koneksi bot
    if not ctx.voice_client:
        await channel.connect()
    elif ctx.voice_client.channel != channel:
        await ctx.voice_client.move_to(channel)
    
    # Bersihkan antrian jika bot baru saja connect
    if ctx.guild.id in queues:
        queues[ctx.guild.id] = []
    
    try:
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            # Handle playlist
            if 'entries' in info:
                info = info['entries'][0]
                
            url2 = info['url'] if 'url' in info else info['formats'][0]['url']
            title = info['title']
            
            player = discord.FFmpegPCMAudio(url2, **ffmpeg_options)
            
            # Cek jika sedang memutar
            if ctx.voice_client.is_playing():
                guild_id = ctx.guild.id
                if guild_id not in queues:
                    queues[guild_id] = []
                queues[guild_id].append(player)
                
                embed = discord.Embed(
                    title="📥 Ditambahkan ke Antrian",
                    description=f"[{title}]({url})",
                    color=discord.Color.blue()
                )
                await ctx.send(embed=embed)
            else:
                ctx.voice_client.play(player, after=lambda x=None: check_queue(ctx, ctx.guild.id))
                
                embed = discord.Embed(
                    title="🎵 Sedang Memutar",
                    description=f"[{title}]({url})",
                    color=discord.Color.green()
                )
                await ctx.send(embed=embed)
                
    except Exception as e:
        await ctx.send(f"❌ Error: {str(e)}")

@bot.command()
async def queue(ctx, *, url):
    try:
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            # Handle playlist
            if 'entries' in info:
                info = info['entries'][0]
                
            url2 = info['url'] if 'url' in info else info['formats'][0]['url']
            title = info['title']
            
            player = discord.FFmpegPCMAudio(url2, **ffmpeg_options)
            
            guild_id = ctx.guild.id
            if guild_id in queues:
                queues[guild_id].append(player)
            else:
                queues[guild_id] = [player]
            
            embed = discord.Embed(
                title="📥 Ditambahkan ke Antrian",
                description=f"[{title}]({url})",
                color=discord.Color.blue()
            )
            await ctx.send(embed=embed)
            
    except Exception as e:
        await ctx.send(f"❌ Error: {str(e)}")

@bot.command()
async def pause(ctx):
    if ctx.voice_client.is_playing():
        ctx.voice_client.pause()
        await ctx.send("⏸️ Musik dijeda")
    else:
        await ctx.send("❌ Tidak ada musik yang sedang diputar")

@bot.command()
async def resume(ctx):
    if ctx.voice_client.is_paused():
        ctx.voice_client.resume()
        await ctx.send("▶️ Musik dilanjutkan")
    else:
        await ctx.send("❌ Musik tidak dijeda")

@bot.command()
async def stop(ctx):
    if ctx.voice_client:
        if ctx.guild.id in queues:
            queues[ctx.guild.id] = []
        await ctx.voice_client.disconnect()
        await ctx.send("⏹️ Musik dihentikan dan bot keluar")

@bot.command()
async def skip(ctx):
    if ctx.voice_client.is_playing() or ctx.voice_client.is_paused():
        ctx.voice_client.stop()
        await ctx.send("⏭️ Lagu dilewati")
        check_queue(ctx, ctx.guild.id)
    else:
        await ctx.send("❌ Tidak ada lagu yang diputar")

@bot.command()
async def join(ctx):
    if not ctx.author.voice:
        await ctx.send("🚫 Anda harus berada di voice channel terlebih dahulu!")
        return
        
    channel = ctx.author.voice.channel
    if not ctx.voice_client:
        await channel.connect()
        await ctx.send(f"✅ Bot bergabung ke **{channel.name}**")
    elif ctx.voice_client.channel != channel:
        await ctx.voice_client.move_to(channel)
        await ctx.send(f"✅ Bot pindah ke **{channel.name}**")

@bot.command()
async def leave(ctx):
    if ctx.voice_client:
        if ctx.guild.id in queues:
            queues[ctx.guild.id] = []
        await ctx.voice_client.disconnect()
        await ctx.send("👋 Bot keluar dari voice channel")
    else:
        await ctx.send("❌ Bot tidak berada di voice channel")

bot.run(TOKEN)