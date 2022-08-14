from discord.ext import commands
import time
from dotenv import load_dotenv
import os
import scraping as scp
bot = commands.Bot(command_prefix='/')

@bot.command(name="hello")
async def hello(ctx):
    await ctx.send(f"hello {ctx.message.author.name} !")

@bot.command(name="stop-ark-server")
async def hello(ctx):
    await ctx.send(f"wait a moment...")
    time.sleep(5)
    await ctx.send(f"ark server at 153.156.106.10 is stopped!")

@bot.command(name="start-ark-server")
async def hello(ctx):
    await ctx.send(f"wait a moment...")
    time.sleep(11)
    await ctx.send(f"ark server at 153.156.106.10 is started!")

@bot.command(name="derby")
async def hello(ctx, pred_id):
    if not (pred_id.isdecimal() and len(pred_id) == 4):
        await ctx.send(f"Please sure your race ID")
        await ctx.send(f"you must input https://race.netkeiba.com/special/index.html?id= [ here value!!! ]")
        return
    await ctx.send(f"start scraping {pred_id}!")
    try: 
        scp.scraping(pred_id)
    except:
        await ctx.send(f"Sorry! Error occured in scrape")
        return
    await ctx.send(f"end scraping!")
    await ctx.send(f"start pred!")
    try:
        result = scp.prediction(pred_id)
    except:
        await ctx.send(f"Sorry! Error occured in pred")
        return
    await ctx.send(f"{result}")

load_dotenv()
bot.run(os.environ.get('DISCORD_TOKEN'))