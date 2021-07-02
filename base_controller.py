import re
import requests
from moduls import Cache
from datetime import datetime
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import create_engine

fx_token = 'MWdKxqvjFC19ecEWBkYY'

engine = create_engine('sqlite:///bot.db')
Session = sessionmaker()
Session.configure(bind=engine)
session = Session()


def send_get(endpoint, params):
    global req
    url = f"https://fxmarketapi.com/{endpoint}"
    params = {"api_key": fx_token, **params}
    try:
        req = requests.get(url, params=params)
    except requests.HTTPError:
        print('HTTPError')
    return req


def create_add(currency, price, timestamp):
    print(currency, price, timestamp)
    session.add(Cache(currency, price, datetime.fromtimestamp(timestamp)))
    session.commit()


def create_all_add():
    pass


def update_currency(currency, price, timestamp):
    currency = session.query(Cache).filter_by(currency=currency).first()
    print(dir(currency))
    currency.price = price
    currency.created = datetime.fromtimestamp(timestamp)
    session.commit()


def get_currency(currency):
    cashed = session.query(Cache)
    arr = [(i.created, i.price) for i in cashed if
           i.currency == currency]  # Тут должен был быть нормальный поиск, через
                                    #фильтр, но поскольку я мало работал с SQLite,
                                    #баг быстро залатать у меня не вышло и я слепил костыть
    if arr:
        created, price = arr[0]
        if (datetime.now() - created).total_seconds() / 60 <= 10:
            return price
        else:
            convert_req = send_get('apilive', {'currency': currency}).json()
            print(currency, convert_req.get('price').get(currency), convert_req.get('timestamp'))
            update_currency(currency, convert_req.get('price').get(currency), convert_req.get('timestamp'))
            return convert_req.get('price').get(currency)

    convert_req = send_get('apilive', {'currency': (currency)}).json()
    create_add(currency, convert_req.get('price').get(currency), convert_req.get('timestamp'))
    return convert_req.get('price').get(currency)
