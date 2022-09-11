from disnake.ext import commands
import disnake

import random
import sys

from .Game import Game


class Connect4(commands.Cog):
    # :red_square:
    # :yellow_square:
    # :white_large_square:

    p1 = 1
    p2 = -1

    reactions = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣"]

    board = [
        [0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0],
    ]

    # Eval Point Values
    winLossVal = 50
    verticalLineVal = 5
    horizontalLineVal = 5
    diagonalUpVal = 5
    diagonalDownVal = 5

    def __init__(self, bot):
        self.bot = bot

    @Game.games.sub_command(description="Play Connect 4 agaist an other user")
    async def connect4(self, interaction, opponent: disnake.User):
        """
        Play Connect4 agaist an other user

        Parameters
        ----------
        opponent: The user you would like to play against
        """
        if opponent.bot and opponent is self.bot: 
            await interaction.response.send_message("Please select a different player")
            return
            
        players = [interaction.author, opponent]
        random.shuffle(players)

        game = f"{players[0].mention} vs {players[1].mention}    \n"
        game += f"{players[0].mention}'s turn\n"
        game += self.boardToString(self.board)

        await interaction.response.send_message(game)
        gameMessage = await interaction.original_message()

        for x in range(7):  # Add the game reactions
            await gameMessage.add_reaction(self.reactions[x])

        if players[0].bot:
            await self.playMiniMax(gameMessage.id, interaction.channel)

    def boardToString(self, board):  # Turns a board into a string
        game = "Connect 4\n"

        for y in range(6):
            for x in range(7):
                if board[x][y] == 0: game += ":white_large_square:"
                if board[x][y] == self.p1: game += ":red_square:"
                if board[x][y] == self.p2: game += ":yellow_square:"

                if x == 6: game += "\n"
                else: game += "       "

        return game

    def stringToBoard(self, string):  # Turns a string into a board
        board = string.replace("       ", "").replace("\n", "").split(":")
        board = [i for i in board if i != ""]

        players = board.pop(0)

        players, player = players.split("    ")

        player = player.split("'")[0].replace("<@", "").replace(">", "")
        players = players.replace("<@", "").replace(">", " ").replace(
            " ", "").replace("!", "").split("vs")

        game = [
            [0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0],
        ]

        x = 0
        y = 0

        for i in range(len(board)):
            if board[i] == "white_large_square": game[x][y] = 0
            if board[i] == "red_square": game[x][y] = self.p1
            if board[i] == "yellow_square": game[x][y] = self.p2

            if x <= 5: x += 1
            elif y == 6: continue
            else:
                x = 0
                y += 1

        return players, game, players.index(player)

    def gameHeader(self, board, players, currentPlayer, nextPlayer):
        game = f"<@{players[0]}> vs <@{players[1]}>    \n"
        if self.checkWin(board, currentPlayer[0]):
            # Tell the person they won
            game += f"<@{currentPlayer[1]}> Won\n"

        else:
            # Tell the person that its their turn
            game += f"<@{players[nextPlayer]}>'s turn\n"

        return game

    @commands.Cog.listener()
    async def on_raw_reaction_add(self,
                                  payload: disnake.RawReactionActionEvent):
        user = payload.member
        if user.bot: return

        emoji = payload.emoji
        channel = await self.bot.fetch_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)

        if not "Connect 4" in message.content: return
        await message.remove_reaction(emoji, user)

        if "Won" in message.content: return

        players, board, turn = self.stringToBoard(message.content)
        if not str(user.id) == players[turn].replace("!", ""):
            return

        currentPlayer, currentPlayerInfo, nextPlayer = self.getCurrentPlayer(
            turn, players)

        playLane = 0
        for x in range(7):  # Finds the lane the player selected
            if self.reactions[x] == emoji.name:
                playLane = x  # 1, 2, 3, 4, 5, 6, 7
                break

        board, _ = self.playInCol(board, playLane, currentPlayer)

        currentPlayer = (currentPlayer, currentPlayerInfo)
        gameMessage = self.gameHeader(board, players, currentPlayer,
                                      nextPlayer)
        gameMessage += self.boardToString(board)

        await message.edit(gameMessage)
        message = await channel.fetch_message(payload.message_id)

        if (await self.bot.fetch_user(players[nextPlayer])).bot:
            await self.playMiniMax(payload.message_id, channel)

    async def playMiniMax(self, messageID, channel):
        message = await channel.fetch_message(messageID)
        if "Won" in message.content: return

        players, board, turn = self.stringToBoard(message.content)
        currentPlayer, currentPlayerInfo, nextPlayer = self.getCurrentPlayer(
            turn, players)

        score, playLane = self.minimax(board, 8, -sys.maxsize - 1, sys.maxsize,
                                       currentPlayer, True)
        board, _ = self.playInCol(board, playLane, currentPlayer)

        currentPlayer = (currentPlayer, currentPlayerInfo)
        gameMessage = self.gameHeader(board, players, currentPlayer,
                                      nextPlayer)
        gameMessage += self.boardToString(board)

        await message.edit(gameMessage)

    # https://www.youtube.com/watch?v=l-hh51ncgDI
    def minimax(self, board, depth, alpha, beta, maximizingPlayer, player):
        if depth == 0 or self.isGameDone(board) != None:
            return self.evalBoard(board)

        if maximizingPlayer:
            maxMove = 0
            maxEval = -sys.maxsize - 1

            for col in self.validCols(board):
                board, y = self.playInCol(board, col, player)
                eval = self.minimax(board, depth - 1, alpha, beta, False,
                                    self.p1 if player == self.p2 else self.p1)
                board = self.undoPlayInCol(col, y, board)

                if type(eval) == tuple: eval, _ = eval

                if maxEval < eval:
                    maxEval = eval
                    maxMove = col

                alpha = max(alpha, eval)
                if beta <= alpha:
                    break

            return maxEval, maxMove

        else:
            minMove = 0
            minEval = sys.maxsize

            for col in self.validCols(board):
                board, y = self.playInCol(board, col, player)
                eval = self.minimax(board, depth - 1, alpha, beta, True,
                                    self.p1 if player == self.p2 else self.p1)
                board = self.undoPlayInCol(col, y, board)

                if type(eval) == tuple: eval, _ = eval

                if minEval > eval:
                    minEval = eval
                    minMove = col

                beta = min(beta, eval)
                if beta <= alpha:
                    break

            return minEval, minMove

    def getCurrentPlayer(self, turn, players):
        if turn == 0: currentPlayer = self.p1
        elif turn == 1: currentPlayer = self.p2
        currentPlayerInfo = players[turn].replace("!", "")

        if turn == 0: nextPlayer = 1
        elif turn == 1: nextPlayer = 0

        return currentPlayer, currentPlayerInfo, nextPlayer

    def playInCol(self, board, col, player):
        for y in range(6):  # Finds the first empty space in the lane
            if board[col][y] == 1 or board[col][y] == -1:
                board[col][y - 1] = player
                return board, y - 1

            elif y == 5 and board[col][y] == 0:
                board[col][y] = player
                return board, y

    def undoPlayInCol(self, col, y, board):
        board[col][y] = 0
        return board

    def validCols(self, board):
        validColumns = []
        for x in range(len(board)):
            if board[x][0] == 0:
                validColumns.append(x)

        return validColumns

    def evalBoard(self, board):
        # Check if game is over
        gameDonePoints = self.isGameDone(board)
        gameDonePoints = 0 if gameDonePoints == None else gameDonePoints

        # Count number of horizontal lines that are unblocked on both players of length 3
        horizontalLinePoints = 0
        for y in range(4):
            for x in range(7):
                t = board[x][y] + board[x][y + 1] + board[x][y + 2]
                if t == -3:
                    horizontalLinePoints += self.horizontalLineVal * 3
                elif t == 3:
                    horizontalLinePoints -= 3 * self.horizontalLineVal * 3

        # Count number of vertical lines that are unblocked on both players of length 3
        verticalLinePoints = 0
        for y in range(6):
            for x in range(5):
                t = board[x][y] + board[x + 1][y] + board[x + 2][y]
                if t == -3:
                    verticalLinePoints += self.verticalLineVal * 3
                if t == 3:
                    verticalLinePoints -= 3 * self.verticalLineVal * 3

        # Count number of diagonal up lines that are unblocked on both players of length 3
        diagonalLinePoints = 0
        for x in range(5):
            for y in range(4):
                t = board[x][y] + board[x + 1][y + 1] + board[x + 2][y + 2]
                if t == -3:
                    diagonalLinePoints += self.diagonalUpVal * 3
                if t == 3:
                    diagonalLinePoints -= 2 * self.diagonalUpVal * 3

        # Count number of diagonal down lines that are unblocked on both players of length 3
        for y in range(4):
            for x in range(2, 6):
                t = board[x][y] + board[x - 1][y + 1] + board[x - 2][y + 2]
                if t == -3:
                    diagonalLinePoints += self.diagonalDownVal * 3
                if t == 3:
                    diagonalLinePoints -= 2 * self.diagonalDownVal * 3

        return gameDonePoints + horizontalLinePoints + verticalLinePoints + diagonalLinePoints

    def isGameDone(self, board):
        botWin = self.checkWin(board, -1)

        if botWin != None and botWin:  # Bot wins
            return self.winLossVal

        elif botWin == None:  # Draw
            return 0

        elif self.checkWin(board, 1):  # Bot losses
            return -self.winLossVal * 4

    def checkWin(self, board, player):
        # Check for horizontal Win
        for y in range(3):
            for x in range(7):
                t = board[x][y] + board[x][y + 1] + board[x][y +
                                                             2] + board[x][y +
                                                                           3]
                if t == 4 or t == -4:
                    return True

        # Check for vertical wins
        for y in range(6):
            for x in range(4):
                t = board[x][y] + board[x + 1][y] + board[x +
                                                          2][y] + board[x +
                                                                        3][y]
                if t == 4 or t == -4:
                    return True

        # Check for positively sloped wins
        for x in range(4):
            for y in range(3):
                t = board[x][y] + board[x + 1][y + 1] + board[x + 2][
                    y + 2] + board[x + 3][y + 3]
                if t == 4 or t == -4:
                    return True

        # Check for negatively sloped wins
        for y in range(3):
            for x in range(3, 6):
                t = board[x][y] + board[x - 1][y + 1] + board[x - 2][
                    y + 2] + board[x - 3][y + 3]
                if t == 4 or t == -4:
                    return True

        # Check if its a draw
        for x in board:
            for y in x:
                if y == 0:
                    return False

        return None
