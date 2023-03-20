import discord
from discord.ext import commands

from revChatGPT.ChatGPT import Chatbot


class Summarize(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(aliases=['ask','chat'])
    async def gpt(self, ctx: commands.Context, *, argument):
        async with ctx.typing():
            await ctx.message.add_reaction("<a:typing:907302657209819208>")
            chatbot = Chatbot({"session_token": "-"}, conversation_id=None, parent_id=None)
            response = chatbot.ask(argument, conversation_id=None, parent_id=None) # You can specify custom conversation and parent ids. Otherwise it uses the saved conversation (yes. conversations are automatically saved)

            await ctx.reply(response['message'])


async def setup(bot):
  await bot.add_cog(Summarize(bot))
