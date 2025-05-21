import discord
import os



intents = discord.Intents.default()  # Use default intents for general use cases
intents.guilds = True  # Enable guilds intent
intents.messages = True  # Enable messages intent to read messages

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f"Logged in as {client.user}")

@client.event
async def on_message(message):
    # Avoid the bot responding to its own messages
    if message.author == client.user:
        return

    if message.content.lower() == "setup server":
        try:
            with open("input.txt", "r") as file:
                category = None
                for line in file:
                    line = line.strip()
                    if line.startswith("{") and line.endswith("}"):
                        category_name = line[1:-1]
                        category = await message.guild.create_category(category_name)
                    elif line.startswith("[") and line.endswith("]") and category is not None:
                        # Added error handling for split
                        try:
                            name, *optional_topic = line[1:-1].split("|")
                            topic = optional_topic[0] if optional_topic else ""
                            await message.guild.create_text_channel(name, category=category, topic=topic)
                        except ValueError as e:
                            print(f"Error processing line '{line}': {e}")
            await message.channel.send("Server setup complete!")
        except Exception as e:
            await message.channel.send(f"An error occurred: {e}")
            print(f"An error occurred: {e}")

    elif message.content.lower() == "purge":
        try:
            for category in list(message.guild.categories):
                await category.delete()
            for channel in list(message.guild.channels):
                if isinstance(channel, discord.TextChannel):
                    await channel.delete()
            await message.channel.send("Server purge complete!")
        except Exception as e:
            await message.channel.send(f"An error occurred during purge: {e}")
            print(f"An error occurred during purge: {e}")

# Start the bot with the token
client.run("MTIzNzIwNzY0MTM5OTQ5Njc1NQ.GeJ5FH.8M0YTf7YA9oBvf1XJcf6J0MTyDhim73OObJQu0")
