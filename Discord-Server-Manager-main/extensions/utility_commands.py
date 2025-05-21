import discord
from discord.ext import commands

class UtilityCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='ping', help='Checks the bot\'s latency')
    async def ping(self, ctx):
        latency = round(self.bot.latency * 1000)
        await ctx.send(f'Pong! Latency: {latency}ms')

    @commands.command(name='echo', help='Repeats the user\'s message')
    async def echo(self, ctx, *, message):
        await ctx.send(message)

async def setup(bot):
    await bot.add_cog(UtilityCommands(bot))
