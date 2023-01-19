import ccxt
import pandas as pd
import ta
from ta.trend import EMAIndicator, SMAIndicator
from pandas_ta import overlap
from datetime import datetime
import discord
from discord import channel
from discord.ext import commands
from keys import api_key, secret

#exchange information
exchange = ccxt.binance({
    "apiKey": api_key,
    "secret": secret#,
    #"options": {"defaultType": "future"}
})

#defining global variables to be compared and used in the bot
currentTrend = ""
Timeframe = ""
#WaveTrend Indicator
def WaveTrend(coin_pair, Timeframe):
    #Gets ohlcv data 
    global currentTrend
    markets = exchange.load_markets()
    bars = exchange.fetch_ohlcv(coin_pair.upper(), timeframe=Timeframe, limit=50)
    #puts data into a dataframe to be used later on
    df = pd.DataFrame(bars, columns=["Timestamps", "Open", "High", "Low", "Close", "Volume"])
    #calculates indicator numbers
    df["hlc3"] = overlap.hlc3(df["High"], df["Low"], df["Close"])
    esa = EMAIndicator(df["hlc3"], window=10)
    df["ESA"] = esa.ema_indicator()
    d = EMAIndicator(abs(df["hlc3"]-df["ESA"]), window=10)
    df["d"] = d.ema_indicator()
    df["ci"] = (df["hlc3"]-df["ESA"])/(0.015*df["d"])
    tci = EMAIndicator(df["ci"], window=21)
    df["tci"] = tci.ema_indicator()
    wt1 = df["tci"]
    wt2 = SMAIndicator(wt1, window=4)
    df["wt2"] = wt2.sma_indicator()

    if df["tci"].iloc[-1] > df["wt2"].iloc[-1] and currentTrend != "Bullish":
        print(str(datetime.now())+" Current Trend is Bullish")
        currentTrend = "Bullish"
    elif df["tci"].iloc[-1] < df["wt2"].iloc[-1] and currentTrend != "Bearish":
        print(str(datetime.now())+" Current Trend is Bearish")
        currentTrend = "Bearish"
    else:
        pass

    #print(df)
    #print(currentTrend)

         
#Put your discord token here
discord_token = ""
bot = commands.Bot(command_prefix='!')

#log in
@bot.event
async def on_ready():
    print("We have logged in as {0.user}".format(bot))

#performs the function every 60 seconds to check for trend change
@bot.command()
async def trend(ctx, ticker, timeframe):
    #print(ticker)
    #print(timeframe)
    #channel = bot.get_channel(channel_id) 
    WaveTrend(coin_pair=ticker, Timeframe=timeframe.lower())
    if currentTrend == "Bullish":
        #await channel.send("Current Trend is: "+currentTrend)
        embed=discord.Embed(title="{ticker} ({TF})".format(ticker = ticker.upper(), TF=timeframe), color=0x37b350)
        embed.set_author(name="TrendBot V2", icon_url="https://media.discordapp.net/attachments/816703768090509312/849286582489448458/bell.png")
        embed.set_thumbnail(url="https://media.discordapp.net/attachments/816703768090509312/849284839696760877/crop.png?width=380&height=676")
        embed.add_field(name="Current Trend", value="Bullish", inline=False)
        embed.set_footer(text="Bot is currently in development!\nBy Fast#0531")
        await ctx.send(embed=embed)
    elif currentTrend == "Bearish":
        embed=discord.Embed(title="{ticker} ({TF})".format(ticker = ticker.upper(), TF=timeframe), color=0xe32b2b)
        embed.set_author(name="TrendBot V2", icon_url="https://media.discordapp.net/attachments/816703768090509312/849286582489448458/bell.png")
        embed.set_thumbnail(url="https://media.discordapp.net/attachments/816703768090509312/849284839696760877/crop.png?width=380&height=676")
        embed.add_field(name="Current Trend", value="Bearish", inline=False)
        embed.set_footer(text="Bot is currently in development!\nBy Fast#0531")
        await ctx.send(embed=embed)

bot.run(discord_token)