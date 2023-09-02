import asyncio
import discord
import os
import shutil
import sys
import requests
import json
from discord.ext import commands
import pkg_resources
from dotenv import load_dotenv
import time
from datetime import datetime, timedelta

load_dotenv()

intents = discord.Intents.default()

intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='sc.', intents=intents)

api_key = os.getenv("OPENAI_API_KEY")

current_status = 0

def stsreqcheck():
    url = "https://api.server-discord.com/v2/bots/1101491674858922065/stats"
    headers = {
        'Authorization': "SDC "
    }
    data = {
        'servers': len(bot.guilds),
        'shards': 1,
    }
    r = requests.post(url=url, headers=headers, data=data)
    if r.status_code == 200:
        print(f"[SDC REQ LOG]: Установлено новое кол-во серверов на мониторинге: {len(bot.guilds)}")
    else:
        print(f"[SDC REQ LOG]: Ошибка в отправке запроса на установку кол-ва серверов! Code: {r.status_code}")


async def update_status():
    global current_status
    while True:
        if current_status == 0:
            server_count = len(bot.guilds)
            with open('users.txt', 'r') as user_file:
                user_count = len(user_file.readlines())
            status_text = f"{server_count} серверов, {user_count} пользователей"
            await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=status_text))
            current_status = 1
        else:
            new_status_text = f"/help | /register"
            await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name=new_status_text))
            current_status = 0
        await asyncio.sleep(30)

@bot.event
async def on_ready():
    for Filename in os.listdir('./cogs'):
        if Filename.endswith('.py'):
            await bot.load_extension(f'cogs.{Filename[:-3]}')
    print(f'{bot.user} is now running!')
    print("Bot is Up and Ready!")
    stsreqcheck()
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} commands")
        await update_status()
    except Exception as e:
        print(e)


@bot.event
async def on_guild_join(guild):
    system_channel = guild.system_channel
    owner = guild.owner

    if system_channel is not None:
        await system_channel.send("""👋 Приветствую всех!

    🌟 Добро пожаловать в увлекательный мир SkillCraft Studio! Я - твой гид в мире творчества и нейросетей. 🤖✨

    🚀 Со мной можешь создавать уникальные навыки для Aika AI, делая её разговоры ещё интереснее и увлекательнее.

    🛠️ Чтобы начать, введи команду /register и следуй инструкциям. Если у тебя уже есть OpenAI API ключ, то укажи его в процессе регистрации. А если нет, не переживай! Я помогу тебе получить ключ для полноценного взаимодействия.

    🔑 Если API ключ вызывает вопросы, воспользуйся командой /buy-key. Это позволит тебе приобрести ключ и начать своё творческое путешествие в мире диалогов с ботом.

    Не упусти свой шанс создать неповторимые навыки, делиться своим творчеством и стать частью нашего сообщества. Давай сделаем общение с искусственным интеллектом увлекательным и интересным для всех! 🌈🚀""")
    else:
        await owner.send("""👋 Приветствую всех!

    🌟 Добро пожаловать в увлекательный мир SkillCraft Studio! Я - твой гид в мире творчества и нейросетей. 🤖✨

    🚀 Со мной можешь создавать уникальные навыки для Aika AI, делая её разговоры ещё интереснее и увлекательнее.

    🛠️ Чтобы начать, введи команду /register и следуй инструкциям. Если у тебя уже есть OpenAI API ключ, то укажи его в процессе регистрации. А если нет, не переживай! Я помогу тебе получить ключ для полноценного взаимодействия.

    🔑 Если API ключ вызывает вопросы, воспользуйся командой /buy-key. Это позволит тебе приобрести ключ и начать своё творческое путешествие в мире диалогов с ботом.

    Не упусти свой шанс создать неповторимые навыки, делиться своим творчеством и стать частью нашего сообщества. Давай сделаем общение с искусственным интеллектом увлекательным и интересным для всех! 🌈🚀""")


# Load command
@commands.is_owner()
@bot.command()
async def load(ctx, extension):
    await bot.load_extension(f'cogs.{extension}')
    await ctx.author.send(f'> **Loaded {extension} done.**')


@bot.command(name="ping")
async def ban(ctx):
    await ctx.send("Понг")


