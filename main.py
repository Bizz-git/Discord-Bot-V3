# cercare "da sistemare" per i problemi attuali
# creato da Bizz-git
# data 27/08/2024
# verisone 3.0
# sistema di logging e version logging

import discord
from discord import client
from discord.ext import commands
from discord.voice_client import VoiceClient
from dhooks import Webhook, File
#from googlesearch import search
import requests
from bs4 import BeautifulSoup
from discord.utils import get
#from youtube_dl import YoutubeDL
import yt_dlp as youtube_dl
from playsound import playsound
from gtts import gTTS
import asyncio
import logging

# custom function -> utils.py
from utils import ConfigManager, os, random
from discord_queue import MusicQueue


# Configura il logging
logging.basicConfig(level=logging.INFO)

intents = discord.Intents.default()
intents.message_content = True

client = commands.Bot(intents=intents, command_prefix='.')

config_manager = ConfigManager('./config.json')
d_queue = MusicQueue()

# hook
hook_video = Webhook("https://discord.com/api/webhooks/797622097249697813/Zj-DHlXo2prxSsdgzttfJpJBbMc22A22JM1mM0s3S6fRB_iNx1Ri0c6DXf6LmagpxhGC")

# Custom functions
async def set_default():
    try:
        # inizialiazza la queue
        for k, v in d_queue.get_queue():
            logging.warning(f'file canellato **{k}°: {v}**')
            os.remove(v)

        d_queue.clear()
        d_queue.set_playing(False)
        return True
    except Exception as err:
        logging.error(str(err))
        return str(err)

# non funzionante (vallo a capire...)
async def audio_optimizer(target_volume, voice_source):
    # Incrementa gradualmente il volume
    steps = 10
    step_delay = 0.1  # Secondi tra i passi
    volume = 0.0  # Volume iniziale
    step_size = (target_volume - volume) / steps

    # Imposta inizialmente il volume a 0
    voice_source.volume = volume
    await asyncio.sleep(1)  # Attendi un momento prima di iniziare l'incremento

    for _ in range(steps):
        volume += step_size
        voice_source.volume = max(0.0, min(1.0, volume))
        await asyncio.sleep(step_delay)

    # Assicurati di impostare il volume finale esattamente
    voice_source.volume = target_volume

############################################################################
# @events

@client.event
async def on_ready():
    config_manager.read_from_json()
    global prefix
    prefix = config_manager.data["prefix"]
    description = config_manager.data["description"]
    print(f"Bot pronto\nPrefisso: {prefix}")

    _ = await set_default()

    #activity = discord.Game(name=":)")
    #await client.change_presence(status=discord.Status.idle, activity=activity)
    await client.change_presence(activity=discord.Activity(
        type=discord.ActivityType.watching, name=description))



'''
# implementare log dei vari messaggi per evitare scam, o problemi con alcune persone
@client.event
async def on_message(message):
    # Da implementare
    return
'''


# resetta i valori del volume (a quanto pare non serve per la musica)
@client.event
async def on_voice_state_update(member, before, after):
    if member == client.user:
        if before.channel is not None and after.channel is None:
            """ config_manager.write_to_json("music", 1.0)
            config_manager.write_to_json("sound", 1.0)
            config_manager.write_to_json("voice", 1.0) """
            logging.info(f"Bot disconnesso dal canale vocale.")



@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        embed = discord.Embed(
        title="Parametro mancante!",
        description=f"Usa il comando '**{prefix}bot**' per maggiori informazioni",
        color=discord.Color.red())

        await ctx.send(embed=embed)


############################################################################
# @commands
@client.command()
async def ping(ctx):
    await ctx.send(f'Ping: {round(client.latency * 1000)}ms')



