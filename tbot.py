import telegram
import logging
from telegram.ext import (Updater, Filters, CommandHandler, ConversationHandler, CallbackQueryHandler, MessageHandler)
from telegram import InlineKeyboardMarkup

import console
import board
import alphabeta
from mytokens import *
from matches_game import MatchesGame, ACTIVE_GAMES
from wolfram_api_client import ask

SECOND = 2


class Zaebot:
    """
    Telegram bot with the following functionalities:
    - It is self-explanatory.
    - It can solve simple equations and math tasks (integrate, derive, …)
    - It can play “tic-tac-toe” and “matches”
    - It can play XO 5-in-a-row
    """
    token = telegram_token
    board_size = 3

    def __init__(self):

        self.custom_kb = []
        self.updater = Updater(token=self.token)
        self.dispatcher = self.updater.dispatcher
        self.games = {}
        self.human = {}

    def start(self, bot, update):
        bot.send_message(chat_id=update.message.chat_id, text="I'm a bot, let's play!")

    def t3(self, bot, update):
        custom_kb = [['X'], ['O']]
        reply = telegram.ReplyKeyboardMarkup(custom_kb)
        bot.sendMessage(chat_id=update.message.chat_id, text='Choose your side:', reply_markup=reply)

        return 0

    def t5(self, bot, update):
        custom_kb = [['X'], ['O']]
        reply = telegram.ReplyKeyboardMarkup(custom_kb)
        bot.sendMessage(chat_id=update.message.chat_id, text='Choose your side:', reply_markup=reply)

        return 0

    def ttt3(self, bot, update):
        try:
            if update.message.text == "X":
                human_move = board.State.X
            elif update.message.text == 'O':
                human_move = board.State.O
        except:
            pass
        reply = telegram.ReplyKeyboardRemove()
        bot.send_message(chat_id=update.message.chat_id, text='Preparing...', reply_markup=reply)
        self.board_size = 3
        self.games[update.message.chat_id] = [console.Console(self.board_size), [], human_move]

        for i in range(0, 9, 3):
            self.games[update.message.chat_id][1].append([telegram.InlineKeyboardButton(' ', callback_data=str(i)),
                                                          telegram.InlineKeyboardButton(' ', callback_data=str(i + 1)),
                                                          telegram.InlineKeyboardButton(' ', callback_data=str(i + 2))])
        reply = InlineKeyboardMarkup(self.games[update.message.chat_id][1])

        if human_move == board.State.O:
            self.play_move(bot, update, update.message.chat_id)

        bot.send_message(chat_id=update.message.chat_id, text='Let\'s play, my dear opponent! ', reply_markup=reply)

        return 1

    def ttt5(self, bot, update):
        try:
            if update.message.text == "X":
                human_move = board.State.X
            elif update.message.text == 'O':
                human_move = board.State.O
        except:
            pass
        reply = telegram.ReplyKeyboardRemove()
        bot.send_message(chat_id=update.message.chat_id, text='Preparing...', reply_markup=reply)
        self.board_size = 5
        self.games[update.message.chat_id] = [console.Console(self.board_size), [], human_move]
        for i in range(0, 25, 5):
            self.games[update.message.chat_id][1].append([telegram.InlineKeyboardButton(' ', callback_data=str(i)),
                                                          telegram.InlineKeyboardButton(' ', callback_data=str(i + 1)),
                                                          telegram.InlineKeyboardButton(' ', callback_data=str(i + 2)),
                                                          telegram.InlineKeyboardButton(' ', callback_data=str(i + 3)),
                                                          telegram.InlineKeyboardButton(' ', callback_data=str(i + 4))])
        reply = InlineKeyboardMarkup(self.games[update.message.chat_id][1])

        if human_move == board.State.O:
            self.play_move(bot, update, update.message.chat_id)

        bot.send_message(chat_id=update.message.chat_id, text='Let\'s play, my dear opponent! ', reply_markup=reply)

        return 1

    def tictac3(self, bot, update):

        id = update.callback_query.message.chat_id

        print(id)

        self.play_move(bot, update, id)

        if self.games[id][0].board.game_over:
            self.get_winner(bot, update, id)
            return -1

        self.play_move(bot, update, id)

        if self.games[id][0].board.game_over:
            self.get_winner(bot, update, id)
            return -1

        return 1

    def play_move(self, bot, update, id):
        mc = self.games[id][0].board.move_count

        if self.games[id][0].board.get_turn() == self.games[id][2]:
            self.get_player_move(bot, update, id)
        else:
            abp = alphabeta.AlphaBetaPruning(self.games[id][0].board.board_width ** 2 - 1)
            if self.games[id][0].board.board_width > 3:
                m_p = 5
            else:
                m_p = self.games[id][0].board.board_width ** 2 - 1
            abp.run(player=self.games[id][0].board.get_turn(), board=self.games[id][0].board, max_ply=m_p)

        for i in range(self.board_size):
            for j in range(self.board_size):
                if self.games[id][0].board.board[i][j] == board.State.X:
                    self.games[id][1][i][j] = telegram.InlineKeyboardButton("❌",
                                                                            callback_data=str(i * self.board_size + j))
                elif self.games[id][0].board.board[i][j] == board.State.O:
                    self.games[id][1][i][j] = telegram.InlineKeyboardButton('⭕️',
                                                                            callback_data=str(i * self.board_size + j))

        reply = InlineKeyboardMarkup(self.games[id][1])

        if self.games[id][0].board.move_count == 1 and self.games[id][2] == board.State.O:
            pass
        elif mc < self.games[id][0].board.move_count:
            bot.editMessageText(chat_id=update.callback_query.message.chat_id,
                                message_id=update.callback_query.message.message_id,
                                text='Let\'s play, my dear opponent! ',
                                reply_markup=reply)

    def get_player_move(self, bot, update, id):

        move = int(update.callback_query.data)
        if not self.games[id][0].board.move(move):
            try:
                query = update.callback_query
                reply = InlineKeyboardMarkup(self.games[id][1])
                bot.editMessageText(
                    chat_id=query.message.chat_id,
                    message_id=query.message.message_id,
                    text="Press on the blank box please",
                    reply_markup=reply
                )
            except telegram.error.BadRequest:
                pass

    def get_winner(self, bot, update, id):
        winner = self.games[id][0].board.get_winner()

        if winner == board.State.Blank:
            s = "The TicTacToe is a Draw."
        else:
            s = "Player " + str(winner.name) + " wins!"

        if self.games[id][0].board.board_width == 3:
            s += "\nTo start a new game press please\n"
            s += "/tictactoe"
        elif self.games[id][0].board.board_width == 5:
            s += "\nTo start a new game press please\n"
            s += "/tictactoe_5x5"

        query = update.callback_query
        reply = InlineKeyboardMarkup(self.games[id][1])
        bot.editMessageText(
            chat_id=query.message.chat_id,
            message_id=query.message.message_id,
            text=s,
            reply_markup=reply
        )
        del self.games[id]

    def solve(self, bot, update, args):
        """
        Solve math tasks using Wolfram Alpha.
        """
        if not ''.join(args):
            result = 'You need to specify a task. For example, "\solve x+1=4"'
            bot.send_message(chat_id=update.message.chat_id, text=result)
            return
        request = ' '.join(args)
        result = ask(request)
        if result is None:
            result = "I don't know!"
        bot.send_message(chat_id=update.message.chat_id, text=result)

    def matches(self, bot, update):
        """
        Matches Game. 
        """
        game = ACTIVE_GAMES.get(update.message.chat_id, None)
        if game is None:
            game = MatchesGame(chat_id=update.message.chat_id)
            ACTIVE_GAMES[update.message.chat_id] = game
        bot.send_message(chat_id=update.message.chat_id, text=game.RULES)
        bot.send_message(chat_id=update.message.chat_id, text='Do you want to make first move? (y/n)')

    def exit(self, bot, update):
        """
        Exit Matches Game.
        """
        try:
            del ACTIVE_GAMES[update.message.chat_id]
        except KeyError:
            pass
        response = "The game is finished."
        bot.send_message(chat_id=update.message.chat_id, text=response)

    def move(self, bot, update):
        """
        Handles Matches moves.
        """
        text = update.message.text.strip()
        game = ACTIVE_GAMES.get(update.message.chat_id, None)
        if game is not None:
            response = game.get_response(text)
            for r in response:
                bot.send_message(chat_id=update.message.chat_id, text=r)
        else:
            bot.send_message(chat_id=update.message.chat_id, text=text)

    def handlers(self):
        start_handler = CommandHandler('start', self.start)
        self.dispatcher.add_handler(start_handler)

        conv_handler = ConversationHandler(
            entry_points=[CommandHandler('tictactoe', self.t3)],
            states={
                0: [MessageHandler(Filters.text, self.ttt3), CallbackQueryHandler(self.ttt3)],
                1: [CallbackQueryHandler(self.tictac3)]
            },
            fallbacks=[CommandHandler('start', self.start)]
        )

        conv_handler_5 = ConversationHandler(
            entry_points=[CommandHandler('tictactoe_5x5', self.t5)],
            states={
                0: [MessageHandler(Filters.text, self.ttt5), CallbackQueryHandler(self.ttt5)],
                1: [CallbackQueryHandler(self.tictac3)],
            },
            fallbacks=[CommandHandler('start', self.start)]
        )

        self.dispatcher.add_handler(conv_handler)
        self.dispatcher.add_handler(conv_handler_5)

        solve_handler = CommandHandler('solve', self.solve, pass_args=True)
        matches_handler = CommandHandler('matches', self.matches)
        exit_handler = CommandHandler('exit', exit)
        move_handler = MessageHandler(Filters.text, self.move)
        self.dispatcher.add_handler(solve_handler)
        self.dispatcher.add_handler(matches_handler)
        self.dispatcher.add_handler(exit_handler)
        self.dispatcher.add_handler(move_handler)


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
    bot = Zaebot()
    bot.handlers()
    bot.updater.start_polling()
    bot.updater.idle()
