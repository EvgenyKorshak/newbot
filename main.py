import telebot
from telebot import types
import sqlite3
bot = telebot.TeleBot('7622919181:AAGSw-4PJpa2nEm1zvjvIj0-f_tL2GkTvJA')

@bot.message_handler(commands=['start'])
def start(message):
    conn = sqlite3.connect('bot.sql')
    cur = conn.cursor()
    cur.execute('CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY AUTOINCREMENT, username varchar(255))')
    conn.commit()
    cur.close()
    conn.close()
    bot.send_message(message.chat.id, f'Привет, {message.from_user.first_name}')
    bot.send_message(message.chat.id, 'Таблица создана')
@bot.message_handler(commands=['add'])
def add(message):
    name = bot.send_message(message.chat.id, 'Введите имя')

    bot.register_next_step_handler(name, next_add)

def next_add(message):
    name = message.text.strip()
    conn = sqlite3.connect('bot.sql')
    cur = conn.cursor()
    cur.execute("INSERT INTO users(username) VALUES ('%s')" % (name))
    conn.commit()
    cur.close()
    conn.close()


@bot.message_handler(commands=['show'])
def show(message):
    name = message.text.strip()
    conn = sqlite3.connect('bot.sql')
    cur = conn.cursor()
    cur.execute("Select * from users")
    res =""
    for el in cur.fetchall():
        res += f'{el[1]}\n'

    bot.send_message(message.chat.id, res)
    cur.close()
    conn.close()


bot.polling(none_stop=True)