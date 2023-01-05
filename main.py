import ast
import discord
import aiohttp
from colorama import Fore
from pkgutil import iter_modules
from discord.ext import commands, tasks
import traceback
from secretsVals import webhookurl, token


class MyBot(commands.Bot):

    def __init__(self):
        super().__init__(command_prefix='-',
                         intents=discord.Intents.all(),
                         activity=discord.Activity(type=discord.ActivityType.watching, name="Campers"),
                         owner_ids=[838974822288851005, 641069257140207616]
                         )

        self.initial_extensions = [m.name for m in iter_modules(['cogs'], prefix='cogs.')]
        self.reset_db_on_startup = False

    async def setup_hook(self):
        self.background_task.start()
        self.session = aiohttp.ClientSession()

        for ext in self.initial_extensions:
            try:
                if ext != "cogs.jishaku":
                    await self.load_extension(ext)
                    print(f"{Fore.GREEN} {ext} loaded {Fore.RESET}")

            except:
                print(f"{Fore.RED} {ext} not loaded {Fore.RESET}")
                print(traceback.print_exc(limit=None, file=None, chain=True))


    @tasks.loop(minutes=10)
    async def background_task(self):
        print('Running background task...')


    async def close(self):
        await super().close()
        await self.session.close()

    async def on_ready(self):
        try:
            await bot.load_extension('jishaku')
            print(f"{Fore.GREEN} cogs.jishaku loaded{Fore.RESET}")
        except:
            print(f"{Fore.RED} cogs.jishaku NOT loaded {Fore.RESET}")

        print(f"{Fore.GREEN}{bot.user.name} is Online - Version: {discord.__version__}{Fore.RESET}")
        
        value = ""
        for x in self.initial_extensions:
            value += f"`✅` Loaded - `{x.replace('.','/')}`\n"

        embed = discord.Embed(title=f'{bot.user.name} Is Now Online', description = value)
        embed.timestamp = discord.utils.utcnow()
        embed.color = discord.Color.green()
        
        webhook = discord.SyncWebhook.from_url(webhookurl)
        webhook.send(embed=embed)

        if self.reset_db_on_startup:
            database = bot.get_channel(1057770300927914005)
            async for sent in database.history(limit=50):
                if sent.author.id == bot.user.id:
                    try:
                        last_line = ast.literal_eval(sent.content)
                        break
                    except:
                        continue

            if last_line != [0,0]:
                await database.send([0,0])

try:
    bot = MyBot()
    bot.run(token)
    
finally:
    webhook = discord.SyncWebhook.from_url(webhookurl)
    send_info = "\n\n`1. sudo rsync -a -e \"ssh -i downloads/Key.pem\" ~/downloads/Python\ -\ VSC/Campers-Bot ubuntu@ec2-52-53-200-96.us-west-1.compute.amazonaws.com:/home/ubuntu`\n`2. sudo ssh -i downloads/Key.pem ubuntu@ec2-52-53-200-96.us-west-1.compute.amazonaws.com`"
    webhook.send(content=f'Hum Campers is Now Offline 🛑 {send_info}')