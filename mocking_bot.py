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
    message_is_command, get_guild_by_name, get_member_by_tag, get_guild_by_context, get_tag

import random
import time
import asyncio
import unidecode

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
OWM_KEY = os.getenv('OWM_KEY')

intents = discord.Intents.all()
# client = discord.Client(intents=intents)
client = Bot('%', intents=intents)

my_translator = MyTranslator()
my_weather = MyWeather(OWM_KEY, my_translator)


class StatusCog(commands.Cog):
    def __init__(self):
        self.printer.start()

    def cog_unload(self):
        self.printer.cancel()

    @tasks.loop(seconds=30.0)
    async def printer(self):
        status = get_rand_status()
        await client.change_presence(activity=discord.Activity(type=status[0], name=status[1]))


@client.event
async def on_ready():
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

    await client.change_presence(status=discord.Status.offline)

    # init stuff
    # StatusCog()


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

    await client.process_commands(message)


@client.command()
async def hello(ctx):
    await ctx.channel.send('Nu dau bani cu împrumut! 😝')


@client.command()
async def bye(ctx):
    await ctx.channel.send('Mă duc să mor puțin... BRB')


@client.command()
async def play(ctx):
    await ctx.channel.send('Nu mă joc cu nubii!!! 😎')


@client.command()
async def supremus(ctx):
    embed = create_embed(
        'https://media.sketchfab.com/models/263640bbe33e46febaf00d80ed3438ec/thumbnails/6fad7468a2cf449fae7003c658829788/d3d84fa90ac04e248b0dbd3ff12df660.jpeg')
    await ctx.channel.send('Am găsit-o pe prietena lui Supremus... 💘', embed=embed)


@client.command()
async def weather(ctx):
    await ctx.channel.send(my_weather.compose_weather_status())


@client.command()
async def leu(ctx):
    embed = create_embed('https://upload.wikimedia.org/wikipedia/commons/b/b4/1_leu._Romania%2C_2005_a.jpg')
    await ctx.channel.send(
        f'{ctx.author.name}, ai un leu?', embed=embed
    )


@client.command()
async def summon(ctx):
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


@client.command()
async def leave(ctx):
    connected = ctx.author.voice
    guild, guild_name = get_guild_by_context(ctx)
    if connected:
        channel_name = connected.channel.name
        for vc in client.voice_clients:
            if vc.guild.name == guild_name and vc.is_connected() and vc.channel.name == channel_name:
                await vc.disconnect()


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


@client.command()
async def sing(ctx, *, search):
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
            ctx.voice_client.play(player, after=lambda e: print('Player error: %s' % e) if e else remove_file(path))
        await ctx.send(f'De la {user.mention} cu dedicație pentru toată lumea: 🎶 {player.title} 🎶')
    else:
        await ctx.channel.send(f'{user.mention} is not in a channel.')


@client.command()
async def pause(ctx):
    vc = ctx.voice_client

    if vc.is_playing():
        vc.pause()
        await ctx.channel.send(f'"{vc.source.title}" is paused now.')


@client.command()
async def resume(ctx):
    vc = ctx.voice_client

    if vc.is_paused():
        vc.resume()
        await ctx.channel.send(f'"{vc.source.title}" is resuming now...')


@client.command()
async def stop(ctx):
    vc = ctx.voice_client

    if vc.is_playing():
        title = vc.source.title
        vc.stop()
        await ctx.channel.send(f'"{title}" is stopped now.')


@client.event
async def on_error(event, *args, **kwargs):
    with open('err.log', 'a') as f:
        if event == 'on_message':
            f.write(f'Unhandled message: {args[0]}\n')
        else:
            raise


@client.event
async def on_member_update(before, after):
    channel = discord.utils.get(after.guild.channels, name='general')
    guild = get_guild_by_name(client, GUILD)
    members = [get_member_by_tag(guild, tag.value) for tag in SendGreetingTag]
    greeting_tag_list = [tag.value for tag in SendGreetingTag]
    activity_tag_list = [tag.value for tag in ActivityTag]

    if after.guild == guild:
        if before.status == Status.offline and after.status == Status.online:
            print("{} has gone {}.".format(after.name, after.status))
            if get_tag(after) in greeting_tag_list:
                await after.create_dm()
                await after.dm_channel.send(
                    f'Te-a chemat cineva?! 😠'
                )

        if after.activity is not None and after.activity.type == discord.ActivityType.playing:
            if "league of legends" in str(after.activity.name).lower() and get_tag(after) in activity_tag_list:
                await after.create_dm()
                await after.dm_channel.send(
                    f'Iar te joci LoL? Mai bine șterge-l...'
                )
            if "warframe" in str(after.activity.name).lower() and get_tag(after) == Tag.ANDREI.value:
                await after.create_dm()
                await after.dm_channel.send(
                    f'O să te joci Warframe și după ce mori, nu?'
                )
            if "league of legends" in str(after.activity.name).lower() and get_tag(after) == Tag.ME.value:
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


# RUN THE MASTER OF MOCKING
client.run(TOKEN)
