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

if 'positive' not in data['stats']:
    data['stats']['positive'] = 0

if 'negative' not in data['stats']:
    data['stats']['negative'] = 0

if 'n_coins' not in data['stats']:
    data['stats']['n_coins'] = 0

if 'p_coins' not in data['stats']:
    data['stats']['p_coins'] = 0

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
            if keys[1] == str(call.message.chat.id):
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Ваш предыдущий ход еще не завершен!")
                #return
            with open('stats.json', 'r') as f:                                
                stats = json.load(f)
            if call.data == "coin_y":
                stats["stats"]["positive"] = str(int(stats["stats"]["positive"]) + 1)                    
                stats['stats'][str(call.message.chat.id)]['positive'] = str(int(stats['stats'][str(call.message.chat.id)]['positive']) + 1)
                bot.send_message(keys[1], 'Противник положил монетку!')
                stats['balance'][str(keys[1])] = str(int(stats['balance'][str(keys[1])]) + 3)
                if mode == 0:
                    stats['stats']['n_coins'] = str(int(stats['stats']['n_coins']) + 3)
                    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Противник не положил монетку!")
                    stats['balance'][str(call.message.chat.id)] = str(int(stats['balance'][str(call.message.chat.id)]) - 1) 
                else:
                    stats['stats']['p_coins'] = str(int(stats['stats']['p_coins']) + 4)
                    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Противник положил монетку!")
                    stats['balance'][str(call.message.chat.id)] = str(int(stats['balance'][str(call.message.chat.id)]) + 2) 
            if call.data == "coin_n":
                stats["stats"]["negative"] = str(int(stats["stats"]["negative"]) + 1)
                stats['stats'][str(call.message.chat.id)]['negative'] = str(int(stats['stats'][str(call.message.chat.id)]['negative']) + 1)
                bot.send_message(keys[1], 'Противник не положил монетку!')
                if mode == 1:
                    stats['stats']['n_coins'] = str(int(stats['stats']['n_coins']) + 3)
                    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Противник положил монетку!")
                    stats['balance'][str(call.message.chat.id)] = str(int(stats['balance'][str(call.message.chat.id)]) + 3)
                else:
                    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Противник не положил монетку!")
            
            bot.send_message(call.message.chat.id, f'Ваш баланс: {stats["balance"][str(call.message.chat.id)]}')
            bot.send_message(keys[1], f'Ваш баланс: {stats["balance"][str(keys[1])]}')
            
            with open('stats.json', 'w') as f:
                json.dump(stats, f, indent=4)
        
        else:
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Ожидание хода")
            data["count"] = str(int(data["count"]) + 1)
            mode = 0
            if call.data == "coin_y":
                with open('stats.json', 'r') as f:
                    stats = json.load(f)
                stats["stats"]["positive"] = str(int(stats["stats"]["positive"]) + 1)
                stats['stats'][str(call.message.chat.id)]['positive'] = str(int(stats['stats'][str(call.message.chat.id)]['positive']) + 1)
                
                mode = 1
                stats['balance'][str(call.message.chat.id)] = str(int(stats['balance'][str(call.message.chat.id)]) - 1)
                with open('stats.json', 'w') as f:
                    json.dump(stats, f, indent=4)
            data[str(call.message.chat.id)] = str(mode)
            if call.data == "coin_n":
                with open('stats.json', 'r') as f:
                    stats = json.load(f)
                stats["stats"]["negative"] = str(int(stats["stats"]["negative"]) + 1)
                stats['stats'][str(call.message.chat.id)]['negative'] = str(int(stats['stats'][str(call.message.chat.id)]['negative']) + 1)
                
                with open('stats.json', 'w') as f:
                    json.dump(stats, f, indent=4)

        with open('queue.json', 'w') as f:
            json.dump(data, f, indent=4)

@bot.message_handler(commands=['start', 'info'])
def display_info(message):
    bot.send_message(message.chat.id, f"Привет! Этот бот - математическая игра про монетку и игровой автомат! Правила довольно просты: Если вы кинете монетку то ваш противник получит от автомата 3 монетки и наоборот - если противник кинет монетку то вы получите 3 монетки! Монетку можно не кидать и тогда ваш противник не получит ничего!")
    with open('stats.json', 'r') as f:
        data = json.load(f)
    data['balance'][str(message.chat.id)] = 10
    if str(message.chat.id) not in data['stats']:
        data['stats'][str(message.chat.id)] = {}
        data['stats'][str(message.chat.id)]['positive'] = 0
        data['stats'][str(message.chat.id)]['negative'] = 0
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

@bot.message_handler(commands=['stats'])
def getstats(message):
    with open('stats.json', 'r') as f:
        data = json.load(f)
    if str(message.chat.id) not in data['stats']:
        data['stats'][str(message.chat.id)]['positive'] = 0
        data['stats'][str(message.chat.id)]['negative'] = 0
    general_positive = data['stats']['positive']
    general_negative = data['stats']['negative']
    general_ncoins = data['stats']['n_coins']
    general_pcoins = data['stats']['p_coins']
    
    player_positive = data['stats'][str(message.chat.id)]['positive']
    player_negative = data['stats'][str(message.chat.id)]['negative']
    bot.send_message(message.chat.id, f'Статистика:\nОбщая статистика:\nИгроки ложили монетку {general_positive} раз\nИгроки не ложили монетку {general_negative} раз\nСтатистика по монетам: {general_pcoins}/{general_ncoins}\n(Игроки дали монету/Не дали монету)\nСтатистика игрока @{message.chat.username}:\nВы ложили монетку {player_positive} раз\nВы не ложили монетку {player_negative} раз')

bot.polling()
