from disnake.ext import commands
import disnake

from typing import List
import random
import sys

from .Game import Game

class TicTacToe(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @Game.games.sub_command(description="Play tictactoe agaist an other user")
    async def tictactoe(self, interaction, opponent: disnake.User, bet=0):
        """
        Play tictactoe agaist an other user

        Parameters
        ----------
        opponent: The user you would like to play against
        bet: The amount of Pizzacoin bet on
        """
        if opponent.bot and opponent is self.bot: 
            await interaction.response.send_message("Please select a different player")
            return

        players = [interaction.author, opponent]
        random.shuffle(players)

        game = Game(players[0], players[1], bet)
        await interaction.response.send_message(f"{players[0].mention} goes first",
                            view=game)

        if players[0].id == self.bot.application_id:
            await game.playMiniMax(await interaction.original_message())

class TicTacToeButton(disnake.ui.Button['TicTacToe']):
    def __init__(self, x: int, y: int):
        super().__init__(style=disnake.ButtonStyle.secondary,
                         label='\u200b',
                         row=y)
        self.x = x
        self.y = y

    async def callback(self, interaction: disnake.Interaction):
        assert self.view is not None
        view: Game = self.view
        state = view.board[self.y][self.x]
        if state in (view.X, view.O):
            return

        if interaction.user == view.currentPlayer:
            self.changeState(view)

            view.currentPlayerMarker = view.X if view.currentPlayerMarker == view.O else view.O
            view.currentPlayer = view.player2 if view.currentPlayer == view.player1 else view.player1
            content = f"It is now {view.currentPlayer.mention}'s turn"

        winner = view.checkBoardWinner()
        if winner is not None:
            if winner == view.X:
                content = f'{view.player1.mention} won!'
            elif winner == view.O:
                content = f'{view.player2.mention} won!'
            else:
                content = "It's a tie!"

            for child in view.children:
                child.disabled = True

            view.stop()

        await interaction.response.edit_message(content=content, view=view)

        if view.currentPlayer.bot:
            await view.playMiniMax(await interaction.original_message())
    
    def changeState(self, view):
        self.disabled = True
        view.board[self.y][self.x] = view.currentPlayerMarker

        self.style = disnake.ButtonStyle.danger if view.currentPlayer == view.player1 else disnake.ButtonStyle.success
        self.label = 'X' if view.currentPlayerMarker == view.X else "O"

class Game(disnake.ui.View):
    children: List[TicTacToeButton]
    X = -1
    O = 1
    Tie = 2

    winLossVal          = 50
    verticalLineVal     = 5
    horizontalLineVal   = 5
    diagonalVal         = 5

    def __init__(self, player1, player2, bet=0):
        super().__init__()
        self.currentPlayer = player1
        self.currentPlayerMarker = self.X
        self.board = [
            [0, 0, 0],
            [0, 0, 0],
            [0, 0, 0],
        ]

        self.player1 = player1
        self.player2 = player2
        self.bet = bet

        for x in range(3):
            for y in range(3):
                self.add_item(TicTacToeButton(x, y))

    async def playMiniMax(self, message):
        message = await message.channel.fetch_message(message.id)

        score = 0
        move = ()
        x = self.minimax(self.board, 3, -sys.maxsize-1, sys.maxsize, True)

        if type(x) == tuple: score, move = x
        else: return
        while self.board[move[0]][move[1]] != 0:
            score, move = self.minimax(self.board, 3, -sys.maxsize-1, sys.maxsize, True)
        
        for i, child in enumerate(self.children):
            if child.y == move[0] and child.x == move[1]:
                self.children[i].changeState(self)

                self.currentPlayerMarker = self.X if self.currentPlayerMarker == self.O else self.O
                self.currentPlayer = self.player2 if self.currentPlayer == self.player1 else self.player1
                content = f"It is now {self.currentPlayer.mention}'s turn"
                break

        winner = self.checkBoardWinner()
        if winner is not None:
            if winner == self.X:
                content = f'{self.player1.mention} won!'
            elif winner == self.O:
                content = f'{self.player2.mention} won!'
            else:
                content = "It's a tie!"

            for child in self.children:
                child.disabled = True

            self.stop()

        await message.edit(content=content, view=self)

    def minimax(self, board, depth, alpha, beta, maximizingPlayer):
        if depth == 0 or self.isGameDone(board) != None:
            return self.evalBoard(board)

        if maximizingPlayer:
            maxMove = 0
            maxEval = -sys.maxsize -1
            for move in self.validMoves(board):
                board = self.doMove(board, move, self.O)
                eval = self.minimax(board, depth-1, alpha, beta, False)
                board = self.undoMove(board, move)

                if type(eval) == tuple: eval, _ = eval

                if maxEval < eval:
                    maxEval = eval
                    maxMove = move

                alpha = max(alpha, eval)
                if beta <= alpha:
                    break

            return maxEval, maxMove

        else:
            minMove = 0
            minEval = sys.maxsize
            for move in self.validMoves(board):
                board = self.doMove(board, move, self.X)
                eval = self.minimax(board, depth-1, alpha, beta, True)
                board = self.undoMove(board, move)

                if type(eval) == tuple: eval, _ = eval

                if minEval > eval:
                    minEval = eval
                    minMove = move

                beta = min(beta, eval)
                if beta <= alpha:
                    break

            return minEval, minMove

    def evalBoard(self, board):
        gameDonePoints = self.isGameDone(board)
        gameDonePoints = 0 if gameDonePoints == None else gameDonePoints

        horizontalLinePoints = 0
        for across in self.board:
            value = sum(across)
            if value == 2:
                horizontalLinePoints += self.horizontalLineVal
            elif value == -2:
                horizontalLinePoints += -self.horizontalLineVal * 2

        verticalLinePoints = 0
        for line in range(2):
            value = self.board[0][line] + self.board[1][line]
            if value == 2:
                verticalLinePoints += self.verticalLineVal
            elif value == -2:
                verticalLinePoints += -self.verticalLineVal * 2

        diagonalLinePoints = 0
        diag = self.board[0][2] + self.board[1][1]
        if diag == 2:
            diagonalLinePoints = self.diagonalVal
        elif diag == -2:
            diagonalLinePoints = -self.diagonalVal*2

        diag = self.board[1][1] + self.board[2][0]
        if diag == 2:
            diagonalLinePoints = self.diagonalVal
        elif diag == -2:
            diagonalLinePoints = -self.diagonalVal*2

        diag = self.board[1][1] + self.board[2][2]
        if diag == 2:
            diagonalLinePoints = self.diagonalVal
        elif diag == -2:
            diagonalLinePoints = -self.diagonalVal*2

        diag = self.board[0][0] + self.board[1][1]
        if diag == 2:
            diagonalLinePoints = self.diagonalVal
        elif diag == -2:
            diagonalLinePoints = -self.diagonalVal*2

        return gameDonePoints + horizontalLinePoints + verticalLinePoints + diagonalLinePoints

    def isGameDone(self, board):
        game = Game(self.player1, self.player2)
        game.board = board
        botWin = game.checkBoardWinner()
        del game

        if botWin == self.O:
            return self.winLossVal

        elif botWin == self.Tie:
            return 0

        elif botWin == self.X:
            return -self.winLossVal*4

    def validMoves(self, board):
        moves = []

        for i, x in enumerate(board):
            for j, y in enumerate(x):
                if y == 0: moves.append((i, j))

        return moves

    def doMove(self, board, move, player):
        board[move[0]][move[1]] = player
        return board

    def undoMove(self, board, move):
        board[move[0]][move[1]] = 0
        return board

    def checkBoardWinner(self):
        winner = None
        for across in self.board:
            value = sum(across)
            if value == 3:
                winner = self.O
            elif value == -3:
                winner = self.X

        for line in range(3):
            value = self.board[0][line] + self.board[1][line] + self.board[2][
                line]
            if value == 3:
                winner = self.O
            elif value == -3:
                winner = self.X

        diag = self.board[0][2] + self.board[1][1] + self.board[2][0]
        if diag == 3:
            winner = self.O
        elif diag == -3:
            winner = self.X

        diag = self.board[0][0] + self.board[1][1] + self.board[2][2]
        if diag == 3:
            winner = self.O
        elif diag == -3:
            winner = self.X

        if all(i != 0 for row in self.board for i in row):
            winner = self.Tie

        if winner == self.X:
            return self.X

        elif winner == self.O:
            return self.O

        elif winner == self.Tie:
            return self.Tie

        return None
