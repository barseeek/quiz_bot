from telegram import ReplyKeyboardMarkup
from vk_api.keyboard import VkKeyboard, VkKeyboardColor


def get_vk_keyboard():
    keyboard = VkKeyboard(one_time=True)

    keyboard.add_button('Новый вопрос', color=VkKeyboardColor.PRIMARY)
    keyboard.add_button('Сдаться', color=VkKeyboardColor.NEGATIVE)

    keyboard.add_line()
    keyboard.add_button('Мой счет', color=VkKeyboardColor.NEGATIVE)

    return keyboard.get_keyboard()


TG_BOARD = ReplyKeyboardMarkup(
    [
        ['Новый вопрос', 'Сдаться'],
        ['Мой счет']
    ]
)

VK_BOARD = get_vk_keyboard()


