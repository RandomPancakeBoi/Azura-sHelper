import discord
from discord.ext import commands, tasks
from discord import app_commands
from discord.ui import Button, View

import os
import re
import json
import random
import asyncio
import datetime

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

logs_config_file = "logs_config.json"

commands_info = {
    "General": [
        ("hello", "No permissions required", "Greets the user."),
        ("ping", "No permissions required", "Pings the bot to check its latency."),
        ("aboutme", "No permissions required", "Displays your 'About Me' section."),
        ("socials", "No permissions required", "Shows your social media links."),
        ("twitch", "No permissions required", "Shows your Twitch link."),
        ("youtube", "No permissions required", "Shows your YouTube link."),
        ("twitter", "No permissions required", "Shows your Twitter link."),
        ("discord", "No permissions required", "Shows your Discord link."),
        ("kofi", "No permissions required", "Shows your Ko-fi link."),
        ("donate", "No permissions required", "Shows your donation links."),
        ("invite", "No permissions required", "Invite any user to this server. All you need is there user ID."),
        ("poll", "No permissions requiured", "Creates a poll with up to four options.")
    ],
    "Points": [
        ("points", "No permissions required", "Shows your current points."),
        ("setpoints", "Administrator", "Sets the points of a user."),
        ("addpoints", "Administrator", "Adds points to a user or everyone."),
        ("removepoints", "Administrator", "Removes points from a user or everyone."),
        ("give", "No permissions required", "Gives some of your points to someone else."),
        ("leaderboard", "No permissions required", "Shows the leaderboard of users with the most points."),
    ],
    "Fun": [
        ("8ball", "No permissions required", "Answers a random question."),
        ("gamble", "No permissions required", "Allows you to gamble your points in a 50/50 chance."),
        ("dice / d", "No permissions required", "Rolls a dice of any size."),
        ("color", "No permissions required", "Generates a random color for you."),
        ("danceparty", "No permissions required", "Starts a dance party!!"),
    ],
    "Information": [
        ("avatar", "No permissions required", "Displays a user's avatar."),
        ("serveravatar", "No permissions required", "Displays the server's icon."),
        ("serverinfo", "No permissions required", "Displays information about the server."),
        ("userinfo", "No permissions required", "Displays information about a user."),
    ],
    "Moderation": [
        ("purge", "Moderator", "Purge messages in any channel, you can even target specific users."),
        ("ban", "Administrator", "Bans a user from the server."),
        ("unban", "Administrator", "Unbans a user from the server."),
        ("kick", "Moderator", "Kicks a user from the server."),
        ("mute", "Moderator", "Mutes a user."),
        ("unmute", "Moderator", "Unmutes a user."),
        ("vcmute", "Moderator", "Mutes a user in vc."),
        ("vcunmute", "Moderator", "Unmutes a user in vc."),
        ("vcmutechannel", "Moderator", "Mutes everyone in vc who lack manage message permissions.."),
        ("vcunmute", "Moderator", "Unmutes everyone in vc who lack manage message permissions."),
        ("setup-mute", "Administrator", "Sets up the mute system."),
        ("logs-setup", "Administrator", "Sets up logging."),
        ("logs-disable", "Administrator", "Disables logging."),
        ("warn", "Moderator", "Warns a user."),
        ("remove-warning", "Moderator", "Removes a warning from a user."),
        ("warns", "Moderator", "Shows the warnings of a user."),
        ("rr", "Administrator", "Creates a reaction role."),
        ("clear-rr", "Administrator", "Clears a reaction role."),
    ]
}

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

async def send_punishment_log(guild: discord.Guild, title: str, user: discord.User, moderator: discord.User, reason: str):
    # Check if punishment logs are enabled
    with open("logs_config.json", "r") as f:
        config = json.load(f)

    guild_id = str(guild.id)
    punishment_logs_enabled = config.get(guild_id, {}).get("punishment_logs_enabled", False)

    if not punishment_logs_enabled:
        return None
    
    channel = discord.utils.get(guild.text_channels, name="punishment-logs")
    if not channel:
        return None
    
    embed = discord.Embed(title=title, color=4915330)
    embed.add_field(name="User", value=f"{user} ({user.id})", inline=False)
    embed.add_field(name="Moderator", value=f"{moderator} ({moderator.id})", inline=False)
    embed.add_field(name="Reason", value=reason or "No Reason Provided", inline=False)
    embed.set_footer(text=f"Time: {discord.utils.format_dt(discord.utils.utcnow(), 'F')}")
    
    message = await channel.send(embed=embed)
    return message.id

async def log_purged_messages(guild, messages):
    try:
        with open("logs_config.json", "r") as f:
            config = json.load(f)

    except (FileNotFoundError, json.JSONDecodeError):
        return
    
    guild_id = str(guild.id)
    if guild_id not in config or not config[guild_id].get("purge_logs_enabled"):
        return
    
    channel_id = config[guild_id].get("purge_channel_id")
    if not channel_id:
        return
    
    log_channel = guild.get_channel(channel_id)
    if not log_channel:
        return
    
    for message in messages:
        embed = discord.Embed(
            title="Message Purged",
            description = f"**Author:** {message.author} (`{message.author.id}`)\n"
                        f"**Channel:** {message.channel.mention}\n"
                        f"**Content:** {message.content or '*[No content]*'}",
            timestamp = message.created_at,
            color = 4915330
        )

        await log_channel.send(embed = embed)

def load_log_config():
    if not os.path.exists(logs_config_file):
        return {}
    with open(logs_config_file, "r") as f:
        return json.load(f)

def save_log_config(data):
    with open(logs_config_file, "w") as f:
        json.dump(data, f, indent = 4)

def load_warnings():
    try:
        with open('warnings.json', 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}
    
def save_warnings(warnings):
    with open('warnings.json', 'w') as f:
        json.dump(warnings, f, indent = 4)

def load_points():
    if not os.path.exists("points.json"):
        return {}
    with open("points.json", "r") as f:
        return json.load(f)

def save_points(data):
    with open("points.json", "w") as f:
        json.dump(data, f, indent = 4)

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
    intents.members = True # Required To Read All Members

    # Bot Prefix With '/' Command Integration
    client = commands.Bot(command_prefix="!", intents=intents, application_id=1365716156006273114)
    client.help_command = None

    @client.event
    async def on_ready():
        print(f"Logged In As {client.user}")
        await client.tree.sync()
        for command in client.tree.get_commands():
            print(f"Command: {command.name}")  # Lists Registered Commands
        print("Slash Commands Synced")

        for guild in client.guilds:
            await guild.chunk()


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

        def check(message):
            return (not message.pinned) and (target is None or message.author == target)

        messages = await ctx.channel.purge(limit=amount, check=check)

        await ctx.send(
            f"Purged {len(messages)} Messages" + (f" From {target.mention}" if target else ""),
            delete_after=5
        )

        await log_purged_messages(ctx.guild, messages)

    # Slash Command Equivalent
    @client.tree.command(name="purge", description="Purge Past Messages, This Can Target A User Or Target Everyone")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def slash_purge(interaction: discord.Interaction, amount: int = 15, target: discord.Member = None):
        def check(message):
            return (not message.pinned) and (target is None or message.author == target)

        messages = await interaction.channel.purge(limit=amount, check=check)

        await interaction.response.send_message(
            f"Purged {len(messages)} Messages" + (f" From {target.mention}" if target else "")
        )

        await log_purged_messages(interaction.guild, messages)


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
        await send_punishment_log(ctx.guild, "User Banned", user, ctx.author, reason)

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
            await send_punishment_log(interaction.guild, "User Banned", user, interaction.user, reason)
        
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
            await send_punishment_log(ctx.guild, "User Unbanned", user, ctx.author, reason)

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
            await send_punishment_log(interaction.guild, "User Unbanned", user, interaction.user, reason)

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
        await send_punishment_log(ctx.guild, "User Kicked", user, ctx.author, reason)

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
            await send_punishment_log(interaction.guild, "User Kicked", user, interaction.user, reason)
        
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

