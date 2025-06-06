# This example requires the 'message_content' intent.
from contextlib import nullcontext
from dis import disco
from typing import Generator

import discord
import feedparser
from discord import app_commands, guild
from discord.ext import tasks
import requests
import re
from discord.webhook.async_ import interaction_message_response_params, interaction_response_params
from unicodedata import category

import os

# print("Bot manually paused.")
# exit()

class MyClient(discord.Client):
    def __init__(self):
        super().__init__(intents=discord.Intents.all())
        self.synced = False
        self.emoji = True

    async def on_ready(self):
        print(f'Logged on as {self.user}!')
        await self.wait_until_ready()

        channel = self.get_channel(1376588125975085086)

        message = await channel.fetch_message(1376759456817221692)
        await message.add_reaction('✅')

        message = await channel.fetch_message(1376760364867260558)
        for emoji in TARGET_EMOJI_PIXELY:
            if emoji == '✅':
                continue
            await message.add_reaction(emoji)

        message = await channel.fetch_message(1376761822446751744)
        for emoji in TARGET_EMOJI_EX:
            await message.add_reaction(emoji)

        await self.change_presence(activity=discord.CustomActivity(name="작동 중"))
        check_youtube_channels_update.start()
        if not self.synced:
            await tree.sync()
            self.synced = True


intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

client = MyClient()
interaction = discord.Interaction
tree = app_commands.CommandTree(client)


token = os.getenv("BOT_TOKEN")
TARGET_EMOJI_PIXELY = {
    '🦈' : '랃프'
    ,'🐶' : '덕프'
    ,'⭐' : '각프'
    ,'🦖' : '룡프'
    ,'🐋' : '뜰프'
    ,'🐰' : '션프'
    ,'🌈' : '올멤'
    , '✅': '꿈뜰이'
}
TARGET_EMOJI_EX = {
    '🥦': '팀샐'
    , '🍊': '패스'
    , '🎙️' : '시스'
    , '💡' : '그외'
}
TARGET_CHANNEL_ID = 1376588125975085086
TARGET_MESSAGE_ID = {1376759456817221692, 1376760364867260558, 1376761822446751744}
YOUTUBE_CHANNEL_LATEST_VIDEO = {
    "rather" : ""
    , "duck_gae" : ""
    , "각별" : ""
    , "rulrudino" : ""
    , "sleepground" : ""
    , "suhyen" : ""
}


@client.event
async def on_raw_reaction_add(payload):
    # Check if the reaction is in the correct channel
    if payload.channel_id != TARGET_CHANNEL_ID:
        return

    if payload.message_id not in TARGET_MESSAGE_ID:
        return

    # Check if the correct emoji was used
    if (str(payload.emoji.name) not in TARGET_EMOJI_PIXELY.keys()
            and str(payload.emoji.name) not in TARGET_EMOJI_EX.keys()):
        return

    # Get the guild, member, and role
    guild = client.get_guild(payload.guild_id)
    if guild is None:
        return

    member = guild.get_member(payload.user_id)
    if member is None or member.bot:
        return

    if str(payload.emoji.name) in TARGET_EMOJI_PIXELY.keys() or str(payload.emoji.name):
        # Get the role
        ROLE_NAME = TARGET_EMOJI_PIXELY.get(str(payload.emoji.name))
        role = discord.utils.get(guild.roles, name=ROLE_NAME)
        if role is None:
            print(f"Role '{ROLE_NAME}' not found!")
            return

        # Add the role to the user
        try:
            await member.add_roles(role)
            print(f"Added role '{ROLE_NAME}' to {member.display_name}")
        except discord.Forbidden:
            print("Missing permissions to add role.")
        except discord.HTTPException as e:
            print(f"Failed to add role: {e}")
    else:
        channel = discord.utils.get(guild.channels, name=TARGET_EMOJI_EX.get(payload.emoji.name))
        overwrite = discord.PermissionOverwrite()
        overwrite.send_messages = False
        overwrite.read_messages = True
        await channel.set_permissions(member, overwrite=overwrite)
        print(f"{member} now can see {TARGET_EMOJI_EX.get(payload.emoji.name)}")

@client.event
async def on_raw_reaction_remove(payload: discord.RawReactionActionEvent):
    # Check if the reaction is in the correct channel
    if payload.channel_id != TARGET_CHANNEL_ID:
        return

    if payload.message_id not in TARGET_MESSAGE_ID:
        return

     # Check if the correct emoji was used
    if str(payload.emoji.name) not in TARGET_EMOJI_PIXELY.keys():
        print(str(payload.emoji.name))
        return

    # Get the guild, member, and role
    guild = client.get_guild(payload.guild_id)
    if guild is None:
        return

    member = guild.get_member(payload.user_id)
    if member is None or member.bot:
        return

    # Get the role
    ROLE_NAME = TARGET_EMOJI_PIXELY.get(str(payload.emoji.name))
    role = discord.utils.get(guild.roles, name=ROLE_NAME)
    if role is None:
        print(f"Role '{ROLE_NAME}' not found!")
        return

    # Remove the role to the user
    try:
        await member.remove_roles(role)
        print(f"Removed role '{ROLE_NAME}' to {member.display_name}")
    except discord.Forbidden:
        print("Missing permissions to add role.")
    except discord.HTTPException as e:
        print(f"Failed to add role: {e}")

