import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import Button, View

import os
import re
import json
import random

from dotenv import load_dotenv

load_dotenv("token.env")
token = os.getenv("DISCORD_TOKEN")

# · · ─────── ·𖥸· ─────── · · Extra Variables · · ─────── ·𖥸· ─────── · ·
eight_ball_response = [
    "Simply Put, You're Fucked.", "Fuck Ya!!", "Yeah, Bitch.", "Maybe, Maybe Not, Who The Fuck Knows. Definitely Not Me.", "Deep Wang.... DEEEEEEEEP WANGGGGGGG", "That's A Possibility, Or I'm Just Dumb.", 
    "Sorry, This Service Is In Use. Please Try Again.", "Error Code 404: Please Try Again Later.",  "Unfortunatly, I'm Just A Bot. I'm Not A Fortune Teller.", "Yes, Just Yes.", 
    "Yes, I Can Smell You. It Smells Like Bitch.", "Does A Bear Shit In The Woods?", "Dick Cheese. Shaken, Not Stirred.", "Anything Is A Dildo If You're Brave Enough.", "Ask A Moderator",
    "Denied. Reasoning? You're A Bitch.", "Don't Worry I Will Be Gentle...", "Fight Me Pussy.", "Would This Help? https://fans.ly/ItMeAzura", "Balding Ball Sack."
    "It Is Certain", "It Is Decidedly So", "Without A Doubt", "Yes Definitely", "You May Rely On It", "As I See It, Yes", "Most Likely", "Outlook Good", "Yes", "Signs Point To Yes", 
    "Reply Hazy, Try Again", "Ask Again Later", "Better Not Tell You Now", "Cannot Predict Now", "Concentrate And Ask Again", "Don't Count On It", "My Reply Is No", "My Sources Say No", 
    "Outlook Not So Good", "Very Doubtful"
]

# · · ─────── ·𖥸· ─────── · · Helper Functions · · ─────── ·𖥸· ─────── · ·
def load_reaction_roles():
    if os.path.exists("reaction_roles.json"):
        with open("reaction_roles.json", "r") as f:
            return json.load(f)
    else:
        return {}
    
def save_reaction_roles(data):
    with open("reaction_roles.json", "w") as f:
        json.dump(data, f, indent = 4)

reaction_roles = load_reaction_roles()

# · · ─────── ·𖥸· ─────── · · Utilities · · ─────── ·𖥸· ─────── · ·
def parse_message_link(link_or_id):
    link_pattern = r"https:\/\/discord(?:app)?\.com\/channels\/(\d+)\/(\d+)\/(\d+)"
    match = re.match(link_pattern, link_or_id)

    if match:
        guild_id = int(match.group(1))
        channel_id = int(match.group(2))
        message_id = int(match.group(3))
        return (guild_id, channel_id, message_id)
    
    else: # Assume Its Just A Message ID
        return (None, None, int(link_or_id))


# · · ─────── ·𖥸· ─────── · · Commands · · ─────── ·𖥸· ─────── · ·
if token is None:
    print("Error: Token not found") # Check For Token
else:
    print("Token Found.")

# · · ─────── ·𖥸· ─────── · · Initialisation Of Bot · · ─────── ·𖥸· ─────── · ·

    intents = discord.Intents.default()
    intents.message_content = True  # Required To Read Message Content

    # Bot Prefix With '/' Command Integration
    client = commands.Bot(command_prefix="!", intents=intents, application_id=1365716156006273114)

    @client.event
    async def on_ready():
        print(f"Logged In As {client.user}")
        await client.tree.sync()
        for command in client.tree.get_commands():
            print(f"Command: {command.name}")  # Lists Registered Commands
        print("Slash Commands Synced")

# · · ─────── ·𖥸· ─────── · · Client Basic Commands · · ─────── ·𖥸· ─────── · ·

    # Traditional Hello World
    @client.command()
    async def hello(ctx):
        await ctx.send("Hello There! I Am A Custom Made Discord Bot. Thank You For Checking My Basic Commands")

    # Slash Command Equivalent
    @client.tree.command(name="hello", description="Say Hello With A Slash Command!")
    async def slash_hello(interaction: discord.Interaction):
        await interaction.response.send_message("Hello There! I Am A Custom Made Discord Bot. Thank You For Checking My Slash Commands")

    # Ping Commands
    @client.command()
    async def ping(ctx):
        latency = round(client.latency * 1000)
        await ctx.send(f"Pong! Latency: {latency}ms")

    @client.tree.command(name="ping", description="Check This Bot's Latency!")
    async def slash_ping(interaction: discord.Interaction):
        latency = round(client.latency * 1000)
        await interaction.response.send_message(f"Pong! Latency: {latency}ms")

