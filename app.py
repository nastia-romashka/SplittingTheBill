import asyncio
import os
import logging
from pyexpat.errors import messages

from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram import F
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

TOKEN = '7278593611:AAHnok5stRNTA0-7hwrgb2bV9ObZ2ui-sb4'
bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("bot_errors.log"),  # Логи записываются в файл
        logging.StreamHandler()  # Логи выводятся в консоль
    ]
)

# Состояния для FSM
class FeedbackState(StatesGroup):
    waiting_for_feedback = State()
    waiting_for_photo = State()

# Кнопки
upload_button = KeyboardButton(text='📸 Загрузить чек')
feedback_button = KeyboardButton(text='💬 Оставить отзыв')

# Создаем клавиатуру с кнопками
greet_kb = ReplyKeyboardMarkup(
    keyboard=[
        [upload_button],  # Кнопка "Загрузить чек" в первой строке
        [feedback_button]  # Кнопка "Оставить отзыв" во второй строке
    ],
    resize_keyboard=True,# Автоматически подстраивать размер клавиатуры
    input_field_placeholder='Выберите пункт меню'
)

# Команда /start
@dp.message(Command('start'))
async def start_command(message: types.Message):
    await message.answer("Привет! Я бот [...]! Я помогу тебе разделить счет.")
    await message.answer("Загрузи фотографию чека, и я предложу тебе удобные варианты разделения.", reply_markup=greet_kb)

# Обработчик нажатия кнопки "Загрузить чек"
@dp.message(F.text =='📸 Загрузить чек')
async def request_photo(message: types.Message, state: FSMContext):
    await message.answer("Пожалуйста, загрузите фотографию чека.")
    await state.set_state(FeedbackState.waiting_for_photo)  # Устанавливаем состояние ожидания фотографии
members_button = InlineKeyboardButton(text="количество", callback_data="members")
position_button = InlineKeyboardButton(text="разделение по позициям", callback_data="position")
w_button = InlineKeyboardButton(text="x1", callback_data="x1")
q_button = InlineKeyboardButton(text="x2", callback_data="x2")
keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [members_button, position_button],
        [w_button, q_button]

    ])
# Обработчик получения фотографии
@dp.message(FeedbackState.waiting_for_photo,F.photo)
async def handle_photo(message: types.Message, state: FSMContext):
    # Получаем файл фотографии
    photo = message.photo[-1]  # Получаем наибольшее качество фотографии
    file_id = photo.file_id
    file = await bot.get_file(file_id)
    file_path = f'feedbacks/{file.file_path.split("/")[-1]}'
    await bot.download_file(file.file_path, file_path)
    await message.answer("Спасибо! Чек загружен. Теперь вы можете оставить отзыв или продолжить.")
    await state.clear()  # Очистка состояния
@dp.message(Command('test'))
async def handle_solution(message: types.Message,state: FSMContext):
    await message.answer("выберите удобный вариант разделения",reply_markup=keyboard)

@dp.callback_query(F.data == "members")
async def members(callback_query: types.CallbackQuery,state: FSMContext):
    user_id: int = callback_query.from_user.id
    await callback_query.message.answer('введите количество посетителей')
    await state.set_state()
# обработка фото ...

# @dp.message(Command('💬 Оставить отзыв'))
# async def handle_feedback(message: types.Message, state: FSMContext):
#     await message.answer("Пожалуйста, оставьте свой отзыв:")
#     await state.set_state(FeedbackState.waiting_for_feedback)
#
# @dp.message(FeedbackState.waiting_for_feedback)
# async def save_feedback(message: types.Message, state: FSMContext):
#     feedback_text = message.text
#     user_id = message.from_user.id  # Получаем id пользователя
#     try:
#         # Сохраняем отзыв в файл
#         save_feedback_to_file(feedback_text, user_id)
#         await message.answer("Спасибо за ваш отзыв!")
#     except Exception as e:
#         await message.answer(f"Произошла ошибка при сохранении отзыва: {str(e)}")
#     finally:
#         await state.clear()  # Очистка состояния
#
# # Функция для записи отзыва в файл
# def save_feedback_to_file(feedback_text, user_id):
#     folder = 'feedbacks'  # Папка для хранения отзывов
#     if not os.path.exists(folder):
#         os.makedirs(folder)  # Если папка не существует, создаем её
#     file_path = os.path

async def main():
    print('Бот запущен')
    await dp.start_polling(bot)

# Запуск бота
if __name__ == '__main__':
    asyncio.run(main())