import discord

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

# Dictionary to store registered aliases
registered_aliases = {}

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

@client.event
async def on_message(message):
    if message.content.startswith('!log'):
        # Check if the command has the required number of arguments
        args = message.content.split()
        if len(args) != 2:
            await message.channel.send('Invalid usage. Use !log #, where # is the number of messages to log.')
            return
        
        try:
            # Convert the argument to an integer
            num_messages = int(args[1])
        except ValueError:
            await message.channel.send('Invalid argument. Please provide a valid number of messages.')
            return

        # Fetch the message history from the channel
        messages = []
        async for msg in message.channel.history(limit=num_messages):
            # Check if the author of the message is the bot itself
            if msg.author == client.user:
                continue
            messages.append(msg)

        # Reverse the messages list to save them in oldest at the top order
        messages.reverse()

        # Open a file to log the messages
        file_name = f'{message.channel.name}_log.txt'
        with open(file_name, 'w', encoding='utf-8') as log_file:
            for msg in messages:
                author_name = get_registered_alias(msg.author)
                log_file.write(f'{author_name}: {msg.content}\n')

        await message.channel.send(f'Logged {len(messages)} messages to {file_name}')

    elif message.content.startswith('!register'):
        # Check if the command has the required number of arguments
        args = message.content.split()
        if len(args) != 2:
            await message.channel.send('Invalid usage. Use !register (name) to register your alias.')
            return
        
        alias = args[1]
        registered_aliases[message.author.id] = alias
        await message.channel.send(f'Your alias has been registered as "{alias}".')

def get_registered_alias(author):
    return registered_aliases.get(author.id, author.name)

# Replace 'YOUR_BOT_TOKEN' with your actual bot token
client.run('NzA4MTIxOTg1MDM2NzE0MDI1.GD1MyR.U2Ms7lib1e1EcJZVGJ7fieqUgY45aTduGGa63w')
