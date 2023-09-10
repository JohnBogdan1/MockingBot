import os

import discord
from discord.ext import tasks, commands
from discord.ext.commands import Bot
from discord import Status

from dotenv import load_dotenv
from tag import Tag, SendGreetingTag, ActivityTag
from translate_api import MyTranslator
from weather_api import MyWeather
from youtube_api import YTDLSource

from utils import get_statuses, set_interval, is_command, message_has, create_embed, remove_file, get_rand_status, \
    message_is_command, get_guild_by_name, get_member_by_tag, get_guild_by_context, get_tag, get_custom_emoji, \
    get_text_as_emoji_text, scrap_image_urls, find_image, many_emj, get_channel_by_name, get_members, \
    get_member_by_tag2, get_sfx_list, process_sfx_title, get_last_other_msg, get_random_angry, get_last_msg

import random
import time
import asyncio
import unidecode
import emoji  # https://www.webfx.com/tools/emoji-cheat-sheet/
from collections import deque

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
OWM_KEY = os.getenv('OWM_KEY')

intents = discord.Intents.all()
# client = discord.Client(intents=intents)
client = Bot('%', intents=intents, status=discord.Status.offline, case_insensitive=True)

my_translator = MyTranslator()
my_weather = MyWeather(OWM_KEY, my_translator)
emojis = None
ENDLINE = "\n.\n.\n.\n"
sfx_path = "sfx/"
mock_path = "mock/"
HISTORY_LIMIT = 25
# Initializing a queue
q = deque()
player_queue = {}


class StatusCog(commands.Cog):
    def __init__(self):
        self.printer.start()

    def cog_unload(self):
        self.printer.cancel()

    @tasks.loop(seconds=30.0)
    async def printer(self):
        activity_, status_ = get_rand_status()
        await client.change_presence(activity=discord.Activity(type=activity_[0], name=activity_[1]), status=status_)


@client.event
async def on_ready():
    global emojis
    print(f'[{client.user}] has connected to Discord!\n')

    print(
        f'[{client.user}] is connected to the following guilds:'
    )
    print('#####################################################')
    for guild in client.guilds:
        print(
            f'{guild.name}(id: {guild.id})'
        )
    print('#####################################################')

    if not emojis:
        emojis = {e.name: str(e) for e in client.emojis}

    # init stuff
    StatusCog()
    # await client.change_presence(status=discord.Status.offline)


@client.event
async def on_member_join(member):
    await member.create_dm()
    await member.dm_channel.send(
        f'Bine ai venit, {member.name}! 😇 Rău ai nimerit! 😈'
    )


@client.event
async def on_member_remove(member):
    await member.create_dm()
    await member.dm_channel.send(
        f'Să nu te mai intorci!'
    )


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    """
    if message_has(message.content, 'hello'):
        await message.channel.send('Nu dau bani cu împrumut! 😝')
    """
    if message_has(message.content, 'cine e forta') or message_has(message.content, 'forta'):
        await message.channel.send('Salam e forta!')

    await client.process_commands(message)


@client.command()
async def hello(ctx):
    await ctx.channel.send('Nu dau bani cu împrumut! 😝')


@client.command()
async def bye(ctx):
    await ctx.channel.send('Mă duc să mor puțin... BRB')


@client.command()
async def play(ctx):
    await ctx.channel.send('Nu mă joc cu nubiii!!! 😎')



@client.command()
async def supremus(ctx):
    member = get_member_by_tag2(client, Tag.SUPREMUS.value)
    embed = create_embed(
        'https://media.sketchfab.com/models/263640bbe33e46febaf00d80ed3438ec/thumbnails/6fad7468a2cf449fae7003c658829788/d3d84fa90ac04e248b0dbd3ff12df660.jpeg',
        title='Suprema')
    await ctx.channel.send(f'Am găsit-o pe prietena lui Supremus... 💘 {member.mention}', embed=embed)


@client.command(help="Shows weather in a city.", usage="'city[, country]'")
async def weather(ctx, *, city: str = None):
    await ctx.channel.send(my_weather.compose_weather_status(city))


