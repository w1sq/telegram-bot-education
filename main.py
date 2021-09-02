# coding=utf8
import asyncio
from asyncio import events
import logging
import time
import aiogram.utils.markdown as fmt
from datetime import datetime
from aiogram import Bot, Dispatcher, executor,types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import InputTextMessageContent, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton, InlineQueryResultPhoto
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Text
from aiogram.types.bot_command import BotCommand
from aiogram.types.inline_query_result import InlineQueryResultArticle
from db_data import db_session
from db_data.__all_models import Users
from sqlite3 import IntegrityError

with open('key.txt','r') as file:
    API_KEY = file.readline()
logging.basicConfig(level=logging.INFO, filename='botlogs.log')
bot = Bot(token=API_KEY)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
db_session.global_init()
print('Bot started')

class NicknamePass(StatesGroup):
    answer = State()

class Timesleep(StatesGroup):
    answer = State()

def generate_multiinline_keyboard (answer):
    keyboard = InlineKeyboardMarkup()
    temp_buttons = []
    for i in answer:
        temp_buttons.append(InlineKeyboardButton(text=str(i[0]), callback_data=str(i[1])))
    keyboard.add(*temp_buttons)
    return keyboard

def generate_inline_keyboard (*answer):
    keyboard = InlineKeyboardMarkup()
    temp_buttons = []
    for i in answer:
        temp_buttons.append(InlineKeyboardButton(text=str(i[0]), callback_data=str(i[1])))
    keyboard.add(*temp_buttons)
    return keyboard

def generate_inline_url_keyboard (*answer):
    keyboard = InlineKeyboardMarkup()
    temp_buttons = []
    for i in answer:
        temp_buttons.append(InlineKeyboardButton(text=str(i[0]), url=i[1]))
    keyboard.add(*temp_buttons)
    return keyboard

def timedate_magic(string1):
    ln = len(string1.split('/'))
    new = []
    for i in string1.split('/'):
        if len(i) == 1:
            new.append('0'+i)
        else:
            new.append(i)
    string1='/'.join(new)
    if ln == 4:
        return string1
    elif ln == 3:
        return string1+f'/{datetime.now().year}'
    elif ln == 2:
        return string1+f'/{"0" + str(datetime.now().month) if  datetime.now().month < 10 else datetime.now().month}/{datetime.now().year}'
    elif ln == 1:
        return string1+f'/{"0" + str(datetime.now().day) if  datetime.now().day < 10 else datetime.now().day}/{"0" + str(datetime.now().month) if  datetime.now().month < 10 else datetime.now().month}/{datetime.now().year}'


async def set_commands(bot: Bot):
    commands = [
        BotCommand(command="/start", description="Запустить бота")
    ]
    await bot.set_my_commands(commands)

anketa_keyb = InlineKeyboardMarkup(resize_keyboard=True).row\
(InlineKeyboardButton(text= 'Заполнить анкету',url='https://docs.google.com/forms/d/e/1FAIpQLSeWhaRPIJYR_mRkZGLbrg8l4Zlm0ycKnNIMDHo1GbEqQ9pw6w/viewform?usp=sf_link')).row\
    (InlineKeyboardButton(text='Я заполнил анкету',callback_data='#anketa'))

cancel_keyb = InlineKeyboardMarkup(resize_keyboard=True).row\
(InlineKeyboardButton(text='Отменить',callback_data='cancel'))

first_day_keyb = InlineKeyboardMarkup(resize_keyboard=True).row\
(InlineKeyboardButton(text= 'Материал первого дня',url='https://docs.google.com/presentation/d/1W-nfDvOCzSpgkyvL_Tk2qy6aNKaCjvYrk0pVrL9cdz8/edit?usp=sharing')).row\
    (InlineKeyboardButton(text='Прочитал',callback_data='#1_day_test'))

first_test_keyb = InlineKeyboardMarkup(resize_keyboard=True).row\
(InlineKeyboardButton(text= 'Перейти к тесту',url='https://docs.google.com/forms/d/e/1FAIpQLSfGhzDqgEfDbWeK34TkSro39lZsDT42kJYiQrbg7KsfHh2gxQ/viewform?usp=sf_link')).row\
    (InlineKeyboardButton(text='Выполнил',callback_data='#1_day_quest'))