@client.command()
async def bot(ctx):
    embed = discord.Embed(
        title="Comandi",
        description='Ecco la lista dei comandi che posso eseguire:',
        color=discord.Color.random())

    embed.set_author(
        name="YR' BOSS",
        url="https://www.youtube.com/channel/UCdzRr1DVLdAiyqL6K63DppQ",
        icon_url=ctx.author.avatar.url)

    embed.set_thumbnail(url=client.user.avatar.url)

    embed.add_field(name="bot",
                    value='Mostra tutti i comandi che posso eseguire',
                    inline=True)
    embed.add_field(name="ping",
                    value='Mostra la mia latenza in /ms',
                    inline=True)
    embed.add_field(name="sondaggio",
                    value='Posso creare un sondaggio',
                    inline=True)
    embed.add_field(name="sconti",
                    value='Ti aggiorno con gli sconti su Amazon di oggi',
                    inline=True)
    embed.add_field(name="spam",
                    value='Mando constantemente dei messaggi che vuoi',
                    inline=True)
    embed.add_field(name="hub",
                    value='Se ti piace hub, adorerai hub premium',
                    inline=True)
    embed.add_field(name="play",
                    value='Avvio le tue canzoni preferite',
                    inline=True)
    embed.add_field(name="sound",
                    value='Riproduco dei suoni che vuoi',
                    inline=True)
    embed.add_field(name="game",
                    value='Giochiamo al gioco dell\'impiccato',
                    inline=True)

    embed.set_footer(
        text=f"Ricordati di usare il prefisso prima di ogni comando\nes. {prefix}nome_comando")

    await ctx.send(embed=embed)



@client.command()
async def ciao(ctx):
    generated = config_manager.generate_random_string(24)
    logging.info(f'Stringa generata: {generated}')
    await ctx.send('Ciao!')



