import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram import F
from aiogram.filters.command import Command
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from aiogram.client.default import DefaultBotProperties
import DbContext
from Repositories.QuizRepository import QuizRepository

logging.basicConfig(level=logging.INFO)

API_TOKEN = str(os.getenv("BOT_TOKEN"))

bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode='HTML'))
dp = Dispatcher()
dp.message()

@dp.message(Command('start'))
async def cmd_start(message: types.Message):
    builder = ReplyKeyboardBuilder()
    builder.add(types.KeyboardButton(text='Начать квиз'))
    await message.answer(
        "<b>🎌 Добро пожаловать в LinguaMate!</b>\n\n"
        "Сегодня мы проверим твои знания японского языка 🇯🇵\n\n"
        "<i>Готов начать?</i>", reply_markup=builder.as_markup(resize_keyboard=True)
    )

@dp.message(F.text.in_(['Начать квиз', '🔁 Пройти заново']))
@dp.message(Command("quiz"))
async def cmd_quiz(message: types.Message):
    await new_quiz(message)

@dp.message(Command("stats"))
async def stats(message: types.Message):
    row = await DbContext.pool.fetchrow(
        "select correct_answers_count from quiz_state where user_id = $1",
        message.from_user.id
    )

    if row:
        await message.answer(
            f"📊 Ваш последний результат: {row['correct_answers_count']} правильных ответов"
        )
    else:
        await message.answer("Вы ещё не проходили квиз.")

@dp.message(F.text == "📊 Мой результат")
async def stats_button(message: types.Message):
    await stats(message)

async def new_quiz(message):
    quiz = QuizRepository()
    user_id = message.from_user.id  
    await quiz.add(user_id, 0)
    await DbContext.pool.execute("""
        UPDATE quiz_state
        SET correct_answers_count = 0
        WHERE user_id = $1
    """, user_id)
    await get_question(message, user_id, quiz)

async def get_question(message, user_id, quiz):
    questions = await quiz.getAll()
    current_question_id = await quiz.get(user_id)
    question = questions[current_question_id]

    kb = generate_options_keyboard(
        question["options"],
        question["correct_answer"]
    )

    await bot.send_chat_action(message.chat.id, "typing")
    await asyncio.sleep(0.5)

    await message.answer(
        f"🎌 <b>Вопрос {current_question_id + 1} из {len(questions)}</b>\n"
        f"📊 Прогресс: {int((current_question_id / len(questions)) * 100)}%\n\n"
        f"{question['question']}",
        reply_markup=kb
    )

def generate_options_keyboard(opts, answer):
    builder = InlineKeyboardBuilder()

    for opt in opts:
        builder.add(types.InlineKeyboardButton(
            text = opt,
            callback_data="correct_answer" if opt == answer else "wrong_answer"
        ))

    builder.adjust(2)
    return builder.as_markup()

@dp.callback_query(F.data=="correct_answer")
async def right_answer(callback: types.CallbackQuery):
    await answer(callback, "correct_answer")

@dp.callback_query(F.data=="wrong_answer")
async def wrong_answer(callback: types.CallbackQuery):
    await answer(callback, "wrong_answer")

async def answer(callback, answer):
    await callback.bot.edit_message_reply_markup(
        chat_id = callback.from_user.id,
        message_id = callback.message.message_id,
        reply_markup=None
    )

    quiz = QuizRepository()
    current_question_id = await quiz.get(callback.from_user.id)
    questions = await quiz.getAll()

    await bot.send_chat_action(callback.message.chat.id, "typing")
    await asyncio.sleep(0.5)

    if answer == "correct_answer":
        await DbContext.pool.execute("""
            UPDATE quiz_state
            SET correct_answers_count = correct_answers_count + 1
            WHERE user_id = $1
        """, callback.from_user.id)
        await callback.message.answer("✅ <b>Верно!</b> 🎉")
    else:
        correct_answer = questions[current_question_id]['correct_answer']
        await callback.message.answer(
            f"❌ <b>Неправильно.</b>\n\n"
            f"Правильный ответ: <b>{correct_answer}</b>"
        )
    
    current_question_id += 1
    await quiz.add(callback.from_user.id, current_question_id)

    if current_question_id < len(questions):
        await get_question(callback.message, callback.from_user.id, quiz)
    else:
        builder = ReplyKeyboardBuilder()
        builder.add(types.KeyboardButton(text="🔁 Пройти заново"))
        builder.add(types.KeyboardButton(text="📊 Мой результат"))

        await bot.send_chat_action(callback.message.chat.id, "typing")
        await asyncio.sleep(1)

        await callback.message.answer(
            "🎉 <b>Квиз завершён!</b>\n\n"
            "🌸 Спасибо за участие!\n\n"
            "Хочешь попробовать снова?",
            reply_markup=builder.as_markup(resize_keyboard=True)
        )


async def main():
    await DbContext.init_db()
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())