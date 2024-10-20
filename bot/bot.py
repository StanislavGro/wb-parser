import asyncio
import os

from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import FSInputFile
from aiogram.utils.media_group import MediaGroupBuilder
from dotenv import find_dotenv, load_dotenv

from utills.info_generator import create_product_info, logger, replace_sensitive_symbols
from wb_fsm import WbFsm

load_dotenv(find_dotenv())

bot = Bot(token=os.getenv('BOT_TOKEN'))
dp = Dispatcher()


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Ping!")


@dp.message(Command("wildberries"))
async def cmd_wb(message: types.Message, state: FSMContext):
    await message.answer(text="Введите артикул товара с WB 👇🏻")
    await state.set_state(WbFsm.input_vendor_code)


@dp.message(WbFsm.input_vendor_code)
async def choosing_vendor_code(message: types.Message, state: FSMContext):
    vendor_code = int(message.text)

    result = create_product_info([vendor_code])

    logger.info(result)

    logger.info(result['Images'][f'{vendor_code}'])

    title = replace_sensitive_symbols(result['Product name'][0])

    sale = replace_sensitive_symbols(result['Amount of discount'][0])
    logger.info(sale)
 
    price = replace_sensitive_symbols(result['Price'][0])
    logger.info(price)

    url = replace_sensitive_symbols(result['Product URL'][0])
    logger.info(url)

    rating = replace_sensitive_symbols(f"{result['Rating'][0]}")
    logger.info(rating)

    number_of_reviews = result['Number of reviews'][0]
    logger.info(number_of_reviews)

    if number_of_reviews == 0:
        number_of_reviews_string = "Оценок нет:"
    elif number_of_reviews == 1:
        number_of_reviews_string = f"Оценка {number_of_reviews} покупателя:"
    else:
        number_of_reviews_string = f"Оценка {number_of_reviews} покупателей:"

    raw_descr = replace_sensitive_symbols(result['Description'][0])
    count_of_symbols = 1024 - len(title + "\n") - len("\nЦена: " + sale + " " + price) - len(f"*{number_of_reviews_string}* {rating} из 5\n\n") - len("\nСсылочка на WB")
    restrict_descr = raw_descr[:count_of_symbols]
    last_dot = restrict_descr.rfind(".")
    descr = restrict_descr[:last_dot + 1]
    logger.info(descr)

    text = f"*{title}*\n\n" \
           f"{descr}\n\n" \
           f"*{number_of_reviews_string}* {rating} из 5\n\n" \
           f"*Цена:* ||{sale} ₽|| ~{price} ₽~\n\n" \
           f"[Ссылочка на WB]({url})"

    album_builder = MediaGroupBuilder(
        caption=text
    )

    for i, photo_path in enumerate(result['Images'][f'{vendor_code}']):
        if i == 0:
            album_builder.add_photo(
                media=FSInputFile(photo_path),
                parse_mode=ParseMode.MARKDOWN_V2,
                caption=text,
            )
        else:
            album_builder.add_photo(
                media=FSInputFile(photo_path),
                parse_mode=ParseMode.MARKDOWN_V2,
            )

    await message.answer_media_group(
        media=album_builder.build(),
    )

    logger.info("Successful sent!")

    await state.clear()


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
