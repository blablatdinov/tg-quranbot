from aiogram import Bot

from settings import settings


def get_bot_instance():
    return Bot(token=settings.API_TOKEN, parse_mode='HTML')