# · · ─────── ·𖥸· ─────── · · Purge Commands · · ─────── ·𖥸· ─────── · ·

    # Purge Commands
    @client.command()
    @commands.has_permissions(manage_messages=True)
    async def purge(ctx, amount: int = 15, target: discord.Member = None): 
        await ctx.message.delete()
        if target:
            def check(message):
                return message.author == target
            await ctx.channel.purge(limit=amount, check=check)
            await ctx.send(f"Purged {amount} Messages From {target.mention}")
        else:
            await ctx.channel.purge(limit=amount)
            await ctx.send(f"Purged {amount} Messages")

    # Slash Command Equivalent
    @client.tree.command(name="purge", description="Purge Past Messages, This Can Target A User Or Target Everyone")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def slash_purge(interaction: discord.Interaction, amount: int = 15, target: discord.Member = None):
        if target:
            def check(message):
                return message.author == target
            await interaction.channel.purge(limit=amount, check=check)
            await interaction.response.send_message(f"Purged {amount} Messages From {target.mention}")
        else:
            await interaction.channel.purge(limit=amount)
            await interaction.response.send_message(f"Purged {amount} Messages")


# · · ─────── ·𖥸· ─────── · · Reaction Roles · · ─────── ·𖥸· ─────── · ·

    # Reaction Roles "!"
    @client.command(name="rr")
    @commands.has_permissions(manage_channels=True)
    async def reaction_role(ctx, message_link_or_id: str, *args):
        guild_id_from_link, channel_id, message_id = parse_message_link(message_link_or_id)

        if message_id is None:
                await ctx.send("Error: Message Not Found In This Server.")
                return

        if guild_id_from_link and guild_id_from_link != ctx.guild.id:
            await ctx.send("Error: Message Not Found In This Server")
            return

        if len(args) < 2 or len(args) % 2 not in (0, 1):
            await ctx.send("Error: Command Parameters Not Met, You Must Provide Emoji-Role Pairs.")
            return

        emoji_role_pairs = []
        config_mode = "default"

        i = 0
        while i < len(args):
            if i+1 >= len(args):
                config_mode = args[i].lower()
                break

            emoji = args[i]
            role_mention = args[i+1]
            role = await commands.RoleConverter().convert(ctx, role_mention)

            emoji_role_pairs.append((emoji, role.id))
            i += 2

        if len(emoji_role_pairs) > 6:
            await ctx.send("Error: You Can Only Have 6 Pairs Of Reaction Roles Setup.")
            return

        if config_mode not in ("default", "add", "remove"):
            config_mode = "default"

        guild_id_str = str(ctx.guild.id)

        if guild_id_str not in reaction_roles:
            reaction_roles[guild_id_str] = []

        if len(reaction_roles[guild_id_str]) >= 3:
            await ctx.send("Error: This Server Already Has Three Sets Of Reaction Roles. This Is The Limit.")
            return
        
        # Fetch The Correct Channel And Message
        if channel_id:
            channel = ctx.guild.get_channel(channel_id)
            if channel is None:
                await ctx.send("Error: Could Not Locate Message Channel.")
                return
            try:
                message = await channel.fetch_message(message_id)
            except discord.NotFound:
                await ctx.send(f"Error: Message Could Not Be Located Within <#{channel_id}>.")
                return
            
        else:
            message = None
            for channel in ctx.guild.text_channels:
                try:
                    message = await channel.fetch_message(message_id)
                    if message:
                        break
                except (discord.NotFound, discord.Forbidden):
                    continue

            if message is None:
                await ctx.send("Error: Message Could Not Be Found In This Server.")
                return
            
        # Save The Setup
        reaction_roles[guild_id_str].append({
            "message_id": message_id,
            "pairs": emoji_role_pairs,
            "config": config_mode
        })

        save_reaction_roles(reaction_roles)

        for emoji, _ in emoji_role_pairs:
            await message.add_reaction(emoji)

        await ctx.send(f"Reaction Roles Setup Complete On Message {message_id}.")
        

    @client.tree.command(name="rr", description="Setup Reaction Roles Easily.")
    @app_commands.checks.has_permissions(manage_channels=True)
    @app_commands.describe(
        message="Provide A Message Link Or ID",
        config="Choose How Reactions Work: Default, Add Only, Remove Only."
    )
    async def slash_reaction_role(
        interaction: discord.Interaction,
        message: str,
        emoji1: str, role1: discord.Role,
        emoji2: str = None, role2: discord.Role = None,
        emoji3: str = None, role3: discord.Role = None,
        emoji4: str = None, role4: discord.Role = None,
        emoji5: str = None, role5: discord.Role = None,
        config: str = "default"
    ):
        guild_id_from_link, channel_id, message_id = parse_message_link(message)

        if message_id is None:
            await interaction.response.send_message("Error: Message Not Found In This Server.", ephemeral=True)
            return

        if guild_id_from_link and guild_id_from_link != interaction.guild.id:
            await interaction.response.send_message("Error: Message Not Found In This Server", ephemeral=True)
            return

        emoji_role_pairs = []
        input_pairs = [
            (emoji1, role1),
            (emoji2, role2),
            (emoji3, role3),
            (emoji4, role4),
            (emoji5, role5)
        ]

        for emoji, role in input_pairs:
            if emoji and role:
                emoji_role_pairs.append((emoji, role.id))

        if not emoji_role_pairs:
            await interaction.response.send_message("Error: Command Parameters Not Met, You Must Provide Emoji-Role Pairs.", ephemeral=True)
            return

        if config.lower() not in ("default", "add", "remove"):
            config = "default"

        guild_id_str = str(interaction.guild.id)

        if guild_id_str not in reaction_roles:
            reaction_roles[guild_id_str] = []

        if len(reaction_roles[guild_id_str]) >= 3:
            await interaction.response.send_message("Error: This Server Already Has Three Sets Of Reaction Roles. This Is The Limit.", ephemeral=True)
            return

        # Fetch correct message
        if channel_id:
            channel = interaction.guild.get_channel(channel_id)
            if channel is None:
                await interaction.response.send_message("Error: Could Not Locate Message Channel.", ephemeral=True)
                return
            try:
                message_obj = await channel.fetch_message(message_id)
            except discord.NotFound:
                await interaction.response.send_message(f"Error: Message Could Not Be Located Within <#{channel_id}>.", ephemeral=True)
                return
        else:
            message_obj = None
            for channel in interaction.guild.text_channels:
                try:
                    message_obj = await channel.fetch_message(message_id)
                    if message_obj:
                        break
                except (discord.NotFound, discord.Forbidden):
                    continue

            if message_obj is None:
                await interaction.response.send_message("Error: Message Could Not Be Found In This Server.", ephemeral=True)
                return

        # Save the setup
        reaction_roles[guild_id_str].append({
            "message_id": message_id,
            "pairs": emoji_role_pairs,
            "config": config.lower()
        })

        save_reaction_roles(reaction_roles)

        for emoji, _ in emoji_role_pairs:
            await message_obj.add_reaction(emoji)

        await interaction.response.send_message(f"Reaction Roles Setup Complete On Message {message_id}.", ephemeral=True)


    # Clearing Reaction Roles
    @client.command(name="rr-clear")
    @commands.has_permissions(manage_channels=True)
    async def rr_clear(ctx, message_id: str):
        data = load_reaction_roles()
        guild_id = str(ctx.guild.id)

        if guild_id not in data:
            await ctx.send("Error: There Are No Reaction Roles Setup In This Server.")
            return

        message_entry = None
        for entry in data[guild_id]:
            if str(entry["message_id"]) == str(message_id):
                message_entry = entry
                break

        if not message_entry:
            await ctx.send("Error: There Are No Reaction Roles Associated With That Message.")
            return

        try:
            channel = await client.fetch_channel(ctx.channel.id)  # or entry's channel_id if you store it
            message = await channel.fetch_message(int(message_id))

            for emoji, role_id in message_entry["pairs"]:
                await message.clear_reaction(emoji)
        except Exception as e:
            await ctx.send(f"Error: Failed To Clear Reactions From Message. {e}")
            return

        # Remove from the list
        data[guild_id].remove(message_entry)
        save_reaction_roles(data)

        await ctx.send(f"Success: All Reaction Roles Cleared From Message {message_id}.")


    @client.tree.command(name="clear-rr", description="Clear A Previously Setup Reaction Roles.")
    @app_commands.checks.has_permissions(manage_channels=True)
    @app_commands.describe(message_id="The ID Of The Message With The Reaction Roles.")
    async def slash_rr_clear(interaction: discord.Interaction, message_id: str):
        data = load_reaction_roles()
        guild_id = str(interaction.guild.id)

        if guild_id not in data:
            await interaction.response.send_message("Error: There Are No Reaction Roles Setup In This Server.", ephemeral=True)
            return

        message_entry = None
        for entry in data[guild_id]:
            if str(entry["message_id"]) == str(message_id):
                message_entry = entry
                break

        if not message_entry:
            await interaction.response.send_message("Error: There Are No Reaction Roles Associated With That Message.", ephemeral=True)
            return

        try:
            channel = await client.fetch_channel(interaction.channel_id)  # or store 'channel_id' separately if needed
            message = await channel.fetch_message(int(message_id))

            for emoji, role_id in message_entry["pairs"]:
                await message.clear_reaction(emoji)

        except Exception as e:
            await interaction.response.send_message(f"Error: Failed To Clear Reactions From Message. {e}", ephemeral=True)
            return

        # Remove the entry
        data[guild_id].remove(message_entry)
        save_reaction_roles(data)

        await interaction.response.send_message(f"Success: All Reaction Roles Cleared From Message {message_id}.", ephemeral=True)

