

import discord
from discord.ext import commands
import os

intents = discord.Intents.default()
intents.typing = False
intents.presences = False
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)


@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')

@bot.command(name='create_roles', help='Creates roles based on the provided text file. Format: Role Name,color,permission1,...')
async def create_roles(ctx):
    if not ctx.message.author.guild_permissions.manage_roles:
        await ctx.send("You do not have permission to use this command.")
        return

    if not os.path.exists('roles.txt'):
        await ctx.send("Could not find roles.txt file.")
        return

    with open('roles.txt', 'r') as file:
        for line in file:
            role_info = line.strip().split(',')
            role_name = role_info[0].strip()
            # Default color is 0 (no color) if not specified or invalid
            color = discord.Colour(int(role_info[1].strip(), 16)) if len(role_info) > 1 and role_info[1].strip() else 0
            permissions = discord.Permissions()

            for perm in role_info[2:]:
                perm = perm.strip()
                if hasattr(permissions, perm):
                    setattr(permissions, perm, True)
                else:
                    await ctx.send(f"Invalid permission: {perm}")
                    return

            await ctx.guild.create_role(name=role_name, color=color, permissions=permissions)

    await ctx.send("Roles created successfully!")

bot.run("MTIwMjgyMTIwODYyMjc2NDA1Mg.GsUQlT.05tpuBRg40g1BivPStaktUDm3E3OOC_JJ5EaK4")