# · · ─────── ·𖥸· ─────── · · Muting, Unmuting And Mute Setup Command · · ─────── ·𖥸· ─────── · ·

    @client.command(name = "mute")
    @commands.has_permissions(manage_roles = True)
    async def mute(ctx, user: discord.Member, *, reason: str = None):
        muted_role = discord.utils.get(ctx.guild.roles, name = "Muted")

        if not muted_role:
            await ctx.send("Error: 'Muted' Role Not Found. Please Create One Or Use The 'mute-setup' Command")
            return
        
        if muted_role in user.roles:
            await ctx.send(f"Error: {user.name} Is Already Muted.")

        if not reason:
            await ctx.send("Error: You must provide a reason for setting up the 'Muted' role.")
            return

        await user.add_roles(muted_role, reason = reason)

        embed = discord.Embed(title="Mute Information", description=f"You have been muted in {ctx.guild.name}.", color=4915330)
        embed.add_field(name="Reasoning", value=reason if reason else "No Reason Provided.", inline=False)

        try:
            await user.send(embed = embed)
        except discord.Forbidden:
            await ctx.send(f"Error: Cound Not Message {user.name}. They May Have Dms Closed.")

        await ctx.send(f"Success: {user.name} Has Been Muted.")
        await send_punishment_log(ctx.guild, "User Muted", user, ctx.author, reason)

    @client.tree.command(name="mute", description="Mute A User In The Server")
    @app_commands.describe(user="User To Mute", reason="Reason For Muting")
    async def slash_mute(interaction: discord.Interaction, user: discord.Member, reason: str = None):
        muted_role = discord.utils.get(interaction.guild.roles, name="Muted")

        if not muted_role:
            await interaction.response.send_message("Error: 'Muted' Role Not Found. Please Create One Or Use The 'mute-setup' Command", ephemeral=True)
            return
        
        if muted_role in user.roles:
            await interaction.response.send_message(f"Error: {user.name} Is Already Muted.", ephemeral=True)
            return
        
        if not reason:
            await interaction.response.send_message("Error: You must provide a reason for setting up the 'Muted' role.", ephemeral=True)
            return

        await user.add_roles(muted_role, reason=reason)

        embed = discord.Embed(title="Mute Information", description=f"You have been muted in {interaction.guild.name}.", color=4915330)
        embed.add_field(name="Reasoning", value=reason if reason else "No Reason Provided.", inline=False)

        try:
            await user.send(embed=embed)
        except discord.Forbidden:
            await interaction.followup.send(f"Error: Could Not Message {user.name}. They May Have DMs Closed.", ephemeral=True)

        await interaction.response.send_message(f"Success: {user.name} Has Been Muted.", ephemeral=False)
        await send_punishment_log(interaction.guild, "User Muted", user, interaction.user, reason)

    @client.command(name="unmute")
    @commands.has_permissions(manage_roles=True)
    async def unmute(ctx, user: discord.Member):
        muted_role = discord.utils.get(ctx.guild.roles, name="Muted")

        if not muted_role:
            await ctx.send("Error: 'Muted' Role Not Found. Please Create One Or Use The 'mute-setup' Command")
            return

        if muted_role not in user.roles:
            await ctx.send(f"Error: {user.name} Is Not Muted.")
            return

        await user.remove_roles(muted_role)

        embed = discord.Embed(title="Unmute Information", description=f"You have been unmuted in {ctx.guild.name}.", color=4915330)

        try:
            await user.send(embed=embed)
        except discord.Forbidden:
            await ctx.send(f"Error: Could Not Message {user.name}. They May Have DMs Closed.")

        await ctx.send(f"Success: {user.name} Has Been Unmuted.")
        await send_punishment_log(ctx.guild, "User Unmuted", user, ctx.author, reason = None)

    @client.tree.command(name="unmute", description="Unmute A User In The Server")
    @app_commands.describe(user="User To Unmute")
    async def slash_unmute(interaction: discord.Interaction, user: discord.Member):
        muted_role = discord.utils.get(interaction.guild.roles, name="Muted")

        if not muted_role:
            await interaction.response.send_message("Error: 'Muted' Role Not Found. Please Create One Or Use The 'mute-setup' Command", ephemeral=True)
            return

        if muted_role not in user.roles:
            await interaction.response.send_message(f"Error: {user.name} Is Not Muted.", ephemeral=True)
            return

        await user.remove_roles(muted_role)

        embed = discord.Embed(title="Unmute Information", description=f"You have been unmuted in {interaction.guild.name}.", color=4915330)

        try:
            await user.send(embed=embed)
        except discord.Forbidden:
            await interaction.followup.send(f"Error: Could Not Message {user.name}. They May Have DMs Closed.", ephemeral=True)

        await interaction.response.send_message(f"Success: {user.name} Has Been Unmuted.")
        await send_punishment_log(interaction.guild, "User Unmuted", user, interaction.user, reason = None)


    @client.command(name = "setup-mute")
    @commands.has_permissions(manage_roles = True)
    async def setup_mute(ctx):
        muted_role = discord.utils.get(ctx.guild.roles, name="Muted")

        if muted_role:
            await ctx.send("Error: A Role Named 'Muted' Already Exists.")
            return

        try:
            muted_role = await ctx.guild.create_role(name="Muted", colour=discord.Colour(0x000001), reason="Muted role setup.")

            for channel in ctx.guild.channels:
                await channel.set_permissions(muted_role, 
                                            send_messages=False, 
                                            speak=False, 
                                            add_reactions=False,
                                            view_channel=True,
                                            read_message_history = True)

            await ctx.send("Success: 'Muted' Role Has Been Created And Configured.")
        except discord.Forbidden:
            await ctx.send("Error: Missing Permissions To Create Roles Or Edit Channel Permissions.")
        except Exception as e:
            await ctx.send(f"Error: An Unexpected Error Occurred. {str(e)}")

    @client.tree.command(name="setup-mute", description="Setup The Muted Role In The Server")
    async def slash_setup_mute(interaction: discord.Interaction):
        if not interaction.user.guild_permissions.manage_roles:
            await interaction.response.send_message("Error: You Do Not Have Permission To Run This Command.", ephemeral=True)
            return

        muted_role = discord.utils.get(interaction.guild.roles, name="Muted")

        if muted_role:
            await interaction.response.send_message("Error: A Role Named 'Muted' Already Exists.", ephemeral=True)
            return

        try:
            muted_role = await interaction.guild.create_role(name="Muted", colour=discord.Colour(0x000001), reason="Muted Role Setup.")

            for channel in interaction.guild.channels:
                await channel.set_permissions(muted_role, 
                                            send_messages=False, 
                                            speak=False, 
                                            add_reactions=False,
                                            view_channel=True,
                                            read_message_history=True)

            await interaction.response.send_message("Success: 'Muted' Role Has Been Created And Configured.")
        except discord.Forbidden:
            await interaction.response.send_message("Error: Missing Permissions To Create Roles Or Edit Channel Permissions.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"Error: An Unexpected Error Occurred. {str(e)}", ephemeral=True)

    @client.command(name="vcmute")
    @commands.has_permissions(mute_members=True)
    async def vcmute(ctx, target: discord.Member = None):
        voice = ctx.author.voice

        if not voice or not voice.channel:
            await ctx.send("You must be in a voice channel to use this command.")
            return

        vc = voice.channel

        if target:
            # Mute specific member
            if target in vc.members:
                await target.edit(mute=True)
                await ctx.send(f"🔇 {target.mention} has been server muted in {vc.name}.")
            else:
                await ctx.send(f"{target.display_name} is not in your voice channel.")
        else:
            # Mute everyone without Manage Messages permission
            muted = []
            for member in vc.members:
                if member.bot or member.guild_permissions.manage_messages:
                    continue
                try:
                    await member.edit(mute=True)
                    muted.append(member.display_name)
                except:
                    pass

            if muted:
                await ctx.send(f"🔇 Server muted: {', '.join(muted)}")
            else:
                await ctx.send("No users were muted. They may all have permissions or be bots.")

    @client.tree.command(name="vcmute", description="Mute users in the voice channel.")
    async def slash_vcmute(interaction: discord.Interaction, target: discord.Member = None):
        if not interaction.user.guild_permissions.mute_members:
            await interaction.response.send_message("You do not have permission to mute members.", ephemeral=True)
            return
        voice = interaction.user.voice

        if not voice or not voice.channel:
            await interaction.response.send_message("You must be in a voice channel to use this command.", ephemeral=True)
            return

        vc = voice.channel

        if target:
            # Mute specific member
            if target in vc.members:
                await target.edit(mute=True)
                await interaction.response.send_message(f"🔇 {target.mention} has been server muted in {vc.name}.", ephemeral=True)
            else:
                await interaction.response.send_message(f"{target.display_name} is not in your voice channel.", ephemeral=True)
        else:
            # Mute everyone without Manage Messages permission
            muted = []
            for member in vc.members:
                if member.bot or member.guild_permissions.manage_messages:
                    continue
                try:
                    await member.edit(mute=True)
                    muted.append(member.display_name)
                except:
                    pass

            if muted:
                await interaction.response.send_message(f"🔇 Server muted: {', '.join(muted)}", ephemeral=True)
            else:
                await interaction.response.send_message("No users were muted. They may all have permissions or be bots.", ephemeral=True)

    @client.tree.command(name="vcunmute", description="Server mute a targeted user.")
    async def slash_vcunmute(interaction: discord.Interaction, target: discord.Member = None):
        if not interaction.user.guild_permissions.mute_members:
            await interaction.response.send_message("You do not have permission to mute members.", ephemeral=True)
            return
        voice = interaction.user.voice

        if not voice or not voice.channel:
            await interaction.response.send_message("You must be in a voice channel to use this command.")
            return

        vc = voice.channel

        if target:
            # Unmute specific member
            if target in vc.members:
                await target.edit(mute=False)
                await interaction.response.send_message(f"🔊 {target.mention} has been unmuted in {vc.name}.")
            else:
                await interaction.response.send_message(f"{target.display_name} is not in your voice channel.")
        else:
            # Unmute everyone who is muted
            unmuted = []
            for member in vc.members:
                if member.bot or member.guild_permissions.manage_messages:
                    continue
                try:
                    # Only unmute if the user is currently muted
                    if member.mute:
                        await member.edit(mute=False)
                        unmuted.append(member.display_name)
                except discord.Forbidden:
                    pass

            if unmuted:
                await interaction.response.send_message(f"🔊 Unmuted: {', '.join(unmuted)}")
            else:
                await interaction.response.send_message("No users were unmuted. They may all have permissions, be bots, or not be muted.")

    @client.command(name="vcmutechannel")
    @commands.has_permissions(mute_members=True)
    async def vcmute_channel(ctx, channel: discord.VoiceChannel = None):
        if not channel:
            await ctx.send("You must provide a valid voice channel.")
            return

        muted = []
        for member in channel.members:
            if member.bot or member.guild_permissions.manage_messages:
                continue  # Skip bots and members with Manage Messages permission
            try:
                await member.edit(mute=True)
                muted.append(member.display_name)
            except:
                pass

        if muted:
            await ctx.send(f"🔇 Server muted in {channel.name}: {', '.join(muted)}")
        else:
            await ctx.send(f"No users were muted in {channel.name}. They may all have permissions or be bots.")

    @client.tree.command(name="vcmutechannel", description="Mute everyone in a specific voice channel.")
    @commands.has_permissions(mute_members=True)
    async def slash_vcmute_channel(interaction: discord.Interaction, channel: discord.VoiceChannel):
        if not channel:
            await interaction.response.send_message("You must provide a valid voice channel.", ephemeral=True)
            return

        muted = []
        for member in channel.members:
            if member.bot or member.guild_permissions.manage_messages:
                continue  # Skip bots and members with Manage Messages permission
            try:
                await member.edit(mute=True)
                muted.append(member.display_name)
            except:
                pass

        if muted:
            await interaction.response.send_message(f"🔇 Server muted in {channel.name}: {', '.join(muted)}")
        else:
            await interaction.response.send_message(f"No users were muted in {channel.name}. They may all have permissions or be bots.", ephemeral=True)

    @client.command(name="vcunmutechannel")
    @commands.has_permissions(mute_members=True)
    async def vcmute_channel(ctx, channel: discord.VoiceChannel):
        if not channel:
            await ctx.send("You must provide a valid voice channel.")
            return

        unmuted = []
        for member in channel.members:
            if member.bot or member.guild_permissions.manage_messages:
                continue  # Skip bots and members with Manage Messages permission
            try:
                await member.edit(mute=False)
                unmuted.append(member.display_name)
            except:
                pass

        if unmuted:
            await ctx.send(f"🔊 Server unmuted in {channel.name}: {', '.join(unmuted)}")
        else:
            await ctx.send(f"No users were unmuted in {channel.name}. They may all have permissions or be bots.")

    @client.tree.command(name="vcunmutechannel", description="Unmute everyone in a specific voice channel.")
    @commands.has_permissions(mute_members=True)
    async def slash_vcunmute_channel(interaction: discord.Interaction, channel: discord.VoiceChannel):
        if not channel:
            await interaction.response.send_message("You must provide a valid voice channel.", ephemeral=True)
            return

        unmuted = []
        for member in channel.members:
            if member.bot or member.guild_permissions.manage_messages:
                continue  # Skip bots and members with Manage Messages permission
            try:
                await member.edit(mute=False)
                unmuted.append(member.display_name)
            except:
                pass

        if unmuted:
            await interaction.response.send_message(f"🔊 Server unmuted in {channel.name}: {', '.join(unmuted)}")
        else:
            await interaction.response.send_message(f"No users were unmuted in {channel.name}. They may all have permissions or be bots.", ephemeral=True)

# · · ─────── ·𖥸· ─────── · · Log Setups · · ─────── ·𖥸· ─────── · ·
    @client.command(name="logs-setup")
    @commands.has_permissions(administrator=True)
    async def logs_setup(ctx, category_name: str, punishment_flag: str, purge_flag: str):
        # Convert flags to lowercase for consistency
        punishment_flag = punishment_flag.lower()
        purge_flag = purge_flag.lower()

        # Validate the flags to ensure they are either 'enable' or 'disable'
        if punishment_flag not in ["enable", "disable"] or purge_flag not in ["enable", "disable"]:
            await ctx.send("Error: Please use `enable` or `disable` for each log type.")
            return

        # Find or create the category
        category = discord.utils.get(ctx.guild.categories, name=category_name)
        if not category:
            category = await ctx.guild.create_category(name=category_name)

        # Only create the punishment channel if punishment logs are enabled
        punishment_channel = None
        if punishment_flag == "enable":
            punishment_channel = discord.utils.get(ctx.guild.text_channels, name="punishment-logs")
            if not punishment_channel:
                punishment_channel = await ctx.guild.create_text_channel("punishment-logs", category=category)

        # Only create the purge channel if purge logs are enabled
        purge_channel = None
        if purge_flag == "enable":
            purge_channel = discord.utils.get(ctx.guild.text_channels, name="purge-logs")
            if not purge_channel:
                purge_channel = await ctx.guild.create_text_channel("purge-logs", category=category)

        # Load the existing config or initialize an empty config
        try:
            with open("logs_config.json", "r") as f:
                config = json.load(f)
        except FileNotFoundError:
            config = {}

        guild_id = str(ctx.guild.id)
        config[guild_id] = {
            "punishment_logs_enabled": punishment_flag == "enable",
            "purge_logs_enabled": purge_flag == "enable",
            # Store channel IDs if they were created
            "punishment_channel_id": punishment_channel.id if punishment_channel else None,
            "purge_channel_id": purge_channel.id if purge_channel else None
        }

        # Save the updated config
        with open("logs_config.json", "w") as f:
            json.dump(config, f, indent=4)

        # Build the response message based on the flags
        response = f"Logs Setup Complete:\n- Punishment Logs: `{punishment_flag}`\n- Purge Logs: `{purge_flag}`"

        # Send confirmation message
        await ctx.send(response)


    @client.tree.command(name="logs-setup", description="Set up punishment and purge logs.")
    @app_commands.describe(
        category_name="The name of the category to create the log channels in",
        punishment_flag="Enable or disable punishment logs",
        purge_flag="Enable or disable purge logs"
    )
    async def slash_logs_setup(interaction: discord.Interaction, category_name: str, punishment_flag: str, purge_flag: str):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("Error: You Do Not Have Permission To Run This Command.", ephemeral=True)
            return
        # Convert flags to lowercase for consistency
        punishment_flag = punishment_flag.lower()
        purge_flag = purge_flag.lower()

        # Validate the flags to ensure they are either 'enable' or 'disable'
        if punishment_flag not in ["enable", "disable"] or purge_flag not in ["enable", "disable"]:
            await interaction.response.send_message("Error: Please use `enable` or `disable` for each log type.", ephemeral=True)
            return

        # Find or create the category
        category = discord.utils.get(interaction.guild.categories, name=category_name)
        if not category:
            category = await interaction.guild.create_category(name=category_name)

        # Only create the punishment channel if punishment logs are enabled
        punishment_channel = None
        if punishment_flag == "enable":
            punishment_channel = discord.utils.get(interaction.guild.text_channels, name="punishment-logs")
            if not punishment_channel:
                punishment_channel = await interaction.guild.create_text_channel("punishment-logs", category=category)

        # Only create the purge channel if purge logs are enabled
        purge_channel = None
        if purge_flag == "enable":
            purge_channel = discord.utils.get(interaction.guild.text_channels, name="purge-logs")
            if not purge_channel:
                purge_channel = await interaction.guild.create_text_channel("purge-logs", category=category)

        # Load the existing config or initialize an empty config
        try:
            with open("logs_config.json", "r") as f:
                config = json.load(f)
        except FileNotFoundError:
            config = {}

        guild_id = str(interaction.guild.id)
        config[guild_id] = {
            "punishment_logs_enabled": punishment_flag == "enable",
            "purge_logs_enabled": purge_flag == "enable",
            # Store channel IDs if they were created
            "punishment_channel_id": punishment_channel.id if punishment_channel else None,
            "purge_channel_id": purge_channel.id if purge_channel else None
        }

        # Save the updated config
        with open("logs_config.json", "w") as f:
            json.dump(config, f, indent=4)

        # Build the response message based on the flags
        response = f"Logs Setup Complete:\n- Punishment Logs: `{punishment_flag}`\n- Purge Logs: `{purge_flag}`"

        # Send confirmation message
        await interaction.response.send_message(response)


    @client.command(name="logs-disable")
    @commands.has_permissions(administrator=True)
    async def logs_disable(ctx, punishment: str = "disable", purge: str = "disable"):
        log_config = load_log_config()
        guild_id = str(ctx.guild.id)

        embed = discord.Embed(title="Logs Disabled", color=4915330)
        channels_deleted = []

        # Remove Punishment Logs if disabled
        if punishment.lower() == "disable" and guild_id in log_config:
            if "punishment_logs_enabled" in log_config[guild_id] and log_config[guild_id]["punishment_logs_enabled"]:
                punishment_channel_id = log_config[guild_id].get("punishment_channel_id")
                punishment_channel = discord.utils.get(ctx.guild.text_channels, id=punishment_channel_id)
                
                if punishment_channel:
                    await punishment_channel.delete()
                    channels_deleted.append("Punishment Logs")
                    print(f"Punishment logs channel '{punishment_channel.name}' deleted.")
                
                # Remove punishment log data from the config
                log_config[guild_id].pop("punishment_logs_enabled", None)
                log_config[guild_id].pop("punishment_channel_id", None)

        # Remove Purge Logs if disabled
        if purge.lower() == "disable" and guild_id in log_config:
            if "purge_logs_enabled" in log_config[guild_id] and log_config[guild_id]["purge_logs_enabled"]:
                purge_channel_id = log_config[guild_id].get("purge_channel_id")
                purge_channel = discord.utils.get(ctx.guild.text_channels, id=purge_channel_id)
                
                if purge_channel:
                    await purge_channel.delete()
                    channels_deleted.append("Purge Logs")
                    print(f"Purge logs channel '{purge_channel.name}' deleted.")
                
                # Remove purge log data from the config
                log_config[guild_id].pop("purge_logs_enabled", None)
                log_config[guild_id].pop("purge_channel_id", None)

        # Save the updated log config
        save_log_config(log_config)

        # Build response message
        if channels_deleted:
            embed.add_field(name="Deleted Channels", value=", ".join(channels_deleted), inline=False)
        else:
            embed.add_field(name="No Channels Were Deleted", value="No logs were disabled.", inline=False)

        # Send the response to the user
        await ctx.send(embed=embed)

        print("Log configurations have been updated and removed successfully.")


    @client.tree.command(name="logs-disable", description="Disable punishment and/or purge logs.")
    @app_commands.checks.has_permissions(administrator=True)
    async def slash_logs_disable(interaction: discord.Interaction, punishment: str = "disable", purge: str = "disable"):
        log_config = load_log_config()
        guild_id = str(interaction.guild.id)

        embed = discord.Embed(title="Logs Disabled", color=4915330)
        channels_deleted = []

        # Remove Punishment Logs if disabled
        if punishment.lower() == "disable" and guild_id in log_config:
            if "punishment_logs_enabled" in log_config[guild_id] and log_config[guild_id]["punishment_logs_enabled"]:
                punishment_channel_id = log_config[guild_id].get("punishment_channel_id")
                punishment_channel = discord.utils.get(interaction.guild.text_channels, id=punishment_channel_id)
                
                if punishment_channel:
                    await punishment_channel.delete()
                    channels_deleted.append("Punishment Logs")
                    print(f"Punishment logs channel '{punishment_channel.name}' deleted.")
                
                # Remove punishment log data from the config
                log_config[guild_id].pop("punishment_logs_enabled", None)
                log_config[guild_id].pop("punishment_channel_id", None)

        # Remove Purge Logs if disabled
        if purge.lower() == "disable" and guild_id in log_config:
            if "purge_logs_enabled" in log_config[guild_id] and log_config[guild_id]["purge_logs_enabled"]:
                purge_channel_id = log_config[guild_id].get("purge_channel_id")
                purge_channel = discord.utils.get(interaction.guild.text_channels, id=purge_channel_id)
                
                if purge_channel:
                    await purge_channel.delete()
                    channels_deleted.append("Purge Logs")
                    print(f"Purge logs channel '{purge_channel.name}' deleted.")
                
                # Remove purge log data from the config
                log_config[guild_id].pop("purge_logs_enabled", None)
                log_config[guild_id].pop("purge_channel_id", None)

        # Save the updated log config
        save_log_config(log_config)

        # Build response message
        if channels_deleted:
            embed.add_field(name="Deleted Channels", value=", ".join(channels_deleted), inline=False)
        else:
            embed.add_field(name="No Channels Were Deleted", value="No logs were disabled.", inline=False)

        # Send the response to the user
        await interaction.response.send_message(embed=embed)

        print("Log configurations have been updated and removed successfully.")


# · · ─────── ·𖥸· ─────── · · Warning Commands · · ─────── ·𖥸· ─────── · ·
    @client.command(name="warn")
    @commands.has_permissions(manage_messages=True)
    async def warn(ctx, user: discord.User, *, reason: str = None):
        # Load the warnings data
        warnings_data = load_warnings()

        # Prepare the warning information
        if str(user.id) not in warnings_data:
            warnings_data[str(user.id)] = []

        # Create the warning and send punishment log
        message_id = await send_punishment_log(ctx.guild, "User Warned", user, ctx.author, reason)

        if message_id:
            # Add the new warning to the user's list of warnings with the message_id
            warnings_data[str(user.id)].append({
                "reason": reason,
                "message_id": message_id
            })

            # Save the updated warnings data
            save_warnings(warnings_data)

            # Notify the user and moderator
            await ctx.send(f"{user.mention} has been warned for: {reason}")
            await user.send(f"You have been warned in {ctx.guild.name} for: {reason}")
        else:
            await ctx.send("Error: Punishment log channel does not exist.")

    @client.command(name="remove-warning")
    @commands.has_permissions(manage_channels=True)
    async def remove_warning(ctx, user: discord.User, warning_number: int, *, reason: str = None):
        # Load the warnings data
        warnings_data = load_warnings()

        # Get the user's warnings
        user_warnings = warnings_data.get(str(user.id), [])

        # Check if the warning number is valid
        if warning_number > len(user_warnings) or warning_number <= 0:
            await ctx.send(f"Error: Invalid warning number. {user.mention} has only {len(user_warnings)} warnings.")
            return

        # Get the warning to be removed
        warning_to_remove = user_warnings[warning_number - 1]
        message_id = warning_to_remove["message_id"]

        # Remove the warning from the list
        user_warnings.pop(warning_number - 1)

        # Update the user's warnings in the JSON file
        warnings_data[str(user.id)] = user_warnings
        save_warnings(warnings_data)

        # **Delete the punishment log message** using the saved message_id
        punishment_channel = discord.utils.get(ctx.guild.text_channels, name="punishment-logs")
        if punishment_channel:
            try:
                # Fetch the punishment log message by its message_id
                punishment_log_message = await punishment_channel.fetch_message(message_id)
                
                # Delete the punishment log message
                await punishment_log_message.delete()
                print(f"Punishment log message {message_id} deleted in {punishment_channel.name}.")
            
            except discord.NotFound:
                print(f"Punishment log message {message_id} not found.")
            except discord.Forbidden:
                print(f"Bot does not have permission to delete messages in the punishment logs channel.")

        # Log the removal action in punishment logs (if implemented)
        await send_punishment_log(ctx.guild, "Warning Removed", user, ctx.author, reason)

        # Notify the user
        await ctx.send(f"Warning {warning_number} for {user.mention} has been removed.")


    @client.command(name="warns")
    @commands.has_permissions(manage_messages=True)
    async def warns(ctx, user: discord.User = None):
        # Default to the message author if no user is provided
        if not user:
            user = ctx.author

        # Load the warnings data
        warnings_data = load_warnings()

        # Check if the user has any warnings
        if str(user.id) not in warnings_data or not warnings_data[str(user.id)]:
            await ctx.send(f"{user.mention} has no warnings.")
            return

        # Get the list of warnings for the user
        user_warnings = warnings_data[str(user.id)]

        # Create an embed to display the warnings
        embed = discord.Embed(title=f"Warnings for {user}", color=4915330)

        # Add each warning to the embed
        for idx, warning in enumerate(user_warnings, start=1):
            embed.add_field(name=f"Warning {idx}", value=warning.get("reason", "No reason provided."), inline=False)

        # Send the embed with the warnings
        await ctx.send(embed=embed)


    @client.tree.command(name="warn", description="Warn a user in the server.")
    @app_commands.describe(
        user="The user to warn",
        reason="The reason for the warning"
    )
    async def slash_warn(interaction: discord.Interaction, user: discord.User, reason: str = None):
        if not interaction.user.guild_permissions.manage_messages:
            await interaction.response.send_message("Error: You Do Not Have Permission To Run This Command.", ephemeral=True)
            return
        # Load the warnings data
        warnings_data = load_warnings()

        # Prepare the warning information
        if str(user.id) not in warnings_data:
            warnings_data[str(user.id)] = []

        # Create the warning and send punishment log
        message_id = await send_punishment_log(interaction.guild, "User Warned", user, interaction.user, reason)

        if message_id:
            # Add the new warning to the user's list of warnings with the message_id
            warnings_data[str(user.id)].append({
                "reason": reason,
                "message_id": message_id
            })

            # Save the updated warnings data
            save_warnings(warnings_data)

            # Notify the user and moderator
            await interaction.response.send_message(f"{user.mention} has been warned for: {reason}")
            await user.send(f"You have been warned in {interaction.guild.name} for: {reason}")
        else:
            await interaction.response.send_message("Error: Punishment log channel does not exist.")

    @client.tree.command(name="remove-warning", description="Remove a specific warning from a user.")
    @app_commands.describe(
        user="The user to remove a warning from",
        warning_number="The number of the warning to remove",
        reason="The reason for removing the warning"
    )
    async def slash_remove_warning(interaction: discord.Interaction, user: discord.User, warning_number: int, reason: str = None):
        if not interaction.user.guild_permissions.manage_messages:
            await interaction.response.send_message("Error: You Do Not Have Permission To Run This Command.", ephemeral=True)
            return
        # Load the warnings data
        warnings_data = load_warnings()

        # Get the user's warnings
        user_warnings = warnings_data.get(str(user.id), [])

        # Check if the warning number is valid
        if warning_number > len(user_warnings) or warning_number <= 0:
            await interaction.response.send_message(f"Error: Invalid warning number. {user.mention} has only {len(user_warnings)} warnings.")
            return

        # Get the warning to be removed
        warning_to_remove = user_warnings[warning_number - 1]
        message_id = warning_to_remove["message_id"]

        # Remove the warning from the list
        user_warnings.pop(warning_number - 1)

        # Update the user's warnings in the JSON file
        warnings_data[str(user.id)] = user_warnings
        save_warnings(warnings_data)

        # **Delete the punishment log message** using the saved message_id
        punishment_channel = discord.utils.get(interaction.guild.text_channels, name="punishment-logs")
        if punishment_channel:
            try:
                # Fetch the punishment log message by its message_id
                punishment_log_message = await punishment_channel.fetch_message(message_id)
                
                # Delete the punishment log message
                await punishment_log_message.delete()
                print(f"Punishment log message {message_id} deleted in {punishment_channel.name}.")
            
            except discord.NotFound:
                print(f"Punishment log message {message_id} not found.")
            except discord.Forbidden:
                print(f"Bot does not have permission to delete messages in the punishment logs channel.")

        # Log the removal action in punishment logs (if implemented)
        await send_punishment_log(interaction.guild, "Warning Removed", user, interaction.user, reason)

        # Notify the user
        await interaction.response.send_message(f"Warning {warning_number} for {user.mention} has been removed.")

    @client.tree.command(name="warns", description="View the warnings of a user.")
    @app_commands.describe(
        user="The user whose warnings you want to view"
    )
    async def slash_warns(interaction: discord.Interaction, user: discord.User = None):
        # Default to the message author if no user is provided
        if not user:
            user = interaction.user

        # Load the warnings data
        warnings_data = load_warnings()

        # Check if the user has any warnings
        if str(user.id) not in warnings_data or not warnings_data[str(user.id)]:
            await interaction.response.send_message(f"{user.mention} has no warnings.")
            return

        # Get the list of warnings for the user
        user_warnings = warnings_data[str(user.id)]

        # Create an embed to display the warnings
        embed = discord.Embed(title=f"Warnings for {user}", color=4915330)

        # Add each warning to the embed
        for idx, warning in enumerate(user_warnings, start=1):
            embed.add_field(name=f"Warning {idx}", value=warning.get("reason", "No reason provided."), inline=False)

        # Send the embed with the warnings
        await interaction.response.send_message(embed=embed)

# · · ─────── ·𖥸· ─────── · · Points Commands · · ─────── ·𖥸· ─────── · ·
    @client.command(name = "points")
    async def points(ctx, user: discord.User = None):
        if user is None:
            user = ctx.author

        if user.bot:
            await ctx.send("Bot's Don't Earn Points, Get Outta Here Stinky.")
            return
        
        points_data = load_points()
        user_points = points_data.get(str(user.id), 0)

        embed = discord.Embed(
            title=f"{user.name}'s Points",
            description=f"{user.mention} has **{user_points}** points. Within {ctx.guild.name}",
            color=4915330
        )

        if ctx.guild.icon:
            embed.set_thumbnail(url=ctx.guild.icon.url)

        embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.display_avatar.url)

        await ctx.send(embed=embed)

    @client.command(name="setpoints")
    @commands.has_permissions(administrator=True)
    async def setpoints(ctx, target: str, points: int):
        points_data = load_points()

        if target == "`E$":
            count = 0
            for member in ctx.guild.members:
                if not member.bot and not member.system:
                    points_data[str(member.id)] = points
                    count += 1

            save_points(points_data)
            await ctx.send(f"✅ Set **{points}** points for **{count}** members in this server.")
            return

        try:
            # Convert to User object
            member = await commands.UserConverter().convert(ctx, target)
        except commands.BadArgument:
            await ctx.send("❌ Invalid user.")
            return

        if member.bot or member.system:
            await ctx.send("❌ Cannot set points for bots or system users.")
            return

        points_data[str(member.id)] = points
        save_points(points_data)
        await ctx.send(f"✅ Set **{points}** points for {member.mention}.")

    @client.command(name="addpoints")
    @commands.has_permissions(administrator=True)
    async def addpoints(ctx, user_or_everyone: str, amount: int):
        if amount <= 0:
            await ctx.send("Amount must be greater than zero.")
            return

        # Load points
        try:
            with open("points.json", "r") as f:
                points = json.load(f)
        except FileNotFoundError:
            points = {}

        added_to = []

        # Add points to everyone
        if user_or_everyone == "`E$":
            for member in ctx.guild.members:
                if member.bot or member.system:
                    continue
                points[str(member.id)] = points.get(str(member.id), 0) + amount
                added_to.append(str(member))

            with open("points.json", "w") as f:
                json.dump(points, f, indent=4)

            embed = discord.Embed(
                title="Points Added Server-wide",
                description=f"Added `{amount}` points to all members (excluding bots and webhooks).",
                color=discord.Color.green()
            )
            embed.set_thumbnail(url=ctx.guild.icon.url if ctx.guild.icon else discord.Embed.Empty)
            await ctx.send(embed=embed)

        else:
            # Try to parse user
            try:
                user = await commands.MemberConverter().convert(ctx, user_or_everyone)
            except commands.BadArgument:
                await ctx.send("Could not find that user.")
                return

            if user.bot or user.system:
                await ctx.send("You can't add points to bots or system users.")
                return

            points[str(user.id)] = points.get(str(user.id), 0) + amount
            with open("points.json", "w") as f:
                json.dump(points, f, indent=4)

            embed = discord.Embed(
                title="Points Added",
                description=f"Added `{amount}` points to {user.mention}.",
                color=discord.Color.green()
            )
            embed.set_thumbnail(url=ctx.guild.icon.url if ctx.guild.icon else discord.Embed.Empty)
            await ctx.send(embed=embed)

    @client.command(name="removepoints")
    @commands.has_permissions(administrator=True)
    async def removepoints(ctx, user_or_everyone: str, amount: int):
        if amount <= 0:
            await ctx.send("Amount must be greater than zero.")
            return

        # Load points
        try:
            with open("points.json", "r") as f:
                points = json.load(f)
        except FileNotFoundError:
            points = {}

        removed_from = []

        if user_or_everyone == "`E$":
            for member in ctx.guild.members:
                if member.bot or member.system:
                    continue

                user_id = str(member.id)
                points[user_id] = max(0, points.get(user_id, 0) - amount)
                removed_from.append(member.display_name)

            with open("points.json", "w") as f:
                json.dump(points, f, indent=4)

            embed = discord.Embed(
                title="Points Removed Server-wide",
                description=f"Removed `{amount}` points from all members (excluding bots/system users).",
                color=discord.Color.red()
            )
            embed.set_thumbnail(url=ctx.guild.icon.url if ctx.guild.icon else discord.Embed.Empty)
            await ctx.send(embed=embed)

        else:
            # Convert the user argument to a Member object
            try:
                user = await commands.MemberConverter().convert(ctx, user_or_everyone)
            except commands.BadArgument:
                await ctx.send("Could not find that user.")
                return

            if user.bot or user.system:
                await ctx.send("You can't remove points from bots or system users.")
                return

            user_id = str(user.id)
            points[user_id] = max(0, points.get(user_id, 0) - amount)

            with open("points.json", "w") as f:
                json.dump(points, f, indent=4)

            embed = discord.Embed(
                title="Points Removed",
                description=f"Removed `{amount}` points from {user.mention}.",
                color=discord.Color.red()
            )
            embed.set_thumbnail(url=ctx.guild.icon.url if ctx.guild.icon else discord.Embed.Empty)
            await ctx.send(embed=embed)

    @client.command(name="give")
    async def give(ctx, user: discord.Member, amount: int):
        if user.bot or user.system:
            await ctx.send("You can't give points to bots or system users.")
            return

        if amount <= 0:
            await ctx.send("Amount must be greater than zero.")
            return

        giver_id = str(ctx.author.id)
        receiver_id = str(user.id)

        # Load points
        try:
            with open("points.json", "r") as f:
                points = json.load(f)
        except FileNotFoundError:
            points = {}

        # Ensure users exist in the points dictionary
        giver_points = points.get(giver_id, 0)
        receiver_points = points.get(receiver_id, 0)

        if giver_points < amount:
            await ctx.send(f"You don't have enough points to give. You currently have `{giver_points}`.")
            return

        # Transfer points
        points[giver_id] = giver_points - amount
        points[receiver_id] = receiver_points + amount

        # Save updated points
        with open("points.json", "w") as f:
            json.dump(points, f, indent=4)

        # Create response embed
        embed = discord.Embed(
            title="Points Transferred",
            description=f"{ctx.author.mention} gave `{amount}` points to {user.mention}.",
            color=discord.Color.green()
        )
        embed.set_thumbnail(url=ctx.guild.icon.url if ctx.guild.icon else discord.Embed.Empty)
        await ctx.send(embed=embed)

    @client.tree.command(name="points", description="Check your points or someone else's.")
    @app_commands.describe(user="Leave blank to check yourself.")
    async def slash_points(interaction: discord.Interaction, user: discord.User = None):
        await interaction.response.defer()
        user = user or interaction.user

        if user.bot:
            await interaction.followup.send("Bots don't earn points.")
            return

        points_data = load_points()
        points = points_data.get(str(user.id), 0)

        embed = discord.Embed(
            title=f"{user.name}'s Points",
            description=f"{user.mention} has **{points}** points in **{interaction.guild.name}**.",
            color=discord.Color.blurple()
        )
        if interaction.guild.icon:
            embed.set_thumbnail(url=interaction.guild.icon.url)

        embed.set_footer(text=f"Requested by {interaction.user}", icon_url=interaction.user.display_avatar.url)
        await interaction.followup.send(embed=embed)

    # --- /setpoints ---
    @client.tree.command(name="setpoints", description="Set points for a user or everyone (E$).")
    @app_commands.describe(target="Mention a user or type E$ for everyone", points="Points to set")
    async def slash_setpoints(interaction: discord.Interaction, target: str, points: int):
        await interaction.response.defer()
        if not interaction.user.guild_permissions.administrator:
            await interaction.followup.send("❌ You don't have permission.")
            return

        points_data = load_points()

        if target == "`E$":
            count = 0
            for member in interaction.guild.members:
                if not member.bot and not member.system:
                    points_data[str(member.id)] = points
                    count += 1
            save_points(points_data)
            await interaction.followup.send(f"✅ Set **{points}** points for **{count}** members.")
            return

        try:
            member = await commands.MemberConverter().convert(interaction, target)
        except commands.BadArgument:
            await interaction.followup.send("❌ Invalid user.")
            return

        if member.bot or member.system:
            await interaction.followup.send("❌ Cannot set points for bots or system users.")
            return

        points_data[str(member.id)] = points
        save_points(points_data)
        await interaction.followup.send(f"✅ Set **{points}** points for {member.mention}.")


    @client.tree.command(name="addpoints", description="Add points to a user or everyone (E$).")
    @app_commands.describe(user_or_everyone="User to add points to or E$ for everyone", amount="Amount of points to add")
    async def slash_addpoints(interaction: discord.Interaction, user_or_everyone: str, amount: int):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ You don't have permission.", ephemeral=True)
            return

        if amount <= 0:
            await interaction.response.send_message("Amount must be greater than zero.", ephemeral=True)
            return

        points_data = load_points()

        added_to = []

        if user_or_everyone == "`E$":
            for member in interaction.guild.members:
                if member.bot or member.system:
                    continue
                points_data[str(member.id)] = points_data.get(str(member.id), 0) + amount
                added_to.append(str(member))

            save_points(points_data)

            embed = discord.Embed(
                title="Points Added Server-wide",
                description=f"Added `{amount}` points to all members (excluding bots and system users).",
                color=discord.Color.green()
            )
            embed.set_thumbnail(url=interaction.guild.icon.url if interaction.guild.icon else discord.Embed.Empty)
            await interaction.response.send_message(embed=embed)

        else:
            try:
                user = await commands.MemberConverter().convert(interaction, user_or_everyone)
            except commands.BadArgument:
                await interaction.response.send_message("❌ Could not find that user.", ephemeral=True)
                return

            if user.bot or user.system:
                await interaction.response.send_message("❌ You can't add points to bots or system users.", ephemeral=True)
                return

            points_data[str(user.id)] = points_data.get(str(user.id), 0) + amount
            save_points(points_data)

            embed = discord.Embed(
                title="Points Added",
                description=f"Added `{amount}` points to {user.mention}.",
                color=discord.Color.green()
            )
            embed.set_thumbnail(url=interaction.guild.icon.url if interaction.guild.icon else discord.Embed.Empty)
            await interaction.response.send_message(embed=embed)

    @client.tree.command(name="removepoints", description="Remove points from a user or everyone (E$).")
    @app_commands.describe(user_or_everyone="User to remove points from or E$ for everyone", amount="Amount of points to remove")
    async def slash_removepoints(interaction: discord.Interaction, user_or_everyone: str, amount: int):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ You don't have permission.", ephemeral=True)
            return

        if amount <= 0:
            await interaction.response.send_message("Amount must be greater than zero.", ephemeral=True)
            return

        points_data = load_points()

        removed_from = []

        if user_or_everyone == "`E$":
            for member in interaction.guild.members:
                if member.bot or member.system:
                    continue
                user_id = str(member.id)
                points_data[user_id] = max(0, points_data.get(user_id, 0) - amount)
                removed_from.append(member.display_name)

            save_points(points_data)

            embed = discord.Embed(
                title="Points Removed Server-wide",
                description=f"Removed `{amount}` points from all members (excluding bots and system users).",
                color=discord.Color.red()
            )
            embed.set_thumbnail(url=interaction.guild.icon.url if interaction.guild.icon else discord.Embed.Empty)
            await interaction.response.send_message(embed=embed)

        else:
            try:
                user = await commands.MemberConverter().convert(interaction, user_or_everyone)
            except commands.BadArgument:
                await interaction.response.send_message("❌ Could not find that user.", ephemeral=True)
                return

            if user.bot or user.system:
                await interaction.response.send_message("❌ You can't remove points from bots or system users.", ephemeral=True)
                return

            user_id = str(user.id)
            points_data[user_id] = max(0, points_data.get(user_id, 0) - amount)

            save_points(points_data)

            embed = discord.Embed(
                title="Points Removed",
                description=f"Removed `{amount}` points from {user.mention}.",
                color=discord.Color.red()
            )
            embed.set_thumbnail(url=interaction.guild.icon.url if interaction.guild.icon else discord.Embed.Empty)
            await interaction.response.send_message(embed=embed)

    @client.tree.command(name="give", description="Give your points to another user.")
    @app_commands.describe(user="The user to give points to", amount="Amount of points to give")
    async def slash_give(interaction: discord.Interaction, user: discord.Member, amount: int):
        if user.bot or user.system:
            await interaction.response.send_message("You can't give points to bots or system users.", ephemeral=True)
            return

        if amount <= 0:
            await interaction.response.send_message("Amount must be greater than zero.", ephemeral=True)
            return

        giver_id = str(interaction.user.id)
        receiver_id = str(user.id)

        # Load points
        try:
            with open("points.json", "r") as f:
                points = json.load(f)
        except FileNotFoundError:
            points = {}

        # Ensure users exist in the points dictionary
        giver_points = points.get(giver_id, 0)
        receiver_points = points.get(receiver_id, 0)

        if giver_points < amount:
            await interaction.response.send_message(
                f"You don't have enough points to give. You currently have `{giver_points}`.",
                ephemeral=True
            )
            return

        # Transfer points
        points[giver_id] = giver_points - amount
        points[receiver_id] = receiver_points + amount

        # Save updated points
        with open("points.json", "w") as f:
            json.dump(points, f, indent=4)

        # Create response embed
        embed = discord.Embed(
            title="Points Transferred",
            description=f"{interaction.user.mention} gave `{amount}` points to {user.mention}.",
            color=discord.Color.green()
        )
        embed.set_thumbnail(url=interaction.guild.icon.url if interaction.guild.icon else discord.Embed.Empty)

        await interaction.response.send_message(embed=embed)