# · · ─────── ·𖥸· ─────── · · 8 Ball Command · · ─────── ·𖥸· ─────── · ·
    @client.command(name = "8ball")
    async def eight_ball(ctx, *, question: str):
        await ctx.message.delete()
        response = random.choice(eight_ball_response)
        await ctx.send(f"🎱 Question: {question}\nAnswer: **{response}**")

    @client.tree.command(name = "8ball", description = "Ask The Magic 8-Ball A Question.")
    @app_commands.describe(question = "Your Question To The Magic 8-Ball.")
    async def slash_eight_ball(interaction: discord.Interaction, question: str):
        response = random.choice(eight_ball_response)
        await interaction.response.send_message(f"🎱 Question: {question}\nAnswer: **{response}**")

# · · ─────── ·𖥸· ─────── · · About Me (Azura) · · ─────── ·𖥸· ─────── · ·
    @client.command(name = "aboutme")
    async def aboutme(ctx):
        embed = discord.Embed(
            description = "Name's Azura, I do stuff I guess?\n\nI have a tendency to break out into rants, a lot.\n\nThat's about it, if you like what ya see then feel free to follow.",
            color = discord.Color.from_rgb(75, 0, 130) #4b0082
        )

        embed.set_author(
            name = "ItMeAzura",
            icon_url = "https://images-ext-1.discordapp.net/external/ANmfUyalqYltI1qS6gzX4eyF8L4mivf9UhynHvuz5VU/%3Fsize%3D4096/https/cdn.discordapp.com/avatars/183918385518608385/a_3808d70cd7c41630feb10191c5253d02.gif"
        )

        embed.add_field(
            name = "I Stream On Twitch!!",
            value = "[Check Me Out!!](https://www.twitch.tv/itmeazura/about)",
            inline = False
        )

        embed.set_thumbnail(
            url = "https://images-ext-1.discordapp.net/external/lMJ0re7bL-vsWyJcf1X-cbTWF0Az2KQTfR_O4XF94LI/%3Fwidth%3D958%26height%3D958/https/images-ext-1.discordapp.net/external/4n6cYHd5RMidVXgqLDSAYjF7_8xr9r0ZNqx0bGTVXbg/%253Fsize%253D4096/https/cdn.discordapp.com/icons/928794195286696019/ae9d3597896864f904eaa17e6e243eea.png"
        )

        await ctx.send(embed = embed)

    @client.tree.command(name="aboutme", description="Display Azura's About Me Information")
    async def slash_aboutme(interaction: discord.Interaction):
        embed = discord.Embed(
            description = "Name's Azura, I do stuff I guess?\n\nI have a tendency to break out into rants, a lot.\n\nThat's about it, if you like what ya see then feel free to follow.",
            color = discord.Color.from_rgb(75, 0, 130) #4b0082
        )

        embed.set_author(
            name = "ItMeAzura",
            icon_url = "https://images-ext-1.discordapp.net/external/ANmfUyalqYltI1qS6gzX4eyF8L4mivf9UhynHvuz5VU/%3Fsize%3D4096/https/cdn.discordapp.com/avatars/183918385518608385/a_3808d70cd7c41630feb10191c5253d02.gif"
        )

        embed.add_field(
            name = "I Stream On Twitch!!",
            value = "[Check Me Out!!](https://www.twitch.tv/itmeazura/about)",
            inline = False
        )

        embed.set_thumbnail(
            url = "https://images-ext-1.discordapp.net/external/lMJ0re7bL-vsWyJcf1X-cbTWF0Az2KQTfR_O4XF94LI/%3Fwidth%3D958%26height%3D958/https/images-ext-1.discordapp.net/external/4n6cYHd5RMidVXgqLDSAYjF7_8xr9r0ZNqx0bGTVXbg/%253Fsize%253D4096/https/cdn.discordapp.com/icons/928794195286696019/ae9d3597896864f904eaa17e6e243eea.png"
        )

        await interaction.response.send_message(embed = embed)