@tree.command(name='퍼컬지정', description="닉네임 색을 바꿉니다.")
async def slash(interaction: discord.Interaction, 테마: str):
    role = discord.utils.get(interaction.guild.roles, name=interaction.user.name)

    if role: # role is already there
        await role.edit(color=int(테마, 16))
    else : # role is not in the list
        # new role
        role = await interaction.guild.create_role(name = interaction.user.name, color = int(테마, 16))

    # Build new role order
    # Start with all roles except the new one
    new_roles_order = [r for r in interaction.guild.roles]

    # Insert new role just above the 6th role
    target_index = 10
    new_roles_order.insert(target_index, role)
    print(new_roles_order)

    await interaction.guild.edit_role_positions(positions={role: i for i, role in enumerate(new_roles_order)})
    await interaction.user.add_roles(role)

    await interaction.response.send_message(f"퍼컬이 {테마}으로 변경되었습니다.", ephemeral=True)

@tree.command(name='퍼컬삭제', description="퍼컬을 삭제합니다")
async def slash(interaction: discord.Interaction):
    role = discord.utils.get(interaction.guild.roles, name=interaction.user.name)

    if role:
        await role.delete()
        await interaction.response.send_message("퍼스널 컬러가 삭제되었습니다.", ephemeral=True)
    else:
        await interaction.response.send_message("퍼스널 컬러가 존재하지 않습니다.", ephemeral=True)


@tree.command(name='개인채널생성', description='개인채널을 생성합니다')
async def slash(interaction: discord.Interaction):
    if discord.utils.get(interaction.guild.channels, name=interaction.user.name):
        await interaction.response.send_message(content='개인채널이 이미 존재합니다.', ephemeral=True)
        return

    overwrite = {
        interaction.guild.default_role: discord.PermissionOverwrite(view_channel=False),  # hide from everyone
        interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True),  # allow the user
        interaction.guild.me: discord.PermissionOverwrite(view_channel=True)  # allow bot
    }
    await interaction.guild.create_text_channel(name=interaction.user.name
                , category=discord.utils.get(interaction.guild.categories, name='개인채널')
                , overwrites=overwrite)
    await interaction.response.send_message(content=f'{interaction.user.name}님의 개인채널이 생성되었습니다!', ephemeral=True)


@tasks.loop(minutes=5)
async def check_youtube_channels_update():
    await client.get_channel(1377058977296416909).send(f"refresh in 5 mins")
    for channel_data in YOUTUBE_CHANNEL_LATEST_VIDEO:
        rss_url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_data}"
        feed = feedparser.parse(rss_url)

        if not feed.entries:
            continue

        latest_entry = feed.entries[0]
        latest_video_id = latest_entry.yt_videoid

        if latest_video_id != YOUTUBE_CHANNEL_LATEST_VIDEO.get(channel_data):
            YOUTUBE_CHANNEL_LATEST_VIDEO.update({channel_data : latest_video_id})
            await client.get_channel(1380438892745854996).send(f"새 영상이 업로드 되었습니다!"
                                f"\nhttps://www.youtube.com/watch?v={latest_entry}")

@tree.command(name='latestvideo', description='get latest youtube video for SG')
async def slash(interaction: discord.Interaction):
    for channel_data in YOUTUBE_CHANNEL_LATEST_VIDEO:
        url = f"https://www.youtube.com/@{channel_data}"
        rss_url = f"https://www.youtube.com/feeds/videos.xml?channel_id={get_channel_id(url)}"
        feed = feedparser.parse(rss_url)

        if not feed.entries:
            continue

        latest_entry = feed.entries[0]
        latest_video_id = latest_entry.yt_videoid

        await interaction.response.send_message(f"https://www.youtube.com/watch?v={latest_video_id}")


def get_channel_id(youtube_url: str):
    try:
        # Fetch page source
        headers = {'User-Agent': 'Mozilla/5.0'}
        res = requests.get(youtube_url, headers=headers)
        html = res.text

        # Look for the channel_id pattern in the page source
        match = re.search(r'<link rel="canonical" href="https://www\.youtube\.com/channel/(UC[\w-]{22})">', html)
        if match:
            return match.group(1)
        else:
            print("here")
            raise ValueError("Channel ID not found in page.")
    except Exception as e:
        print("runtime")
        raise RuntimeError(f"Failed to extract channel ID: {e}")


import logging

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')

# Assume client refers to a discord.Client subclass...
client.run(token, log_handler=handler, log_level=logging.DEBUG)

