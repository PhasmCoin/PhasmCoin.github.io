
import os
import json
import requests
from flask import Flask, render_template, request
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext

app = Flask(__name__)

# Функция для получения баланса пользователя
def get_balance(user_id):
    # Вызов API CryptoCloud для получения баланса пользователя
    response = requests.get(f'https://api.cryptocloud.com/balance/{user_id}')
    data = json.loads(response.text)
    return data['balance']

# Функция для продажи криптовалюты
def sell_crypto(user_id, amount):
    # Вызов API CryptoCloud для продажи криптовалюты
    response = requests.post(f'https://api.cryptocloud.com/sell/{user_id}/{amount}')
    data = json.loads(response.text)
    return data['status']

# Функция для сохранения данных пользователя
def save_user_data(user_id, balance):
    # Сохранение данных пользователя в файл
    with open(f'user_data/{user_id}.json', 'w') as f:
        json.dump({'balance': balance}, f)

# Функция для загрузки данных пользователя
def load_user_data(user_id):
    # Загрузка данных пользователя из файла
    try:
        with open(f'user_data/{user_id}.json', 'r') as f:
            data = json.load(f)
            return data['balance']
    except FileNotFoundError:
        # Если файл с данными пользователя не найден, создаем новый файл с нулевым балансом
        save_user_data(user_id, 0)
        return 0

# Функция для вывода меню
def show_menu(update: Update, context: CallbackContext):
    # Отправка сообщения с меню
    update.message.reply_text('Выберите действие:\n1. Показать баланс\n2. Продать Phasm')

# Функция для обработки команды "Показать баланс"
def show_balance(update: Update, context: CallbackContext):
    # Получение баланса пользователя
    user_id = update.message.from_user.id
    balance = get_balance(user_id)
    # Отправка сообщения с балансом
    update.message.reply_text(f'Ваш баланс Phasm: {balance}')

# Функция для обработки команды "Продать Phasm"
def sell_phasm(update: Update, context: CallbackContext):
    # Получение количества Phasm для продажи
    amount = context.args[0]
    # Получение ID пользователя
    user_id = update.message.from_user.id
    # Продажа Phasm
    status = sell_crypto(user_id, amount)
    # Обновление баланса пользователя
    balance = load_user_data(user_id) - float(amount)
    save_user_data(user_id, balance)
    # Отправка сообщения с результатом продажи
    update.message.reply_text(f'Вы продали {amount} Phasm. Ваш новый баланс: {balance}')

# Функция для обработки команды "Старт"
def start(update: Update, context: CallbackContext):
    # Отправка гифки на 3 секунды
    #update.message.reply_animation('start.gif')
    # Задержка в 3 секунды
    #import time
    #time.sleep(3)
    # Отправка меню
    show_menu(update, context)

# Создание экземпляра Updater и регистрация обработчиков команд
updater = Updater(token='6477130900:AAFUZAmTtsJBjWkkuF7RSl2_4NUDjl6Dreg', use_context=True)
dispatcher = updater.dispatcher
dispatcher.add_handler(CommandHandler('start', start))
dispatcher.add_handler(CommandHandler('balance', show_balance))
dispatcher.add_handler(CommandHandler('sell', sell_phasm))

# Запуск веб-сервера Flask для обработки запросов от Telegram API
@app.route('/webhook', methods=['POST'])
def webhook():
