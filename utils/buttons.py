import discord
from typing import List
from discord.ext import commands


class LookingForButton(discord.ui.Button):
    sep = '\u2001'

    def __init__(self, disabled: bool = False, label: str = None):
        super().__init__(style=discord.ButtonStyle.blurple, label=(label or f'{self.sep*14}Join 🎮{self.sep*14}'),
                        disabled=disabled, row=0)

    async def callback(self, interaction: discord.Interaction):
        assert self.view is not None
        view: LookingToPlay = self.view
        if interaction.user and interaction.user.id == view.ctx.author.id:
            return await interaction.response.send_message(embed=discord.Embed(title='Error Occured', description='You can\'t play with yourself', color=discord.Color.red()),
                                                            ephemeral=True)
        view.value = interaction.user
        view.stop()

class CancelButton(discord.ui.Button):
    sep = '\u2001'

    def __init__(self, disabled: bool = False, label: str = None):
        super().__init__(style=discord.ButtonStyle.red, label=(label or f'{self.sep*14}Exit ❌{self.sep*14}'),
                        disabled=disabled, row=1)

    async def callback(self, interaction: discord.Interaction):
        assert self.view is not None
        view: LookingToPlay = self.view
        if interaction.user.id == view.ctx.author.id:
            view.value = None
            for item in view.children:
                item.disabled = True
            await view.message.edit(view=view)
            view.stop()
        else:
            await interaction.response.send_message(embed=discord.Embed(title='Error Occured', description='Only the game author can do that action!', color=discord.Color.red()), 
                                                    ephemeral=True)

class GiveUp(discord.ui.Button):
    sep = '\u2001'

    def __init__(self, disabled: bool = False, label: str = None):
        super().__init__(style=discord.ButtonStyle.red, label=(label or f'{self.sep*4}Give up 🏳️{self.sep*4}'),
                        custom_id='giveUp' ,disabled=disabled, row=3)

    async def callback(self, interaction: discord.Interaction):
        assert self.view is not None
        view: TicTacToe = self.view
        for child in view.children:
            child.disabled = True
        if interaction.user.id == view.player1.id:
            winner = view.player2
        elif interaction.user.id == view.player2.id:
            winner = view.player1
        embed = discord.Embed(title=f'{interaction.user} gave up 🏳️',description=f'{winner.mention} has won 🏆',color=discord.Color.greyple())
        await interaction.response.edit_message(embed=embed ,view=view)
        view.stop()
        
class LookingToPlay(discord.ui.View):
    def __init__(self, timeout: int = 120, label: str = None):
        super().__init__(timeout=timeout)
        self.message: discord.Message = None
        self.value: discord.User = None
        self.ctx: commands.Context = None
        self.add_item(LookingForButton(label=label))
        self.add_item(CancelButton())

    async def on_timeout(self) -> None:
        for button in self.children:
            button.disabled = True
        await self.message.edit(embed=discord.Embed(title='Timed out ⏰',description='Timed out - game has ended.'), view=None)



class TicTacToeButton(discord.ui.Button['TicTacToe']):
    def __init__(self, x: int, y: int):

        super().__init__(style=discord.ButtonStyle.secondary, label='  ', row=y)
        self.x = x
        self.y = y


    async def callback(self, interaction: discord.Interaction):
        assert self.view is not None
        view: TicTacToe = self.view
        state = view.board[self.y][self.x]
        if state in (view.X, view.O):
            return

        if view.current_player == view.player1:
            self.style = discord.ButtonStyle.blurple
            self.label = '\U0001f1fd'
            self.disabled = True
            view.board[self.y][self.x] = view.X
        else:
            self.style = discord.ButtonStyle.red
            self.label = '🅾'
            self.disabled = True
            view.board[self.y][self.x] = view.O

        winner = view.check_board_winner()
        if winner is not None:
            if winner == view.X:
                embed = discord.Embed(title=f'{view.current_player.name} is the winner - \U0001f1fd', description=f'{view.current_player.mention} has won 🏆', color=discord.Color.blue())
            elif winner == view.O:
                embed = discord.Embed(title=f'{view.current_player.name} is the winner - 🅾',  description=f'{view.current_player.mention} has won 🏆', color=discord.Color.red())
            else:
                embed = discord.Embed(title=f' It\'s a tie ☠️', color=discord.Color.red())

            for child in view.children:
                child.disabled = True


        else:
            if view.current_player == view.player1:
                view.current_player = view.player2
                embed = discord.Embed(title="Tic Tac Toe", description=f"{view.current_player.mention}'s turn - 🅾",color=interaction.message.embeds[0].color)
            else:
                view.current_player = view.player1
                embed = discord.Embed(title="Tic Tac Toe", description=f"{view.current_player.mention}'s turn - \U0001f1fd", color=interaction.message.embeds[0].color)

        await interaction.response.edit_message(embed=embed, view=view)


class TicTacToe(discord.ui.View):

    children: List[TicTacToeButton]
    X = -1
    O = 1
    Tie = 2

    def __init__(self, ctx: commands.Context, player1: discord.Member, player2: discord.Member, starter: discord.User):
        super().__init__()
        self.current_player = starter
        self.ctx: commands.Context = ctx
        self.player1: discord.Member = player1
        self.player2: discord.Member = player2
        self.board = [
            [0, 0, 0],
            [0, 0, 0],
            [0, 0, 0],
        ]

        for x in range(3):
            for y in range(3):
                self.add_item(TicTacToeButton(x, y))
        self.add_item(GiveUp())

    def check_board_winner(self):
        for across in self.board:
            value = sum(across)
            if value == 3:
                return self.O
            elif value == -3:
                return self.X

        for line in range(3):
            value = self.board[0][line] + self.board[1][line] + self.board[2][line]
            if value == 3:
                return self.O
            elif value == -3:
                return self.X

        diag = self.board[0][2] + self.board[1][1] + self.board[2][0]
        if diag == 3:
            return self.O
        elif diag == -3:
            return self.X

        diag = self.board[0][0] + self.board[1][1] + self.board[2][2]
        if diag == 3:
            return self.O
        elif diag == -3:
            return self.X

        if all(i != 0 for row in self.board for i in row):
            return self.Tie

        return None

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user and interaction.data['custom_id'] == 'giveUp':
            return True
        if interaction.user and interaction.user.id == self.current_player.id:
            return True
        elif interaction.user and interaction.user.id in (self.player1.id, self.player2.id):
            await interaction.response.send_message(embed=discord.Embed(title='Not your turn', description='Wait for your turn to make a move', color=discord.Color.red()), ephemeral=True)
        elif interaction.user:
            await interaction.response.send_message(embed=discord.Embed(title='Forbidden ', description='You aren\'t a part of this game!', color=discord.Color.red()), ephemeral=True)
        return False