second_day_keyb = InlineKeyboardMarkup(resize_keyboard=True).row\
(InlineKeyboardButton(text= 'Материал второго дня',url='https://docs.google.com/presentation/d/1Y8Zg2mnGAyT4NCPD56GKYv9ZasvjFhRXiAFxBYuvxPA/edit?usp=sharing')).row\
    (InlineKeyboardButton(text='Прочитал',callback_data='#2_day_test'))

second_test_keyb = InlineKeyboardMarkup(resize_keyboard=True).row\
(InlineKeyboardButton(text= 'Перейти к тесту',url='https://docs.google.com/forms/d/e/1FAIpQLSeobRQILqKKWWK5Mj7bQsbT1kHr4H2RonouaXpX6QI1QRmawg/viewform?usp=sf_link')).row\
    (InlineKeyboardButton(text='Выполнил',callback_data='#2_day_quest'))

third_day_keyb = InlineKeyboardMarkup(resize_keyboard=True).row\
(InlineKeyboardButton(text= 'Материал третьего дня',url='https://docs.google.com/presentation/d/1XHbotRh6ve3FsNv_f7IP-Jw5QghIQOCP7MWaCBGfUDw/edit?usp=sharing')).row\
    (InlineKeyboardButton(text='Прочитал',callback_data='#3_day_test'))

third_test_keyb = InlineKeyboardMarkup(resize_keyboard=True).row\
(InlineKeyboardButton(text= 'Перейти к тесту',url='https://docs.google.com/forms/d/e/1FAIpQLSe8MYZbbtFWPtEoVcAJ-_kKh2FSmtofYfumDgfiY6ryvakkCg/viewform?usp=sf_link')).row\
    (InlineKeyboardButton(text='Выполнил',callback_data='#3_day_quest'))

@dp.message_handler(commands=['start'])
async def start(message):
    user_name = message.chat.username
    db_sess = db_session.create_session()
    user = db_sess.query(Users).get(user_name)
    if user:
        if user.day != 4:
            await message.answer(f'Добро пожаловать назад, продолжить обучение на дне {user.day}',reply_markup=generate_inline_keyboard(['Продолжить',f'#{user.day}_day_material']))
        else:
            await message.answer('Добро пожаловать назад, я вижу ты решил пройти обучение снова. Начинаем?',reply_markup=generate_inline_keyboard(['да!','#1_day_material']))
    else:
        await message.answer(f'''Привет это Date Invest-бот. Ты решил вступить в нашу команду?\n
    Тогда тебе нужно заполнить анкету и пройти трёхдневное обучение. По времени, каждый из дней обучения занимает 1-2 час(-а)
                            ''', reply_markup=anketa_keyb)

@dp.message_handler(commands=['pass'])
async def pass_start(message):
    await NicknamePass.answer.set()
    await message.answer(f'Напишите nickname человека, которого хотите допустить', reply_markup=cancel_keyb)

@dp.message_handler(state=NicknamePass.answer)
async def pass_user(message,state):
    user_name = message.text.strip
    db_sess = db_session.create_session()
    user = db_sess.query(Users).get(user_name)
    if not user:
        await message.answer('Вы ввели неправильный nickname пользователя, попробуйте снова')
        await state.finish()
    else:
        if not user.authorized:
            user.authorized = True
            db_sess.commit()
            await message.answer(f'Пользователь {user_name} успешно допущен до обучения')
            await bot.send_message(user.telegram_id,'Если ты заполнил анкету тогда пора переходить к обучению!',reply_markup=first_day_keyb)
        else:
            await message.answer(f'Пользователь {user_name} уже допущен')
        db_sess.close()