# · · ─────── ·𖥸· ─────── · · Leaderboard Commands · · ─────── ·𖥸· ─────── · ·
    @client.command(name="leaderboard")
    async def leaderboard(ctx):
        points_data = load_points()

        sorted_users = sorted(points_data.items(), key=lambda x: x[1], reverse=True)
        top_users = sorted_users[:10]

        leaderboard_message = "🏆 **Top 10 Users with the Most Points** 🏆\n\n"
        for index, (user_id, points) in enumerate(top_users, start=1):
            user = ctx.guild.get_member(int(user_id))  # Get the member from the guild
            if user:
                leaderboard_message += f"{index}. **{user.name}**: {points} points\n"
            else:
                leaderboard_message += f"{index}. **User #{user_id}**: {points} points\n"

        embed = discord.Embed(
            title="Leaderboard",
            description=leaderboard_message,
            color=4915330
        )
        embed.set_thumbnail(url=ctx.guild.icon.url if ctx.guild.icon else discord.Embed.Empty)
        await ctx.send(embed=embed)

    @client.tree.command(name="leaderboard", description="Shows the top 10 users with the most points.")
    async def slash_leaderboard(interaction: discord.Interaction):
        points_data = load_points()

        # Sort users by points in descending order
        sorted_users = sorted(points_data.items(), key=lambda x: x[1], reverse=True)

        # Get the top 10 users
        top_users = sorted_users[:10]

        # Build the leaderboard message
        leaderboard_message = "🏆 **Top 10 Users with the Most Points** 🏆\n\n"
        for index, (user_id, points) in enumerate(top_users, start=1):
            user = interaction.guild.get_member(int(user_id))  # Get the member from the guild
            if user:
                leaderboard_message += f"{index}. **{user.name}**: {points} points\n"
            else:
                leaderboard_message += f"{index}. **User #{user_id}**: {points} points\n"

        # Send the leaderboard message
        embed = discord.Embed(
            title="Leaderboard",
            description=leaderboard_message,
            color=discord.Color.blue()
        )
        embed.set_thumbnail(url=interaction.guild.icon.url if interaction.guild.icon else discord.Embed.Empty)
        
        await interaction.response.send_message(embed=embed)

