import datetime
from multiprocessing import *
from schedule import every, repeat, run_pending
import schedule
from config import *
import telebot
from keyboard import *
from polygon_scan import polygon_scan
import time

bot = telebot.TeleBot(token=api_key)


def start_contest():
    while True:
        schedule.run_pending()
        time.sleep(5)


class Process_for_contest:
    p0 = Process(target=start_contest, args=())

    def start_process(self):
        self.p0 = Process(target=start_contest)
        self.p0.start()


@bot.message_handler(commands=["start"], func=lambda call: True)
def start(message):
    global users
    user_id = int(message.from_user.id)
    user = users.get_elem(user_id)
    print(user_id)
    if user is False:
        users += user_id
        user = users.get_elem(user_id)

    if message.from_user.username is None:
        bot.delete_message(chat_id=user_id,
                           message_id=message.id)
        r = bot.send_message(chat_id=user_id,
                             text="У Вас нет username. Измените это в настройках. После напишите ёще раз /start")
        user.message_id = r.id

    if user.username is None:
        user.username = message.from_user.username

    if user.message_id == 0:
        r = bot.send_message(chat_id=user_id,
                             text=setting.start_text,
                             reply_markup=setting.start_keyboard)
        if user_id in admins:
            admin = admins.get_elem(user_id)
            admin.message_id = r.id
        user.message_id = r.id
    else:
        try:
            bot.delete_message(chat_id=user_id,
                               message_id=message.id)
            if user.status_registration:
                bot.edit_message_text(chat_id=user_id,
                                      text=setting.start_text,
                                      reply_markup=setting.start_keyboard_y_reg,
                                      message_id=user.message_id)
            else:
                bot.edit_message_text(chat_id=user_id,
                                      text=setting.start_text,
                                      reply_markup=setting.start_keyboard,
                                      message_id=user.message_id)
        except:
            r = bot.send_message(chat_id=user_id,
                                 text=setting.start_text,
                                 reply_markup=setting.start_keyboard)
            if user_id in admins:
                admin = admins.get_elem(user_id)
                admin.message_id = r.id
            user.message_id = r.id
    save_object(data=users, file_name="users.pkl")


@bot.callback_query_handler(func=lambda call: call.data == "registration")
def user_reg(call):
    global setting
    user_id = int(call.from_user.id)
    user = users.get_elem(user_id)
    link = lines.ship_link(count=setting.many_can_link)
    user.link = link
    user.time_start = datetime.datetime.now()
    user.status_registration = False
    bot.edit_message_text(chat_id=user_id,
                          text=f"Ваша ссылка: {link}\n"
                               f" Для регистрации у Вас есть {setting.time_reg} минут",
                          reply_markup=keyboard_for_w,
                          message_id=user.message_id)
    save_object(lines, "lines.pkl")
    save_object(users, "users.pkl")


@bot.callback_query_handler(func=lambda call: call.data == "ready_reg")
def user_reg(call):
    global setting
    user_id = int(call.from_user.id)
    user = users.get_elem(user_id)

    bot.edit_message_text(chat_id=user_id,
                          text=f"Введите полученную ссылку и кошелек через пробел",
                          message_id=user.message_id)
    user.flag = 1
    save_object(users, "users.pkl")


@bot.message_handler(content_types=["text"], func=lambda message: int(message.from_user.id) in users and
                                                                  users.get_elem(int(message.from_user.id)).flag == 1)
def read_link(message):
    user_id = int(message.from_user.id)
    user = users.get_elem(user_id)
    bot.delete_message(chat_id=user_id,
                       message_id=message.id)
    info = message.text.split(" ")
    if len(info) == 2:
        bot.edit_message_text(chat_id=user_id,
                              text="принял ссылочку! подождите немножко идет проверка",
                              message_id=user.message_id)
        if polygon_scan(wallet=info[1].lower(),
                        time=setting.time_reg):
            visit_link = info[0]
            lines.reception_link(main_link=user.link,
                                 visit_link=visit_link,
                                 count=setting.many_can_link)

            bot.edit_message_text(chat_id=user_id,
                                  text="все прошло успешно! спасибо за участие",
                                  reply_markup=setting.start_keyboard_y_reg,
                                  message_id=user.message_id)
            user.status_registration = True
            user.flag = 0
        else:
            lines.del_link(main_link=user.link)
            bot.edit_message_text(chat_id=user_id,
                                  text="Ваш платеж не был найден. По всем вопросам обращайтесь в поддержку",
                                  reply_markup=setting.start_keyboard_y_reg,
                                  message_id=user.message_id)
            user.status_registration = True
            user.flag = 0

    else:
        bot.edit_message_text(chat_id=user_id,
                              text="Необходимо ввести через пробел(ссылка кошелек)",
                              message_id=user.message_id)
    save_object(lines, "lines.pkl")
    save_object(users, "users.pkl")


@bot.message_handler(commands="admin", func=lambda message: int(message.from_user.id) in admins)
def mes_admin(message):
    user_id = int(message.from_user.id)
    admin = admins.get_elem(user_id)
    bot.delete_message(chat_id=user_id,
                       message_id=message.id)
    bot.edit_message_text(chat_id=user_id,
                          message_id=admin.message_id,
                          text="админ панель",
                          reply_markup=admin_start_keyboard)


