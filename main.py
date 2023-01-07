import asyncio
from aiogram import Bot, Dispatcher, executor, types
from io import BytesIO
import ddmAPI
import os
from dotenv import load_dotenv

load_dotenv()

bot = Bot(token=os.getenv('TOKEN'))
dp = Dispatcher(bot)

kb = [[types.KeyboardButton(text="🛠️ Contact Support"), types.KeyboardButton(text="❔ About")]]
keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, input_field_placeholder="")  # Create keyboard


@dp.message_handler(content_types=['document'])
async def fileHandle(message):
    await message.reply("❌ Please send me the picture as a *'Photo'*, not as a *'File'*",
                        parse_mode="Markdown")


@dp.message_handler(content_types=['photo'])
async def handle_docs_photo(message: types.Message):
    msg = await message.reply("*Processing...*", parse_mode="Markdown")
    image = BytesIO()
    msg_photo = message.photo[-1]
    bytes = await msg_photo.download(destination_file=image)
    loop = asyncio.get_event_loop()
    converted_image_pil = await loop.run_in_executor(None, ddmAPI.GetImage, bytes.read(), msg_photo["width"],
                                                     msg_photo["height"])
    print(f"{message.from_user.id} started processing photo")
    if isinstance(converted_image_pil, str):  # Exception
        await msg.edit_text(text=converted_image_pil, parse_mode="Markdown")
    else:
        bio = BytesIO()
        bio.name = 'image.jpeg'
        converted_image_pil.save(bio, 'JPEG')
        bio.seek(0)
        await msg.delete()
        await message.reply_photo(photo=bio, caption="_Created via @MeInComicsBot_", parse_mode="Markdown")


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
