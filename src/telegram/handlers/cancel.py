from aiogram import Router
from src.telegram.callback import CancelCallback
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

cancel_router = Router()

@cancel_router.callback_query(CancelCallback.filter())
async def cancel(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.delete()
    await call.answer()