@client.command()
async def leu(ctx):
    msg_arr = (await ctx.channel.history(limit=HISTORY_LIMIT).flatten())
    msg = get_last_other_msg(ctx, msg_arr)
    embed = create_embed('https://upload.wikimedia.org/wikipedia/commons/b/b4/1_leu._Romania%2C_2005_a.jpg')
    await ctx.channel.send(
        f'{msg.author.mention}{ctx.author.name}, iti da ', embed=embed
    )


@client.command(usage="'mesaj'", help="Says something using tts.")
async def striga(ctx, *, mesaj):
    await ctx.send(
        mesaj, tts=True
    )


@striga.error
async def info_error(ctx, error):
    await ctx.send("Nu vreau si nu imi place!")


@client.command(name="ping", help="Shows latency")
async def ping(ctx):
    await ctx.send("My ping is {} ms ".format(round(client.latency * 1000)))


@client.command()
async def summon(ctx):
    connected = ctx.author.voice
    vc = ctx.voice_client
    if connected:
        if not vc:
            await connected.channel.connect()
        else:
            if not vc.is_connected():
                await connected.channel.connect()
            else:
                channel_name = connected.channel.name
                if vc.channel.name != channel_name:
                    await vc.disconnect()
                    await connected.channel.connect()
    else:
        await ctx.send("Intra pe canal!")


@client.command()
async def leave(ctx):
    connected = ctx.author.voice
    guild, guild_name = get_guild_by_context(ctx)
    if connected:
        channel_name = connected.channel.name
        for vc in client.voice_clients:
            if vc.guild.name == guild_name and vc.is_connected() and vc.channel.name == channel_name:
                await vc.disconnect()
    else:
        await ctx.send("Nu sunt pe canal!")


@client.command()
async def cloak(ctx):
    guild, guild_name = get_guild_by_context(ctx)
    member = guild.get_member(client.user.id)

    if member.status == discord.Status.online:
        await client.change_presence(status=discord.Status.offline)
        client.remove_cog(StatusCog.__name__)


@client.command()
async def uncloak(ctx):
    guild, guild_name = get_guild_by_context(ctx)
    member = guild.get_member(client.user.id)

    if member.status == discord.Status.offline:
        await client.change_presence(status=discord.Status.online)
        client.add_cog(StatusCog())


@client.command(help="Put the bot play something from YouTube.")
async def sing(ctx, *, search):
    global q
    global player_queue
    user = ctx.message.author
    server = ctx.message.guild
    connected = ctx.author.voice
    channel_name = connected.channel.name
    vc = ctx.voice_client

    if connected:
        if not vc:
            await connected.channel.connect()
        else:
            if not vc.is_connected():
                await connected.channel.connect()
            else:
                if vc.channel.name != channel_name:
                    await vc.disconnect()
                    await connected.channel.connect()
        async with ctx.typing():
            player, path = await YTDLSource.from_url(ctx, search, loop=client.loop)
            # player = await YTDLSource.create_source(ctx, search, loop=client.loop)
            if ctx.voice_client.is_playing():
                await stop(ctx)

            ctx.voice_client.play(player, after=lambda e: print('Player error: %s' % e) if e else remove_file(path))

        await ctx.send(f'De la {user.mention} cu dedicație pentru toată lumea: 🎶 {player.title} 🎶')
    else:
        await ctx.channel.send(f'{user.mention} is not in a voice channel.')


@sing.error
async def info_error(ctx, error):
    await ctx.send("Nu sunt pe sistem!")


@client.command(help="Pause the song.")
async def pause(ctx):
    vc = ctx.voice_client

    if vc.is_playing():
        vc.pause()
        await ctx.channel.send(f'"{vc.source.title}" is paused now.')
    else:
        await ctx.channel.send(f'Nothing to pause!')


@client.command(help="Resume the song.")
async def resume(ctx):
    vc = ctx.voice_client

    if vc.is_paused():
        vc.resume()
        await ctx.channel.send(f'"{vc.source.title}" is resuming now...')
    else:
        await ctx.channel.send(f'Nothing to resume!')


@client.command(help="Stop the song.")
async def stop(ctx):
    vc = ctx.voice_client

    if vc.is_playing() or vc.is_paused():
        title = vc.source.title
        vc.stop()
        await ctx.channel.send(f'"{title}" is stopped now.')
    else:
        await ctx.channel.send(f'Nothing to stop!')