@dp.message_handler(state=Timesleep.answer)
async def proceed_time(message,state):
    alarm = timedate_magic(message.text)
    try:
        alarm = datetime.strptime(alarm,'%H/%d/%m/%Y')
    except ValueError:
        await message.answer('Дата неправильная')
        return
    if datetime.now() < alarm:
        secs = alarm - datetime.now()
    else:
        await message.answer('Прошлое уже прошло, введите другую дату')
        return 
    db_sess = db_session.create_session()
    day = db_sess.query(Users).get(message.chat.username).day
    await message.answer(f'Хорошо, я тебе напомню {" в ".join(str(alarm).split())}')
    await asyncio.sleep(secs.seconds)
    await state.finish()
    await events[f'#{day+1}_day'](call = message,mode=False)

@dp.message_handler(state='*', commands='❌Отмена')
@dp.message_handler(state='*', commands='cancel')
@dp.message_handler(Text(equals='❌Отмена', ignore_case=True), state='*')
async def cancel_handler(state: FSMContext):
    current_state = await state.get_state()

    logging.info('Cancelling state %r', current_state)
    await state.finish()

async def anketa(call,*args):
    try:
        message = call.message
        db_sess = db_session.create_session()
        user_name = message.chat.username
        user = db_sess.query(Users).get(user_name)
        if not user:
            user=Users(name=message.chat.username,telegram_id=message.chat.id)
            db_sess.add(user)
            db_sess.commit()
            db_sess.close()
            await bot.send_message('1729616674', f'@{message.chat.username} заполнил анкету',reply_markup=generate_inline_keyboard(['Допустить',f'#pass {message.chat.id} {message.chat.username}']))
            await message.answer('Подожди, пока координатор ознакомиться с твоей анкетой')
    except Exception:
        await message.answer('Создайте уникальный nickname для телеграма чтобы воспользоваться ботом.')
        return
        
async def cancel(call,*args):
    await cancel_handler(state=call.state)
    await call.answer('Отменено')

async def first_day_material(call,*args):
    message = call.message
    db_sess = db_session.create_session()
    user = db_sess.query(Users).get(message.chat.username)
    user.day = 1
    db_sess.commit()
    db_sess.close()
    await message.answer(
    fmt.text(fmt.text(fmt.hunderline("День 1")),'\n\nПриступай к изучению материалов первого дня'), parse_mode="HTML",reply_markup=first_day_keyb)

async def first_day_test(call,*args):
    message = call.message
    await message.answer(fmt.text(fmt.text(fmt.hunderline("День 1")),'\n\nТы уже готов сдать тест по 1 дню обучения?'), parse_mode="HTML",reply_markup=first_test_keyb)

async def first_day_quest(call,*args):
    message = call.message
    await message.answer(
    fmt.text(fmt.text(fmt.hunderline("День 1")),'\n\nУ тебя остались вопросы по первому дню?'), parse_mode="HTML",reply_markup=generate_multiinline_keyboard([['да','#quest'],['нет','#2_day']]))

async def quest(call,*args):
    message = call.message
    db_sess = db_session.create_session()
    user_day = db_sess.query(Users).get(message.chat.username).day
    await message.answer('Напиши свой вопрос координатору - @date_invest',reply_markup=generate_inline_keyboard(['дальше',f'#{user_day+1}_day']))

async def second_day(call,mode=True,*args):
    if mode:
        message = call.message
    else:
        message= call
    await message.answer(
    fmt.text(fmt.text(fmt.hunderline("День 1")),'\n\nГотов ли ты приступить к следующему дню обучения?'), parse_mode="HTML",reply_markup=generate_multiinline_keyboard([['да','#2_day_material'],['нет','#wait']]))

async def w_question(call,*args):
    await call.message.answer('Когда тебе удобно продолжить?\nНапиши в формате час день месяц(цифрами) год \nPs только час - обязательно, все остальное будет подставленно от сегодня при незаполнении')
    await Timesleep.answer.set()

async def first_day(call,mode=True,*args):
    if mode:
        message = call.message
    else:
        message= call
    await message.answer(
    fmt.text(fmt.text(fmt.hunderline("День 1")),'\n\nПриступай к изучению материалов первого дня'), parse_mode="HTML",reply_markup=first_day_keyb)

