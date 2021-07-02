import telebot
import requests
import json
import re
from base_controller import *
import pandas as pd
import matplotlib as plt
from datetime import datetime, timedelta
from PIL import Image
import io


fx_token = 'MWdKxqvjFC19ecEWBkYY'
tele_token = '757726714:AAHmiML_JheD3wnGwtMP_qFHvKXnqQ4bCUc'
bot = telebot.TeleBot(tele_token)


def send_get(endpoint, params):
    url = f"https://fxmarketapi.com/{endpoint}"
    params = {"api_key": fx_token, **params}
    try:
        req = requests.get(url, params=params)
    except requests.HTTPError:
        print('HTTPError')
    return req



@bot.message_handler(commands=['list'])
def get_list(message):
    print('asds')
    req_currencies_list = send_get('apicurrencies', {})
    cur_dict = req_currencies_list.json().get('currencies')
    f = {i:get_currency(i) for i in cur_dict}
    text = json.dumps(f, indent=4, sort_keys=True)
    pure_text = re.sub('[{}]', '', text.__str__())
    bot.send_message(message.chat.id, pure_text)


@bot.message_handler(regexp="/convert")
def exchange(message):
    s = message.text
    frm, to = re.findall(r'[A-Z]{3}', s)
    amount = re.findall(r'[0-9]+', s)[0]
    price = get_currency(frm+to)
    print(f'price ={price}')
    bot.send_message(message.chat.id, text=f'{amount} {frm} to {to} is {price*float(amount)}')


@bot.message_handler(regexp="/history")
def hist_graph(message):
    print('work')
    s = message.text
    d = re.findall(r'[A-Z]{3}', s)
    f = re.findall(r'[0-9]+', s)
    w = re.findall(r'days|months|years|weeks', s)
    cur_date = {'days': 1, 'weeks': 7, 'months': 30.5, 'years': 365}
    per = int(f[0]) * cur_date.get(w[0])
    currency = d[0] + d[1]
    print(per, currency)
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=per)
    try:
        df = pd.read_json(f"https://fxmarketapi.com/apipandas?api_key={fx_token}&currency={currency}&start_date={start_date}&end_date={end_date}")
        plot = df.plot()
        fig = plot.get_figure()
        fig.suptitle(currency)
        buf = io.BytesIO()
        fig.savefig(buf, format='png')
        buf = io.BytesIO()
        buf.seek(0)
        im = Image.open(buf)
        im.show()
        buf.close()
        bot.send_photo(message.chat.id, im)
    except TypeError:
        bot.send_message(message.chat.id, 'Have no data to plot graph')




if __name__ == '__main__':
    bot.polling()


