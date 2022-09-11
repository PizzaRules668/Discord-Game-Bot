from disnake.ext import commands
import disnake

import random
import re

from .Game import Game 


class Checkers(commands.Cog):
    p1 = (1, 2, 0)
    p2 = (-1, -2, 7)
    
    letterToMove = {
        "a": "0",
        "b": "1",
        "c": "2",
        "d": "3",
        "e": "4",
        "f": "5",
        "g": "6",
        "h": "7"
    }

    def __init__(self, bot):
        self.bot = bot
        self.moveFinder = re.compile("[a-hA-H][1-8]")

    @Game.games.sub_command(description="Play checkers agaist an other user")
    async def checkers(self, interaction, opponent: disnake.User):
        """
        Play checkers agaist an other user

        Parameters
        ----------
        opponent: The user you would like to play against
        """
        if not opponent.bot:
            board = [[-1, 0, -1, 0, 0, 0, 1, 0],
                     [0, -1, 0, 0, 0, 1, 0, 1],
                     [-1, 0, -1, 0, 0, 0, 1, 0],
                     [0, -1, 0, 0, 0, 1, 0, 1],
                     [-1, 0, -1, 0, 0, 0, 1, 0],
                     [0, -1, 0, 0, 0, 1, 0, 1],
                     [-1, 0, -1, 0, 0, 0, 1, 0],
                     [0, -1, 0, 0, 0, 1, 0, 1]]

            players = [interaction.author, opponent]
            random.shuffle(players)

            game = f"{players[0].mention} vs {players[1].mention}\n"
            game += f"It's {players[0].mention} Turn\n"
            game += self.boardToString(board)

            await interaction.response.send_message(game)
            gameMessage = await interaction.original_message()

            thread = await gameMessage.channel.create_thread(
                name=f"{players[0].name} vs {players[1].name} in Checkers",
                message=gameMessage)

            await thread.add_user(interaction.author)
            await thread.add_user(opponent)

    def stringToBoard(self, board):  # Turn string into a board
        board = board.replace("\n", ":").replace(" ", ":").split(":")
        board = [i for i in board if i != ""]
        board = [i for i in board if "regional_indicator" not in i]
        board = [
            i for i in board if i not in
            ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣"]
        ]

        player1 = board.pop(0).replace("<@", "").replace(">", "")
        player2 = board.pop(1).replace("<@", "").replace(">", "")
        players = [player1, player2]
        board.pop(0)
        board.pop(0)

        board.pop(0)
        currentPlayer = board.pop(0).replace("<@", "").replace(">", "")
        board.pop(0)
        board.pop(0)

        game = [[0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0], 
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0], 
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0], 
                [0, 0, 0, 0, 0, 0, 0, 0]]

        x = 0
        y = 0

        for i in range(len(board)):
            if board[i] == "white_large_square": game[x][y] = 0
            if board[i] == "black_large_square": game[x][y] = 0
            if board[i] == "red_square": game[x][y] = self.p1[0]
            if board[i] == "red_circle": game[x][y] = self.p1[1]
            if board[i] == "yellow_square": game[x][y] = self.p2[0]
            if board[i] == "yellow_circle": game[x][y] = self.p2[1]

            if x < 7: x += 1
            elif y == 8: continue
            else:
                x = 0
                y += 1

        return players, currentPlayer, game

    def boardToString(self, board):
        game = "Checkers\n       "

        for i in ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣"]:
            game += i + " "
        game += "\n"

        for y, emoji in zip(range(8), [
                ":regional_indicator_a:", ":regional_indicator_b:",
                ":regional_indicator_c:", ":regional_indicator_d:",
                ":regional_indicator_e:", ":regional_indicator_f:",
                ":regional_indicator_g:", ":regional_indicator_h:"
        ]):
            game += emoji + " "
            for x in range(8):
                if board[x][y] == 0 and (x + y) % 2 == 0: game += ":white_large_square: "
                if board[x][y] == 0 and (x + y) % 2 != 0: game += ":black_large_square: "
                if board[x][y] == self.p1[0]: game += ":red_square: "
                if board[x][y] == self.p1[1]: game += ":red_circle: "
                if board[x][y] == self.p2[0]: game += ":yellow_square: "
                if board[x][y] == self.p2[1]: game += ":yellow_circle: "

                if x == 7: game += "\n"

        return game

    @commands.Cog.listener()
    async def on_thread_join(self, thread):
        async for member in thread.guild.fetch_members(limit=10):
            if not member.name in thread.name:
                await thread.remove_user(member)

    def calculateMoveDirection(self, move1, move2):
        upDown = move1[0] - move2[0]
        leftRight = move1[1] - move2[1]

        return (upDown, leftRight)

    def checkMove(self, move, board, currentPlayer, secondJump=False):
        moves = self.moveFinder.findall(move)
        move3 = None

        opponent = [self.p1, self.p2]
        opponent.remove(currentPlayer)

        try:
            move1 = (int(self.letterToMove[moves[0][0]]), int(moves[0][1]) - 1)
            move2 = (int(self.letterToMove[moves[1][0]]), int(moves[1][1]) - 1)
            if len(moves) == 3:
                move3 = (int(self.letterToMove[moves[2][0]]), int(moves[2][1]) - 1)

            direction = self.calculateMoveDirection(move1, move2)
        except:
            return 3, board

        # If not moving the correct way, and not a king piece
        if direction[0] != currentPlayer[0] and board[move1[1]][move1[0]] != currentPlayer[1]:
            return 0, board

        # If move diagonal
        if abs(direction[0]) > 1 or abs(direction[1]) > 1:
            return 0, board

        # If move vertically
        if direction[1] == 0:
            return 0, board

        # If move horizontally
        if direction[0] == 0:
            return 0, board

        # If empty piece
        if board[move1[1]][move1[0]] == 0:
            return 0, board

        # Else if your piece
        elif board[move1[1]][move1[0]] == currentPlayer[0] or \
             board[move1[1]][move1[0]] == currentPlayer[1]:

            # If target place is empty
            if board[move2[1]][move2[0]] == 0 and not secondJump:
                board[move2[1]][move2[0]] = board[move1[1]][move1[0]]
                board[move1[1]][move1[0]] = 0

                # If at end of board
                if move2[0] == currentPlayer[2]:
                    board[move2[1]][move2[0]] = currentPlayer[1]

                return 1, board

            # Else If target place has a piece 
            elif board[move2[1]][move2[0]] != currentPlayer[0]:
                # If idk
                if board[move2[1]][move2[0]] != opponent[0] or \
                   board[move2[1]][move2[0]] != opponent[1]:
                    # If able to jump
                    if board[move2[1] - direction[1]][move2[0] - direction[0]] == 0:
                        # If not going to jump into void
                        if  (move2[1] - direction[1] != 0 or move2[1] - direction[1] != 7) and \
                            (move2[0] - direction[0] != 0 or move2[0] - direction[0] != 7):
                            board[move2[1] - direction[1]][move2[0] - direction[0]] = board[move1[1]][move1[0]]
                            board[move1[1]][move1[0]] = 0
                            board[move2[1]][move2[0]] = 0

                            # If at end of board
                            if move2[0] - direction[0] == currentPlayer[2]:
                                board[move2[1] - direction[1]][move2[0] - direction[0]] = currentPlayer[1]

                            # If want to jump again
                            if move3 != None:
                                endPos = list(self.letterToMove.keys())[list(self.letterToMove.values()).index(str(move2[0] - direction[0]))]
                                moves[1] = endPos + str(move2[1])
                                return self.checkMove(" ".join(moves[1:]), board, currentPlayer, secondJump=True)

                            return 2, board


                return 0, board

        else:
            return 0, board

        return 0, board

    def checkIfOver(self, board):
        hasP1 = False
        hasP2 = False

        for x in board:
            for y in x:
                if y == self.p1[0] or y == self.p1[1]: hasP1 = True
                if y == self.p2[0] or y == self.p2[1]: hasP2 = True
        
        if not hasP1: return False, 0
        if not hasP2: return False, 1

        return True, -1

    @commands.Cog.listener()
    async def on_message(self, message):
        if type(message.channel) is disnake.DMChannel: return
        if not "Checkers" in message.channel.name: return
        if not message.author.name in message.channel.name: return
        if message.author.bot: return
        if type(message.channel) is not disnake.threads.Thread: return

        message = await message.channel.fetch_message(message.id)
        topMessage = await message.channel.parent.fetch_message(message.channel.id)
        if "Game over" in topMessage.content: return

        players, currentPlayer, game = self.stringToBoard(topMessage.content)
        if message.author.id == currentPlayer: return

        currentPlayerI = self.p1 if players.index(currentPlayer) == 0 else self.p2

        possible, newBoard = self.checkMove(message.content, game, currentPlayerI)
        if possible == 0:
            await message.reply("Invalid Move")
            return

        elif possible == 3:
            return

        gameMessage = f"<@{players[0]}> vs <@{players[1]}>\n"

        over, winner = self.checkIfOver(newBoard)
        if not over:
            gameMessage += f"Game over <@{players[winner]}> Won!\n"
        else:
            players.remove(str(currentPlayer))
            gameMessage += f"It's <@{players[0]}> Turn\n"
        gameMessage += self.boardToString(newBoard)

        await topMessage.edit(gameMessage)