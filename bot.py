import logging

import environs

from log import TelegramLogsHandler
from telegram import Update
from telegram.ext import Updater, MessageHandler, Filters, CallbackContext


logger = logging.getLogger('bot')


def reply_to_user(update: Update, context: CallbackContext) -> None:
    logger.info('Получено сообщение в tg "{}" от {}'.format(update.message.text, update.effective_chat.id))
    update.message.reply_text(update.message.text)


def main():
    env = environs.Env()
    env.read_env()

    chat_id = env.str('TELEGRAM_CHAT_ID')
    telegram_log_token = env.str('TELEGRAM_LOG_BOT_TOKEN')

    tg_handler = TelegramLogsHandler(chat_id, telegram_log_token)

    logger.addHandler(tg_handler)
    logger.setLevel(env.str('LOG_LEVEL', 'INFO'))

    updater = Updater(env.str('TELEGRAM_BOT_TOKEN'))
    dispatcher = updater.dispatcher
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, reply_to_user))
    updater.start_polling()

    logger.info('Quiz TG бот запущен')

    updater.idle()


if __name__ == '__main__':
    main()