@client.command(help="Play a random sound, if the number parameter is missing.\n\nThe sfx sounds are following:\n - "
                     + "\n - ".join(get_sfx_list(sfx_path)), usage="'1 | 2 | 3 ...'")
async def sfx(ctx, *, idx=None):
    global sfx_path
    user = ctx.message.author
    connected = ctx.author.voice
    if connected:
        await summon(ctx)
        guild = ctx.guild
        voice_client: discord.VoiceClient = discord.utils.get(client.voice_clients, guild=guild)
        sfx_arr = os.listdir(sfx_path)
        # sfx_arr.sort()
        parsed_idx = (str(idx).split(",") if len(str(idx)) > 1 else str(idx)) if idx is not None else str(
            random.randint(1, len(sfx_arr)))
        parsed_idx = list(parsed_idx)
        idx = int(parsed_idx[0]) - 1
        sfx_idx = sfx_arr[idx]
        sfx_path_idx = sfx_path + sfx_idx
        audio_source = discord.FFmpegPCMAudio(sfx_path_idx)
        sfx_title = "[" + str(idx + 1) + "]" + process_sfx_title(sfx_idx)
        if voice_client.is_playing():
            await stop(ctx)
        voice_client.play(audio_source, after=None)
        voice_client.source.title = sfx_title
        await ctx.send(f'🎶 {sfx_title} 🎶')
        # await sfx(ctx, idx=",".join(parsed_idx[1:]))
    else:
        await ctx.channel.send(f'{user.mention} is not in a voice channel.')


@client.command(help="")
async def cheer(ctx):
    global mock_path
    user = ctx.message.author
    connected = ctx.author.voice
    if connected:
        await summon(ctx)
        guild = ctx.guild
        voice_client: discord.VoiceClient = discord.utils.get(client.voice_clients, guild=guild)
        fname = "Merry Christmas.mp3"
        fpath = mock_path + fname
        audio_source = discord.FFmpegPCMAudio(fpath)
        sfx_title = process_sfx_title(fname)
        if voice_client.is_playing():
            await stop(ctx)
        voice_client.play(audio_source, after=None)
        voice_client.source.title = sfx_title
        # await ctx.send(f'🎶 {sfx_title} 🎶')
        # await sfx(ctx, idx=",".join(parsed_idx[1:]))
    else:
        await ctx.channel.send(f'{user.mention} is not in a voice channel.')


@client.command(help="")
async def hell(ctx):
    global mock_path
    user = ctx.message.author
    connected = ctx.author.voice
    if connected:
        await summon(ctx)
        guild = ctx.guild
        voice_client: discord.VoiceClient = discord.utils.get(client.voice_clients, guild=guild)
        fname = "Hell is Repetition.mp3"
        fpath = mock_path + fname
        audio_source = discord.FFmpegPCMAudio(fpath)
        sfx_title = process_sfx_title(fname)
        if voice_client.is_playing():
            await stop(ctx)
        voice_client.play(audio_source, after=None)
        voice_client.source.title = sfx_title
        # await ctx.send(f'🎶 {sfx_title} 🎶')
        # await sfx(ctx, idx=",".join(parsed_idx[1:]))
    else:
        await ctx.channel.send(f'{user.mention} is not in a voice channel.')


@client.command(help="")
async def sin(ctx):
    global mock_path
    user = ctx.message.author
    connected = ctx.author.voice
    if connected:
        await summon(ctx)
        guild = ctx.guild
        voice_client: discord.VoiceClient = discord.utils.get(client.voice_clients, guild=guild)
        fname = "Born in Sin.mp3"
        fpath = mock_path + fname
        audio_source = discord.FFmpegPCMAudio(fpath)
        sfx_title = process_sfx_title(fname)
        if voice_client.is_playing():
            await stop(ctx)
        voice_client.play(audio_source, after=None)
        voice_client.source.title = sfx_title
        # await ctx.send(f'🎶 {sfx_title} 🎶')
        # await sfx(ctx, idx=",".join(parsed_idx[1:]))
    else:
        await ctx.channel.send(f'{user.mention} is not in a voice channel.')