# · · ─────── ·𖥸· ─────── · · Avatar Commands  · · ─────── ·𖥸· ─────── · ·
    @client.command(name="avatar")
    async def avatar(ctx, user: discord.User = None):
        if user is None:
            user = ctx.author  # Default to the message author if no user is provided

        embed = discord.Embed(color=discord.Color.from_rgb(75, 0, 130))  # Set the color
        embed.set_image(url=user.display_avatar.url)  # Set the avatar image in the embed
        await ctx.send(embed=embed)

    @client.command(name="serveravatar")
    async def serveravatar(ctx):
        embed = discord.Embed()
        embed.set_image(url=ctx.guild.icon.url)  # Set the guild's icon in the embed
        await ctx.send(embed=embed)

    @client.tree.command(name="avatar", description="Displays the avatar of a targeted user or yourself.")
    async def slash_avatar(interaction: discord.Interaction, user: discord.User = None):
        if user is None:
            user = interaction.user  # Default to the user who invoked the command if no user is provided

        embed = discord.Embed(color=discord.Color.from_rgb(75, 0, 130))  # Set the color
        embed.set_image(url=user.display_avatar.url)  # Set the avatar image in the embed
        await interaction.response.send_message(embed=embed)
    
    @client.tree.command(name="serveravatar", description="Displays the server avatar.")
    async def slash_serveravatar(interaction: discord.Interaction):
        embed = discord.Embed()
        embed.set_image(url=interaction.guild.icon.url)  # Set the guild's icon in the embed
        await interaction.response.send_message(embed=embed)

