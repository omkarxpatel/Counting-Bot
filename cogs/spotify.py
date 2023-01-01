import discord
from discord.ext import commands
from utils import functions


class Spotify(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(aliases=['sp'])
    @commands.cooldown(5, 60.0, type=commands.BucketType.user)
    async def spotify(self, ctx: commands.Context, member: discord.Member = None):
  
        member = member or ctx.author
        async with ctx.typing():
            spotify = functions.Spotify(bot=self.bot, member=member)
            embed = await spotify.get_embed()

            if not embed:
                if member == ctx.author:
                    return await ctx.send(f"You are currently not listening to spotify!", mention_author=False)
                return await ctx.reply(f"{member.mention} is not listening to Spotify", mention_author=False, allowed_mentions=discord.AllowedMentions(users=False))
            
            await ctx.send(embed=embed[0], file=embed[1])



async def setup(bot):
  await bot.add_cog(Spotify(bot))