@client.command(help="")
async def lust(ctx):
    global mock_path
    user = ctx.message.author
    connected = ctx.author.voice
    if connected:
        await summon(ctx)
        guild = ctx.guild
        voice_client: discord.VoiceClient = discord.utils.get(client.voice_clients, guild=guild)
        fname = "Born in Lust.mp3"
        fpath = mock_path + fname
        audio_source = discord.FFmpegPCMAudio(fpath)
        sfx_title = process_sfx_title(fname)
        if voice_client.is_playing():
            await stop(ctx)
        voice_client.play(audio_source, after=None)
        voice_client.source.title = sfx_title
        # await ctx.send(f'🎶 {sfx_title} 🎶')
        # await sfx(ctx, idx=",".join(parsed_idx[1:]))
    else:
        await ctx.channel.send(f'{user.mention} is not in a voice channel.')


@client.command(help="")
async def ignorant(ctx):
    global mock_path
    user = ctx.message.author
    connected = ctx.author.voice
    if connected:
        await summon(ctx)
        guild = ctx.guild
        voice_client: discord.VoiceClient = discord.utils.get(client.voice_clients, guild=guild)
        fname = "You dont like knowing do you.mp3"
        fpath = mock_path + fname
        audio_source = discord.FFmpegPCMAudio(fpath)
        sfx_title = process_sfx_title(fname)
        if voice_client.is_playing():
            await stop(ctx)
        voice_client.play(audio_source, after=None)
        voice_client.source.title = sfx_title
        # await ctx.send(f'🎶 {sfx_title} 🎶')
        # await sfx(ctx, idx=",".join(parsed_idx[1:]))
    else:
        await ctx.channel.send(f'{user.mention} is not in a voice channel.')


@sfx.error
async def info_error(ctx, error):
    await ctx.send("Nu sunt pe sistem!")


@client.event
async def on_member_update(before, after):
    channel = discord.utils.get(after.guild.channels, name='a-quiet-place')
    guild = get_guild_by_name(client, GUILD)
    members = [get_member_by_tag(guild, tag.value) for tag in SendGreetingTag]
    greeting_tag_list = [tag.value for tag in SendGreetingTag]
    activity_tag_list = [tag.value for tag in ActivityTag]

    if after.guild == guild and 1 == 2:
        if before.status == Status.offline and after.status == Status.online:
            print("{} has gone {}.".format(after.name, after.status))
            """if get_tag(after) in greeting_tag_list:
                await after.create_dm()
                await after.dm_channel.send(
                    f'Te-a chemat cineva?! 😠'
                )"""
            pass
        elif before.status == Status.online and after.status == Status.offline:
            print("{} has gone {}.".format(after.name, after.status))

        if after.activity is not None and after.activity.type == discord.ActivityType.playing:
            if "league of legends" in str(after.activity.name).lower() and get_tag(after) in activity_tag_list:
                await after.create_dm()
                await after.dm_channel.send(
                    f'Iar te joci LoL? Mai bine șterge-l...'
                )
            if "warframe" in str(after.activity.name).lower() and get_tag(after) == Tag.SUPREMUS.value:
                await after.create_dm()
                await after.dm_channel.send(
                    f'O să te joci Warframe și după ce mori, nu?'
                )
            if "league of legends" in str(after.activity.name).lower() and get_tag(after) == Tag.JOHN.value:
                """await after.create_dm()
                await after.dm_channel.send(
                    f'/tts Iar te joci LoL? Mai bine șterge-l...'
                )"""
                if channel:
                    await channel.send(f'{after.mention} is playing {after.activity.name} again.....')
        elif before.activity is not None and after.activity is None:
            if get_tag(after) in activity_tag_list:
                await after.create_dm()
                await after.dm_channel.send(
                    f'Ce faci? Nu ți-e rușine să nu te mai joci?!'
                )

    if before.status == Status.offline and after.status == Status.online and get_tag(after) == Tag.SUPREMUS.value and 1==2:
        embed = discord.Embed(title="WARFRAME QUEEN", color=0x00ff00)
        file = discord.File("files/memes/wf_queen.png", filename="wf_queen.png")
        embed.set_image(url="attachment://wf_queen.png")
        await channel.send(file=file, embed=embed)


