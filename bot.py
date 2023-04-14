import telegram.ext
import json
import requests
from telegram.ext import CommandHandler, MessageHandler, Filters, Updater


def read_crypto_data():
    try:
        with open('crypto_data.json', 'r') as c:
            data = json.load(c)
    except FileNotFoundError:
        data = {}
    return data


def read_coingecko_data():
    try:
        with open('coingecko_data.json', 'r') as c:
            data = json.load(c)
    except FileNotFoundError:
        data = {}
    return data


def write_coingecko_data(data):
    with open('coingecko_data.json', 'w') as d:
        json.dump(data, d)


def write_crypto_data(data):
    with open('crypto_data.json', 'w') as d:
        json.dump(data, d)


def coingecko_data(symbol):
    try:
        data = read_coingecko_data()
        coindata = []
        for coin in data:
            if symbol.lower() == coin["symbol"].lower() or symbol.lower() == coin["name"].lower() or symbol.lower() == coin["id"].lower():
                url = f"https://api.coingecko.com/api/v3/coins/{coin['id']}"
                r = requests.get(url)
                coindata.append(r.json())
        return coindata
    except Exception as e:
        print(e)
    return None


def handle_user_message(update, context):
    message = update.message
    chat_id = message.chat_id
    user_id = message.from_user.id
    try:
        # Use the bot.get_chat_member() method to check if the user is a member of the group
        chat_member = context.bot.getChatMember(chat_id=config["TEEGRAM_PRIVATE_CHATS_IDS"], user_id=user_id)
        if chat_member.status == "left":
            bot.send_message(chat_id=chat_id, text="Пожалуйста, подпишитесь на группу, чтобы использовать этого бота. http://t.me/CryptoBot?start=SBYbESyyL_-nsyN2Yy")
            return
    except:
        for admin in ADMIN_IDS:
            bot.send_message(chat_id=admin, text=f"Error: can't get chat member status for {user_id} in {chat_id}.")
        return
    text = message.text
    data = read_crypto_data()
    try:
        COINDATA = coingecko_data(text.lower())
        if len(COINDATA) != 0:
            for coinData in COINDATA:
                message = f"<b>{coinData['name']} ({coinData['symbol']})</b>\n"
                if coinData['image']['large'] is not None:
                    message += f"<b>Расположение валюты:</b>  {coinData['market_cap_rank']}\n"
                if coinData['market_data']['current_price']['usd'] is not None:
                    message += f"<b>Цена валюты:</b>  {'{:,.2f}'.format(coinData['market_data']['current_price']['usd'])}$"
                if coinData['market_data']['price_change_percentage_24h'] is not None:
                    if coinData['market_data']['price_change_percentage_24h'] > 0:
                        message += f" (🟩⬆️{'{:,.2f}'.format(coinData['market_data']['price_change_percentage_24h'])}%)\n"
                    else:
                        message += f" (🟥⬇️{'{:,.2f}'.format(coinData['market_data']['price_change_percentage_24h'])}%)\n"
                if coinData['market_data']['market_cap']['usd'] is not None:
                    message += f"<b>Рыночная капитализация:</b>  {'{:,.2f}'.format(coinData['market_data']['market_cap']['usd'])}$"
                if coinData['market_data']['market_cap_change_percentage_24h'] is not None:
                    if coinData['market_data']['market_cap_change_percentage_24h'] > 0:
                        message += f" (🟩⬆️{'{:,.2f}'.format(coinData['market_data']['market_cap_change_percentage_24h'])}%)\n"
                    else:
                        message += f" (🟥⬇️{'{:,.2f}'.format(coinData['market_data']['market_cap_change_percentage_24h'])}%)\n"
                if coinData['market_data']['total_volume']['usd'] is not None:
                    message += f"<b>Общее количество монет в обороте на рынке:</b>  {'{:,.2f}'.format(coinData['market_data']['circulating_supply'])} {coinData['symbol']}\n"
                if coinData['market_data']['total_supply'] is not None:
                    message += f"<b>Общее предложение:</b>  {'{:,.2f}'.format(coinData['market_data']['total_supply'])} {coinData['symbol']}\n"
                if coinData['market_data']['max_supply'] is not None:
                    message += f"<b>Максимальное количество монет:</b>  {'{:,.2f}'.format(coinData['market_data']['max_supply'])} {coinData['symbol']}\n"
                if coinData['market_data']['total_volume']['usd'] is not None:
                    message += f"<b>Обьем за 24 часа:</b>  {'{:,.2f}'.format(coinData['market_data']['total_volume']['usd'])}$\n"
                licit = ""
                for coin in data:
                    if coinData["id"] == coin["id"]:
                        licit = coin["licit"]
                if licit == "yes":
                    message += f"<b>Шариат:</b>  🟢Дозволенный проект🟢\n"
                elif licit == "no":
                    message += f"<b>Шариат:</b>  🔴Недозволенный проект🔴\n"
                elif licit == "maybe":
                    message += f"<b>Шариат:</b>  🟠Проект в котором есть сомнения и лучше воздержаться от него🟠\n"
                else:
                    message += f"<b>Шариат:</b>  ⚫️Проект монеты еще не проверен⚫️\n"

                bot.send_photo(
                    chat_id=chat_id,
                    caption=message,
                    photo=coinData['image']['large'],
                    parse_mode=telegram.ParseMode.HTML
            )
    except Exception as e:
        print(e)


