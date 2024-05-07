import logging
import random

import environs
import redis
from telegram import Update
from telegram.ext import Updater, MessageHandler, Filters, CallbackContext

from keyboards import QUIZ_BOARD
from log import TelegramLogsHandler
from quiz import get_questions

logger = logging.getLogger('bot')


def reply_to_user(update: Update, context: CallbackContext) -> None:
    logger.info('Получено сообщение в tg "{}" от {}'.format(update.message.text, update.effective_chat.id))
    message = update.message.text
    if message == 'Новый вопрос':
        message = random.choice(list(context.bot_data['questions']))
        context.bot_data['redis'].set(update.effective_chat.id, message)

    update.message.reply_text(
        text=message,
        reply_markup=QUIZ_BOARD
    )


def main():
    env = environs.Env()
    env.read_env()

    chat_id = env.str('TELEGRAM_CHAT_ID')
    telegram_log_token = env.str('TELEGRAM_LOG_BOT_TOKEN')

    r = redis.Redis(
        host=env.str('REDIS_HOST', 'localhost'),
        port=env.int('REDIS_PORT', 6379),
        password=env.str('REDIS_PASSWORD')
    )
    tg_handler = TelegramLogsHandler(chat_id, telegram_log_token)

    logger.addHandler(tg_handler)
    logger.setLevel(env.str('LOG_LEVEL', 'INFO'))

    updater = Updater(env.str('TELEGRAM_BOT_TOKEN'))
    dispatcher = updater.dispatcher

    dispatcher.bot_data['questions'] = get_questions(env.str('FILENAME_QUIZ', 'questions.txt'))
    dispatcher.bot_data['redis'] = r

    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, reply_to_user))
    updater.start_polling()
    logger.info('Quiz TG бот запущен')

    updater.idle()


if __name__ == '__main__':
    main()
