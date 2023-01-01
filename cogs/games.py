import asyncio
import discord
import random
from utils import buttons
from discord.ext import commands


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
                embedtimeout = discord.Embed(title="You didnt respond on time!", description=f'The correct number was {answer}\n You guessed {counter} times')
                return await ctx.send(embed=embedtimeout)

            else:
                if message.content.lower() in ['end', 'cancel']:
                    embedcancel = discord.Embed(title='Canceled the game', description=f'Dont worry! You will get it next time.\n The correct number was {answer}\nYou guessed {counter} times')
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
        """Starts a tic-tac-toe game."""
        embed = discord.Embed(description=f'🔎 | {ctx.author.mention}'
                                        f'\n👀 |  A member is looking for someone to play **Tic-Tac-Toe**')

        embed.set_thumbnail(url='https://i.imgur.com/DZhQwnD.gif')
        embed.set_author(name='Tic-Tac-Toe', icon_url='https://i.imgur.com/RTwo0om.png')

        player1 = ctx.author
        view = buttons.LookingToPlay(timeout=120)

        view.ctx = ctx
        view.message = await ctx.send(embed=embed,
                                    view=view)
        await view.wait()
        player2 = view.value
        
        if player2:
            starter = random.choice([player1, player2])
            ttt = buttons.TicTacToe(ctx, player1, player2, starter=starter)
            ttt.message = await view.message.edit(view=ttt, embed=discord.Embed(title='Tic Tac Toe',description=f'{starter.mention} goes first',color=embed.color))


async def setup(bot):
  await bot.add_cog(FunClass(bot))