@bot.command(name="ban")
async def ban(ctx, user_id: int, reason: str):
    with open('admins.txt', 'r') as file:
        admin_ids = [int(line.strip()) for line in file.readlines()]

    if ctx.author.id in admin_ids:
        with open('blocked_users.txt', 'a') as file:
            file.write(f"{user_id}\n")

        user = await bot.fetch_user(user_id)
        await user.send(f'**Ваш аккаунт в NeuMag был заблокирован. Причина:** {reason}')

        await ctx.send(f"Пользователь с ID {user_id} был заблокирован.")
    else:
        await ctx.send("У вас нет разрешения на использование команды.")


@bot.command(name="unban")
async def unban(ctx, user_id: int):
    with open('admins.txt', 'r') as file:
        admin_ids = [int(line.strip()) for line in file.readlines()]

    if ctx.author.id in admin_ids:
        with open('blocked_users.txt', 'r') as file:
            blocked_users = [line.strip() for line in file.readlines()]

        if str(user_id) in blocked_users:
            blocked_users.remove(str(user_id))
            with open('blocked_users.txt', 'w') as file:
                for user in blocked_users:
                    file.write(f"{user}\n")

            user = await bot.fetch_user(user_id)
            await user.send('**Ваш аккаунт в NeuMag был разблокирован.**')

            await ctx.send(f"Пользователь с ID {user_id} был разблокирован.")
        else:
            await ctx.send(f"Пользователь с ID {user_id} не заблокирован.")
    else:
        await ctx.send("У вас нет разрешения на использование команды.")


@bot.command(name="premium")
async def premium(ctx, user_id: int):
    with open('admins.txt', 'r') as file:
        admin_ids = [int(line.strip()) for line in file.readlines()]

    if ctx.author.id in admin_ids:
        premium_users_dir = 'premium_users'
        os.makedirs(premium_users_dir, exist_ok=True)

        user_dir = os.path.join(premium_users_dir, str(user_id))
        os.makedirs(user_dir, exist_ok=True)

        period_file_path = os.path.join(user_dir, 'buy_date.txt')
        current_date = datetime.now().strftime('%d.%m.%Y')

        with open(period_file_path, 'w') as period_file:
            period_file.write(current_date)

        user = await bot.fetch_user(user_id)
        await user.send('**Подписка NeuMag Premium успешно активирована.**')

        await ctx.send(f"Папка и файлы для пользователя с ID {user_id} созданы.")
    else:
        await ctx.send("У вас нет разрешения на использование команды.")


# Unload command
@commands.is_owner()
@bot.command()
async def unload(ctx, extension):
    await bot.unload_extension(f'cogs.{extension}')
    await ctx.author.send(f'> **Un-Loaded {extension} done.**')


# Empty discord_bot.log file
@commands.is_owner()
@bot.command()
async def clean(ctx):
    open('discord_bot.log', 'w').close()
    await ctx.author.send(f'> **Successfully emptied the file!**')


# Get discord_bot.log file
@commands.is_owner()
@bot.command()
async def getLog(ctx):
    try:
        with open('discord_bot.log', 'rb') as f:
            file = discord.File(f)
        await ctx.author.send(file=file)
        await ctx.author.send("> **Send successfully!**")
    except:
        await ctx.author.send("> **Send failed!**")

# Upload new Bing cookies and restart the bot
@commands.is_owner()
@bot.command()
async def upload(ctx):
    try:
        if ctx.message.attachments:
            for attachment in ctx.message.attachments:
                if str(attachment)[-4:] == ".txt":
                    content = await attachment.read()
                    print(json.loads(content))
                    with open("cookies.json", "w", encoding = "utf-8") as f:
                        json.dump(json.loads(content), f, indent = 2)
                    if not isinstance(ctx.channel, discord.abc.PrivateChannel):
                        await ctx.message.delete()
                    await set_chatbot(json.loads(content))
                    await ctx.author.send(f'> **Upload new cookies successfully!**')
                    logger.warning("\x1b[31mCookies has been setup successfully\x1b[0m")
                else:
                    await ctx.author.send("> **Didn't get any txt file.**")
        else:
            await ctx.author.send("> **Didn't get any file.**")
    except Exception as e:
        await ctx.author.send(f">>> **Error: {e}**")
        logger.exception(f"Error while upload cookies: {e}")

if __name__ == '__main__':
    bot.run(os.getenv("DISCORD_BOT_TOKEN"))