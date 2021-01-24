import smtplib
import os
from dotenv import load_dotenv

import mimetypes
from email import encoders
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.audio import MIMEAudio
from email.mime.multipart import MIMEMultipart


class mail:

    def __init__(self, user='VIST', mailboxes=None, report_file=None):

        self.mailboxes = mailboxes
        self.report_file = report_file

        # Файл окружения, в котором хранятся логины и пароли
        dotenv_path = '.env'

        # Логин и пароль - либо из файла окружения, либо вводим вручную
        if os.path.exists(dotenv_path):
            load_dotenv(dotenv_path)
            self.mail_login = os.getenv("JIRA_LOGIN_{}".format(user))
            self.mail_pass = os.getenv("JIRA_PASS_{}".format(user))
        else:
            self.mail_login = input('Введи email-адрес: ')
            self.mail_pass = input('Введи пароль к ящику {}: '.format(self.mail_login))

    def send_email(self,msg_txt=None,html_text=None):

        if not self.mailboxes:
            return 0

        host = "smtp.office365.com"
        addr_to = self.mailboxes
        if not msg_txt:
            msg_text = """
Это письмо отправлено автоматически при запуске скрипта выгрузки отчета, на него не нужно отвечать.
"""
        else:
            msg_text = msg_txt

        msg = MIMEMultipart("alternative")
        msg['From'] = self.mail_login
        msg['To'] = (',').join(addr_to)
        msg['Subject'] = "Автоматический отчет"

        file = self.report_file
        if file:
            self.process_attachement(msg, file)

        msg.attach(MIMEText(msg_text, 'plain'))  # Добавляем в сообщение текст

        if html_text:
            msg.attach(MIMEText(html_text, 'html'))  # Добавляем в сообщение текст

        server = smtplib.SMTP(host, 587)  # Создаем объект SMTP
        server.starttls()  # Начинаем шифрованный обмен по TLS
        server.login(self.mail_login, self.mail_pass)  # Получаем доступ
        server.send_message(msg)  # Отправляем сообщение
        server.quit()  # Выходим


    def process_attachement(self, msg, file):  # Функция по обработке списка, добавляемых к сообщению файлов
        if os.path.isfile(file):  # Если файл существует
            self.attach_file(msg, file)  # Добавляем файл к сообщению


    def attach_file(self, msg, filepath):  # Функция по добавлению конкретного файла к сообщению
        filename = os.path.basename(filepath)  # Получаем только имя файла
        ctype, encoding = mimetypes.guess_type(filepath)  # Определяем тип файла на основе его расширения
        if ctype is None or encoding is not None:  # Если тип файла не определяется
            ctype = 'application/octet-stream'  # Будем использовать общий тип
        maintype, subtype = ctype.split('/', 1)  # Получаем тип и подтип
        if maintype == 'text':  # Если текстовый файл
            with open(filepath) as fp:  # Открываем файл для чтения
                file = MIMEText(fp.read(), _subtype=subtype)  # Используем тип MIMEText
                fp.close()  # После использования файл обязательно нужно закрыть
        elif maintype == 'image':  # Если изображение
            with open(filepath, 'rb') as fp:
                file = MIMEImage(fp.read(), _subtype=subtype)
                fp.close()
        elif maintype == 'audio':  # Если аудио
            with open(filepath, 'rb') as fp:
                file = MIMEAudio(fp.read(), _subtype=subtype)
                fp.close()
        else:  # Неизвестный тип файла
            with open(filepath, 'rb') as fp:
                file = MIMEBase(maintype, subtype)  # Используем общий MIME-тип
                file.set_payload(fp.read())  # Добавляем содержимое общего типа (полезную нагрузку)
                fp.close()
                encoders.encode_base64(file)  # Содержимое должно кодироваться как Base64
        file.add_header('Content-Disposition', 'attachment', filename=filename)  # Добавляем заголовки
        msg.attach(file)  # Присоединяем файл к сообщению