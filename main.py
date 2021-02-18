import telebot
import json
from config import token
from telebot import types

bot = telebot.TeleBot(token)

with open('stats.json', 'r') as f:
    data = json.load(f)

if 'balance' not in data:
    data['balance'] = {}
if 'stats' not in data:
    data['stats'] = {}

with open('stats.json', 'w') as f:
    json.dump(data, f, indent=4)
    
print("[INIT] Finished. Bot online")

@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    if call.message:
        with open('queue.json', 'r') as f:
            data = json.load(f)
        if "count" not in data:
            data["count"] = 0
        if int(data["count"]) != 0:
            data["count"] = str(int(data["count"]) - 1)
            keys = list(data.keys())
            mode = int(data.pop(keys[1]))
            with open('stats.json', 'r') as f:                                
                stats = json.load(f)
            if call.data == "coin_y":
                bot.send_message(keys[1], 'Противник положил монетку!')
                stats['balance'][str(keys[1])] = str(int(stats['balance'][str(keys[1])]) + 3)
                if mode == 0:
                    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Противник не положил монетку!")
                    stats['balance'][str(call.message.chat.id)] = str(int(stats['balance'][str(call.message.chat.id)]) - 1) 
                else:
                    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Противник положил монетку!")
                    stats['balance'][str(call.message.chat.id)] = str(int(stats['balance'][str(call.message.chat.id)]) + 2) 
            if call.data == "coin_n":
                bot.send_message(keys[1], 'Противник не положил монетку!')
                if mode == 1:
                    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Противник положил монетку!")
                    stats['balance'][str(call.message.chat.id)] = str(int(stats['balance'][str(call.message.chat.id)]) + 3)
                else:
                    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Противник не положил монетку!")
            with open('stats.json', 'w') as f:
                json.dump(stats, f, indent=4)
        else:
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Ожидание хода")
            data["count"] = str(int(data["count"]) + 1)
            mode = 0
            if call.data == "coin_y":
                with open('stats.json', 'r') as f:
                    stats = json.load(f)
                mode = 1
                stats['balance'][str(call.message.chat.id)] = str(int(stats['balance'][str(call.message.chat.id)]) - 1)
                with open('stats.json', 'w') as f:
                    json.dump(stats, f, indent=4)
            data[str(call.message.chat.id)] = str(mode)
        with open('queue.json', 'w') as f:
            json.dump(data, f, indent=4)

@bot.message_handler(commands=['start', 'info'])
def display_info(message):
    bot.send_message(message.chat.id, "Привет! Этот бот - математическая игра про монетку и игровой автомат! Правила довольно просты: Если вы кинете монетку то ваш противник получит от автрмата 3 монетки и наоборот - если протмвник кинет монетку то вы получите 3 монетки! Монетку можно не кидать и тогда ваш противник не получит ничего!")
    with open('stats.json', 'r') as f:
        data = json.load(f)
    data['balance'][str(message.chat.id)] = 10
    with open('stats.json', 'w') as f:
        json.dump(data, f, indent=4)

@bot.message_handler(commands=['balance'])
def get_balance(message):
    with open('stats.json', 'r') as f:
        data = json.load(f)
    current = data['balance'][str(message.chat.id)]
    bot.send_message(message.chat.id, f'Ваш баланс: {current}')

@bot.message_handler(commands=['coin'])
def coin(message):
    menu = types.InlineKeyboardMarkup()
    menu.add(types.InlineKeyboardButton(text = 'Положить монетку', callback_data ='coin_y'))
    menu.add(types.InlineKeyboardButton(text = 'Не класть монетку', callback_data ='coin_n'))
    bot.send_message(message.chat.id, text ='Игра', reply_markup = menu)

bot.polling()
