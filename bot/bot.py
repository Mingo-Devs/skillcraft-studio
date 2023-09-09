import asyncio
import discord
import os
import requests
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.default()

intents.message_content = True
intents.guilds = True

bot = commands.Bot(command_prefix='sc.', intents=intents)

current_status = 0

def stsreqcheck():
    url = "https://api.server-discord.com/v2/bots/{bot_id}/stats"
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
    print(f'{bot.user} запущен!')
    print("SkillCraft Studio готов!")
    stsreqcheck()
    try:
        synced = await bot.tree.sync()
        print(f"Синхронизированно {len(synced)} комманд")
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
        await user.send(f'**Ваш аккаунт в SkillCraft Studio был заблокирован. Причина:** {reason}')

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
            await user.send('**Ваш аккаунт в SkillCraft Studio был разблокирован.**')

            await ctx.send(f"Пользователь с ID {user_id} был разблокирован.")
        else:
            await ctx.send(f"Пользователь с ID {user_id} не заблокирован.")
    else:
        await ctx.send("У вас нет разрешения на использование команды.")


@bot.command(name="addcode")
async def addcode(ctx, *, text):
    with open('codes.txt', 'a') as file:
        file.write(f"{text}\n")
    await ctx.send(f"Код активации был добавлен в список")


@bot.command(name="addkey")
async def addkeys(ctx, key):
    with open('keys.txt', 'a') as file:
        file.write(f"{key}\n")
    await ctx.send(f"OpenAI API ключ был добавлен в списко")


if __name__ == '__main__':
    bot.run(os.getenv("DISCORD_BOT_TOKEN"))