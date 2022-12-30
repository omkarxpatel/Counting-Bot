import io
import typing
import discord
import textwrap
import datetime
import asyncio
import traceback
from pkgutil import iter_modules
from contextlib import redirect_stdout
from discord.ext import commands

def setup(bot):
    bot.add_cog(DeveloperCog(bot))

class DeveloperCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self._last_result = None
        self.error_channel = 1054268278027063376

    def cleanup_code(self, content):
        if content.startswith('```') and content.endswith('```'):
            return '\n'.join(content.split('\n')[1:-1])

        return content.strip('` \n')
        

    @commands.is_owner()
    @commands.command(pass_context=True, hidden=True, name='eval')
    async def eval(self, ctx, *, body: str):
        if not body:
            await ctx.reply("Please enter a body argument", delete_after=5)

        env = {
            'bot': self.bot,
            'ctx': ctx,
            'channel': ctx.channel,
            'author': ctx.author,
            'guild': ctx.guild,
            'message': ctx.message,
            '_': self._last_result
        }

        env.update(globals())

        body = self.cleanup_code(body)
        stdout = io.StringIO()

        to_compile = f'async def func():\n{textwrap.indent(body, "  ")}'

        try:
            exec(to_compile, env)
        except Exception as e:
            return await ctx.send(f'```py\n{e.__class__.__name__}: {e}\n```')

        func = env['func']
        try:
            with redirect_stdout(stdout):
                ret = await func()
        except Exception:
            value = stdout.getvalue()
            await ctx.send(f'```py\n{value}{traceback.format_exc()}\n```')
        else:
            value = stdout.getvalue()
            try:
                await ctx.message.add_reaction('\u2705')
            except:
                pass

            if ret is None:
                if value:
                    await ctx.send(f'```py\n{value}\n```')
            else:
                self._last_result = ret
                await ctx.send(f'```py\n{value}{ret}\n```')


    @commands.is_owner()
    @commands.command(pass_context=True, hidden=True, aliases=['relall', 'rall'])
    async def reloadall(self, ctx, argument: typing.Optional[str]):
        self.bot.last_rall = datetime.datetime.utcnow()
        cogs_list = ""
        to_send = ""
        err = False
        first_reload_failed_extensions = []
        if argument == 'silent' or argument == 's':
            silent = True
        else:
            silent = False
        if argument == 'channel' or argument == 'c':
            channel = True
        else:
            channel = False


        for filename in [m.name for m in iter_modules(['cogs'])]:
                cogs_list = f"{cogs_list} \n{filename}"

        embed = discord.Embed(color=discord.Color.green(), description=cogs_list)
        message = await ctx.send(embed=embed)

        for filename in [m.name for m in iter_modules(['cogs'])]:
                try:
                    await self.bot.reload_extension("cogs.{}".format(filename))
                    to_send = f"{to_send} \n`✅` Loaded - `cogs/{filename}`"
                except Exception:
                    first_reload_failed_extensions.append(filename)

        for filename in first_reload_failed_extensions:
            try:
                await self.bot.reload_extension("cogs.{}".format(filename))
                
                to_send = f"{to_send} \n`✅` Loaded `cogs/{filename}`"

            except discord.ext.commands.ExtensionNotLoaded:
                to_send = f"{to_send} \n`❌` Not loaded - `cogs/{filename}`"
            except discord.ext.commands.ExtensionNotFound:
                to_send = f"{to_send} \n`❌`  Not found - `cogs/{filename}`"
            except discord.ext.commands.NoEntryPointError:
                to_send = f"{to_send} \n`❌` No setup func - `cogs/{filename}`"
            except discord.ext.commands.ExtensionFailed as e:
                traceback_string = "".join(traceback.format_exception(etype=None, value=e, tb=e.__traceback__))
                to_send = f"{to_send} \n`❌` Execution error - `cogs/{filename}`"
                embed_error = f"\n`❌` Execution error - Traceback `cogs/{filename}`" \
                              f"\n```py\n{traceback_string}\n```"
                if not silent:
                    target = ctx if channel else ctx.author
                    if len(embed_error) > 2000:
                        await target.send(file=io.StringIO(embed_error))
                    else:
                        await target.send(embed_error)

                err = True

        await asyncio.sleep(0.4)
        if err:
            if not silent:
                if not channel:
                    to_send = f"{to_send} \n\n📬 {ctx.author.mention}, I sent you all the tracebacks."
                else:
                    to_send = f"{to_send} \n\n📬 Sent all tracebacks here."
            if silent:
                to_send = f"{to_send} \n\n📭 silent, no tracebacks sent."
            embed = discord.Embed( title='Reloaded some extensions', description=to_send, color=discord.Color.green())
            await message.edit(embed=embed)
        else:
            embed = discord.Embed(title='Reloaded all extensions', description=to_send, color=discord.Color.green())
            await message.edit(embed=embed)

async def setup(bot):
  await bot.add_cog(DeveloperCog(bot))