def start(update, context):
    bot.send_message(
        chat_id=update.message.chat_id,
        text="""Добро пожаловать в бот Crypto Halal предоставления шариатской нормы валюты
Этот бот позволяет вам ознакомиться с положениями более чем 1750 валют самых сильных валют, в соответствии с веб-сайтом CoinMarketCap
Вы можете искать шариатское решение о валюте, которую вы желаете приобрести, используя символ валюты"""
    )


def add_coin_data(update, context):
    message = update.message
    chat_id = message.chat_id
    user_id = message.from_user.id
    username = message.from_user.username
    args = context.args
    if user_id in ADMIN_IDS:
        if len(args) == 2:
            coin = {}
            symbol = args[0].lower()
            licit = args[1].lower()
            coin["added_by"] = username
            coin["added_by_id"] = user_id
            coin["id"] = symbol
            data = read_crypto_data()
            for i in range(len(data)):
                if data[i]["id"] == symbol:
                    bot.send_message(chat_id=chat_id, text=f"{symbol.upper()} already exists in the database.")
                    return
            if licit == "yes" or licit == "no" or licit == "maybe":
                coin["licit"] = licit
            else:
                bot.send_message(
                    chat_id=chat_id,
                    text="make sure it's /add_coin_data <CoinGecko ID> <licit (yes, no, maybe)>"
                )
                return
            data.append(coin)
            write_crypto_data(data)
            bot.send_message(chat_id=chat_id, text=f"{symbol.upper()} added to the database.")
        else:
            bot.send_message(
                chat_id=chat_id,
                text="Invalid input format. make sure it's /add_coin_data <CoinGecko ID> <licit (yes, no, maybe)>"
            )


def delete_coin_data(update, context):
    message = update.message
    chat_id = message.chat_id
    user_id = message.from_user.id
    args = context.args
    if user_id in ADMIN_IDS:
        if len(args) == 1:
            symbol = args[0].lower()
            data = read_crypto_data()
            found = False
            for i in range(len(data)):
                if data[i]["id"] == symbol:
                    del data[i]
                    bot.send_message(chat_id=chat_id, text=f"{symbol.upper()} deleted from the database.")
                    found = True
                    break
            if not found:
                bot.send_message(chat_id=chat_id, text=f"{symbol.upper()} not found in the database.")
            else:
                write_crypto_data(data)
        else:
            bot.send_message(
                chat_id=chat_id,
                text="Invalid input format. make sure it's /delete_coin_data <CoinGecko ID>"
            )


def coin_id(update, context):
    message = update.message
    chat_id = message.chat_id
    args = context.args
    if len(args) == 1:
        symbol = args[0].lower()
        url = f"https://api.coingecko.com/api/v3/coins/list"
        # Send the API request and parse the response
        response = requests.get(url)
        data = response.json()
        for i in range(len(data)):
            if data[i]["symbol"] == symbol:
                bot.send_message(
                    chat_id=chat_id,
                    text=f"{data[i]['name'].upper()} ({data[i]['symbol'].upper()})\nCoinGecko ID: {data[i]['id']}"
                )
        write_coingecko_data(data)
    else:
        bot.send_message(
            chat_id=chat_id,
            text="Invalid input format. make sure it's /coin_id <symbol>."
        )


def get_total_coins(update, context):
    message = update.message
    chat_id = message.chat_id
    data = read_crypto_data()
    bot.send_message(chat_id=chat_id, text=f"Total coins: {len(data)}")


with open('config.json', 'r') as f:
    config = json.load(f)
bot = telegram.Bot(token=config["BOT_TOKEN"])
ADMIN_IDS = config["BOT_ADMINS"]  # Replace with the IDs of the admins


def main():
    updater = Updater(token=config["BOT_TOKEN"], use_context=True)
    dispatcher = updater.dispatcher
    start_handler = CommandHandler('start', start)
    add_coin_handler = CommandHandler('add_coin_data', add_coin_data)
    delete_coin_handler = CommandHandler('delete_coin_data', delete_coin_data)
    coin_id_handler = CommandHandler('coin_id', coin_id)
    total_coins_handler = CommandHandler('total_coins', get_total_coins)
    user_handler = MessageHandler(Filters.text, handle_user_message)
    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(add_coin_handler)
    dispatcher.add_handler(delete_coin_handler)
    dispatcher.add_handler(coin_id_handler)
    dispatcher.add_handler(total_coins_handler)
    dispatcher.add_handler(user_handler)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
