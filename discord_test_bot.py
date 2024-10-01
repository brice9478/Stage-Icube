import discord
from discord.ext import commands

intents = discord.Intents.all()
client = commands.Bot(command_prefix = '!', intents=intents)

@client.event
async def on_ready():
    print("XxxxxxxxxxxxX \\\nX I'm ready X  >----{Let's go!}-\nXxxxxxxxxxxxX /")
    channel = client.get_channel(1280872988446822484)
    await channel.send("I- init~#/tiATi- #i_ng p- pro- ogRrr#am...")

@client.command()
async def hello(ctx):
    await ctx.send("Hel-llo/#~lo, I- I'm the te- test## Bo-T")

@client.command()
async def bye(ctx):
    await ctx.send("E- endi'#$dIng p- pro- ogr#@rrrrr#am_")
    exit(0)

client.run('MTI4MDg4MDUyNjc0MzU2ODUwNw.G-zERY.k2w73zaZvY-D5ETsBQtZtbZSAae262q_uCt2x4')
