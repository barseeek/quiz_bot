# quiz_bot

Проект состоит из двух ботов, один для Telegram, а другой для VKontakte.
Боты задают случайные вопросы из текстового файла и проверяют ответ, можно пропустить вопрос, если не знаешь ответа.

[Сообщество VK с ботом ](https://vk.com/sh1t_post1ng)

[Телеграм бот](https://t.me/quiz_less0n_bot)

## Как запустить
Для начала работы необходимо выполнить несколько шагов по настройке среды и конфигурации проекта.

1. Клонируйте репозиторий

    ```bash
    git clone https://github.com/barseeek/quiz_bot.git
    ```
2. Установите Python и зависимости:
   
    ```bash   
    pip install -r requirements.txt
    ```
3. Получите токены доступов и настройте переменные окружения как описано ниже.
4. Запустите ботов
    ```bash   
    python tg_bot.py
    python vk_bot.py
    ```   

## Как настроить

### Переменные окружения
Для работы ботов необходимо установить следующие переменные окружения:

```ini
TELEGRAM_BOT_TOKEN=Токен бота Telegram.
TELEGRAM_LOG_BOT_TOKEN=Токен бота Telegram для логгирования
LANGUAGE_CODE=Языковой код (например, ru-RU).
TELEGRAM_CHAT_ID=Идентификатор пользователя Telegram для логгирования.
LOG_LEVEL=Уровень логгирования.
VK_ACCESS_TOKEN=Токен доступа Vkontakte.
FILENAME_QUIZ=имя файла с вопросами, по умолчанию "questions.txt", лежит в корневой папке проекта
```