@client.event
async def on_voice_state_update(member, before, after):
    voice_client = None
    if before.channel is None and after.channel is not None and not member.bot and 1 == 2:
        channel = after.channel

        for vc in client.voice_clients:
            if vc.guild.name == GUILD and vc.is_connected() and vc.channel.name == channel.name:
                voice_client = vc
                break

        if not voice_client:
            voice_client = await channel.connect()
        if voice_client and not voice_client.is_connected:
            voice_client.connect()

        fname = "Born in Sin.mp3"
        fpath = mock_path + fname
        audio_source = discord.FFmpegPCMAudio(fpath)
        sfx_title = process_sfx_title(fname)

        # prev_url = voice_client.source.data['url']
        # prev_source = discord.FFmpegPCMAudio(prev_url)
        # print(prev_source)
        if voice_client.is_playing():
            voice_client.stop()

        await asyncio.sleep(1)

        voice_client.play(audio_source, after=None)
        voice_client.source.title = sfx_title

        """await asyncio.sleep(5)
        if voice_client.is_playing():
            voice_client.stop()
            voice_client.play(prev_source, after=None)
        else:
            voice_client.play(prev_source, after=None)"""


@client.command(aliases=['s'])
async def say(ctx, *, msg):
    await ctx.channel.send(msg)


@client.command(aliases=['v'])
async def volume(ctx, vol):
    guild = ctx.guild
    new_volume = float(vol.strip())
    voice_client: discord.VoiceClient = discord.utils.get(client.voice_clients, guild=guild)
    if 0 <= new_volume <= 200:
        new_volume = new_volume / 100
        if voice_client.is_playing():
            voice_client.source.volume = new_volume
    else:
        await ctx.channel.send('Please enter a volume between 0 and 200!')


spam_loop = None


@client.command(help="Spams every x seconds.", usage="'x' 'mesaj'")
async def repeta(ctx, delay: float, *, msg, count=None):
    global spam_loop

    @tasks.loop(seconds=delay, count=count)
    async def spam_loop(q):
        await ctx.send(q)

    spam_loop.start(msg.format(ctx.message))
    # await ctx.send("Successfully activated SpamMode")
    if count is None:
        emj = get_custom_emoji(ctx, emojis, ":AYAYA:")
        await ctx.send(emoji.emojize("Foloseste **%opreste** ca sa opresti spam-ul " + emj + ENDLINE))
    else:
        emj = get_custom_emoji(ctx, emojis, ":epicface:")
        await ctx.send(
            emoji.emojize(ENDLINE + "Ah, am gresit. Acum incearca **%infrana**. Sigur e asta... ") + emj + ENDLINE)


@client.command(help="May stop the spam.")
async def opreste(ctx):
    global spam_loop
    # spam_loop.cancel()
    # await ctx.send("Successfully deactivated SpamMode")
    if spam_loop:
        await ctx.send(emoji.emojize(ENDLINE + "Cred ca de fapt e **%imobileste** :worried:" + ENDLINE))
    else:
        await ctx.send("Spam-ul nu e in viata!")


@client.command(help="Actually may stop the spam.")
async def infrana(ctx):
    global spam_loop
    if spam_loop:
        i = random.uniform(0, 1)
        if i > 0.8:
            spam_loop.cancel()
        else:
            emj = get_custom_emoji(ctx, emojis, ":haHAA:")
            await ctx.send(emoji.emojize(ENDLINE + "De fapt, e **%ingheata** 100%!!! " + emj + ENDLINE))
    else:
        await ctx.send("Spam-ul nu e in viata!")


# <:emoji_name:emoji_id>
# <:letroll:>
@client.command(help="Stops one spam.")
async def imobileste(ctx):
    global spam_loop
    if spam_loop:
        spam_loop.cancel()
        emj = get_custom_emoji(ctx, emojis, ":letroll:")
        await repeta(ctx, delay=0.5,
                     msg=(get_text_as_emoji_text("BAZZZNIGGA") + emj.format(ctx.message) * 3), count=100)
    else:
        await ctx.send("Spam-ul nu e in viata!")


