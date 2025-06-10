# This example requires the 'message_content' intent.

import discord
from discord import app_commands

from pymongo import MongoClient
from discord.ext import tasks
import feedparser

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from config import *

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
        check_youtube_videos_update.start()
        check_youtube_post_update.start()
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

MONGO_URI = os.getenv("MONGO_URI")
mongo_client = MongoClient(MONGO_URI)
db = mongo_client["youtube_bot"]
collection = db["youtube_channels"]

driver = uc.Chrome(options=options)
driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
stealth(driver,
        languages=["en-US", "en"],
        vendor="Google Inc.",
        platform="Win32",
        webgl_vendor="Intel Inc.",
        renderer="Intel Iris OpenGL Engine",
        fix_hairline=True,
        )
driver.get("https://www.google.com/")

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
        role_name = TARGET_EMOJI_PIXELY.get(str(payload.emoji.name))
        role = discord.utils.get(guild.roles, name=role_name)
        if role is None:
            print(f"Role '{role_name}' not found!")
            return

        # Add the role to the user
        try:
            await member.add_roles(role)
            print(f"Added role '{role_name}' to {member.display_name}")
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
    role_name = TARGET_EMOJI_PIXELY.get(str(payload.emoji.name))
    role = discord.utils.get(guild.roles, name=role_name)
    if role is None:
        print(f"Role '{role_name}' not found!")
        return

    # Remove the role to the user
    try:
        await member.remove_roles(role)
        print(f"Removed role '{role_name}' to {member.display_name}")
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
async def check_youtube_videos_update():

    print(f"refresh in 5 mins for videos")

    for channel_data in collection.find():
        channel_id = channel_data["channel_id"]
        last_video_id = channel_data.get("last_video_id", "")

        rss_url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
        print(rss_url)
        feed = feedparser.parse(rss_url)

        if not feed.entries:
            continue

        latest_entry = feed.entries[0]
        latest_video_id = latest_entry.yt_videoid
        print(latest_video_id)

        if last_video_id == "":
            update_channel_data(channel_id, latest_video_id, "last_video_id")
            print("No new video")
        elif last_video_id != latest_video_id:
            update_channel_data(channel_id, latest_video_id, "last_video_id")
            print("New video uploaded!")
            await client.get_channel(1380438892745854996).send(f"새 영상이 업로드 되었습니다!"
                                                               f"\nhttps://www.youtube.com/watch?v={latest_video_id}")
        else:
            print("No new video")

def update_channel_data(channel_id: int, last_id, type_of: str) :
    collection.update_one(
        {"channel_id": channel_id}
        , {"$set": {type_of: last_id}}
    )

@tasks.loop(minutes=5)
async def check_youtube_post_update():
    print("refresh in 5 mins for post update")

    for channel_data in collection.find():
        channel_id = channel_data["channel_id"]
        last_post_id = channel_data.get("last_post_id", "")
        driver.get(f"https://www.youtube.com/channel/{channel_id}/community")
        try:
            # Wait up to 10 seconds for posts to appear
            posts = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.ID, "published-time-text"))
            )

            print(f"Successfully found {len(posts)} post(s)!")

            latest_post_url = posts[0].find_element(By.TAG_NAME, 'a').get_attribute('href')
            latest_post_id = latest_post_url.replace(f"https://www.youtube.com/channel/{channel_id}/community?lb=", "")
            print(latest_post_url)

            if last_post_id == "":
                update_channel_data(channel_id, latest_post_id, "last_post_id")
            elif last_post_id != latest_post_id:
                update_channel_data(channel_id, latest_post_id, "last_post_id")
                await client.get_channel(1380438892745854996).send(f"새 포스트가 업로드되었습니다!"
                        f"\nhttps://www.youtube.com/channel/{channel_id}/community?lb={latest_post_id}")
            else:
                print(f"No new post for {channel_data.get('channel_name', '')}")
        except Exception as e:
            print(f"Elements not found. {channel_data.get('channel_name', '')}")


import logging

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')

# Assume client refers to a discord.Client subclass...
client.run(token, log_handler=handler, log_level=logging.DEBUG)

