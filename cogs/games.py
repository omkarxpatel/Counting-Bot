import time
import asyncio
import typing
import discord
import random
from utils import ttt_helper
from discord.ext import commands
from utils.typerace_helper import wordsTotal


class FunClass(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.ob = True


    @commands.command()
    async def guess(self, ctx: commands.Context, number: int = 100):
        guesses = range(number)
        answer = random.choice(guesses)
        await ctx.send(f"A random number has been selected from 0 - {number}")

        condition = True
        counter = 0

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        while condition:
            try:
                message = await self.bot.wait_for('message', check=check)

            except asyncio.TimeoutError:
                embedtimeout = discord.Embed(title="You didnt respond on time!", description=f'The correct number was `{answer}`\n You guessed `{counter}` times')
                return await ctx.send(embed=embedtimeout)

            else:
                if message.content.lower() in ['end', 'cancel']:
                    embedcancel = discord.Embed(title='Canceled the game', description=f'The correct number was `{answer}`\nYou guessed `{counter}` times')
                    return await ctx.send(embed=embedcancel)

                if message.content.isdigit():
                    if int(message.content) > answer:
                        message_reply = "That's incorrect! You can keep trying or type `cancel` to end the game\n**Hint:** `guess lower`"
                    
                    elif int(message.content) < answer:
                        message_reply = "That's incorrect! You can keep trying or type `cancel` to end the game\n**Hint:** `guess higher`"
                    
                    if int(message.content) == answer:
                        counter += 1
                        embedwin = discord.Embed(title='Correct!', description=f'You guessed the correct number!\nThe number was `{answer}`\nYou guessed in `{counter}` tries')
                        return await ctx.send(embed=embedwin)
                    
                    else:
                        counter += 1
                        await ctx.send(message_reply)


    @commands.max_concurrency(1, commands.BucketType.user, wait=False)
    @commands.command(aliases=['ttt', 'tic'])
    async def tictactoe(self, ctx: commands.context):

        embed = discord.Embed(description=f'🔎 | {ctx.author.mention}'
                                        f'\n👀 |  A member is looking for someone to play **Tic-Tac-Toe**')

        embed.set_thumbnail(url='https://i.imgur.com/DZhQwnD.gif')
        embed.set_author(name='Tic-Tac-Toe', icon_url='https://i.imgur.com/RTwo0om.png')

        player1 = ctx.author
        view = ttt_helper.LookingToPlay(timeout=120)

        view.ctx = ctx
        view.message = await ctx.send(embed=embed,
                                    view=view)
        await view.wait()
        player2 = view.value

        if player2:
            starter = random.choice([player1, player2])
            ttt = ttt_helper.TicTacToe(ctx, player1, player2, starter=starter)
            ttt.message = await view.message.edit(view=ttt, embed=discord.Embed(title='Tic Tac Toe',description=f'{starter.mention} goes first',color=embed.color))


    @commands.max_concurrency(1, commands.BucketType.user, wait=False)
    @commands.command(aliases=['type','type-race'])
    async def typerace(self, ctx: commands.context, length: typing.Optional[int]=6):
        
        leaderboard = []
        total_time = length*5
        generated_words = ""

        val = random.sample(wordsTotal.split(" "), k=length)
        generated_words = " ".join(val)

        inv_char = "\u200b"


        embed = discord.Embed(title="Typing-Race")
        embed.description = f"Enter the following words the fastest in order to win\n```\n{inv_char.join(generated_words)}```"
        embed.set_footer(text=f"Results will appear in {total_time} seconds")
        embed.timestamp = discord.utils.utcnow()

        start_time = time.time()
        value = await ctx.send(embed=embed)

        def check(mes):
            return mes.channel == ctx.channel

        while time.time()-start_time < total_time:
            message = await self.bot.wait_for('message', check=check)
            
            if message.content+" " == generated_words:
                react = False
                for x in leaderboard:
                    if x[0] != message.author.id:
                        react = True

                if react:
                    user_data = [message.author.id, round(time.time()-start_time, 3)]
                    leaderboard.append(user_data)
                    await message.add_reaction("✅")
                    break
            
            else:
                await message.add_reaction("\U000026a0")

        results = "```\n"
        winners = ["🥇","🥈","🥉"]

        for data in leaderboard:

            if data in leaderboard[:3]:
                addon = winners[leaderboard.index(data)]

                results += f"{addon} <@{data[0]}> - {data[-1]}s\n"
        results += "```"

        if results == "```\n```":
            results = "No one typed anything!"


        embed.add_field(name="Results:", value = results)
        await value.edit(embed=embed)
        


async def setup(bot):
  await bot.add_cog(FunClass(bot))