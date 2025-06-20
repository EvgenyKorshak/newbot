import sqlite3
from logging import NullHandler

import telebot
from telebot import types

bot = telebot.TeleBot('7622919181:AAGSw-4PJpa2nEm1zvjvIj0-f_tL2GkTvJA')
@bot.message_handler(commands=['getid'])
def getid(message):
    bot.send_message(message.chat.id, message.from_user.id)

@bot.message_handler(commands=['show'])
def show(message):
    name = message.text.strip()
    conn = sqlite3.connect('bot.sql')
    cur = conn.cursor()
    cur.execute("Select * from users")
    res ="*Список пользователей*\n"
    for el in cur.fetchall():
        res += f'{el[0]} {el[1]} {el[2]}\n'

    bot.send_message(message.chat.id, res, parse_mode='MarkdownV2')
    cur.close()
    conn.close()

@bot.message_handler(commands=['balance'])
def balance(message):
    conn = sqlite3.connect('bot.sql')
    cur = conn.cursor()
    cur.execute("SELECT balance FROM balance WHERE id_user = '%s'" % (message.from_user.id))
    result = cur.fetchone()
    if result is not None:
        bot.send_message(message.chat.id, f'Ваш баланс: {result[0]}')
    else:
        bot.send_message(message.chat.id, 'Баланс не найден')

    cur.close()
    conn.close()





@bot.message_handler(commands=['menu'])
def menu(message):

    markup = types.InlineKeyboardMarkup()
    btn1=types.InlineKeyboardButton("Баланс", callback_data="balance")
    btn2 = types.InlineKeyboardButton("Список пользователей", callback_data="show_users")
    btn3 = types.InlineKeyboardButton("Магазин", callback_data="magazine")
    btn4 = types.InlineKeyboardButton("Покупки/Списания", callback_data="expenses")
    btn6 = types.InlineKeyboardButton("Начисления", callback_data="enrollment")
    btn7 = types.InlineKeyboardButton("Прайсы", callback_data="price")
    btn8 = types.InlineKeyboardButton("Удержания", callback_data="fines")
    markup.add(btn1)
    markup.add(btn7)
    markup.add(btn8)
    markup.add(btn3)
    markup.add(btn6)
    markup.add(btn4)

    conn = sqlite3.connect('bot.sql')
    cur = conn.cursor()
    cur.execute("Select typeUser from users where id = '%s'" % (message.from_user.id))
    result = cur.fetchone()  # Получаем одну запись (кортеж) или None

    if result is not None:
        typeUser = int(result[0])  # Преобразуем строку в число

        if typeUser > 0:  # Теперь можно сравнивать с числом
            markup.add(btn2)
    else:
        bot.send_message(message.chat.id, "Пользователь не найден в базе")


    if result is not None:
        bot.send_message(message.chat.id, "Меню пользователя", reply_markup=markup)
    cur.close()
    conn.close()






