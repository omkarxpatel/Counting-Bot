import ast
import discord
import aiohttp
from colorama import Fore
from pkgutil import iter_modules
import traceback
from discord.ext import commands, tasks


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
        print(f"{Fore.GREEN}{bot.user.name} is Online - Version: {discord.__version__}{Fore.RESET}")
        
        value = ""
        for x in self.initial_extensions:
            value += f"`✅` Loaded - `{x.replace('.','/')}`\n"

        embed = discord.Embed(title=f'{bot.user.name} Is Now Online', description = value)
        embed.timestamp = discord.utils.utcnow()
        embed.color = discord.Color.green()
        
        webhook = discord.SyncWebhook.from_url('https://discordapp.com/api/webhooks/1057495225905463387/PZcbSvaDZEtR-a3uqNU6V5r12O0h7WucMX3rtpnl1dR31M3cJqIDpOV7ChWsPrsMMVac')
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
    token = "MTA1NDE0NDk0MjUyNTY0ODg5OQ.Gt0A9B.inIB-bmhjxut2FTaKc5NTj4d6LK9hEgxge4HIo"
    bot.run(token)
finally:
    webhook = discord.SyncWebhook.from_url('https://discordapp.com/api/webhooks/1057495225905463387/PZcbSvaDZEtR-a3uqNU6V5r12O0h7WucMX3rtpnl1dR31M3cJqIDpOV7ChWsPrsMMVac')
    send_info = "\n\n`1. sudo rsync -a -e \"ssh -i downloads/Key.pem\" ~/downloads/Python\ -\ VSC/Campers-Bot ubuntu@ec2-52-53-200-96.us-west-1.compute.amazonaws.com:/home/ubuntu`\n`2. sudo ssh -i downloads/Key.pem ubuntu@ec2-52-53-200-96.us-west-1.compute.amazonaws.com`"
    webhook.send(content=f'Hum Campers is Now Offline 🛑 {send_info}')