import telebot
import SLAreport
import SLAreportold
import lastcomment
import lostanswers
import checklevels
import logging
import os
from dotenv import load_dotenv

# Задаем параметры логгера
logging.basicConfig(filename='telegram.log', filemode='a+', level=logging.INFO, format='%(asctime)s %(message)s')

dotenv_path = '.env'
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
    token = os.getenv("token")
else:
    logging.info(": Отсутствует токен для telegram-бота. Завершение работы.")
    exit(0)

bot = telebot.TeleBot('{}'.format(token))

script_num = 0
filename = None
sla = None
step = 0
mailboxes = None

def initialize():

    global script_num
    global filename
    global sla
    global step
    global mailboxes

    script_num = 0
    filename = None
    sla = None
    step = 0
    mailboxes = None

@bot.message_handler(content_types=['text'])
def get_text_messages(message):

    global script_num
    global filename
    global sla
    global step
    global mailboxes



    if script_num == 0:

        if message.from_user.id not in (282676440,533227024,592400838):
            bot.send_message(message.from_user.id,
                             "Уважаемый человек, тебя нет в разрешённых пользователях использования моими ресурсами. Прошу обратиться к Антону Наговицыну за добавлением разрешения")
            bot.send_message(533227024,
                             "Поступил запрос от нового пользователя с id={}".format(message.from_user.id))
            return 0

        if message.text == "Привет":
            bot.send_message(message.from_user.id, "Привет, чем я могу тебе помочь?")

        elif message.text == "/help":
            bot.send_message(message.from_user.id, """
Возможные команды (в качестве команды используются цифры):
1 - "Отчёт по выполнению СЛА"
2 - "Отчёт по выполнению СЛА (старый)"
3 - "Отчёт по последним комментариям"
4 - "Отчет по упущенным комментариям"
5 - "Отчет по уровням задач на 1 линии"
... другие команды в разработке""")

        elif message.text == "1":
            bot.send_message(message.from_user.id, "Приступаю к формированию. Прошу ввести рабочий jql-запрос")
            logging.info(": Запрошен отчет по СЛА от пользователя {}".format(message.from_user.id))
            message.text = None
            script_num = 1

        elif message.text == "3":
            bot.send_message(message.from_user.id, "Приступаю к формированию")
            logging.info(": Запрошен отчет по последним комментариям от пользователя {}".format(message.from_user.id))
            message.text = None
            logging.info(": Запуск функции получения отчета")
            bot.send_message(message.from_user.id, "Отчет готовится, нужно немного подождать...")
            filename = lastcomment.lastcomment()
            logging.info(": Отчет получен")
            f = open(filename, "rb")
            logging.info(": Отправка файла в чат")
            bot.send_document(message.from_user.id, f)
            bot.send_message(message.from_user.id, "Выше - выгруженный файл отчета")
            f.close()
            initialize()

        elif message.text == "2":
            bot.send_message(message.from_user.id, "Приступаю к формированию. Прошу ввести рабочий jql-запрос")
            logging.info(": Запрошен отчет по СЛА от пользователя {}".format(message.from_user.id))
            message.text = None
            script_num = 3

        elif message.text == "4":
            bot.send_message(message.from_user.id, "Приступаю к формированию")
            logging.info(": Запрошен отчет по упущенным комментариям от пользователя {}".format(message.from_user.id))
            message.text = None
            logging.info(": Запуск функции получения отчета")
            bot.send_message(message.from_user.id, "Отчет готовится, нужно немного подождать...")
            filename = lostanswers.find_lost_answers()
            logging.info(": Отчет получен")
            f = open(filename, "rb")
            logging.info(": Отправка файла в чат")
            bot.send_document(message.from_user.id, f)
            bot.send_message(message.from_user.id, "Выше - выгруженный файл отчета")
            f.close()
            initialize()

        elif message.text == "5":
            bot.send_message(message.from_user.id, "Приступаю к формированию")
            logging.info(": Запрошен отчет по уровням задач от пользователя {}".format(message.from_user.id))
            message.text = None
            logging.info(": Запуск функции получения отчета")
            bot.send_message(message.from_user.id, "Отчет готовится, нужно немного подождать...")
            out = checklevels.check_levels()
            if out == '':
                out = 'Таких задач не найдено, все уровни в норме'
            logging.info(": Отправка списка в чат")
            bot.send_message(message.from_user.id, out)
            initialize()

        else:
            bot.send_message(message.from_user.id, "Я тебя не понимаю. Напиши /help.")

    elif script_num == 1:
        sla = SLAreport.SLA_rep()
        query = message.text
        logging.info(": Введён запрос {}".format(query))
        message.text = None
        bot.send_message(message.from_user.id, "Отчет готовится, нужно немного подождать...")

        try:
            filename = sla.get_report(query)
        except:
            bot.send_message(message.from_user.id, "Введен некорректный jql-запрос. Скрипт останавливается. Попробуйте всё с начала.")
            initialize()
            return 0

        f = open(filename, "rb")
        logging.info(": Отправка файла в чат")
        bot.send_document(message.from_user.id, f)
        bot.send_message(message.from_user.id, "Выше - выгруженный файл отчета")
        f.close()
        initialize()

    elif script_num == 3:
        query = message.text
        logging.info(": Введён запрос {}".format(query))
        bot.send_message(message.from_user.id, "Отчет готовится, нужно немного подождать...")

        try:
            filename = SLAreportold.report(query)
        except:
            bot.send_message(message.from_user.id, "Введен некорректный jql-запрос. Скрипт останавливается. Попробуйте всё с начала.")
            initialize()
            return 0

        message.text = None
        f = open(filename, "rb")
        logging.info(": Отправка файла в чат")
        bot.send_document(message.from_user.id, f)
        bot.send_message(message.from_user.id, "Выше - выгруженный файл отчета")
        f.close()
        initialize()

bot.polling(none_stop=True, interval=0)