@client.command(help="Stops Time and saves Space.")
async def ingheata(ctx):
    global spam_loop
    if spam_loop:
        spam_loop.cancel()
        emj = get_custom_emoji(ctx, emojis, ":Pog3D:")
        await ctx.send(emoji.emojize("Aia e! " + emj))
    else:
        await ctx.send("Inca nu e prea cald aici...")


@client.command(help="Test img search", hidden=True)
async def testimg(ctx):
    html = find_image("scooby-doo")
    # print(html)
    url = scrap_image_urls(html)
    print(url)


@client.command(help="Search the best image based on query.", usage="'query'")
async def fi(ctx, *, query: str):
    html = find_image(query)
    try:
        url = scrap_image_urls(html, query=query)[0]
    except:
        emj = get_custom_emoji(ctx, emojis, ":kappa:")
        await ctx.channel.send(
            "Nu am gasit nimic in Matrix..." + emj
        )
        return
    embed = create_embed(url, ctx=ctx, title=query)
    await ctx.channel.send(
        f'', embed=embed
    )


@client.command(help="Search a random image based on query.", usage="'query'")
async def rfi(ctx, *, query: str):
    html = find_image(query)
    url = scrap_image_urls(html, rng=True, query=query)[0]
    embed = create_embed(url, ctx=ctx, title=query)
    await ctx.channel.send(
        f'', embed=embed
    )


@client.command(aliases=['ms'])
async def mock_supremus(ctx):
    member = get_member_by_tag2(client, Tag.SUPREMUS.value)
    emj1 = get_custom_emoji(ctx, emojis, ":letroll:")
    emj2 = get_custom_emoji(ctx, emojis, ":wf:")
    await ctx.channel.send(
        many_emj(emj1, cnt=13) + "\n" + emj1 + f" {member.mention} e #1 in " + emj2 + " " * 2 + emj1 + "\n" + many_emj(
            emj1,
            cnt=13))


@client.command(aliases=['mb'])
async def mock_boby(ctx):
    member = get_member_by_tag2(client, Tag.BOBY.value)
    emj = get_custom_emoji(ctx, emojis, ":letroll:")
    await ctx.channel.send(
        many_emj(emj, cnt=11) + "\n" + emj + f"{member.mention} e shamanul la manele" + emj + "\n" + many_emj(emj,
                                                                                                              cnt=11))


@client.command(aliases=['mj'])
async def mock_john(ctx):
    member = get_member_by_tag2(client, Tag.JOHN.value)
    emj = get_custom_emoji(ctx, emojis, ":letroll:")
    await ctx.channel.send(
        many_emj(emj, cnt=15) + "\n" + emj + f"{member.mention}, cand mai iesi din casa?  " + emj + "\n" + many_emj(emj,
                                                                                                                    cnt=15))


@client.command(aliases=['ws'])
async def wake_supremus(ctx):
    member = get_member_by_tag2(client, Tag.SUPREMUS.value)
    emj = get_random_angry(ctx, emojis)
    await ctx.channel.send(f"{member.mention}, trezeste-te! " + emj)


@client.command(aliases=['wb'])
async def wake_boby(ctx):
    member = get_member_by_tag2(client, Tag.BOBY.value)
    emj = get_random_angry(ctx, emojis)
    await ctx.channel.send(f"{member.mention}, trezeste-te! " + emj)


@client.command(aliases=['wj'])
async def wake_john(ctx):
    member = get_member_by_tag2(client, Tag.JOHN.value)
    emj = get_random_angry(ctx, emojis)
    await ctx.channel.send(f"{member.mention}, trezeste-te! " + emj)


@client.command(aliases=['wsf'])
async def wake_supremus_forever(ctx):
    member = get_member_by_tag2(client, Tag.SUPREMUS.value)
    emj = get_random_angry(ctx, emojis)
    await repeta(ctx, delay=1,
                 msg=(f"{member.mention}, trezeste-te! " + emj), count=None)


@client.command(help="?", hidden=True)
async def testque(ctx):
    channel = get_channel_by_name(ctx, name="general")
    msg = (await channel.history(limit=1).flatten())[0]
    emj = get_custom_emoji(ctx, emojis, ":letroll:")
    msg = f"{msg.author.mention} Que? :letroll:".format(ctx.message).replace(':letroll:', emj)
    await ctx.send(msg)


