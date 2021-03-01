import os
import discord
import threading
import random


def set_interval(func, sec):
    def func_wrapper():
        set_interval(func, sec)
        func()

    t = threading.Timer(sec, func_wrapper)
    t.start()
    return t


def message_has(msg, *cmds):
    msg = str(msg).lower()
    for cmd in cmds:
        if msg == ('%' + cmd) or ('%' + cmd) in msg:
            return True

    return False


def message_is_command(msg, cmd):
    return msg == cmd


def get_statuses():
    status_arr = [(discord.ActivityType.listening, 'the silence'), (discord.ActivityType.playing, 'with your feelings'),
                  (discord.ActivityType.streaming, 'https://www.twitch.tv/supremusul'),
                  (discord.ActivityType.watching, 'you cry'),
                  (discord.ActivityType.listening, '%help')]

    return status_arr


def get_rand_status():
    statuses = get_statuses()
    status = statuses[random.randint(0, len(statuses) - 1)]

    return status


def get_tag(username):
    name, tag = str(username).split("#")

    return tag


def create_embed(imageURL):
    embed = discord.Embed()
    embed.set_image(url=imageURL)

    return embed


def get_member_by_tag(guild, tag):
    members = guild.members

    for member in members:
        tag_var = get_tag(member)
        if tag_var == tag:
            return member


def get_guild_by_name(client, name):
    main_guild = None
    for guild in client.guilds:
        if guild.name == name:
            main_guild = guild

    return main_guild


def get_guild_by_context(ctx):
    return ctx.guild, ctx.guild.name


def is_command(msg):
    return msg.startswith("%")


def remove_file(path):
    if os.path.exists(path):
        os.remove(path)
    else:
        print("The file does not exist")
