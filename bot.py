import telebot
 import pymysql
 import logs
 import requests
 import json 
 import my 
 import threading
 import time
 import os

 from telebot import TeleBot, types

 lock = threading.Lock()

 bot = TeleBot(os.environ.get('TELEGRAM_TOKEN')) #telegram token

 print("Bot run!")

 weather = os.environ.get('WEATHER_TOKEN') #weather token
 weather_url = f"https://api.weatherapi.com/v1/forecast.json?key={weather}&days=1&lang=ru&q="


 db = pymysql.connect(os.environ.get('DB_HOST'), os.environ.get('DB_USER'), os.environ.get('DB_PASSWORD'), os.environ.get('DB_DB'), write_timeout=1) #connect to db
 cursor = db.cursor() #db cursor

 events = ['03', '04', '05', '06', '07', '09', '12', '15', '18', '21'] #hour events

 def mailing(): #mailing weather
     now3 = time.ctime() 
     now3 = now3.split(" ")[:-1][-1]
     minute3 = now3.split(":")[1] 

     if minute3 != '00':
         m = int(minute3)
         ts = (60 - m)*60
         print("Checker run error! restart:"+str(ts/60))
         time.sleep(ts)

     print("Checker run!")
     while True: #run event listener
         now = time.ctime()

         now = now.split(" ")[:-1][-1]
         hour = now.split(":")[0]

         if hour in events:
             cursor.execute(f"SELECT id FROM `users` WHERE time = '{hour}'")
             users = cursor.fetchall()

             for user in range(len(users)):
                 user_id = users[user][0]

                 with lock:
                     cursor.execute(f"SELECT city FROM `users` WHERE id = '{user_id}'")
                     city = cursor.fetchone()[0]

                 my.send_weather(user_id, 0, city, write_logs=True)
                 print("Weather")

         print("Sleep to next hour")
         now2 = time.ctime()
         now2 = now2.split(" ")[:-1][-1]
         minute2 = now.split(":")[1]
         sec2 = now.split(":")[2]

         sleep_time = ((int(minute2)*60)+int(sec2)-3600)*-1

         time.sleep(sleep_time)

 second_thread = threading.Thread(target=mailing) #create sec thread for mailing func
 second_thread.start() #start sec thread
 try:

     @bot.message_handler(commands=['start'])
     def c_poll(message):
         user = message.chat.id

         if message.text == "/start":
             try:

                 cursor.execute(f"INSERT INTO `users`(`id`, `city`, `time`) VALUES ({user},'none','none')")
                 db.commit()
                 logs.log(f"New user: {user}")
                 bot.send_message(user, f"👋 Привет {message.chat.first_name}\n☀️ Напиши свой город для отслеживания\n\n⛱ Например: Москва")
             except:
                 with lock:
                     cursor.execute(f"SELECT city FROM users WHERE id = '{str(user)}'")
                     city = cursor.fetchone()[0]
                 print(city)
                 my.send_weather(user, 0, city)


     @bot.message_handler(content_types=['text'])
     def t_poll(message):
         user = message.chat.id

         if message.text == "gg":
             pass
         else:
             city = message.text
             r = requests.get(weather_url+city)
             r = json.loads(r.text)

             try:
                 name = r['location']['name']
                 with lock:
                     cursor.execute(f"UPDATE `users` SET `city`='{name}' WHERE id = '{user}'")
                     db.commit()
                 keyboard = types.InlineKeyboardMarkup()
                 keyboard.row(types.InlineKeyboardButton("Нет", callback_data="weather:0"), types.InlineKeyboardButton("Да", callback_data="addtime"))

                 bot.send_message(user, f"Теперь вы отслеживаете — {name}\n\n☁️ Хотите включиь рассылку погоды?", reply_markup=keyboard)
             except Exception as e:
                 print(e)
                 bot.send_message(int(user), text="⛔️ Город не найден!\n Попробуйте еще раз")






     @bot.callback_query_handler(func=lambda call: True)
     def cb_pool(call):
         keyboard = types.InlineKeyboardMarkup()
         user = call.message.chat.id
         if "weather" in call.data:
             with lock:
                 cursor.execute(f"SELECT city FROM `users` WHERE id = '{user}'")
                 city = cursor.fetchone()[0]


             day = call.data.split(":")[1]
             my.send_weather(user, int(day), city, call.message.message_id)

         elif call.data == "change":
             bot.edit_message_text("☀️ Напиши свой город для отслеживания\n\n⛱ Например: Москва", user, message_id=call.message.message_id)
             #bot.send_message(user,"☀️ Напиши свой город для отслеживания\n\n⛱ Например: Москва")

         elif call.data == "addtime":
             keyboard.row(types.InlineKeyboardButton("06:00", callback_data="time:03"), types.InlineKeyboardButton("07:00", callback_data="time:04"))
             keyboard.row(types.InlineKeyboardButton("08:00", callback_data="time:05"), types.InlineKeyboardButton("09:00", callback_data="time:06"))
             keyboard.row(types.InlineKeyboardButton("10:00", callback_data="time:07"), types.InlineKeyboardButton("12:00", callback_data="time:09"))
             keyboard.row(types.InlineKeyboardButton("15:00", callback_data="time:12"), types.InlineKeyboardButton("18:00", callback_data="time:15"))
             keyboard.row(types.InlineKeyboardButton("21:00", callback_data="time:18"), types.InlineKeyboardButton("00:00", callback_data="time:21"))
             bot.edit_message_text("⏰ Выберите удобное для вас время(МСК)", user, message_id=call.message.message_id, reply_markup=keyboard)

         elif "time" in call.data:
             t = call.data.split(":")[1]
             with lock:
                 cursor.execute(f"UPDATE `users` SET `time`='{t}' WHERE id = '{user}'")
                 db.commit()

             t = t+":00"

             keyboard.row(types.InlineKeyboardButton("←   Назад", callback_data="settings"))

             if t == "none":
                 bot.edit_message_text("⏰ Успешно\n\n✉️ Вы отключили рассылку", user, message_id=call.message.message_id, reply_markup=keyboard)
             else:
                 bot.edit_message_text(f"⏰ Успешно\n\n✉️ Вы добавили рассылку на {t}", user, message_id=call.message.message_id, reply_markup=keyboard)






         elif "settings":
             with lock:
                 cursor.execute(f"SELECT * FROM `users` WHERE id = '{user}'")
                 data = cursor.fetchall()[0]

             city = data[1]
             t2 = data[2]
             keyboard.row(types.InlineKeyboardButton("📍 Поменять город", callback_data="change"))
             if t2 != "none":
                 keyboard.row(types.InlineKeyboardButton("✉️ Поменять время рассылки", callback_data="addtime"))
                 keyboard.row(types.InlineKeyboardButton("🗑 Отключить рассылку", callback_data="time:none"))
                 t2 = t2+":00"
             else:
                 keyboard.row(types.InlineKeyboardButton("✉️ Добавить рассылку", callback_data="addtime"))
                 t2 =  "не подключена"

             keyboard.row(types.InlineKeyboardButton("←   Назад", callback_data="weather:0"))

             bot.edit_message_text(f"⚙️ Настройки\n\n⛱ Город: {city}\n📦 Рассылка: {t2}", user, message_id=call.message.message_id, reply_markup=keyboard)
 except Exception as e:
     print(e)


 bot.polling(True) 