# · · ─────── ·𖥸· ─────── · · Server Info  · · ─────── ·𖥸· ─────── · ·
    @client.command(name="serverinfo")
    async def serverinfo(ctx):
        guild = ctx.guild

        # Create Embed
        embed = discord.Embed(
            title=None,
            color=discord.Color.from_rgb(75, 0, 130),
            description=f"Information about **{guild.name}**"
        )
        
        embed.set_author(name=guild.name, icon_url=guild.icon.url)
        embed.set_thumbnail(url=guild.icon.url)

        embed.add_field(name="Owner", value=guild.owner.name, inline=True)
        embed.add_field(name="Members", value=str(len(guild.members)), inline=True)
        embed.add_field(name="Roles", value=str(len(guild.roles)), inline=True)
        embed.add_field(name="Categories", value=str(len(guild.categories)), inline=True)
        embed.add_field(name="Text Channels", value=str(len(guild.text_channels)), inline=True)
        embed.add_field(name="Voice Channels", value=str(len(guild.voice_channels)), inline=True)

        # Boost info
        boost_count = guild.premium_subscription_count
        boost_tier = guild.premium_tier
        boost_tier_str = ["No Boosts", "Tier 1", "Tier 2", "Tier 3"][boost_tier]
        embed.add_field(name="Boosts", value=f"{boost_count} Boosts - {boost_tier_str}", inline=True)

        embed.set_footer(text=f"Server ID: {guild.id} | Created on: {guild.created_at.strftime('%d/%m/%Y %H:%M')}")

        if guild.banner:
            embed.set_image(url=guild.banner.url)

        # View for buttons
        view = View()

        # Emotes button (always shown)
        emotes_button = Button(label="View Emotes", style=discord.ButtonStyle.primary)

        async def emotes_button_callback(interaction: discord.Interaction):
            emotes_list = "\n".join([f"<:{emoji.name}:{emoji.id}>" for emoji in guild.emojis])
            if not emotes_list:
                emotes_list = "No custom emotes found."
            await interaction.response.send_message(f"Emotes in {guild.name}:\n{emotes_list}", ephemeral=True)

        emotes_button.callback = emotes_button_callback
        view.add_item(emotes_button)

        # Roles button (only if user is admin)
        if ctx.author.guild_permissions.administrator:
            roles_button = Button(label="View Roles", style=discord.ButtonStyle.primary)

            async def roles_button_callback(interaction: discord.Interaction):
                roles_list = "\n".join([role.name for role in guild.roles if role != guild.default_role])
                await interaction.response.send_message(f"Roles in {guild.name}:\n{roles_list}", ephemeral=True)

            roles_button.callback = roles_button_callback
            view.add_item(roles_button)

        await ctx.send(embed=embed, view=view)

    @client.tree.command(name="serverinfo", description="Get detailed information about the server.")
    async def slash_serverinfo(ctx: discord.Interaction):
        guild = ctx.guild

        # Create Embed
        embed = discord.Embed(
            title=None,
            color=discord.Color.from_rgb(75, 0, 130),
            description=f"Information about **{guild.name}**"
        )

        embed.set_author(name=guild.name, icon_url=guild.icon.url)
        embed.set_thumbnail(url=guild.icon.url)

        embed.add_field(name="Owner", value=guild.owner.name, inline=True)
        embed.add_field(name="Members", value=str(len(guild.members)), inline=True)
        embed.add_field(name="Roles", value=str(len(guild.roles)), inline=True)
        embed.add_field(name="Categories", value=str(len(guild.categories)), inline=True)
        embed.add_field(name="Text Channels", value=str(len(guild.text_channels)), inline=True)
        embed.add_field(name="Voice Channels", value=str(len(guild.voice_channels)), inline=True)

        boost_count = guild.premium_subscription_count
        boost_tier = guild.premium_tier
        boost_tier_str = ["No Boosts", "Tier 1", "Tier 2", "Tier 3"][boost_tier]
        embed.add_field(name="Boosts", value=f"{boost_count} Boosts - {boost_tier_str}", inline=True)

        embed.set_footer(text=f"Server ID: {guild.id} | Created on: {guild.created_at.strftime('%d/%m/%Y %H:%M')}")
        
        if guild.banner:
            embed.set_image(url=guild.banner.url)

        # Create view for buttons
        view = View()

        # Emotes button (always shown)
        emotes_button = Button(label="View Emotes", style=discord.ButtonStyle.primary)

        async def emotes_button_callback(interaction: discord.Interaction):
            emotes_list = "\n".join([f"<:{emoji.name}:{emoji.id}>" for emoji in guild.emojis])
            if not emotes_list:
                emotes_list = "No custom emotes found."
            await interaction.response.send_message(f"Emotes in {guild.name}:\n{emotes_list}", ephemeral=True)

        emotes_button.callback = emotes_button_callback
        view.add_item(emotes_button)

        # Roles button (only if user is admin)
        if ctx.user.guild_permissions.administrator:
            roles_button = Button(label="View Roles", style=discord.ButtonStyle.primary)

            async def roles_button_callback(interaction: discord.Interaction):
                roles_list = "\n".join([role.name for role in guild.roles if role != guild.default_role])
                await interaction.response.send_message(f"Roles in {guild.name}:\n{roles_list}", ephemeral=True)

            roles_button.callback = roles_button_callback
            view.add_item(roles_button)

        await ctx.response.send_message(embed=embed, view=view)