@client.command(help="?")
async def que(ctx):
    # channel = get_channel_by_name(ctx, name="general")
    msg_arr = (await ctx.channel.history(limit=HISTORY_LIMIT).flatten())
    msg = get_last_other_msg(ctx, msg_arr)
    emj = get_custom_emoji(ctx, emojis, ":letroll:")
    msg = f"{msg.author.mention} Que? :letroll:".format(ctx.message).replace(':letroll:', emj)
    await ctx.send(msg)


@client.command(help="?")
async def mad(ctx):
    # channel = get_channel_by_name(ctx, name="general")
    msg_arr = (await ctx.channel.history(limit=HISTORY_LIMIT).flatten())
    msg = get_last_other_msg(ctx, msg_arr)
    emj = get_custom_emoji(ctx, emojis, ":letroll:")
    msg = f"{msg.author.mention} Mad? :letroll:".format(ctx.message).replace(':letroll:', emj)
    await ctx.send(msg)


@client.command(help="quote #1", aliases=['q1'])
async def quote1(ctx):
    emj = get_custom_emoji(ctx, emojis, ":Pog3D:")
    await ctx.channel.send("*I'm PRO, the NOOB transformed.* " + emj)


@client.command(help="quote #2", aliases=['q2'])
async def quote2(ctx):
    emj = get_custom_emoji(ctx, emojis, ":Pog3D:")
    await ctx.channel.send("*This is the Internet. You have no power here.* ")


@client.command(help="quote #3", aliases=['q3'])
async def quote3(ctx):
    emj = get_custom_emoji(ctx, emojis, ":Pog3D:")
    await ctx.channel.send("*A world without Light would be dark, but a world without L is just a word.* ")


@client.command(help="quote #4", aliases=['pain'])
async def quote4(ctx):
    emj = get_custom_emoji(ctx, emojis, ":Pog3D:")
    await ctx.channel.send("*A lesson without pain is meaningless. That's because no one can gain without sacrificing something. But by enduring that pain and overcoming it, he shall obtain a powerful, unmatched heart. A fullmetal heart.* ")


@client.command(aliases=['as'])
async def ask_supremus(ctx):
    member = get_member_by_tag2(client, Tag.SUPREMUS.value)
    await ctx.channel.send(f"{member.mention}, plæy or gæy?")


@client.command(aliases=['ab'])
async def ask_boby(ctx):
    member = get_member_by_tag2(client, Tag.BOBY.value)
    await ctx.channel.send(f"{member.mention}, plæy or gæy?")


@client.command(aliases=['aj'])
async def ask_john(ctx):
    member = get_member_by_tag2(client, Tag.JOHN.value)
    await ctx.channel.send(f"{member.mention}, plæy or gæy?")


@client.command(aliases=['p'])
async def pley(ctx):
    await ctx.channel.send(f"plæy or gæy?")


@client.command()
async def outplay(ctx):
    embed = create_embed('https://c.tenor.com/4V2-UCVfPbIAAAAC/jinx-jinx-arcane.gif')
    await ctx.channel.send(f"Wanna join me, come and play.\nBut I might shoot you, in your face.")
    await asyncio.sleep(1)
    await ctx.channel.send(embed=embed)


@client.command(aliases=['r'])
async def react(ctx, emo: str = None, idx: int = None):
    msg_arr = (await ctx.channel.history(limit=HISTORY_LIMIT).flatten())
    msg = get_last_msg(ctx, msg_arr, idx=idx)
    if emo is None:
        emj_arr = list(emojis.values())
        emj = emj_arr[random.randint(0, len(emj_arr) - 1)]
    else:
        emj = emo
    await msg.add_reaction(emoji=emj)


@client.command(aliases=['jd'])
async def just_dance(ctx):
    embed = discord.Embed(color=0x00ff00)
    file = discord.File("files/memes/just_dance_1.png", filename="just_dance_1.png")
    embed.set_image(url="attachment://just_dance_1.png")
    await ctx.send(file=file, embed=embed)


