from aiogram.fsm.state import StatesGroup, State


class WbFsm(StatesGroup):
    input_vendor_code = State()
