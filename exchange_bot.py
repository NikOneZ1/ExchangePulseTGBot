import config
import database
import logging
import time
import pandas
import datetime
import requests
import json
from aiogram import Bot, Dispatcher, executor, types

API_TG_TOKEN = config.API_TG_TOKEN
API_EXCHANGE_KEY = config.API_EXCHANGE_KEY
API_FXM_KEY = config.API_FXM_KEY

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TG_TOKEN)
dp = Dispatcher(bot)
db = database.DB(r'.\sqlite.db')


@dp.message_handler(commands=['list'])
async def get_currency(message: types.Message):
    try:
        last_rates = db.get_latest_rates()[0]
        last_timestamp = last_rates[2]
        if float(time.time()) - float(last_timestamp) > 600:
            exchange_info = requests.get('http://api.exchangeratesapi.io/latest?access_key=' + API_EXCHANGE_KEY)
            rates = json.loads(exchange_info.text)['rates'].items()
            output = '\n'.join(['{}: {}'.format(i[0], i[1]) for i in rates])
            data = [output, time.time()]
            db.add_rates(data)
            await message.answer(output)
        else:
            await message.answer(last_rates[1])
    except:
        exchange_info = requests.get('http://api.exchangeratesapi.io/latest?access_key=' + API_EXCHANGE_KEY)
        rates = json.loads(exchange_info.text)['rates'].items()
        output = '\n'.join(['{}: {}'.format(i[0], i[1]) for i in rates])
        data = [output, time.time()]
        db.add_rates(data)
        await message.answer(output)


@dp.message_handler(commands=['exchange'])
async def exchange_usd_to_cad(message: types.Message):
    mess_text = message.text.split(" ")
    params = {'from': mess_text[2], 'to': mess_text[4], 'amount': mess_text[1], 'api_key': API_FXM_KEY}
    result = requests.get('https://fxmarketapi.com/apiconvert?', params)
    output = json.loads(result.text)['total']
    await message.answer("${}".format(round(output, 2)))


@dp.message_handler(commands=['history'])
async def history(message: types.Message):
    mess_text = message.text.split(' ')
    end_date = datetime.date.today()
    start_date = datetime.date.today() - datetime.timedelta(days=int(mess_text[3]))
    params = {'currency': mess_text[1][0:3]+mess_text[1][4:7], 'start_date': start_date.strftime("%Y-%m-%d"),
              'end_date': end_date.strftime("%Y-%m-%d"), 'interval': 'daily', 'api_key': API_FXM_KEY}
    result = requests.get('https://fxmarketapi.com/apipandas?', params)
    output = pandas.read_json(result.text)
    output.plot(kind='line').get_figure().savefig('history.png')
    await bot.send_photo(message.from_user.id, open(r".\history.png", 'rb'))

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)