@bot.callback_query_handler(func=lambda call: True)
def callback_message(call):
    if call.data == "register":
        global firstname
        global lastname
        bot.send_message(call.message.chat.id, 'Введите имя')
        bot.register_next_step_handler(call.message, add_firstname)
    elif call.data == "balance":
        conn = sqlite3.connect('bot.sql')
        cur = conn.cursor()
        cur.execute("Select balance from balance WHERE id_user=?", (call.from_user.id,))
        bot.send_message(call.message.chat.id, f'Ваш баланс: {cur.fetchone()[0]}')
        cur.close()
        conn.close()
    elif call.data == "show_users":
        show(call.message)
    elif call.data == "magazine":
        conn = sqlite3.connect('bot.sql')
        cur = conn.cursor()
        cur.execute("Select * from magazine")
        magazine = "<b>Магазин</b>\n\n"
        for t in cur.fetchall():
            magazine += f'{t[0]}. {t[1]}: {t[2]}\n\n'

        bot.send_message(call.message.chat.id, magazine, parse_mode='HTML')
        cur.close()
        conn.close()
    elif call.data == "price":
        conn = sqlite3.connect('bot.sql')
        cur = conn.cursor()
        cur.execute("Select * from income")
        price = "<b>Заработок</b>\n\n"
        for t in cur.fetchall():
            price += f'{t[0]}. {t[1]}: {t[2]}\n\n'

        bot.send_message(call.message.chat.id, price, parse_mode='HTML')
        cur.close()
        conn.close()
    elif call.data == "enrollment":
        conn = sqlite3.connect('bot.sql')
        cur = conn.cursor()
        cur.execute("Select typeUser from users where id = '%s'" % (call.from_user.id))
        result = cur.fetchone()  # Получаем одну запись (кортеж) или None

        if result is not None:
            typeUser = int(result[0])  # Преобразуем строку в число

        if typeUser > 0:
            cur.execute(
                "SELECT enrollment.id, u1.firstname,u1.lastname, name, cost, addDate, u2.lastname, u2.firstname, comment FROM enrollment JOIN users u1 ON u1.id = enrollment.idUser JOIN users u2 ON u2.id = enrollment.idAdd order by addDate desc")
        else:
            cur.execute("SELECT enrollment.id, u1.firstname,u1.lastname, name, cost, addDate, u2.lastname, u2.firstname, comment FROM enrollment  JOIN users u1 ON u1.id = enrollment.idUser  JOIN users u2 ON u2.id = enrollment.idAdd  where enrollment.idUser = '%s' order by addDate desc" % (call.from_user.id))
        price = "<i><b>Начислено</b></i>\n\n"
        data=cur.fetchall()
        for t in data:
            price += f'<b>{t[0]}</b>.'
            if typeUser >0:
                price +=f'{t[1]} {t[2]}'
            price += f'\n<b>Вид:</b> {t[3]} \n<b>Сумма:</b> {t[4]} \n<b>Дата начисления:</b> {t[5]} \n<b>Кто начислил:</b> {t[6]} {t[7]} \n<b>Комментарий:</b> {t[8]}\n'
            for i in range(0, 30):
                price +="="
            price +='\n'

        bot.send_message(call.message.chat.id, price, parse_mode='HTML')
        cur.close()
        conn.close()
    elif call.data == "fines":
        conn = sqlite3.connect('bot.sql')
        cur = conn.cursor()
        cur.execute("Select * from fines")
        fines = "<b>Удержания</b>\n\n"
        for t in cur.fetchall():
            fines += f'{t[0]}. {t[1]}: {t[2]}\n\n'

        bot.send_message(call.message.chat.id, fines, parse_mode='HTML')
        cur.close()
        conn.close()
    elif call.data == "expenses":
        conn = sqlite3.connect('bot.sql')
        cur = conn.cursor()
        cur.execute("SELECT expenses.id, u1.firstname,u1.lastname, kind, cost, buyDate, useDate, comment FROM expenses  JOIN users u1 ON u1.id = expenses.idUser  where expenses.idUser = '%s' order by buyDate desc" % (call.from_user.id))
        buy = "<b>Покупки/списания</b>\n\n"
        for t in cur.fetchall():
            buy += f'<b>{t[0]}</b>\n<b>Название: </b>{t[3]}\n<b>Сумма: </b>{t[4]}\n<b>Дата покупки: </b>{t[5]}\n<b>Дата использоватения: </b>{t[6]}\n<b>Комментарий: </b>{t[7]}\n'

        bot.send_message(call.message.chat.id, buy, parse_mode='HTML')
        cur.close()
        conn.close()

def add_firstname(message):
    global firstname
    global lastname
    firstname=message.text
    bot.send_message(message.chat.id, 'Введите фамилию')
    bot.register_next_step_handler(message, add_lastname)
def add_lastname(message):
    global firstname
    global lastname
    lastname=message.text
    conn = sqlite3.connect('bot.sql')
    cur = conn.cursor()
    cur.execute("INSERT INTO users(id, firstname, lastname, typeUser) VALUES (?, ?, ?, ?)",
                    (message.from_user.id, firstname, lastname, '0'))
    conn.commit()
    cur.execute("INSERT INTO balance(id_user, balance) VALUES (?, ?)",
                    (message.from_user.id, '0.0'))
    conn.commit()

    bot.send_message(message.chat.id, "Регистрация успешно завершена!")

    cur.close()
    conn.close()

@bot.message_handler(commands=['start'])
def start(message):
    conn = sqlite3.connect('bot.sql')
    cur = conn.cursor()
    cur.execute('CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY, firstname varchar(255), lastname varchar(255), typeUser varchar(5))')
    conn.commit()
    cur.execute("Select * from users where id = '%s'" % (message.from_user.id))
    checkUser = cur.fetchone()
    if checkUser is None:
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("Зарегистрироваться", callback_data="register"))
        bot.reply_to(message,"Привет. Необходимо зарегистрироваться", reply_markup=markup)


    else:
        bot.send_message(message.chat.id, f"Привет, {checkUser[2]} {checkUser[1]}")



    cur.close()
    conn.close()

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn = types.KeyboardButton("/menu")
    markup.add(btn)
    bot.send_message(message.chat.id, "/menu", reply_markup=markup)



bot.polling(none_stop=True)