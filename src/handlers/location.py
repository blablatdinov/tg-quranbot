from aiogram import types


async def location_handler(message: types.Message):
    print(message.location.latitude)
    print(message.location.longitude)
