import logging
import random
from enum import Enum
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '')))

import environs
import redis
from telegram import Update, ReplyKeyboardRemove
from telegram.ext import Updater, MessageHandler, Filters, CallbackContext, ConversationHandler, CommandHandler

from keyboards import TG_BOARD
from log import TelegramLogsHandler
from quiz import get_questions

logger = logging.getLogger('bot')


class STATES(Enum):
    QUESTION, ANSWER, SKIP = range(3)


def start(update: Update, context: CallbackContext) -> STATES:
    message = 'Добро пожаловать в викторину! Для начала нажмите "Новый вопрос"'
    update.message.reply_text(
        text=message,
        reply_markup=TG_BOARD
    )
    return STATES.QUESTION


def handle_new_question_request(update: Update, context: CallbackContext) -> STATES:
    logger.info('Получено сообщение в tg "{}" от {}'.format(update.message.text, update.effective_chat.id))

    redis_ = context.bot_data['redis_client']
    message = random.choice(list(context.bot_data['questions']))
    redis_.set(update.effective_chat.id, message)

    update.message.reply_text(
        text=message,
        reply_markup=TG_BOARD
    )
    return STATES.ANSWER


def handle_solution_attempt(update: Update, context: CallbackContext) -> STATES:
    logger.info('Получено сообщение в tg "{}" от {}'.format(update.message.text, update.effective_chat.id))
    state = STATES.QUESTION
    redis_ = context.bot_data['redis_client']
    message = update.message.text
    question = redis_.get(update.effective_chat.id)
    answer = context.bot_data['questions'].get(question)
    if answer.lower() in message.lower():
        message = 'Правильно! Поздравляю! Для следующего вопроса нажми «Новый вопрос»'
        redis_.delete(update.effective_chat.id)
    else:
        message = 'Неправильно… Попробуешь ещё раз?'
        state = STATES.ANSWER
    update.message.reply_text(
        text=message,
        reply_markup=TG_BOARD
    )
    return state


def handle_skip_question_request(update: Update, context: CallbackContext) -> STATES:
    logger.info('Получено сообщение в tg "{}" от {}'.format(update.message.text, update.effective_chat.id))

    redis_ = context.bot_data['redis_client']
    question = redis_.get(update.effective_chat.id)
    answer = context.bot_data['questions'].get(question)
    message = 'Правильный ответ - {}'.format(answer)
    update.message.reply_text(
        text=message,
        reply_markup=TG_BOARD
    )

    question = random.choice(list(context.bot_data['questions']))
    redis_.set(update.effective_chat.id, question)
    update.message.reply_text(
        text=question,
        reply_markup=TG_BOARD
    )
    return STATES.ANSWER


def cancel(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text('Bye! I hope we can talk again some day.',
                              reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END


def reply_to_user(update: Update, context: CallbackContext) -> None:
    logger.info('Получено сообщение в tg "{}" от {}'.format(update.message.text, update.effective_chat.id))
    redis_ = context.bot_data['redis_client']
    message = update.message.text

    update.message.reply_text(
        text=message,
        reply_markup=TG_BOARD
    )


def main():
    env = environs.Env()
    env.read_env()

    chat_id = env.str('TELEGRAM_CHAT_ID')
    telegram_log_token = env.str('TELEGRAM_LOG_BOT_TOKEN')

    r = redis.Redis(
        host=env.str('REDIS_HOST', 'localhost'),
        port=env.int('REDIS_PORT', 6379),
        password=env.str('REDIS_PASSWORD'),
        decode_responses=True
    )

    tg_handler = TelegramLogsHandler(chat_id, telegram_log_token)
    logger.addHandler(tg_handler)
    logger.setLevel(env.str('LOG_LEVEL', 'INFO'))
    updater = Updater(env.str('TELEGRAM_BOT_TOKEN'))
    dispatcher = updater.dispatcher

    dispatcher.bot_data['questions'] = get_questions(env.str('FILENAME_QUIZ', 'questions.txt'))
    dispatcher.bot_data['redis_client'] = r

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={
            STATES.QUESTION: [
                MessageHandler(Filters.regex(r'(?i)^Новый вопрос$'),
                               handle_new_question_request)
            ],
            STATES.ANSWER: [
                MessageHandler(Filters.regex(r'(?i)^Сдаться$'),
                               handle_skip_question_request),
                MessageHandler(Filters.text & ~Filters.command,
                               handle_solution_attempt),

            ],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    dispatcher.add_handler(conv_handler)

    updater.start_polling()
    logger.info('Quiz TG бот запущен')

    updater.idle()


if __name__ == '__main__':
    main()
