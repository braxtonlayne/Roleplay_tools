import discord
from discord.ext import commands

class JobSystem:
    def __init__(self, economy):
        self.economy = economy
        self.bot = economy.bot

    @commands.group(name="job", invoke_without_command=True)
    async def job(self, ctx):
        """Job management commands"""
        await ctx.send("Available commands: create, apply, list, quit")

    @job.command(name="create")
    @commands.has_permissions(administrator=True)
    async def job_create(self, ctx, name: str, salary: float, currency: str, interval: int):
        guild_data = self.economy.get_guild_data(ctx.guild.id)
        if name in guild_data["jobs"]:
            await ctx.send(f"Job {name} already exists.")
            return
        if currency not in guild_data["currencies"]:
            await ctx.send(f"Currency {currency} does not exist.")
            return
        guild_data["jobs"][name] = {
            "salary": salary,
            "currency": currency,
            "interval": interval,
            "employees": []
        }
        await ctx.send(f"Job {name} created with salary {salary} {currency} every {interval} minutes.")

    @job.command(name="apply")
    async def job_apply(self, ctx, name: str):
        guild_data = self.economy.get_guild_data(ctx.guild.id)
        if name not in guild_data["jobs"]:
            await ctx.send(f"Job {name} does not exist.")
            return
        user_id = str(ctx.author.id)
        if user_id in guild_data["jobs"][name]["employees"]:
            await ctx.send("You are already employed in this job.")
            return
        guild_data["jobs"][name]["employees"].append(user_id)
        await ctx.send(f"You have been employed as {name}.")

    @job.command(name="list")
    async def job_list(self, ctx):
        guild_data = self.economy.get_guild_data(ctx.guild.id)
        embed = discord.Embed(title="Available Jobs", color=discord.Color.blue())
        for name, job in guild_data["jobs"].items():
            embed.add_field(
                name=name,
                value=f"Salary: {job['salary']} {job['currency']} every {job['interval']} minutes",
                inline=False
            )
        await ctx.send(embed=embed)

    @job.command(name="quit")
    async def job_quit(self, ctx, name: str):
        guild_data = self.economy.get_guild_data(ctx.guild.id)
        if name not in guild_data["jobs"]:
            await ctx.send(f"Job {name} does not exist.")
            return
        user_id = str(ctx.author.id)
        if user_id not in guild_data["jobs"][name]["employees"]:
            await ctx.send("You are not employed in this job.")
            return
        guild_data["jobs"][name]["employees"].remove(user_id)
        await ctx.send(f"You have quit your job as {name}.")

    async def process_salaries(self):
        for guild in self.bot.guilds:
            guild_data = self.economy.get_guild_data(guild.id)
            for job_name, job_data in guild_data["jobs"].items():
                for employee_id in job_data["employees"]:
                    if employee_id not in guild_data["wallets"]:
                        guild_data["wallets"][employee_id] = {cur: 0 for cur in guild_data["currencies"]}
                    guild_data["wallets"][employee_id][job_data["currency"]] += job_data["salary"]