# da sistemare, la ricerca in realtà non produce i link corretti
@client.command()
async def hub(ctx, number, *, ctg):
    num = int(number)
    base_url = "https://it.pornhub.com/video/search?search="
    search_url = base_url + ctg.replace(' ', '+')
    logging.info(search_url)
    response = requests.get(search_url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Trova tutti i tag <li> con la classe "pcVideoListItem"
        video_items = soup.find_all('li', class_='pcVideoListItem', limit=num)
        
        video_links = []
        for item in video_items:
            link_tag = item.find('a', class_='js-linkVideoThumb')
            if link_tag:
                video_url = "https://it.pornhub.com" + link_tag['href']
                title = link_tag.get('data-title', 'No title')
                video_links.append((title, video_url))
        
        for title, link in video_links:
            print(f"Titolo: {title}")
            print(f"Link: {link}\n")
            hook_video.send(f"Titolo {title} - link {link}") 
    else:
        print(f"Errore durante la richiesta: {response.status_code}")
        return []



@client.command()
async def clear(ctx, amount):
    amount_int = int(amount)
    await ctx.channel.purge(limit=amount_int + 1)



@client.command(pass_context=True, aliases=['j'])
async def join(ctx):
    channel = ctx.message.author.voice.channel
    voice = get(client.voice_clients, guild=ctx.guild)

    if voice and voice.is_connected():
        if voice.channel != channel:
            await voice.move_to(channel)
        else:
            await ctx.send(f'Sono già nel tuo canale vocale {voice.channel}')
    else:
        voice = await channel.connect()

    await ctx.send(f"Entrato nel canale vocale **{channel}**")



@client.command(pass_context=True, aliases=['lv'])
async def leave(ctx):
    channel = ctx.message.author.voice.channel
    voice = get(client.voice_clients, guild=ctx.guild)
    
    if voice and voice.is_connected():
        await voice.disconnect()
        await ctx.send(f"Disconnesso da **{channel}**") 
    else:
        await ctx.send("Non connesso al canale vocale")



@client.command(pass_context=True, aliases=['sound'])
async def playsound(ctx, name: str):
    c_path = config_manager.data["sound_path"]
    c_file_path = c_path + name + ".mp3"

    if c_file_path:
        try:
            voice = get(client.voice_clients, guild=ctx.guild)
            voice.play(discord.FFmpegPCMAudio(c_file_path),
                    after=lambda e: print("Sound Fatto!"))
            voice.source = discord.PCMVolumeTransformer(voice.source)
            print('sound ' + str(config_manager.data["sound"]))
            
            #voice.source.volume = int(config_manager.data["sound"])
            voice.source.volume = 1.0
            #await audio_optimizer(int(config_manager.data["sound"]), voice.source)

            await ctx.send(f"Sound: {name}.mp3 in riproduzione\n")
        except Exception as err:
            await ctx.send(f"Errore audio: {err}")
    else:
        await ctx.send(f"Sound non trovato: {c_file_path}\n")

@playsound.error
async def playsound_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        exists = config_manager.list_file_path(config_manager.data["sound_path"])
        await ctx.send(f"I file presenti sono: {exists}") if isinstance(exists, list) else await ctx.send(f"ERRORE PERMESSO: {exists}")
    elif isinstance(error, commands.CommandInvokeError):
        await ctx.send("Errore: C'è stato un problema con l'esecuzione del comando.")
    else:
        await ctx.send(f"Si è verificato un errore durante l'esecuzione del comando play: {str(error)}")




@client.command(pass_context=True, aliases=['t'])
async def talk(ctx, *, msg):
    file_path = config_manager.data["talk_path"]
    logging.info(file_path)

    # da sistemare, usare le funzioni nel file utils.py per ottimizzare i processi
    # al momento non funzionano e non ritornano neanche un errore 
    """ 
    bool, status = config_manager.write_to_txt(file_path, msg)
    logging.warning(status)

    # def read_from_txt(c_path: str, gTTS: function, lang: str, slow_mode: bool) -> list:
    bool, status = config_manager.read_from_txt(file_path, gTTS, "it", False)
    logging.warning(status) 
    """

    try:
        with open("speech/speech.txt", "w") as fh:
            fh.write(str(msg))
        if not fh.closed:
            fh.close()
    except FileNotFoundError:
        print('impossibile creare il file, controllare i permessi') 

    try:
        with open("speech/speech.txt", "r") as fh:
            myText = fh.read().replace("\n", " ")
            language = "it"
            output = gTTS(text=myText, lang=language, tld='it', slow=False)
        if not fh.closed:
            fh.close()
        output.save("speech/speech.mp3")
    except FileNotFoundError:
        print('impossibile trovare il file, controllare i permessi') 
   

    voice = get(client.voice_clients, guild=ctx.guild)
    voice.play(discord.FFmpegPCMAudio("speech/speech.mp3"),
               after=lambda e: print("Testo letto!"))
    voice.source = discord.PCMVolumeTransformer(voice.source)
    #voice.source.volume = int(config_manager.data["voice"])
    voice.source.volume = 1.0



# da sistemare, l'audio non si sente se impostato a < 1.0 durante la prima esecuzione (probabilmente problema di PCMVolumeTransformer)
# a quanto pare funziona con la musica, provare a capire il motivo
@client.command(pass_context=True, aliases=['vol'])
async def volume(ctx, type: str, vol: int) -> str:
    try:
        vol = vol / 100.0
        if type == 'voice':
            config_manager.write_to_json("voice", vol)
        elif type == 'music':
            config_manager.write_to_json("music", vol)
        elif type == 'sound':
            config_manager.write_to_json("sound", vol)
        else:
            await ctx.send('Errore: tipo di volume non trovato')

        voice = get(client.voice_clients, guild=ctx.guild)
        if voice and voice.source:
            if isinstance(voice.source, discord.PCMVolumeTransformer):
                voice.source.volume = max(0.0, min(2.0, vol))
            else:
                voice.source = discord.PCMVolumeTransformer(voice.source)
                voice.source.volume = max(0.0, min(2.0, vol))

            # Update manuale, non serve
            #config_manager.print_data()
            #config_manager.update_values()
            #config_manager.print_data()

            await ctx.send('valore impostato a **' + str(voice.source.volume * 100) + '%**')
        else:
            await ctx.send('nessun audio trovato')
    except Exception as e:
        print('Errore: ' + str(e))



@client.command(pass_context=True, aliases=['pl'])
async def play(ctx, curl: str):
    # check if file already exists
    c_path = config_manager.data["music_path"]
    c_file_path = f"{c_path}{config_manager.generate_random_string(12)}"

    """     
    song_there = os.path.isfile(c_file_path)

    try:
        if song_there:
            os.remove(c_file_path)
    except PermissionError:
        await ctx.send("ERRORE: Ancora in play")
        return 
    """

    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': c_file_path
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(curl, download=True)

    d_queue.add(c_file_path, info)

    if not d_queue.get_playing():
        await play_next(ctx)

    """ try:
        logging.info(f'File path: {c_file_path}')

        voice = get(client.voice_clients, guild=ctx.guild)
        # per audio streaming utilizzare FFMPEG_OPTIONS
        # voice.play(discord.FFmpegPCMAudio(c_file_path, **FFMPEG_OPTIONS),
        voice.play(discord.FFmpegPCMAudio(c_file_path),
                after=lambda e: print("Musica in riproduzione!"))
        voice.source = discord.PCMVolumeTransformer(voice.source)
        logging.info(f'Sto riproducendo: **{info['title']}** a volume {str(config_manager.data["music"])}')

        voice.source.volume = 1.0

        await ctx.channel.send(embed=embed)
    except Exception as err:
        logging.error(f'Errore musica: {err}')
        await ctx.send(f"Errore musica: {err}") """

async def play_next(ctx):
    next_song = d_queue.pop()

    if next_song is None:
        d_queue.set_playing(False)
        return

    d_queue.set_playing(True)
    c_file_path, info = next_song
    c_file_path = c_file_path + ".mp3"

    logging.info(f'debugghino: {c_file_path}')
    voice = get(client.voice_clients, guild=ctx.guild)

    if not voice.is_playing():
        voice.play(discord.FFmpegPCMAudio(c_file_path), after=lambda e: client.loop.create_task(play_next(ctx)))
        voice.source = discord.PCMVolumeTransformer(voice.source)
        voice.source.volume = config_manager.data["music"]

        duration_seconds = info.get('duration', 0)
        minutes = duration_seconds // 60
        seconds = duration_seconds % 60
        embed = discord.Embed(
            title="In riproduzione:",
            description=f"**Title:** {info.get('title', 'Unknown')}\n"
                        f"**Creator:** {info.get('uploader', 'Unknown')}\n"
                        f"**Duration:** {minutes}:{seconds:02d} minutes\n"
                        f"**Views:** {info.get('view_count', 'Unknown')}\n"
                        f"**Volume:** {str(voice.source.volume*100)}%\n",
            color=discord.Color.blue()
        )
        if info.get('thumbnail'):
            embed.set_image(url=info['thumbnail'])

        await ctx.send(embed=embed)

        # da sistemare, errore durante la rimozione: File ancora in uso
        # non viene nemmeno stampato il path del file
        logging.info(f'path file: {c_file_path}')
        os.remove(c_file_path)



@client.command()
async def skip(ctx):
    voice = get(client.voice_clients, guild=ctx.guild)
    if voice.is_playing():
        voice.stop()
        await play_next(ctx)
    else:
        await ctx.send("Nessuna musica in riproduzione da saltare.")



@client.command()
async def stop(ctx):
    voice = get(client.voice_clients, guild=ctx.guild)
    if voice.is_playing():
        voice.stop()
        for k, v in d_queue.get_queue():
            logging.warning(f'file canellato **{k}°: {v}**')
            os.remove(v)

        d_queue.clear()
        d_queue.set_playing(False)
        await ctx.send("Riproduzione fermata e queue svuotata.")
    else:
        await ctx.send("Nessuna musica in riproduzione da fermare.")



@client.command()
async def queue(ctx):
    if d_queue.is_empty():
        embed = discord.Embed(
            title="Queue Vuota",
            description="Non ci sono brani in attesa.",
            color=discord.Color.red()
        )
    else:
        queue_list = "\n".join([f"{i+1}. {song[1]['title']}" for i, song in enumerate(d_queue.get_queue())])
        
        logging.info(f'queue list {queue_list}')
        
        embed = discord.Embed(
            title="Queue Attuale:",
            description=queue_list,
            color=discord.Color.blue()
        )

    await ctx.send(embed=embed)


def set_embed(author_name: str, author_url: str, author_icon: str, title: str, description: str, color: str, footer: str, thumbnail: str, word_field: dict, lifes_field: dict):
    embed = discord.Embed(
        title=title,
        description=description,
        color=color)

    embed.set_author(
        name=author_name,
        url=author_url,
        icon_url=author_icon)

    embed.set_thumbnail(url=thumbnail)

    _ = word_field.get("set", True)
    if _:
        name = word_field.get("name", "Parola segreta")
        value = word_field.get("value", "Unknown")
        inline = word_field.get("inline", True)

        embed.add_field(name=name,
            value=value,
            inline=inline)
        
    _ = lifes_field.get("set", True)
    if _:
        name = lifes_field.get("name", "Tentativi rimasti")
        value = lifes_field.get("value", "Unknown")
        inline = lifes_field.get("inline", True)

        embed.add_field(name=name,
            value=value,
            inline=inline)

    embed.set_footer(
        text=footer)

    return embed


@client.command(pass_context=True)
async def game(ctx, *, msg: str):
    file_path = config_manager.data["games_path"]
    logging.info(file_path)
    game_file_path = file_path + "game.txt"
    logging.info(game_file_path)

    secret_word_list = [
        "Luca", "Gino", "Don Troiette", "104", "Gorgonzola", "Mimmo",
        "Spaghetti", "Phasmophobia", "Porta"
    ]
    hang1 = "|-|\n |===\n |   O\n |      \n |      \n | \n===\n"
    hang2 = "|-|\n |===\n |   O\n |   |  \n |      \n | \n===\n"
    hang3 = "|-|\n |===\n |   O\n |  /|  \n |      \n | \n===\n"
    hang4 = "|-|\n |===\n |   O\n |  /|\\\n |      \n | \n===\n"
    hang5 = "|-|\n |===\n |   O\n |  /|\\\n |  /   \n | \n===\n"
    hang6 = "|-|\n |===\n |   O\n |  /|\\\n |  / \\\n | \n===\n"

    hang = hang1

    wrong_guess = "5"
    x = msg
    if x == "new":
        hang = hang1

        secret_word = random.choice(secret_word_list)
        secret_word = secret_word.lower()
        secret = "#" * len(secret_word)
    
        try:
            with open(game_file_path, "w") as fh:
                fh.write(
                    str(secret_word) + "\n" + wrong_guess + "\n" +
                    str(secret) + "\n")
            if not fh.closed:
                fh.close()
        except FileNotFoundError:
            with open(game_file_path, "x") as fh:
                fh.write(
                    str(secret_word) + "\n" + wrong_guess + "\n" +
                    str(secret) + "\n")
            if not fh.closed:
                fh.close()
        embed = set_embed(None, None, client.user.avatar.url, "Impiccato", hang, discord.Color.blurple(), f"Nuova partita, usa {prefix}game seguito da una lettera per iniziare a giocare", client.user.avatar.url, {"do_add": True, "name": "Parola segreta", "value": secret, "inline": False}, {"do_add": True, "name": "Tentativi rimasti", "value": f"**{str(wrong_guess)}**", "inline": False})
        await ctx.send(embed=embed)
    else:
        ex = 0

        try:
            with open(game_file_path, "r") as fh:
                secret_word = fh.readline()
                wrong_guess = fh.readline()
                secret = fh.readline()
            if not fh.closed:
                fh.close()
        except FileNotFoundError:
            await ctx.send(f'Nessuna partita esistente, creane una con **{prefix}game new**')
            ex = 1
        if ex == 0 and wrong_guess[0] > "0":

            if len(x) > 1:
                print(x + ' ' + secret_word)
                if x == secret_word:
                    secret = x
                    print(x + ' ' + secret_word + ' ' + secret + ' Hai Vinto')

            if x in secret_word:
                win = 0
                
                new_secret_word = ""
                for i, c in enumerate(secret_word):
                    if c == x:
                        new_secret_word += c
                    else:
                        new_secret_word += secret[i]

                secret = new_secret_word
                await ctx.send(f"**{x}** è in secret word!")
                embed = set_embed(None, None, client.user.avatar.url, "Impiccato", hang, discord.Color.blurple(), f"Nuova partita, usa {prefix}game seguito da una lettera per iniziare a giocare", client.user.avatar.url, {"do_add": True, "name": "Parola segreta", "value": secret, "inline": True}, {"do_add": True, "name": "Tentativi rimasti", "value": f"**{str(wrong_guess)}**", "inline": False})
                await ctx.send(embed=embed)

                if secret == secret_word:
                    await ctx.send("Hai vinto!\nLa parola era " + secret_word)
                    win = 1

                if win == 1:
                    wrong_guess = "0"

                with open(game_file_path, "w") as fh:
                    fh.write(str(secret_word) + wrong_guess + str(secret))
                if not fh.closed:
                    fh.close()
            else:
                w = (ord(wrong_guess[0]) - 48)
                w -= 1
                if w == 4:
                    hang = hang2
                if w == 3:
                    hang = hang3
                if w == 2:
                    hang = hang4
                if w == 1:
                    hang = hang5
                wrong_guess = chr(w + 48)
                await ctx.send(f"**{x}** non è in secret word!")
                embed = set_embed(None, None, client.user.avatar.url, "Impiccato", hang, discord.Color.blurple(), f"Nuova partita, usa {prefix}game seguito da una lettera per iniziare a giocare", client.user.avatar.url, {"do_add": True, "name": "Parola segreta", "value": secret, "inline": True}, {"do_add": True, "name": "Tentativi rimasti", "value": f"**{str(wrong_guess)}**", "inline": False})
                await ctx.send(embed=embed)
                if w == 0:
                    await ctx.send(hang6)
                    await ctx.send("Hai perso")

                with open(game_file_path, "w") as fh:
                    fh.write(
                        str(secret_word) + wrong_guess + "\n" + str(secret))
                if not fh.closed:
                    fh.close()

        else:
            if wrong_guess[0] == "0":
                await ctx.send(f'La partita e finita, creane una nuova con **{prefix}game new**')


###########################################################################
# @management
client.run(TOKEN)