# · · ─────── ·𖥸· ─────── · · Azura's Social Links · · ─────── ·𖥸· ─────── · ·
    @client.command(name='socials')
    async def socials(ctx):
        embed = discord.Embed(
            title="Hey there, I see you want my social links, you must like me :D",
            color=4915330
        )

        embed.add_field(
            name="Twitch",
            value="I stream on Twitch fairly regularly, usually using maximum brainpower to conquer whatever challenges chat throws at me. Y’all can be evil sometimes, but use this link to check me out:\nhttps://www.twitch.tv/itmeazura",
            inline=False
        )
        embed.add_field(
            name="YouTube",
            value="I frequently post to my YouTube, check out either my short, or long form content. Here's the link:\nhttps://www.youtube.com/@ItMeAzura",
            inline=False
        )
        embed.add_field(
            name="Twitter",
            value="No, I don't think I will call it _X_. Here's the link.\nhttps://x.com/ItMeAzura",
            inline=False
        )
        embed.add_field(
            name="Discord",
            value="Firstly, why do you need this? You need to be in my discord server to use this command. Anyway, here's the link:\nhttps://discord.gg/Wr5NQBb5Uh",
            inline=False
        )
        embed.add_field(
            name="Kofi",
            value="This is used to raise emergency money, If you can't give me anything, don't worry about it. It's just there\nhttps://ko-fi.com/itmeazura",
            inline=False
        )
        embed.add_field(
            name="Chat Donations",
            value="Firstly, you don't HAVE to donate. But I appreciate everyone who does. It means the world to me.\nhttps://streamelements.com/itmeazura/tip",
            inline=False
        )

        embed.set_author(
            name="ItMeAzura",
            icon_url="https://images-ext-1.discordapp.net/external/ANmfUyalqYltI1qS6gzX4eyF8L4mivf9UhynHvuz5VU/%3Fsize%3D4096/https/cdn.discordapp.com/avatars/183918385518608385/a_3808d70cd7c41630feb10191c5253d02.gif"
        )
        embed.set_thumbnail(
            url="https://images-ext-1.discordapp.net/external/6Uodvf3X3G_WhAhkpo8Yr_e06dYA_8UwbbUf0ElPU1A/https/images-ext-1.discordapp.net/external/lMJ0re7bL-vsWyJcf1X-cbTWF0Az2KQTfR_O4XF94LI/%253Fwidth%253D958%2526height%253D958/https/images-ext-1.discordapp.net/external/4n6cYHd5RMidVXgqLDSAYjF7_8xr9r0ZNqx0bGTVXbg/%25253Fsize%25253D4096/https/cdn.discordapp.com/icons/928794195286696019/ae9d3597896864f904eaa17e6e243eea.png?width=958&height=958"
        )

        await ctx.send(embed=embed)


    @client.tree.command(name="socials", description="Get my social links!")
    async def slash_socials(interaction: discord.Interaction):
        embed = discord.Embed(
            title="Hey there, I see you want my social links, you must like me :D",
            color=4915330
        )

        embed.add_field(
            name="Twitch",
            value="I stream on Twitch fairly regularly, usually using maximum brainpower to conquer whatever challenges chat throws at me. Y’all can be evil sometimes, but use this link to check me out:\nhttps://www.twitch.tv/itmeazura",
            inline=False
        )
        embed.add_field(
            name="YouTube",
            value="I frequently post to my YouTube, check out either my short, or long form content. Here's the link:\nhttps://www.youtube.com/@ItMeAzura",
            inline=False
        )
        embed.add_field(
            name="Twitter",
            value="No, I don't think I will call it _X_. Here's the link.\nhttps://x.com/ItMeAzura",
            inline=False
        )
        embed.add_field(
            name="Discord",
            value="Firstly, why do you need this? You need to be in my discord server to use this command. Anyway, here's the link:\nhttps://discord.gg/Wr5NQBb5Uh",
            inline=False
        )
        embed.add_field(
            name="Kofi",
            value="This is used to raise emergency money, If you can't give me anything, don't worry about it. It's just there\nhttps://ko-fi.com/itmeazura",
            inline=False
        )
        embed.add_field(
            name="Chat Donations",
            value="Firstly, you don't HAVE to donate. But I appreciate everyone who does. It means the world to me.\nhttps://streamelements.com/itmeazura/tip",
            inline=False
        )

        embed.set_author(
            name="ItMeAzura",
            icon_url="https://images-ext-1.discordapp.net/external/ANmfUyalqYltI1qS6gzX4eyF8L4mivf9UhynHvuz5VU/%3Fsize%3D4096/https/cdn.discordapp.com/avatars/183918385518608385/a_3808d70cd7c41630feb10191c5253d02.gif"
        )
        embed.set_thumbnail(
            url="https://images-ext-1.discordapp.net/external/6Uodvf3X3G_WhAhkpo8Yr_e06dYA_8UwbbUf0ElPU1A/https/images-ext-1.discordapp.net/external/lMJ0re7bL-vsWyJcf1X-cbTWF0Az2KQTfR_O4XF94LI/%253Fwidth%253D958%2526height%253D958/https/images-ext-1.discordapp.net/external/4n6cYHd5RMidVXgqLDSAYjF7_8xr9r0ZNqx0bGTVXbg/%25253Fsize%25253D4096/https/cdn.discordapp.com/icons/928794195286696019/ae9d3597896864f904eaa17e6e243eea.png?width=958&height=958"
        )

        await interaction.response.send_message(embed=embed)

    @client.command(name='twitch')
    async def twitch(ctx):
        await ctx.send(
            "I stream on Twitch fairly regularly, usually using maximum brainpower to conquer whatever challenges chat throws at me. Y’all can be evil sometimes, but use this link to check me out:\nhttps://www.twitch.tv/itmeazura"
        )
    
    @client.command(name='youtube')
    async def youtube(ctx):
        await ctx.send(
            "I frequently post to my YouTube, check out either my short, or long-form content. Here's the link:\nhttps://www.youtube.com/@ItMeAzura"
        )

    @client.command(name='twitter')
    async def twitter(ctx):
        await ctx.send(
            "No, I don't think I will call it _X_. Here's the link:\nhttps://x.com/ItMeAzura"
        )

    @client.command(name='discord')
    async def discord_link(ctx):
        await ctx.send(
            "Firstly, why do you need this? You need to be in my discord server to use this command. Anyway, here's the link:\nhttps://discord.gg/Wr5NQBb5Uh"
        )

    @client.command(name='kofi')
    async def kofi(ctx):
        await ctx.send(
            "This is used to raise emergency money. If you can't give me anything, don't worry about it. It's just there:\nhttps://ko-fi.com/itmeazura"
        )

    @client.command(name='donate')
    async def donate(ctx):
        await ctx.send(
            "Firstly, you don't HAVE to donate. But I appreciate everyone who does. It means the world to me. Here's the link:\nhttps://streamelements.com/itmeazura/tip"
        )

    @client.command(name='fansly')
    async def fansly(ctx):
        author_id = ctx.author.id
        try:
            if author_id == 365213219901538319:
                await ctx.author.send("No, Not For You. To Horny Jail You Go.")
            else:
                await ctx.send(
                    "Why, just why. Why in the hell do you want this.... Welp. Here you go. Check your dms..."
                )
                await ctx.author.send("Here you go you heretic. https://fans.ly/ItMeAzura")
        except discord.Forbidden:
            await ctx.send("Error: I Cannot Provide You With The Link As I Cannot Dm You.")
        except Exception as e:
            await ctx.send(f"Error: {str(e)}")

    @client.tree.command(name="twitch", description="Get my Twitch link")
    async def slash_twitch(interaction: discord.Interaction):
        await interaction.response.send_message(
            "I stream on Twitch fairly regularly, usually using maximum brainpower to conquer whatever challenges chat throws at me. Y’all can be evil sometimes, but use this link to check me out:\nhttps://www.twitch.tv/itmeazura"
        )

    @client.tree.command(name="youtube", description="Get my YouTube link")
    async def slash_youtube(interaction: discord.Interaction):

        await interaction.response.send_message(
            "I frequently post to my YouTube, check out either my short, or long-form content. Here's the link:\nhttps://www.youtube.com/@ItMeAzura"
        )

    @client.tree.command(name="twitter", description="Get my Twitter link")
    async def slash_twitter(interaction: discord.Interaction):
        await interaction.response.send_message(
            "No, I don't think I will call it _X_. Here's the link:\nhttps://x.com/ItMeAzura"
        )

    @client.tree.command(name="discord", description="Get my Discord link")
    async def slash_discord(interaction: discord.Interaction):
        await interaction.response.send_message(
            "Firstly, why do you need this? You need to be in my discord server to use this command. Anyway, here's the link:\nhttps://discord.gg/Wr5NQBb5Uh"
        )

    @client.tree.command(name="kofi", description="Get my Ko-fi link")
    async def slash_kofi(interaction: discord.Interaction):
        await interaction.response.send_message(
            "This is used to raise emergency money. If you can't give me anything, don't worry about it. It's just there:\nhttps://ko-fi.com/itmeazura"
        )

    @client.tree.command(name="donate", description="Get my donation link")
    async def slash_donate(interaction: discord.Interaction):
        await interaction.response.send_message(
            "Firstly, you don't HAVE to donate. But I appreciate everyone who does. It means the world to me. Here's the link:\nhttps://streamelements.com/itmeazura/tip"
        )

