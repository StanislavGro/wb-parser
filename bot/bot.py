import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher, types
from aiogram.enums.parse_mode import ParseMode
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import LinkPreviewOptions

from utills.info_generator import create_product_info
from wb_fsm import WbFsm

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

logger.addHandler(handler)

bot = Bot(token="7539583957:AAF4PtePl3ovmTbnX-OIElw44IHsqtbLFB4")
dp = Dispatcher()


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Ping!")


@dp.message(Command("wb"))
async def cmd_wb(message: types.Message, state: FSMContext):
    await message.answer(text="Введите артикул")
    await state.set_state(WbFsm.input_vendor_code)


@dp.message(WbFsm.input_vendor_code)
async def choosing_vendor_code(message: types.Message, state: FSMContext):
    vendor_code = int(message.text)
    result = create_product_info([vendor_code])

    result['Product name'] = (str(result['Product name'])
                             .replace("-", "\\-")
                             .replace(".", "\\.")
                             .replace("!", "\\!")
                             .replace("'", ""))

    result['Description'] = (str(result['Description'])
                             .replace("-", "\\-")
                             .replace(".", "\\.")
                             .replace("!", "\\!"))

    result['Amount of discount'] = (str(result['Amount of discount'])
                                    .replace("-", "\\-")
                                    .replace(".", "\\.")
                                    .replace("!", "\\!"))

    result['Price'] = (str(result['Price'])
                       .replace("-", "\\-")
                       .replace(".", "\\.")
                       .replace("!", "\\!"))

    result['Product URL'] = (str(result['Product URL'])
                             .replace("-", "\\-")
                             .replace(".", "\\.")
                             .replace("!", "\\!"))

    await message.answer(
        text=f"*{result['Product name']}*\n\n"
             f"{result['Description']}\n\n"
             f"Цена: {result['Amount of discount']} ₽ ||~{result['Price']} ₽~||\n\n"
             f"[Ссылочка на WB]({result['Product URL']})",
        parse_mode=ParseMode.MARKDOWN_V2,
        link_preview_options=LinkPreviewOptions(is_disabled=True)
    )
    await state.clear()


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
