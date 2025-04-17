from aiogram.filters.callback_data import CallbackData


class ChannelCallback(CallbackData, prefix="channel"):
    channel_id: str


class WeeklyCallback(CallbackData, prefix="weekly"):
    channel_id: str
    is_weekly: bool


class DailyCallback(CallbackData, prefix="daily"):
    channel_id: str
    is_daily: bool


class DeactivateCallback(CallbackData, prefix="deactivate"):
    channel_id: str


class ConfirmDeactivateCallback(CallbackData, prefix="confirm_deactivate"):
    channel_id: str

