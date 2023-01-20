import asyncio
from aiogram import Bot, Dispatcher, executor, types
import ddmAPI
import os
from dotenv import load_dotenv
import httpx

load_dotenv()

bot = Bot(token=os.getenv('TOKEN'))
dp = Dispatcher(bot)

kb = [[types.KeyboardButton(text="🛠️ Contact Support"), types.KeyboardButton(text="❔ About")]]
keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, input_field_placeholder="")  # Create keyboard

USERAGENT = "Mozilla/5.0 (X11; Linux x86_64; rv:106.0) Gecko/20100101 Firefox/106.0"


@dp.message_handler(content_types=['document'])
async def fileHandle(message):
    await message.reply("❌ Please send me the picture as a *'Photo'*, not as a *'File'*",
                        parse_mode="Markdown")


@dp.message_handler(content_types=['photo'])
async def handle_docs_photo(message: types.Message):
    msg = await message.reply("*Processing...*", parse_mode="Markdown")
    msg_photo = await message.photo[-1].get_url()
    r = httpx.get(url=msg_photo, headers={"User-Agent": USERAGENT})
    r.raise_for_status()
    picture_bytes = r.content
    loop = asyncio.get_event_loop()
    converted_image_pil = await loop.run_in_executor(None, ddmAPI.GetImage, picture_bytes)
    print(f"{message.from_user.id} started processing photo")
    if not converted_image_pil.startswith(('http://', 'https://')):  # Exception
        await msg.edit_text(text=converted_image_pil, parse_mode="Markdown")
    else:
        await msg.delete()
        await message.reply_photo(photo=converted_image_pil,
                                  caption="_Created via @MeInComicsBot_",
                                  parse_mode="Markdown")


@dp.message_handler(commands=['start'])  # Run after /start command
async def send_welcome(message: types.Message):
    await message.answer(
        "👨‍🎨 Hi! Using the bot *“Me In Comics”* _(formerly known as Different Dimension Me)_ anyone can easily create their own anime versions of their photos.\n\n*Just send me images in this chat and I will transform them!*",
        parse_mode="Markdown", reply_markup=keyboard)


@dp.message_handler(text="🛠️ Contact Support")  # Run action after pressing keyboard
async def get_support(message: types.Message):
    await message.reply("🛠️ You can contact support here: @NoveSupportBot")


@dp.message_handler(text="❔ About")  # Run action after pressing keyboard
async def get_about(message: types.Message):
    try:
        await message.reply(
            '❔ Using the bot *“Me In Comics”* _(formerly known as Different Dimension Me)_ anyone can easily create their own anime versions of their photos.\n\n*Just send me images in this chat and I will transform them!*',
            parse_mode='Markdown')
    except:
        pass


if __name__ == '__main__':
    executor.start_polling(dp)
