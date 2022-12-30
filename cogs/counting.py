import ast
import discord
from discord.ext import commands

enabled = True

class StatusDrop(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label='Enable', description='Enables counting in the server', emoji='✅'),
            discord.SelectOption(label='Disable', description='Disables counting in the server', emoji='❌')
        ]
        super().__init__(placeholder='Choose an option', min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction): 
      global enabled

      next_count = 0
      if self.values[0] == 'Enable':
        if enabled:
          value = "`❌` **Error:** Counting is already enabled"

        else:
          value = "`✅` Enabled counting"
          enabled = True
          database = interaction.client.get_channel(1057770300927914005)

          async for sent in database.history(limit=50):
            if sent.author.id == interaction.client.user.id:

              try:
                next_count = ast.literal_eval(sent.content)
                break

              except:
                continue

      else:
        if not enabled:
          value = "`❌` Counting is already disabled"

        else:
          value = "`❌` Disabled counting"
          enabled = False


      embed = discord.Embed(title='Counting status update')
      
      if next_count != 0:
        value += f"\n> The next count is `{next_count[0]+1}`"

      embed.description = value
      embed.timestamp = discord.utils.utcnow()

      await interaction.response.send_message(embed=embed)


class Counter(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.number = 0

    @discord.ui.button(label='Value: 0', style=discord.ButtonStyle.green)
    async def value(self, interaction: discord.Interaction, button: discord.ui.Button):
        button.disabled = True
        button.label = "Value: "+str(self.number)
        await interaction.response.edit_message(view=self)

    @discord.ui.button(label='+1', style=discord.ButtonStyle.green)
    async def one(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.number += 1
        self.value.label = "Value: "+str(self.number)
        await interaction.response.edit_message(view=self)

    @discord.ui.button(label='+5', style=discord.ButtonStyle.green)
    async def five(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.number += 5
        self.value.label = "Value: "+str(self.number)
        await interaction.response.edit_message(view=self)


    @discord.ui.button(label='+10', style=discord.ButtonStyle.green)
    async def ten(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.number += 10
        self.value.label = "Value: "+str(self.number)
        await interaction.response.edit_message(view=self)

    @discord.ui.button(label='Stop', style=discord.ButtonStyle.red)
    async def stop(self, interaction: discord.Interaction, button: discord.ui.Button):

      await interaction.message.edit(view=None)
      await interaction.response.send_message(f"Set the current count to: `{self.number}`\n> The next count is `{self.number+1}`")

      database = interaction.client.get_channel(1057770300927914005)
      await database.send([self.number, 0])


class ConfigDrop(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label='Configurate', description='Configurate the current count', emoji='1️⃣'),
            discord.SelectOption(label='Enable/Disable', description='Enable/Disable counting in the server', emoji='2️⃣'),
            discord.SelectOption(label='Reset', description='Reset the current count', emoji='3️⃣')
            ]
        super().__init__(placeholder='Choose an option', min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction): 

      if self.values[0] == 'Configurate':
        embed = discord.Embed(title = "Set the current count")
        embed.description = f"Click buttons to add to the current value and press stop to set that value"
        embed.timestamp = discord.utils.utcnow()

        await interaction.response.send_message(embed=embed, view = Counter())
        
      
      elif self.values[0] == 'Enable/Disable':
        embed = discord.Embed(title = f"Choose an option")
        embed.description = f"`✅` - Enable Counting\n`❌` - Disable Counting"
        embed.timestamp = discord.utils.utcnow()

        await interaction.response.send_message(embed=embed, view=StatusView())
      
      else:
        embed = discord.Embed(title = "Confirm to reset")
        embed.description = "Confirm that you want to reset the count to `0`\n`✅` - Reset current count to `0`\n`❌` - Cancel reset and keep current count"
        embed.timestamp = discord.utils.utcnow()

        await interaction.response.send_message(embed=embed, view=Confirm())

class Confirm(discord.ui.View):
    def __init__(self):
        super().__init__()

    @discord.ui.button(label='Confirm', style=discord.ButtonStyle.green)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message('Successfully reset the count to `0`\n> The next count is `1`')
        database = interaction.client.get_channel(1057770300927914005)
        await database.send([0,0])
        self.stop()


    @discord.ui.button(label='Cancel', style=discord.ButtonStyle.red)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message('Canceled the reset and kept the current count')
        self.stop()

class StatusView(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(StatusDrop())

class ConfigView(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(ConfigDrop())


class Counting(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    self.saved = [[0,0]]
    self.check = "✅"
    self.cross = "❌"
    self.channels = [1054268278027063376, 948430079342542879]
    
  
  @commands.command()
  async def count(self, ctx):
    embed = discord.Embed(title = f"Choose an option")
    embed.description = f"`{self.check}` - Enable Counting\n`{self.cross}` - Disable Counting"
    embed.timestamp = discord.utils.utcnow()

    await ctx.reply(embed=embed, view=StatusView())

  @commands.command(aliases=['config','configuration'])
  async def configurate(self, ctx):
    embed = discord.Embed(title="Choose an option to configurate")
    embed.description = "`\U00000031` - Configurate the current count\n`\U00000032` - Enable/Disable counting\n`\U00000033` - Reset the current count"
    embed.timestamp = discord.utils.utcnow()
    
    await ctx.reply(embed=embed, view = ConfigView())

  @commands.command()
  async def a(self, ctx):
    await ctx.reply("Hi")
  

  @commands.Cog.listener()
  async def on_message_delete(self, message):
    global enabled

    if enabled:

      if message.channel.id in self.channels:
        if message.author.bot == False:
          
          saved_values = []
          database = self.bot.get_channel(1057770300927914005)
          async for sent in database.history(limit=50):
            if sent.author.id == self.bot.user.id:

              try:
                last_line = ast.literal_eval(sent.content)

                if len(saved_values) == 2:
                  break
                saved_values.append(last_line)

              except:
                continue

            else:
              continue
          
          if saved_values[-1][0]+1 == saved_values[0][0]:
            if discord.utils.get(message.reactions, emoji="\U00002705"):
            
              desc = f"{message.author.mention} deleted their count at `{self.saved[-1][0]}`\n> The next count is `{saved_values[0][0]+1}`"
              embed = discord.Embed(title='Warning!', description=desc)
              embed.timestamp = discord.utils.utcnow()
            
              await message.channel.send(embed=embed)


  @commands.Cog.listener()
  async def on_message(self, message):
    global enabled

    if enabled:
      content = message.content

      if message.channel.id in self.channels:
        if message.author.bot == False:

          database = self.bot.get_channel(1057770300927914005)
          async for sent in database.history(limit=50):
            if sent.author.id == self.bot.user.id:

              try:
                last_line = ast.literal_eval(sent.content)
                break

              except:
                continue

            else:
              continue


          if message.author.id != last_line[-1]:
            if content.isdigit():

              content = int(content)
              latest_value = int(last_line[0])+1

              if latest_value == content:
                await message.add_reaction(f"{self.check}")
                value = [content, message.author.id]

                self.saved.append(value)
                await database.send(value)

              else:
                
                if latest_value == 0:
                  await message.add_reaction("\U000026a0")

                  await message.channel.send(f"{self.cross} The starting value is `1`", delete_after=5)

                else:
                  await message.add_reaction(f"{self.cross}")

                  desc = f"{message.author.mention} ruined it at `{self.saved[-1][0]}`\n> The next count is `1`"
                  embed = discord.Embed(title='Counting Ruined!', description=desc)
                  embed.timestamp = discord.utils.utcnow()
                  
                  await message.channel.send(embed=embed)

                  database = self.bot.get_channel(1057770300927914005)
                  async for sent in database.history(limit=50):
                      if sent.author.id == self.bot.user.id:
                          try:
                              last_line = ast.literal_eval(sent.content)
                              break
                          except:
                              continue

                  if last_line != [0,0]:
                      await database.send([0,0])

                      self.saved.append([0,0])

          else:
            if content.isdigit():
              await message.add_reaction("\U000026a0")

              await message.channel.send(f"{self.cross} You can not count twice in a row", delete_after=5)


async def setup(bot):
  await bot.add_cog(Counting(bot))