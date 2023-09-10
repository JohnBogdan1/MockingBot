import os
import discord
import threading
import random
import bs4
import json
from urllib import request as req
from urllib import parse
from tag import Tag
import re
from difflib import SequenceMatcher


def set_interval(func, sec):
    def func_wrapper():
        set_interval(func, sec)
        func()

    t = threading.Timer(sec, func_wrapper)
    t.start()
    return t


def message_has_cmd(msg, *cmds):
    msg = str(msg).lower()
    for cmd in cmds:
        if msg == ('%' + cmd) or ('%' + cmd) in msg:
            return True

    return False


def message_has(msg, *seq):
    msg = str(msg).lower()
    s = str(seq[0])
    if s in msg:
        return True

    return False


def message_is_command(msg, cmd):
    return msg == cmd


def get_statuses():
    activity_arr = [(discord.ActivityType.listening, 'the silence'),
                    (discord.ActivityType.playing, 'with your feelings'),
                    (discord.ActivityType.streaming, 'https://www.twitch.tv/supremusul'),
                    (discord.ActivityType.watching, 'you cry'), (discord.ActivityType.competing, 'competitions'),
                    (discord.ActivityType.custom, 'dusting the dust'),
                    (discord.ActivityType.listening, '%help')]

    status_arr = [discord.Status.online, discord.Status.idle, discord.Status.dnd, discord.Status.offline
                  ]

    return activity_arr, status_arr


def get_rand_status():
    activities, statuses = get_statuses()
    activity = activities[random.randint(0, len(activities) - 1)]
    status = statuses[random.randint(0, len(statuses) - 1)]

    return activity, status


def get_tag(username):
    name, tag = str(username).split("#")

    if tag == '0':
        return name

    return tag


def create_embed(imageURL, ctx=None, title=''):
    embed = discord.Embed(title=title, description="")
    embed.set_image(url=imageURL)
    if ctx is not None:
        embed.set_footer(icon_url=ctx.author.avatar_url, text=f"Requested by {ctx.author.name}")
    # embed.add_field(name="", value="", inline=False)

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


# https://stackoverflow.com/questions/51982806/how-do-i-make-my-discord-py-bot-use-custom-emoji
def get_custom_emoji(ctx, emojis, custom_emoji):
    return emojis[custom_emoji.replace(":", "")]


def get_text_as_emoji_text(text):
    start = ":regional_indicator_"
    end = ":"
    emoji_text = ""
    for s in text:
        emoji_text += start + s.lower() + end

    return emoji_text


def many_emj(emj, cnt=10):
    return str(emj * cnt)


exception_urls = [
    '.cdninstagram.com',
    'www.instagram.com',
    'www.facebook.com',
    'lookaside.fbsbx.com',
]


def is_exception_url(str):
    return any([x in str for x in exception_urls])


def img_alt_matches_query(alt, query):
    tokens = re.split(r'[\',;!-:]', query)

    for t in tokens:
        if t in alt:
            return True

    return False


def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()


def scrap_image_urls(html, rng=False, query=None, start=0, stop=1):
    soup = bs4.BeautifulSoup(html, 'html.parser', from_encoding='utf8')
    soup = soup.find_all('img')
    # print(soup)
    image_urls = [x for x in soup if x.has_attr('alt') and similar(x['alt'], query) > 0.25]
    image_urls = [x['src'] for x in image_urls if x.has_attr('src')] + [x['data-src'] for x in soup if
                                                                        x.has_attr('data-src')]
    image_urls = [x for x in image_urls if ('http' in x or 'https' in x or 'www' in x) and 'icon' not in x]
    print(image_urls)
    if rng:
        image_urls = [url for url in image_urls if not is_exception_url(url)]
        image_urls = [image_urls[random.randint(0, len(image_urls) - 1)]]
    else:
        image_urls = [url for url in image_urls if not is_exception_url(url)][start:stop]

    return image_urls


def find_image(keyword):
    urlKeyword = parse.quote(keyword)
    url = 'https://www.google.com/search?hl=jp&q=' + urlKeyword + '&btnG=Google+Search&tbs=0&safe=off&tbm=isch'
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:95.0) Gecko/20100101 Firefox/95.0", }
    request = req.Request(url=url, headers=headers)
    page = req.urlopen(request)
    html = page.read()
    page.close()

    return html


def get_channel_by_name(ctx, name="general"):
    channel = discord.utils.get(ctx.guild.channels, name=name)
    channel_id = channel.id

    return channel


def get_members(bot):
    for guild in bot.guilds:
        for member in guild.members:
            print(member)


def get_member_by_tag2(bot, tag):
    for guild in bot.guilds:
        for member in guild.members:
            tag_var = get_tag(member)
            if tag_var == tag:
                return member


def process_sfx_title(sfx):
    return sfx.replace(".mp3", "").replace(".wav", "").replace("[www.fisierulmeu.ro]", "").strip()


def get_sfx_list(sfx_path):
    l = os.listdir(sfx_path)
    fl = []
    for i, sfx in enumerate(l):
        fl.append("[" + str(i + 1) + "] " + process_sfx_title(sfx))
    return fl


def get_last_msg(ctx, msg_arr, idx=None):
    if idx is None:
        idx = 1
    return msg_arr[idx]


def get_last_other_msg(ctx, msg_arr):
    msg = None
    for elem in msg_arr:
        elem_tag = get_tag(elem.author)
        my_tag = get_tag(ctx.author)
        if my_tag != elem_tag and elem_tag != Tag.BOT.value:
            msg = elem
            break

    if msg is None:
        msg = msg_arr[1]
    return msg


def get_random_angry(ctx, emojis):
    emj_arr = [(':angry_' + str(i + 1) + ":") for i in range(7)]
    emj = get_custom_emoji(ctx, emojis, emj_arr[random.randint(0, len(emj_arr) - 1)])
    return emj


def get_queue(q):
    s = "The songs queue is:\n"
    for i, x in enumerate(q):
        s += "[" + str(i + 1) + "] " + x + "\n"

    return s