# · · ─────── ·𖥸· ─────── · · User Info  · · ─────── ·𖥸· ─────── · ·
    @client.command(name="userinfo")
    async def userinfo(ctx, member: discord.Member = None):
        member = member or ctx.author  # Default to the command author if no member is provided

        embed = discord.Embed(
            description=None,
            color=discord.Color.from_rgb(75, 0, 130)
        )

        # Set author with user name and avatar
        embed.set_author(name=member.name, icon_url=member.display_avatar.url)

        # Roles
        roles = [role.mention for role in member.roles if role != ctx.guild.default_role]
        roles_text = ", ".join(roles) if roles else "No roles"

        # Add fields
        embed.add_field(name="Roles", value=roles_text, inline=False)
        embed.add_field(name="User ID", value=member.id, inline=True)
        embed.add_field(name="Display Name", value=member.display_name, inline=True)

        # Footer with account creation date
        embed.set_footer(text=f"Account Created: {member.created_at.strftime('%d/%m/%Y %H:%M')}")

        await ctx.send(embed=embed)

    @client.tree.command(name="userinfo", description="Displays the information on a targeted user or yourself")
    async def slash_userinfo(interaction: discord.Interaction, member: discord.Member = None):
        member = member or interaction.user  # Default to the command author if no member is provided

        embed = discord.Embed(
            description=None,
            color=discord.Color.from_rgb(75, 0, 130)
        )

        # Set author with user name and avatar
        embed.set_author(name=member.name, icon_url=member.display_avatar.url)

        # Roles
        roles = [role.mention for role in member.roles if role != interaction.guild.default_role]
        roles_text = ", ".join(roles) if roles else "No roles"

        # Add fields
        embed.add_field(name="Roles", value=roles_text, inline=False)
        embed.add_field(name="User ID", value=member.id, inline=True)
        embed.add_field(name="Display Name", value=member.display_name, inline=True)

        # Footer with account creation date
        embed.set_footer(text=f"Account Created: {member.created_at.strftime('%d/%m/%Y %H:%M')}")

        # Send the embed
        await interaction.response.send_message(embed=embed)