# · · ─────── ·𖥸· ─────── · · Ban/Kick Commands · · ─────── ·𖥸· ─────── · ·

    @client.command(name = "ban")
    @commands.has_permissions(ban_members = True)
    async def ban(ctx, user: discord.User, *, reason: str = None):
        # Check If A Reason Has Been Provided
        if not reason:
            await ctx.send("Error: You must provide a reason for banning a user. This command will not run otherwise.")
            return
        
        # Ensure The Bot Has Permission To Ban The User
        if ctx.author.top_role <= user.top_role:
            await ctx.send(f"Error: You Cannot Ban A User Who Has {user.top_role.name}")
            return
        
        try:
            # Create Ban Embed Message
            embed = discord.Embed(title = f"You have been banned from {ctx.guild.name}", color = 4915330)
            embed.add_field(name = "Reason For Your Ban", value = reason)
            embed.add_field(name = "Want To Appeal?", value = "You can appeal this ban by using this form: https://forms.gle/NMMNnQrcH53tzaM9A")

            await user.send(embed = embed)
        except discord.Forbidden:
            await ctx.send(f"Error: {user.name} Could Not Be Messaged")

        # Banning The User From The Server
        await ctx.guild.ban(user, reason = reason, delete_message_days = 14) # Removing The Past 14 Days Of Messages
        await ctx.send(f"{user} Has Been Successfully Banned From {ctx.guild.name} For The Following Reason: {reason}")

    @client.tree.command(name = "ban", description = "Ban A User From The Server")
    @app_commands.describe(user = "User To Ban", reason = "Reason For The Ban")
    async def slash_ban(interaction: discord.Interaction, user: discord.Member, reason: str):
        # Check If Reason Is Provided
        if not reason:
            await interaction.response.send_message("Error: You must provide a reason for banning a user. This command will not run otherwise.")
            return
        
        # Ensure The Bot Has Permission To Ban The User
        if not interaction.user.guild.permissions.ban_members:
            await interaction.response.send_message(f"Error: You Cannot Ban A User Who Has {user.top_role.name}")
            return
        
        # Prep The Ban Action
        try:
            await user.ban(reason = reason, delete_message_days = 14)

            # Create Ban Embed Message
            embed = discord.Embed(title = f"You have been banned from {interaction.guild.name}", color = 4915330)
            embed.add_field(name = "Reason For Your Ban", value = reason)
            embed.add_field(name = "Want To Appeal?", value = "You can appeal this ban by using this form: https://forms.gle/NMMNnQrcH53tzaM9A")

            try:
                # Attempt To Send The Dm To User
                await user.send(embed = embed)
            except discord.Forbidden:
                await interaction.response.send_message(f"Error: {user.name} Could Not Be Messaged")
            
            await interaction.response.send_message(f"{user} Has Been Successfully Banned From {interaction.guild.name} For The Following Reason: {reason}")
        
        except discord.DiscordException as e:
            await interaction.response.send_message(f"Error: An Error Occurred While Banning {user.name}. The Error Is As Follows {str(e)}", ephemeral = True)

    @client.command(name = "unban")
    @commands.has_permissions(ban_members = True)
    async def unban(ctx, user: discord.User, *, reason: str):
        if not reason:
            await ctx.send("Error: Reasoning Must Be Presented To Run This Command")
            return

        banned_users = await ctx.guild.bans()
        banned_users = discord.utils.get(banned_users, user = user)

        if not banned_users:
            await ctx.send(f"Error: {user} Is Not Currently Banned")
            return
        
        # Unban The User With Given Reason
        try:
            await ctx.guild.unban(user, reason = reason)

            embed = discord.Embed(title = "Unban Information", description = f"You ban appeal for {ctx.guild.name} was successful.", color = 4915330)
            embed.add_field(name = "Reasoning", value = reason, inline = False)

            rules_channel = None
            for channel in ctx.guild.text_channels:
                if "rules" in channel.name.lower():
                    rules_channel = channel
                    break
            
            if rules_channel:
                invite = await rules_channel.create_invite(max_uses = 1, unique = True, temporary = False)
                embed.add_field(name = "Reinvite Link", value = f"Here is your reinvite link: {invite}", inline = False)
            else:
                invite = await channel.create_invite(max_uses=1, unique=True, temporary=False)
                embed.add_field(name = "Reinvite Link", value = f"Here is your reinvite link: {invite}", inline = False)

            try:
                await user.send(embed = embed)
            except discord.Forbidden:
                await ctx.send(f"Error: {user.name} Could Not Be Messaged.")

            await ctx.send(f"{user.name} Has Been Unbanned From {ctx.guild.name} And Reinvited.")

        except discord.DiscordException as e:
            await ctx.send(f"Error: An Error Has Occured While Banning {user.name}. Here Is The Error: {str(e)}")


    @client.tree.command(name="unban", description="Unban A User And Send Them A Reinvite.")
    @app_commands.describe(user="The User To Unban", reason="The Reason For Unbanning The User")
    @app_commands.checks.has_permissions(ban_members=True)
    async def slash_unban(interaction: discord.Interaction, user: discord.User, reason: str):
        if not reason:
            await interaction.response.send_message("Error: Reasoning Must Be Presented To Run This Command", ephemeral=True)
            return

        banned_users = await interaction.guild.bans()
        banned_users = discord.utils.get(banned_users, user=user)

        if not banned_users:
            await interaction.response.send_message(f"Error: {user} Is Not Currently Banned", ephemeral=True)
            return

        try:
            await interaction.guild.unban(user, reason=reason)

            embed = discord.Embed(title="Unban Information", description=f"You ban appeal for {interaction.guild.name} was successful.", color=4915330)
            embed.add_field(name="Reasoning", value=reason, inline=False)

            rules_channel = None
            for channel in interaction.guild.text_channels:
                if "rules" in channel.name.lower():
                    rules_channel = channel
                    break

            if rules_channel:
                invite = await rules_channel.create_invite(max_uses=1, unique=True, temporary=False)
                embed.add_field(name="Reinvite Link", value=f"Here is your reinvite link: {invite}", inline=False)
            else:
                invite = await interaction.channel.create_invite(max_uses=1, unique=True, temporary=False)
                embed.add_field(name="Reinvite Link", value=f"Here is your reinvite link: {invite}", inline=False)

            try:
                await user.send(embed=embed)
            except discord.Forbidden:
                await interaction.response.send_message(f"Error: {user.name} Could Not Be Messaged.", ephemeral=True)
                return

            await interaction.response.send_message(f"{user.name} Has Been Unbanned From {interaction.guild.name} And Reinvited.")

        except discord.DiscordException as e:
            await interaction.response.send_message(f"Error: An Error Has Occured While Banning {user.name}. Here Is The Error: {str(e)}", ephemeral=True)

    @client.command(name = "kick")
    @commands.has_permissions(kick_members = True)
    async def kick(ctx, user: discord.User, *, reason: str = None):
        # Check If A Reason Has Been Provided
        if not reason:
            await ctx.send("Error: You must provide a reason for kicking a user. This command will not run otherwise.")
            return
        
        # Ensure The Bot Has Permission To Kick The User
        if ctx.author.top_role <= user.top_role:
            await ctx.send(f"Error: You Cannot Kick A User Who Has {user.top_role.name}")
            return
        
        try:
            # Create Kick Embed Message
            embed = discord.Embed(title = f"You have been kicked from {ctx.guild.name}", color = 4915330)
            embed.add_field(name = "Reason For Your Kick", value = reason)

            await user.send(embed = embed)
        except discord.Forbidden:
            await ctx.send(f"Error: {user.name} Could Not Be Messaged")

        # Kicking The User From The Server
        await ctx.guild.kick(user, reason = reason)
        await ctx.send(f"{user} Has Been Successfully Kicked From {ctx.guild.name} For The Following Reason: {reason}")

    @client.tree.command(name = "kick", description = "Kick A User From The Server")
    @app_commands.describe(user = "User To Kick", reason = "Reason For The Kick")
    async def slash_kick(interaction: discord.Interaction, user: discord.Member, reason: str):
        # Check If Reason Is Provided
        if not reason:
            await interaction.response.send_message("Error: You must provide a reason for kicking a user. This command will not run otherwise.")
            return
        
        # Ensure The Bot Has Permission To Kick The User
        if not interaction.user.guild_permissions.kick_members:
            await interaction.response.send_message(f"Error: You Cannot Kick A User Who Has {user.top_role.name}")
            return
        
        try:
            await user.kick(reason = reason)

            # Create Kick Embed Message
            embed = discord.Embed(title = f"You have been kicked from {interaction.guild.name}", color = 4915330)
            embed.add_field(name = "Reason For Your Kick", value = reason)

            try:
                # Attempt To Send The Dm To User
                await user.send(embed = embed)
            except discord.Forbidden:
                await interaction.response.send_message(f"Error: {user.name} Could Not Be Messaged")
            
            await interaction.response.send_message(f"{user} Has Been Successfully Kicked From {interaction.guild.name} For The Following Reason: {reason}")
        
        except discord.DiscordException as e:
            await interaction.response.send_message(f"Error: An Error Occurred While Kicking {user.name}. The Error Is As Follows {str(e)}", ephemeral = True)