@bot.callback_query_handler(func=lambda call: int(call.from_user.id) in admins)
def call_admin(call):
    global setting
    user_id = int(call.from_user.id)
    admin = admins.get_elem(user_id)

    if call.data == "time_for_reg":
        bot.edit_message_text(chat_id=user_id,
                              text="введите время для регистрации",
                              reply_markup=back_admin,
                              message_id=admin.message_id)
        admin.flag = 1

    elif call.data == "quantity_user_1_link":
        bot.edit_message_text(chat_id=user_id,
                              text="введите кол-во пользователей под 1 ссылкой",
                              reply_markup=back_admin,
                              message_id=admin.message_id)
        admin.flag = 2

    elif call.data == "set_start_keyboard":
        bot.edit_message_text(chat_id=user_id,
                              text="выберите",
                              reply_markup=keyboard_for_set_start_key,
                              message_id=admin.message_id)

    elif call.data == "set_start_text":
        bot.edit_message_text(chat_id=user_id,
                              text="установите стартовый текст",
                              reply_markup=back_admin,
                              message_id=admin.message_id)
        admin.flag = 3

    elif call.data == "watch_settings":
        bot.edit_message_text(chat_id=user_id,
                              text=f"вот текущие настройки:\n"
                                   f"кол-во людей под 1 ссылкой: {setting.many_can_link}\n"
                                   f"время для регистрации: {setting.time_reg}\n"
                                   f"текущее стартовое сообщение: {setting.start_text}\n",
                              reply_markup=back_admin,
                              message_id=admin.message_id)

    elif call.data == "del_but":
        # setting.start_keyboard.keyboard[0][0].text
        bot.edit_message_text(chat_id=user_id,
                              text="введите название кнопки",
                              reply_markup=back_to_set_key,
                              message_id=admin.message_id)
        admin.flag = 4

    elif call.data == "add_but":
        bot.edit_message_text(chat_id=user_id,
                              text="введите название кнопки и url через пробел",
                              reply_markup=back_to_set_key,
                              message_id=admin.message_id)
        admin.flag = 5
    elif call.data == "back_in_admin":
        bot.edit_message_text(chat_id=user_id,
                              message_id=admin.message_id,
                              text="админ панель",
                              reply_markup=admin_start_keyboard)
        admin.flag = 0

    elif call.data == "watch_excel":
        bot.delete_message(chat_id=user_id,
                           message_id=admin.message_id)
        file = open("table.xlsx", "rb")
        bot.send_document(chat_id=user_id,
                          data=file)
        r = bot.send_message(chat_id=user_id,
                             text="админ панель",
                             reply_markup=admin_start_keyboard
                             )
        file.close()
        admin.id = r.id
    save_object(data=admins, file_name="admins.pkl")


@bot.message_handler(func=lambda message: int(message.from_user.id) in admins)
def mes_work_admin(message):
    global setting
    user_id = int(message.from_user.id)
    admin = admins.get_elem(user_id)
    bot.delete_message(chat_id=user_id,
                       message_id=message.id)
    global_check = True

    match admin.flag:
        case 1:
            if message.text.isdigit():
                setting.time_reg = int(message.text)
            else:
                global_check = False
                bot.edit_message_text(chat_id=user_id,
                                      message_id=admin.message_id,
                                      text="ошибка! введите целое число",
                                      reply_markup=back_admin)
        case 2:
            if message.text.isdigit():
                setting.many_can_link = int(message.text)
            else:
                global_check = False
                bot.edit_message_text(chat_id=user_id,
                                      message_id=admin.message_id,
                                      text="ошибка! введите целое число",
                                      reply_markup=back_admin)
        case 3:
            setting.start_text = message.text
        case 4:
            check = setting.del_butt(text=message.text)
            if check:
                global_check = False
                bot.edit_message_text(chat_id=user_id,
                                      message_id=admin.message_id,
                                      text="ошибка! такой кнопки нет",
                                      reply_markup=back_admin)

        case 5:
            info = message.text.split(' ')
            if len(info) == 2:
                setting.app_start_keyboard(text=info[0], url=info[1])
            else:
                global_check = False
                bot.edit_message_text(chat_id=user_id,
                                      message_id=admin.message_id,
                                      text="ошибка! введите через пробел",
                                      reply_markup=back_admin)
    if global_check:
        bot.edit_message_text(chat_id=user_id,
                              message_id=admin.message_id,
                              text="изменения сохранены",
                              reply_markup=admin_start_keyboard)

    save_object(data=admins, file_name="admins.pkl")
    save_object(data=setting, file_name="setting.pkl")


@repeat(every(5).seconds)
def job():
    cur_time = datetime.datetime.now()
    users_2 = load_object("users.pkl")
    setting_2 = load_object("setting.pkl")
    for i in users_2.data:
        user = users_2.data[i]
        if cur_time - datetime.timedelta(hours=setting_2.time_reg // 60,
                                         minutes=setting_2.time_reg % 60) < user.time_start and \
                user.status_registration is False:
            user.status_registration = True
            user.flag = 0
            bot.edit_message_text(chat_id=i,
                                  text="К сожалению, Вы не успели",
                                  reply_markup=setting.start_keyboard_y_reg,
                                  message_id=user.message_id)
            lines.del_link(main_link=user.link)
            save_object(users_2, "users.pkl")


if __name__ == "__main__":
    print("START")
    contest_proc = Process_for_contest()
    contest_proc.start_process()
    bot.infinity_polling()
