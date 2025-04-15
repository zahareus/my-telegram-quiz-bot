from aiogram.filters.callback_data import CallbackData

class EditorCallback(CallbackData, prefix="editor"):
    channel_id: str

class SelectEditorCallback(CallbackData, prefix="select_editor"):
    channel_id: str
    user_id: str

class AddEditorCallback(CallbackData, prefix="add_editor"):
    channel_id: str