# · · ─────── ·𖥸· ─────── · · Invite Commands · · ─────── ·𖥸· ─────── · ·
    @client.command(name = "invite")
    @commands.has_permissions(create_instant_invite = True)
    async def invite(ctx, user: discord.User):
        try:
            rules_channel = None
            for channel in ctx.guild.text_channels:
                if "rules" in channel.name.lower():
                    rules_channel = channel
                    break

            if rules_channel:
                invite = await rules_channel.create_invite(max_uses = 1, unique = True, temporary = False)
            else:
                invite = await ctx.channel.create_invite(max_uses = 1, unique = True, temporary = False)

            embed = discord.Embed(title = f"Invite Link For {ctx.guild.name}", color = 4915330)
            embed.add_field(name = "Invite Link", value = f"Here is your invite link: {invite}", inline = False)

            await user.send(embed = embed)
            await ctx.send(f"Success: {user.name} Has Been Sent A Invite Link.")

        except discord.Forbidden:
            await ctx.send(f"Error: Could Not Message {user.name}. They May Have DMs Closed.")
        except discord.HTTPException as e:
            await ctx.send(f"Error: Failed To Create Or Send Invite. Error Details: {str(e)}")


    @client.tree.command(name = "invite", description = "Send A invite Link To A User")
    @app_commands.describe(user = "User To Send The iinvite Link To")
    async def slash_invite(interaction: discord.Interaction, user: discord.User):
        try:
            rules_channel = None
            for channel in interaction.guild.text_channels:
                if "rules" in channel.name.lower():
                    rules_channel = channel
                    break

            if rules_channel:
                invite = await rules_channel.create_invite(max_uses = 1, unique = True, temporary = False)
            else:
                invite = await interaction.channel.create_invite(max_uses = 1, unique = True, temporary = False)

            embed = discord.Embed(title = f"Invite Link For {interaction.guild.name}", color = 4915330)
            embed.add_field(name = "Invite Link", value = f"Here is your invite link: {invite}", inline = False)

            await user.send(embed = embed)
            await interaction.response.send_message(f"Success: {user.name} Has Been Sent A Invite Link.", ephemeral = True)

        except discord.Forbidden:
            await interaction.response.send_message(f"Error: Could Not Message {user.name}. They May Have DMs Closed.", ephemeral = True)
        except discord.HTTPException as e:
            await interaction.response.send_message(f"Error: Failed To Create Or Send Invite. Error Details: {str(e)}", ephemeral = True)



