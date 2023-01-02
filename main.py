from aiogram import Bot, Dispatcher, executor, types
from io import BytesIO
import ddmAPI
import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

bot = Bot(token=os.getenv('TOKEN'))
dp = Dispatcher(bot)

kb = [[types.KeyboardButton(text="🛠️ Contact Support"), types.KeyboardButton(text="❔ About")]]
keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, input_field_placeholder="")  # Create keyboard


def init_db():
    return mysql.connector.connect(
        host=os.getenv("HOST"),
        user=os.getenv("DB_USERNAME"),
        passwd=os.getenv("PASSWORD"),
        database=os.getenv("DATABASE"),
    )


mydb = init_db()


def get_cursor():
    global mydb
    try:
        mydb.ping(reconnect=True, attempts=3, delay=5)
    except mysql.connector.Error as err:
        mydb = init_db()
    return mydb.cursor()


@dp.message_handler(content_types=['document'])
async def fileHandle(message):
    await message.reply("❌ Please send me the picture as a *'Photo'*, not as a *'File'*",
                        parse_mode="Markdown")


@dp.message_handler(content_types=['photo'])
async def handle_docs_photo(message):
    msg = await message.reply("*Processing...*", parse_mode="Markdown")
    image = BytesIO()
    msg_photo = message.photo[-1]
    bytes = await msg_photo.download(destination_file=image)
    converted_image_pil = await ddmAPI.GetImage(bytes.read(), msg_photo["width"], msg_photo["height"])
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
    # ADD NEW USER TO DB #
    mycursor = get_cursor()
    sql = "SELECT * FROM MeInComicsUsers WHERE TelegramUserID = %s"
    val = (message.chat.id,)
    mycursor.execute(sql, val)
    myresult = mycursor.fetchall()
    if len(myresult) == 0:
        sql = "INSERT INTO MeInComicsUsers (TelegramUserID) VALUES (%s)"
        val = (message.chat.id,)
        mycursor.execute(sql, val)
        mydb.commit()
    mycursor.close()
    mydb.close()
    # ADD NEW USER TO DB #
    await message.answer(
        "👨‍🎨 Hi! Using the bot *“Me In Comics”* _(formerly known as Different Dimension Me)_ anyone can easily create their own anime versions of their photos.\n\n*Just send me images in this chat and I will transform them!*",
        parse_mode="Markdown", reply_markup=keyboard)


@dp.message_handler(text="🛠️ Contact Support")  # Run action after pressing keyboard
async def get_support(message: types.Message):
    await message.reply("🛠️ You can contact support here: @EmojiCreatorSupportBot")


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