# · · ─────── ·𖥸· ─────── · · Gamba Commands  · · ─────── ·𖥸· ─────── · ·
    @client.command(name="gamble")
    async def gamble(ctx, amount: str):
        points_data = load_points()
        user_points = points_data.get(str(ctx.author.id), 0)

        if amount.endswith('%'):
            try:
                percentage = int(amount[:-1]) 
                if percentage < 1 or percentage > 100:
                    await ctx.send("Error: Please Enter A Valid Percentage")
                    return

                gamble_amount = int(user_points * (percentage / 100))
            except ValueError:
                await ctx.send("Error: Please Enter A Valid Percentage Or Number, Please Enter A Valid Percentage (e.g., 50%).")
                return
            
        else:
            try:
                gamble_amount = int(amount)
            except ValueError:
                await ctx.send("Error: Please Enter A Valid Percentage Or Number")
                return
            
        if gamble_amount > user_points:
            await ctx.send(f"Error: You Don't Have Enough Points To Gamble {gamble_amount}, You Only Have {user_points}.")
            return
        
        result = random.choice(["win", "lose"])

        if result == "win":
            new_points = user_points + gamble_amount  
            points_data[str(ctx.author.id)] = new_points
            save_points(points_data)
            await ctx.send(f"🎉 You Rule! You Now Have **{new_points}** Points!")
        else:
            new_points = user_points - gamble_amount
            points_data[str(ctx.author.id)] = new_points
            save_points(points_data)
            await ctx.send(f"😔 You Suck! You Now Only Have **{new_points}** Points.")

    @client.tree.command(name="gamble", description="Gamble points (or a percentage of them) for a 50/50 chance to double your points.")
    @app_commands.describe(amount="Amount of points or percentage (e.g., 100 or 50%) to gamble.")
    async def slash_gamble(interaction: discord.Interaction, amount: str):
        points_data = load_points()
        user_points = points_data.get(str(interaction.user.id), 0)

        if amount.endswith('%'):
            try:
                percentage = int(amount[:-1])
                if percentage < 1 or percentage > 100:
                    await interaction.response.send_message("Error: Please Enter A Valid Percentage between 1 and 100.")
                    return

                gamble_amount = int(user_points * (percentage / 100))
            except ValueError:
                await interaction.response.send_message("Error: Please Enter A Valid Percentage (e.g., 50%).")
                return

        else:
            try:
                gamble_amount = int(amount)
            except ValueError:
                await interaction.response.send_message("Error: Please Enter A Valid Percentage Or Number.")
                return

        if gamble_amount > user_points:
            await interaction.response.send_message(f"Error: You Don't Have Enough Points To Gamble {gamble_amount}, You Only Have {user_points}.")
            return
        
        result = random.choice(["win", "lose"])

        if result == "win":
            new_points = user_points + gamble_amount 
            points_data[str(interaction.user.id)] = new_points
            save_points(points_data)
            await interaction.response.send_message(f"🎉 You won! You now have **{new_points}** points!")
        else:
            new_points = user_points - gamble_amount 
            points_data[str(interaction.user.id)] = new_points
            save_points(points_data)
            await interaction.response.send_message(f"😔 You lost! You now have **{new_points}** points.")

