from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from Config import API_TOKEN
from functions import calcCalorie

data, COUNT = None, 0

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())
# kb = ReplyKeyboardMarkup(resize_keyboard=True)
# button1 = KeyboardButton(text='Рассчитать')
# button2 = KeyboardButton(text='Информация')
# kb.add(button1).add(button2)

kb = InlineKeyboardMarkup()
button1 = InlineKeyboardButton(text='Расчитать', callback_data='calories')
button2 = InlineKeyboardButton(text='Формулы расчета', callback_data='formulas')
kb.add(button1).add(button2)


class UserState(StatesGroup):
    age = State()
    growth = State()
    weight = State()


@dp.message_handler(commands=['start'])
async def start(message):
    await message.answer('Привет! Я бот помогающий твоему здоровью.')

@dp.message_handler(text='Расчитать')
async def main_menu(message):
    await message.answer('Выберите опцию:', reply_markup=kb)

@dp.callback_query_handler(text='formulas')
async def formula(call):
    await call.message.answer('Формула Миффлина-Сан Жеора\n10 x вес (кг) + 6,25 x рост (см) – 5 x возраст (г) – 161')

@dp.callback_query_handler(text='calories')
async def setAge(call):
    await call.message.answer('Введите свой возраст')
    await UserState.age.set()
    await call.answer()


# @dp.message_handler(text='Рассчитать')
# async def setAge(message):
#     await message.answer('Введите свой возраст')
#     await UserState.age.set()


@dp.message_handler(state=UserState.age)
async def setGrowth(message, state):
    global COUNT
    if not message.text.isdigit() and COUNT < 3:
        await message.answer('Эх, не правлиьно!\nПопробуй ещё раз')
        COUNT += 1
        print(COUNT)
    elif not message.text.isdigit() and COUNT == 3:
        await message.answer('Ну и не считаем значит калории')
        COUNT = 0
        await state.finish()
    else:
        COUNT = 0
        await state.update_data(age_state=message.text)
        await message.answer(f'Ввведите свой рост')
        await UserState.growth.set()


@dp.message_handler(state=UserState.growth)
async def setWeight(message, state):
    global COUNT
    if not message.text.isdigit() and COUNT < 3:
        await message.answer('Эх, не правлиьно!\nПопробуй ещё раз')
        COUNT += 1
        print(COUNT)
    elif not message.text.isdigit() and COUNT == 3:
        await message.answer('Ну и не считаем значит каллории')
        COUNT = 0
        await state.finish()
    else:
        await state.update_data(growth_state=message.text)
        await message.answer(f'Ввведите свой вес')
        await UserState.weight.set()


@dp.message_handler(state=UserState.weight)
async def send_calories(message, state):
    global data
    global COUNT
    if not message.text.isdigit() and COUNT < 3:
        await message.answer('Эх, не правлиьно!\nПопробуй ещё раз')
        COUNT += 1
        print(COUNT)
    elif not message.text.isdigit() and COUNT == 3:
        await message.answer('Ну и не считаем значит каллории')
        COUNT = 0
        await state.finish()
    else:
        await state.update_data(weight_data=message.text)
        data = await state.get_data()
        await state.finish()
        cal = calcCalorie(age=int(data['age_state']), growth=int(data['growth_state']), weight=int(data['weight_data']))
        await message.answer(f'Суточное потребление калорий {cal}')


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