# · · ─────── ·𖥸· ─────── · · Client Events / Error Checks · · ─────── ·𖥸· ─────── · ·

    @client.event
    async def on_raw_reaction_add(payload):
        guild_id = str(payload.guild_id)
        if guild_id not in reaction_roles:
            return

        for setup in reaction_roles[guild_id]:
            if setup["message_id"] == payload.message_id:
                for emoji, role_id in setup["pairs"]:
                    if str(payload.emoji) == emoji:
                        guild = client.get_guild(payload.guild_id)
                        role = guild.get_role(role_id)
                        member = guild.get_member(payload.user_id)
                        if setup["config"] in ("default", "add"):
                            if role:
                                await member.add_roles(role)
                        break

    @client.event
    async def on_raw_reaction_remove(payload):
        guild_id = str(payload.guild_id)
        if guild_id not in reaction_roles:
            return

        for setup in reaction_roles[guild_id]:
            if setup["message_id"] == payload.message_id:
                for emoji, role_id in setup["pairs"]:
                    if str(payload.emoji) == emoji:
                        guild = client.get_guild(payload.guild_id)
                        role = guild.get_role(role_id)
                        member = guild.get_member(payload.user_id)
                        if setup["config"] in ("default", "remove"):
                            if role:
                                await member.remove_roles(role)
                        break


    @rr_clear.error
    async def rr_clear_error(ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("Error: You Are Missing Permissions To Use This Command.")



    @purge.error
    async def rr_clear_error(ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("Error: You Are Missing Permissions To Use This Command.")

    
    @slash_purge.error
    async def slash_rr_clear_error(interaction: discord.Interaction, error):
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message("Error: You Are Missing Permissions To Use This Command.")

    @slash_rr_clear.error
    async def slash_rr_clear_error(interaction: discord.Interaction, error):
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message("Error: You Are Missing Permissions To Use This Command.")


# · · ─────── ·𖥸· ─────── · · Client Run · · ─────── ·𖥸· ─────── · ·
    client.run(token)