@client.command(aliases=['jds'])
async def just_dance_swag(ctx):
    embed = discord.Embed(color=0x00ff00)
    file = discord.File("files/memes/just_dance_2.png", filename="just_dance_2.png")
    embed.set_image(url="attachment://just_dance_2.png")
    await ctx.send(file=file, embed=embed)


@client.command(aliases=['js'])
async def just_swag(ctx):
    embed = discord.Embed(color=0x00ff00)
    file = discord.File("files/memes/just_swag.jpg", filename="just_swag.jpg")
    embed.set_image(url="attachment://just_swag.jpg")
    await ctx.send(file=file, embed=embed)


@client.command(aliases=['wq'])
async def wf_queen(ctx):
    embed = discord.Embed(title="WARFRAME QUEEN", color=0x00ff00)
    file = discord.File("files/memes/wf_queen.png", filename="wf_queen.png")
    embed.set_image(url="attachment://wf_queen.png")
    await ctx.send(file=file, embed=embed)


@client.command(aliases=['cr'], usage="'0 | 1 | 2 | 3 ...'")
async def chiharau(ctx, id=None):
    filelist = os.listdir("files/memes/")
    filelist = [x for x in filelist if "chiharau" in x.lower()]
    files_len = len(filelist)
    if id is None:
        idx = random.randint(0, files_len - 1)
    else:
        if 0 > id >= files_len:
            await ctx.channel.send('Please enter an id between 0 and ' + str(files_len))
            return
        idx = id
    filename = filelist[idx]
    embed = discord.Embed(title="CHIHARAU", color=0x00ff00)
    file = discord.File("files/memes/" + filename, filename=filename)
    embed.set_image(url="attachment://" + filename)
    await ctx.send(file=file, embed=embed)


@client.command(help="After C gives 'Ceen' to Boby", aliases=['bb'])
async def bobybal(ctx):
    embed = discord.Embed(title="Dr. Boby", color=0x00ff00)
    file = discord.File("files/memes/bobybal.png", filename="bobybal.png")
    embed.set_image(url="attachment://bobybal.png")
    await ctx.send(file=file, embed=embed)


@client.command(help="Choose your sin", aliases=['chs'])
async def choose(ctx):
    embed = discord.Embed(title="Choose", color=0x00ff00)
    file = discord.File("files/memes/choose.png", filename="choose.png")
    embed.set_image(url="attachment://choose.png")
    await ctx.send(file=file, embed=embed)


@client.command(help="The only constant in life is pain and suffering...", aliases=['ps'])
async def pure_suffering(ctx):
    embed = discord.Embed(title="Pure suffering", color=0x00ff00)
    file = discord.File("files/memes/pure suffering.png", filename="pure suffering.png")
    embed.set_image(url="attachment://pure suffering.png")
    await ctx.send(file=file, embed=embed)


@client.command()
async def smile(ctx):
    # https://tenor.com/view/exodiac-yu-gi-oh-smile-anime-gif-17543633
    embed = create_embed("https://c.tenor.com/IhxY0X4JsrkAAAAd/exodiac-yu-gi-oh.gif")
    await ctx.send(embed=embed)


@client.command()
async def obliterated(ctx):
    # https://tenor.com/view/aaaaaaaaa-gif-18979345
    embed = create_embed("https://c.tenor.com/GtCu1jCJS0YAAAAC/aaaaaaaaa.gif")
    await ctx.send(embed=embed)


@client.command()
async def obliterate(ctx):
    # https://tenor.com/view/exodia-yu-gi-oh-anime-summon-gif-17959838
    embed = create_embed("https://c.tenor.com/KH5Q_JwkzEwAAAAd/exodia-yu-gi-oh.gif")
    await ctx.send(embed=embed)


# https://www.sfgate.com/market/article/best-crypto-exchanges-16315558.php


########################################################################################################################


@client.event
async def on_command_error(ctx, exception):
    if "spam_loop" not in str(exception):
        await ctx.send(exception)
    with open('err.log', 'a') as f:
        f.write(f'Unhandled message: {exception}\n')


@client.event
async def on_error(event, *args, **kwargs):
    with open('err.log', 'a') as f:
        f.write(f'Unhandled message: {args[0]}\n')


# RUN THE MASTER OF MOCKING
client.run(TOKEN)