async def passs(call,*args):
    message = call.message
    db_sess = db_session.create_session()
    user = db_sess.query(Users).get(args[1])
    if not user.authorized:
        user.authorized = True
        user.day = 1
        db_sess.commit()
        await bot.send_message(args[0],'Если ты заполнил анкету тогда пора переходить к обучению!',reply_markup=first_day_keyb)
    else:
        await message.answer(f'Пользователь {user.name} уже допущен')
    db_sess.close()

async def second_day_material(call,*args):
    message = call.message
    db_sess = db_session.create_session()
    user = db_sess.query(Users).get(message.chat.username)
    user.day = 2
    db_sess.commit()
    db_sess.close()
    await message.answer(
    fmt.text(fmt.text(fmt.hunderline("День 2")),'\n\nПриступай к изучению материалов второго дня'), parse_mode="HTML",reply_markup=second_day_keyb)

async def second_day_test(call,*args):
    message = call.message
    await message.answer(
    fmt.text(fmt.text(fmt.hunderline("День 2")),'\n\nТы уже готов сдать тест по 2 дню обучения?'), parse_mode="HTML",reply_markup=second_test_keyb)

async def second_day_quest(call,*args):
    message = call.message
    await message.answer(
    fmt.text(fmt.text(fmt.hunderline("День 2")),"\n\nУ тебя остались вопросы по второму дню?"), parse_mode="HTML",reply_markup=generate_multiinline_keyboard([['да','#quest'],['нет','#3_day']]))
    
async def third_day(call,mode=True,*args):
    if mode:
        message = call.message
    else:
        message= call
    await message.answer(
    fmt.text(fmt.text(fmt.hunderline("День 2")),'\n\nГотов ли ты приступить к следующему дню обучения?'), parse_mode="HTML",reply_markup=generate_multiinline_keyboard([['да','#3_day_material'],['нет','#wait']]))

async def third_day_material(call,*args):
    message = call.message
    db_sess = db_session.create_session()
    user = db_sess.query(Users).get(message.chat.username)
    user.day = 3
    db_sess.commit()
    db_sess.close()
    await message.answer(
    fmt.text(fmt.text(fmt.hunderline("День 3")),'\n\nПриступай к изучению материалов третьего дня'), parse_mode="HTML",reply_markup=third_day_keyb)

async def third_day_test(call,*args):
    message = call.message
    await message.answer(
    fmt.text(fmt.text(fmt.hunderline("День 3")),'\n\nТы уже готов сдать тест по 3 дню обучения?'), parse_mode="HTML",reply_markup=third_test_keyb)

async def third_day_quest(call,*args):
    message = call.message
    await message.answer(
    fmt.text(fmt.text(fmt.hunderline("День 3")),'\n\nУ тебя остались вопросы по третьему дню?'), parse_mode="HTML",reply_markup=generate_multiinline_keyboard([['да','#quest'],['нет','#4_day']]))
    
async def fourth_day(call,*args):
    message = call.message
    db_sess = db_session.create_session()
    user = db_sess.query(Users).get(message.chat.username)
    user.day = 4
    db_sess.commit()
    db_sess.close()
    await message.answer('''Поздравляю тебя с прохождением всего обучения,\n
ещё немного и ты сможешь приступить к заработку.\n
Чтобы завершить обучение - напиши координатору @date_invest.\n
Желаю большой удачи и хороших контактов!''')

events = {'#anketa':anketa,
    '#cancel':cancel,
    '#1_day':first_day,
    '#1_day_material': first_day_material,
    '#1_day_test':first_day_test,
    '#1_day_quest':first_day_quest,
    '#quest':quest,
    '#2_day':second_day,
    '#w_question':w_question,
    '#wait':w_question,
    '#pass':passs,
    '#2_day_material':second_day_material,
    '#2_day_test':second_day_test,
    '#2_day_quest':second_day_quest,
    '#3_day':third_day,
    '#3_day_material':third_day_material,
    '#3_day_test':third_day_test,
    '#3_day_quest':third_day_quest,
    '#4_day':fourth_day
}

@dp.callback_query_handler(lambda call: True)
async def ans(call):
    command = call.data.split()
    await events[command[0]](call,*command[1:])

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(set_commands(bot))
    loop.run_until_complete(dp.start_polling())