# · · ─────── ·𖥸· ─────── · · Help Commands  · · ─────── ·𖥸· ─────── · ·
    @client.command(name="help")
    async def help(ctx):
        embed_color = discord.Color.from_rgb(75, 0, 130)
        author = ctx.author  # Save the invoking user

        # Create a button for each category
        button_1 = Button(label="General", style=discord.ButtonStyle.primary, custom_id="general")
        button_2 = Button(label="Points", style=discord.ButtonStyle.primary, custom_id="points")
        button_3 = Button(label="Fun", style=discord.ButtonStyle.primary, custom_id="fun")
        button_4 = Button(label="Information", style=discord.ButtonStyle.primary, custom_id="information")
        button_5 = Button(label="Moderation", style=discord.ButtonStyle.primary, custom_id="moderation")

        view = View(timeout=60)
        for button in (button_1, button_2, button_3, button_4, button_5):
            view.add_item(button)

        embed = discord.Embed(
            title="Help Command",
            description="Click the buttons below to see the list of commands in each category.",
            color=embed_color
        )

        async def button_callback(interaction: discord.Interaction):
            # Restrict interaction to original command user
            if interaction.user.id != author.id:
                await interaction.response.send_message(
                    "You cannot interact with this help menu.", ephemeral=True
                )
                return

            category = interaction.data["custom_id"]
            embed.clear_fields()

            if category == "general":
                embed.title = "General Commands"
                for cmd, perms, desc in commands_info["General"]:
                    embed.add_field(name=cmd, value=f"Permissions: {perms}\nDescription: {desc}", inline=False)
            elif category == "points":
                embed.title = "Points Commands"
                for cmd, perms, desc in commands_info["Points"]:
                    embed.add_field(name=cmd, value=f"Permissions: {perms}\nDescription: {desc}", inline=False)
            elif category == "fun":
                embed.title = "Fun Commands"
                for cmd, perms, desc in commands_info["Fun"]:
                    embed.add_field(name=cmd, value=f"Permissions: {perms}\nDescription: {desc}", inline=False)
            elif category == "information":
                embed.title = "Information Commands"
                for cmd, perms, desc in commands_info["Information"]:
                    embed.add_field(name=cmd, value=f"Permissions: {perms}\nDescription: {desc}", inline=False)
            elif category == "moderation":
                embed.title = "Moderation Commands"
                for cmd, perms, desc in commands_info["Moderation"]:
                    embed.add_field(name=cmd, value=f"Permissions: {perms}\nDescription: {desc}", inline=False)

            await interaction.response.edit_message(embed=embed, view=view)

        # Attach the same callback to all buttons
        for btn in (button_1, button_2, button_3, button_4, button_5):
            btn.callback = button_callback

        await ctx.send(embed=embed, view=view)


    @client.tree.command(name="help", description="Displays this bots help command.")
    async def slash_help(interaction: discord.Interaction):
        embed_color = discord.Color.from_rgb(75, 0, 130)
        author_id = interaction.user.id  # Store the ID of the user who invoked the command

        # Create buttons for each category
        button_1 = Button(label="General", style=discord.ButtonStyle.primary, custom_id="general")
        button_2 = Button(label="Points", style=discord.ButtonStyle.primary, custom_id="points")
        button_3 = Button(label="Fun", style=discord.ButtonStyle.primary, custom_id="fun")
        button_4 = Button(label="Information", style=discord.ButtonStyle.primary, custom_id="information")
        button_5 = Button(label="Moderation", style=discord.ButtonStyle.primary, custom_id="moderation")

        # Create view for buttons
        view = View(timeout=60)
        for button in (button_1, button_2, button_3, button_4, button_5):
            view.add_item(button)

        embed = discord.Embed(
            title="Help Command",
            description="Click the buttons below to see the list of commands in each category.",
            color=embed_color
        )

        async def button_callback(inter: discord.Interaction):
            if inter.user.id != author_id:
                await inter.response.send_message(
                    "You cannot interact with this help menu.", ephemeral=True
                )
                return

            category = inter.data["custom_id"]
            embed.clear_fields()

            if category == "general":
                embed.title = "General Commands"
                for cmd, perms, desc in commands_info["General"]:
                    embed.add_field(name=cmd, value=f"Permissions: {perms}\nDescription: {desc}", inline=False)
            elif category == "points":
                embed.title = "Points Commands"
                for cmd, perms, desc in commands_info["Points"]:
                    embed.add_field(name=cmd, value=f"Permissions: {perms}\nDescription: {desc}", inline=False)
            elif category == "fun":
                embed.title = "Fun Commands"
                for cmd, perms, desc in commands_info["Fun"]:
                    embed.add_field(name=cmd, value=f"Permissions: {perms}\nDescription: {desc}", inline=False)
            elif category == "information":
                embed.title = "Information Commands"
                for cmd, perms, desc in commands_info["Information"]:
                    embed.add_field(name=cmd, value=f"Permissions: {perms}\nDescription: {desc}", inline=False)
            elif category == "moderation":
                embed.title = "Moderation Commands"
                for cmd, perms, desc in commands_info["Moderation"]:
                    embed.add_field(name=cmd, value=f"Permissions: {perms}\nDescription: {desc}", inline=False)

            await inter.response.edit_message(embed=embed, view=view)

        # Set the callback for all buttons
        for btn in (button_1, button_2, button_3, button_4, button_5):
            btn.callback = button_callback

        # Send the initial embed with the buttons
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
    

# · · ─────── ·𖥸· ─────── · · Dice Commands  · · ─────── ·𖥸· ─────── · ·
    @client.command(name="roll", aliases = ["d", "dice"])
    async def roll(ctx, sides: int):
        # Check if the number of sides is valid
        if sides < 2:
            await ctx.send("Please enter a valid number of sides (greater than 1).")
            return

        # Roll the dice
        result = random.randint(1, sides)

        # Send the result
        await ctx.send(f"{ctx.author.mention} You Rolled A {result}.")

    @client.tree.command(name="roll", description="Roll a dice with the chosen number of sides.")
    async def slash_roll(ctx, sides: int):
        # Check if the number of sides is valid
        if sides < 2:
            await ctx.send("Please enter a valid number of sides (greater than 1).")
            return

        # Roll the dice
        result = random.randint(1, sides)

        # Send the result
        await ctx.send(f"{ctx.author.mention} You Rolled A {result}.")

# · · ─────── ·𖥸· ─────── · · Hex Code Commands  · · ─────── ·𖥸· ─────── · ·

    @client.command(name="color", aliases = ["colour", "hex"])
    async def color(ctx):
        # Generate a random hex color
        random_color = "#{:02x}{:02x}{:02x}".format(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

        # Create the embed with the random color
        embed = discord.Embed(
            title="Random Color",
            description=f"Here's a randomly generated hex color: {random_color}",
            color=random_color  # Embed color matches the random color
        )

        # Add an image to the embed (you can use any service to generate a color image)
        embed.set_image(url=f"https://singlecolorimage.com/get/{random_color[1:]}/400x400")

        # Send the embed
        await ctx.send(embed=embed)

    @client.tree.command(name="color", description="Generates a random hex color and shows it.")
    async def slash_color(interaction: discord.Interaction):
        # Generate a random hex color
        random_color = "#{:02x}{:02x}{:02x}".format(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

        # Create the embed with the random color
        embed = discord.Embed(
            title="Random Color",
            description=f"Here's a randomly generated hex color: {random_color}",
            color=discord.Color(int(random_color[1:], 16))  # Embed color matches the random color
        )

        # Add an image to the embed (you can use any service to generate a color image)
        embed.set_image(url=f"https://singlecolorimage.com/get/{random_color[1:]}/400x400")

        # Respond to the interaction
        await interaction.response.send_message(embed=embed)

# · · ─────── ·𖥸· ─────── · · Dance Party Commands  · · ─────── ·𖥸· ─────── · ·
    @client.command(name="danceparty")
    async def danceparty(ctx):
        await ctx.send("https://tenor.com/view/azura-cat-rave-gif-13849479890178963463")

    @client.tree.command(name="danceparty", description="Starts a dance party with Azura cat!")
    async def slash_danceparty(interaction: discord.Interaction):
        await interaction.response.send_message("https://tenor.com/view/azura-cat-rave-gif-13849479890178963463")

# · · ─────── ·𖥸· ─────── · · Temporary Commands  · · ─────── ·𖥸· ─────── · ·
    @client.command(name="suggest")
    async def suggest(ctx, *, suggestion: str):
        # Get the user's name and the current time
        user_name = ctx.author.name
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Define the file where suggestions will be saved
        suggestion_file = "suggestions.txt"

        # Prepare the message to write to the file
        suggestion_message = f"Suggestion by {user_name} ({current_time}): {suggestion}\n"
        
        # Write the suggestion to the file
        with open(suggestion_file, "a") as file:
            file.write(suggestion_message)
        
        # Acknowledge the user that their suggestion has been saved
        await ctx.send(f"Thank you for your suggestion, {user_name}! We've saved it.")

# · · ─────── ·𖥸· ─────── · · Poll Commands  · · ─────── ·𖥸· ─────── · ·

    @client.command(name="poll")
    async def poll(ctx, question: str, *options):
        if len(options) == 0:
            options = ("Yes", "No")
        elif len(options) < 2:
            await ctx.send("You need at least two options to create a poll.")
            return
        elif len(options) > 4:
            await ctx.send("You can only provide up to 4 options.")
            return

        emojis = ["1️⃣", "2️⃣", "3️⃣", "4️⃣"]
        description = "\n".join(f"{emojis[i]} {option}" for i, option in enumerate(options))

        embed = discord.Embed(title=f"📊 {question}", description=description, color=discord.Color.blue())
        embed.set_footer(text=f"Poll started by {ctx.author.display_name}")

        message = await ctx.send(embed=embed)
        for i in range(len(options)):
            await message.add_reaction(emojis[i])

    @client.tree.command(name="poll", description="Create a poll with up to 4 options.")
    @app_commands.describe(
        question="The poll question",
        option1="First option (optional)",
        option2="Second option (optional)",
        option3="Third option (optional)",
        option4="Fourth option (optional)"
    )
    async def poll(
        interaction: discord.Interaction,
        question: str,
        option1: str = None,
        option2: str = None,
        option3: str = None,
        option4: str = None
    ):
        options = [opt for opt in [option1, option2, option3, option4] if opt]

        if len(options) == 0:
            options = ["Yes", "No"]
        elif len(options) < 2:
            await interaction.response.send_message("You need at least two options to create a poll.", ephemeral=True)
            return
        elif len(options) > 4:
            await interaction.response.send_message("You can only provide up to 4 options.", ephemeral=True)
            return

        emojis = ["1️⃣", "2️⃣", "3️⃣", "4️⃣"]
        description = "\n".join(f"{emojis[i]} {option}" for i, option in enumerate(options))

        embed = discord.Embed(title=f"📊 {question}", description=description, color=discord.Color.blurple())
        embed.set_footer(text=f"Poll started by {interaction.user.display_name}")

        await interaction.response.send_message(embed=embed)
        message = await interaction.original_response()

        for i in range(len(options)):
            await message.add_reaction(emojis[i])

# · · ─────── ·𖥸· ─────── · · Client Events  · · ─────── ·𖥸· ─────── · ·

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


    @client.event
    async def on_message(message):
        if message.author.bot or message.webhook_id:
            return
        
        points_data = load_points()
        user_id = str(message.author.id)

        if user_id not in points_data:
            points_data[user_id] = 0

        points_data[user_id] += random.randint(1, 7)
        save_points(points_data)

        await client.process_commands(message)

    @client.event
    async def on_member_join(member):
        if member.bot:
            return
        
        points_data = load_points()
        user_id = str(member.id)

        if user_id not in points_data:
            points_data[user_id] = 500
            save_points(points_data)

# · · ─────── ·𖥸· ─────── · · Error Checks  · · ─────── ·𖥸· ─────── · ·

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


# · · ─────── ·𖥸· ─────── · · Client Run & Define Help Command · · ─────── ·𖥸· ─────── · ·
    client.run(token)