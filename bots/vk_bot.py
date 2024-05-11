import logging
import random

import redis
import vk_api
from environs import Env
from vk_api.longpoll import VkLongPoll, VkEventType

from keyboards import VK_BOARD
from log import TelegramLogsHandler
from quiz import get_questions

logger = logging.getLogger('bot')


def reply_to_user(event, vk_api):
    logger.info('Пришло новое сообщение в VK "{}" от {}'.format(event.text, event.user_id))

    vk_api.messages.send(
        user_id=event.user_id,
        message=event.text,
        keyboard=VK_BOARD,
        random_id=random.randint(1, 1000)
    )


def new_question_request(event, vk_api, redis_client, questions):
    logger.info('Пришло новое сообщение в VK "{}" от {}'.format(event.text, event.user_id))

    message = random.choice(list(questions))
    redis_client.set(event.user_id, message)

    vk_api.messages.send(
        user_id=event.user_id,
        message=message,
        keyboard=VK_BOARD,
        random_id=random.randint(1, 1000)
    )


def solution_attempt(event, vk_api, redis_client, questions):
    logger.info('Пришло новое сообщение в VK "{}" от {}'.format(event.text, event.user_id))

    message = event.text
    question = redis_client.get(event.user_id)
    if not question:
        message = 'Для следующего вопроса нажми «Новый вопрос»'
    else:
        answer = questions.get(question)
        if answer.lower() in message.lower():
            message = 'Правильно! Поздравляю! Для следующего вопроса нажми «Новый вопрос»'
            redis_client.delete(event.user_id)
        else:
            message = 'Неправильно… Попробуешь ещё раз?'

    vk_api.messages.send(
        user_id=event.user_id,
        message=message,
        keyboard=VK_BOARD,
        random_id=random.randint(1, 1000)
    )


def skip_question_request(event, vk_api, redis_client, questions):
    logger.info('Пришло новое сообщение в VK "{}" от {}'.format(event.text, event.user_id))

    question = redis_client.get(event.user_id)
    answer = questions.get(question)
    message = 'Правильный ответ - {}'.format(answer)
    vk_api.messages.send(
        user_id=event.user_id,
        message=message,
        keyboard=VK_BOARD,
        random_id=random.randint(1, 1000)
    )

    question = random.choice(list(questions))
    redis_client.set(event.user_id, question)
    vk_api.messages.send(
        user_id=event.user_id,
        message=question,
        keyboard=VK_BOARD,
        random_id=random.randint(1, 1000)
    )


def main():
    env = Env()
    env.read_env()

    telegram_log_token = env.str('TELEGRAM_LOG_BOT_TOKEN')
    chat_id = env.str('TELEGRAM_CHAT_ID')
    tg_handler = TelegramLogsHandler(chat_id, telegram_log_token)
    logger.setLevel(env.str('LOG_LEVEL', 'INFO'))
    logger.addHandler(tg_handler)

    vk_session = vk_api.VkApi(token=env.str("VK_ACCESS_TOKEN"))
    vk_get_api = vk_session.get_api()
    longpoll = VkLongPoll(vk_session)
    logger.info('Quiz VK бот запущен')

    r = redis.Redis(
        host=env.str('REDIS_HOST', 'localhost'),
        port=env.int('REDIS_PORT', 6379),
        password=env.str('REDIS_PASSWORD'),
        decode_responses=True
    )
    questions = get_questions(env.str('FILENAME_QUIZ', '../questions.txt'))

    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            if event.text == 'Новый вопрос':
                new_question_request(event, vk_get_api, r, questions)
            elif event.text == 'Сдаться':
                skip_question_request(event, vk_get_api, r, questions)
            else:
                solution_attempt(event, vk_get_api, r, questions)


if __name__ == '__main__':
    main()
