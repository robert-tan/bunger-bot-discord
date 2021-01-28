# bot.py
import os
import json
import random
import discord
import asyncio
from discord.enums import Status
from discord.ext import commands
from discord.flags import Intents
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = Intents.all()
client = commands.Bot(command_prefix="!", intents=intents)
data = dict()

SKRIBBL = 'skribbl'
BUNGER_IMAGES = [
    'https://imgur.com/1eItG5Y.gif',
    'https://imgur.com/qNizkLQ.gif',
    'https://imgur.com/wabSxfl.gif',
    'https://imgur.com/wJjuLrW.gif',
    'https://imgur.com/DnVK9nY.gif',
    'https://imgur.com/PuxEZIs.gif',
    'https://imgur.com/nfrg0qX.gif',
    'https://imgur.com/0FOxSGA.gif',
    'https://imgur.com/fU1TDzs.gif',
    'https://tenor.com/view/bugsnax-bunger-bunger-my-beloved-bunger-bugsnax-gif-19836808'
]
DATA_PATH = './data.json'


def get_guild_data(guild):
    if str(guild.id) in data:
        return data[str(guild.id)]
    
    data[guild.id] = {
        SKRIBBL: []
    }
    return data[guild.id]


@client.event
async def on_ready():
    global data
    try:
        with open(DATA_PATH, 'r') as f:
            data = json.load(f)
    except: pass
    print(f'Client {client.user} is ready.')


@client.check
async def globally_block_dms(ctx):
    return ctx.guild is not None


@client.command(name='add-word', brief='Adds a word/phrase to your server\'s custom Skribbl.io word list')
async def add_word(ctx, *args):
    arg = ""
    for word in args:
        arg = arg + word + " "
    arg = arg[:-1]

    print(f'Received !add-word {arg} from {ctx.author.name}')
    skribbl_lst = get_guild_data(ctx.guild)[SKRIBBL]
    skribbl_lst.append(arg)
    serialize_data()
    await ctx.send('"{}" added to the Skribbl.io word list!'.format(arg))


@client.command(name='remove-word', brief='Removes a word/phrase from your server\'s custom Skribbl.io word list')
async def rm_word(ctx, arg):
    print(f'Received !remove-word {arg} from {ctx.author.name}')
    skribbl_lst = get_guild_data(ctx.guild)[SKRIBBL]

    # O(n) but whatever
    if arg not in skribbl_lst:
        await ctx.send('"{}" not in the Skribbl.io word list.'.format(arg))
        return
    skribbl_lst.remove(arg)
    await ctx.send('"{}" removed from the Skribbl.io word list!'.format(arg))


@client.command(name="view-list", brief='View your server\'s custom Skribbl.io word list')
async def view_list(ctx):
    print(f'Received !view-list from {ctx.author.name}')
    skribbl_lst = get_guild_data(ctx.guild)[SKRIBBL]
    if len(skribbl_lst) == 0:
        await ctx.send("There's nothing in the Skribbl.io list. Add one using the `!add-word` command!")
        return

    response = "Your server's Skribbl.io word list is as follows:\n```"
    for word in skribbl_lst:
        response = response + word + ','
    response = response[:-1] + '```\nHave a *BUNGEROUS* skribbl.io gayme'
    await ctx.send(response)
    await bunger(ctx)


@client.command(name="bunger-time", brief='Ping all users with the @bunger role')
async def bunger_time(ctx):
    print(f'Received !bunger-time from {ctx.author.name}')
    users_to_mention = [ 
        user for user in ctx.guild.members 
        if 'bunger' in { role.name.lower() for role in user.roles } 
            and not user.bot
            and user.status != Status.offline
    ]

    for user in users_to_mention:
        print(f'Sending a mention to {user.name}')
        await ctx.send(user.mention + ' IT\'S BUNGER TIME!\n' + random_bunger_image())


@client.command(name='spam-ping', brief='Spam the mentioned user')
async def spam_ping(ctx, arg: discord.Member):
    TIMES_PING = 10
    for i in range(TIMES_PING):
        asyncio.ensure_future(
            send_after_delay(i, ctx, 
                f'{arg.mention} It\'s time to BUNGER! {random_bunger_image()}'
            )
        )


@client.command(brief='RANDOM BUNGER GIF')
async def bunger(ctx):
    await ctx.send(random_bunger_image())


async def send_after_delay(delay, ctx, message):
    await asyncio.sleep(delay)
    await ctx.send(message)


def serialize_data():
    with open(DATA_PATH, 'w') as f:
        f.write(json.dumps(data))


def random_bunger_image():
    return BUNGER_IMAGES[random.randint(0, len(BUNGER_IMAGES) - 1)]


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_forever(client.run(TOKEN))
