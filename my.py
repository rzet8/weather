import requests
import time
import json
import telebot
import logs

from telebot import types

bot = telebot.TeleBot(os.environ.get('TELEGRAM_TOKEN'))

weather = "os.environ.get('WEATHER_TOKEN)
weather_url = f"https://api.weatherapi.com/v1/forecast.json?key={weather}&days=7&lang=ru&country=russia&q="

def normal_time(t):
    if "PM" in t:
        t = t.replace(" PM", "")
        t = t.split(":")
        t = str(int(t[0])+12)+":"+t[1]

    else:
        t = t.replace(" AM", "")
    
    return t

def icon_to_smile(icon_id):
    i = int(icon_id)
    if i == 113:
        return "☀️"
    elif i == 116:
        return "⛅️"
    elif i == 119:
        return "☁️"
    elif i == 122:
        return "☁️"
    elif i == 143:
        return "☁️"
    elif i == 176:
        return "🌦"
    elif i == 179:
        return "⛅️❄️"
    elif i == 182:
        return "🌦❄️"
    elif i == 185:
        return "☁️"
    elif i == 116:
        return "⛅️"
    elif i == 200:
        return "🌩☀️"
    elif i == 227:
        return "☁️❄️"
    elif i == 230:
        return "☁️❄️❄️"
    elif i == 248:
        return "☁️"
    elif i == 260:
        return "☁️"
    elif i == 263:
        return "🌧💦"
    elif i == 266:
        return "🌧💦"
    elif i == 281:
        return "☁️"
    elif i == 284:
        return "⛅️"
    elif i == 293:
        return "🌦"#
    elif i == 296:
        return "🌧"
    elif i == 299:
        return "🌦"
    elif i == 302:
        return "🌧"
    elif i == 305:
        return "🌦💦"
    elif i == 308:
        return "🌧💦"
    elif i == 311:
        return "☁️"
    elif i == 314:
        return "☁️"
    elif i == 317:
        return "🌧❄️"
    elif i == 320:
        return "🌧❄️"
    elif i == 323:
        return "⛅️❄️"
    elif i == 326:
        return "☁️❄️"
    elif i == 329:
        return "⛅️❄️"
    elif i == 332:
        return "☁️❄️"
    elif i == 335:
        return "⛅️❄️❄️"
    elif i == 338:
        return "☁️❄️❄️"
    elif i == 350:
        return "☁️🔘"
    elif i == 353:
        return "🌦"
    elif i == 356:
        return "🌦💦"
    elif i == 359:
        return "🌥💦💦"
    elif i == 362:
        return "🌦❄️"
    elif i == 365:
        return "🌦❄️❄️"
    elif i == 368:
        return "⛅️❄️"
    elif i == 371:
        return "⛅️❄️❄️"
    elif i == 374:
        return "⛅️🔘"
    elif i == 377:
        return "⛅️🔘🔘"
    elif i == 386:
        return "🌩☀️"
    elif i == 389:
        return "🌩"
    elif i == 392:
        return "🌩☀️❄️"
    elif i == 395:
        return "🌩❄️"
    


def send_weather(user, day, city, msgid=None, write_logs=False):
    r = requests.get(weather_url+city)
    r = json.loads(r.text)

    keyboard = types.InlineKeyboardMarkup()
    if city != "none":
        try:
            city = r['location']['name']
            max_temp = str(round(r['forecast']['forecastday'][day]['day']['maxtemp_c']))
            min_temp = str(round(r['forecast']['forecastday'][day]['day']['mintemp_c']))
            avg_temp = str(round(r['forecast']['forecastday'][day]['day']['avgtemp_c']))
            humidity = str(round(r['forecast']['forecastday'][day]['day']['avghumidity']))+"%"
            rain = r['forecast']['forecastday'][day]['day']['daily_chance_of_rain']+"%"
            snow = str(r['forecast']['forecastday'][day]['day']['daily_will_it_snow'])
            if snow == "1":
                snow = "Да"
            else:
                snow = "Нет"
            desc = r['forecast']['forecastday'][day]['day']['condition']['text']
            icon = r['forecast']['forecastday'][day]['day']['condition']['icon'].replace("//cdn.weatherapi.com/weather/64x64/day/", "").replace("//cdn.weatherapi.com/weather/64x64/night/", "").replace(".png", "")
            sunrise = r['forecast']['forecastday'][day]['astro']['sunrise']
            sunset = r['forecast']['forecastday'][day]['astro']['sunset']
            city = r['location']['name']
            date = r['forecast']['forecastday'][day]['hour'][0]['time']
            date = date.split(" ")[0]
            date = date.split("-")
            date = date[2]+"."+date[1]

            lat = r['location']['lat']
            lon = r['location']['lon']

            #keyboard.row(types.InlineKeyboardButton("Посмотреть подробный прогноз", url=f"https://yandex.ru/pogoda/?lat={lat}&lon={lon}"))

            if day == 0:
                keyboard.row(types.InlineKeyboardButton("Прогноз на cледующий день    →", callback_data="weather:1"))
                #🠔🠖
                date = "Сегодня — <b>"+date+"</b>"
            elif day == 1:
                keyboard.row(types.InlineKeyboardButton("←          Назад", callback_data="weather:0"), types.InlineKeyboardButton("Вперед          →", callback_data="weather:2"))
                date = "Завтра — <b>"+date+"</b>"
            elif day == 2:
                keyboard.row(types.InlineKeyboardButton("←    Прогноз на предедущий день", callback_data="weather:1"))
                date = "Послезавтра — <b>"+date+"</b>"
            
            keyboard.row(types.InlineKeyboardButton("⚙️ Настройки", callback_data="settings"))

            msg_text = f"🗓 {date}\n\n<b><i>{city}</i></b> {icon_to_smile(icon)} — <b>{avg_temp}°C</b>\n🌫 <i>{min_temp}</i>°C ~ <i>{max_temp}</i>°C\n\n💬 <b>{desc}</b>\n🌧 Шанс дождя: <b><i>{rain}</i></b>\n❄️ Снег: <b>{snow}</b>\n\n💧 Влажность: <b><i>{humidity}</i></b>\n\n🌫 Восход: <b>{normal_time(sunrise)}</b>\n🌫 Заход: <b>{normal_time(sunset)}</b>\n\n<b><a href='https://yandex.ru/pogoda/?lat={lat}&lon={lon}'>Подробный прогноз на Яндекс.Погода</a></b>"

            try:
                bot.edit_message_text(msg_text, int(user), message_id=msgid, reply_markup=keyboard, parse_mode="HTML")
            except:
                bot.send_message(int(user), msg_text, parse_mode="HTML", reply_markup=keyboard)

            if write_logs == True:
                logs.log("Weather sended to "+str(user))
        
        except Exception as e:
            print(e)
    else:
        keyboard.row(types.InlineKeyboardButton("⚙️ Настройки", callback_data="settings"))
        bot.send_message(int(user), text="⛔️ Ошибка", reply_markup=keyboard)
