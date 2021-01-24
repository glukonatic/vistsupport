from jiraclass import JIRA
from datetime import timedelta, datetime
import dateutil.parser
import pytz
import os
import re
from dotenv import load_dotenv
from progressbar import ProgressBar
import webbrowser
import smtplib
import mimetypes
from email import encoders
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.audio import MIMEAudio
from email.mime.multipart import MIMEMultipart


class Jira:
    """
    Класс, содержащий функции для обращения к API Jira за данными, а так же для внесения изменений в эти данные
    """

    def __init__(self):
        """
        Инициализация объекта класса
        """
        # Определяем список имен сотрудников ТП в Джире
        self.tp_names_list = ['Anton Nagovitsin', 'Aleksey Polyakov', 'Pavel Khromov', 'Sergey Kondratyev',
                              'Anton Mulenkov', 'Yuriy.Likhanov', 'VIST Support']
        self.visthelp_persons = {
            'Aleksey Polyakov' : 'aleksey.polyakov@zyfra.com',
            'Yuriy.Likhanov' : 'yuriy.likhanov@zyfra.com',
            'Anton Mulenkov' : 'anton.mulenkov@zyfra.com',
            'Pavel Khromov' : 'pavel.khromov@zyfra.com',
            'Anton Nagovitsin' : 'anton.nagovitsin@zyfra.com',
        }

    def get_issues(self, project='VISTHELP', days=100):
        # Поисковая строка для получения пула тикетов Jira
        # jql = 'status != Done AND status != Declined AND project = {}'.format(project)
        jql = 'status not in (Done, Closed, Declined, Resolved) AND project = {}'.format(project)
        # Опции для подключения к серверу Jira
        #  сервер:
        jira_options = {'server': 'https://jira.zyfra.com'}
        dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
        if os.path.exists(dotenv_path):
            load_dotenv(dotenv_path)
            jira_login = os.getenv("JIRA_LOGIN_ANTON")
            jira_pass = os.getenv("JIRA_PASS_ANTON")
        else:
            jira_login = input('Введи логин пользователя Jira: ')
            jira_pass = input('Введи пароль: ')
        # Объявляем переменную - объект JIRA, выполняя обращение к серверу
        self.jira = JIRA(options=jira_options, basic_auth=(jira_login, jira_pass))
        # Количество дней от текущего момента в прошлое, за которое требуется обработать задачи
        self.delta = timedelta(days=days)
        # Время в UTC
        self.utc = pytz.UTC
        # Список тикетов, полученные запросом из Jira

        return self.jira.search_issues(jql, maxResults=1000)

    def file_begins_ends(self, flg, header='Последние комментарии', send_email=False):

        # Список строк для формирования заголовка отчета
        string_before = ["<!DOCTYPE html>", "<html lang=\"ru\">", "<head>",
                         "    <title>Выгрузка из Джиры</title>", "    <meta charset=\"utf-8\">",
                         "    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">",
                         "	   <style>",
                         "h2 { text-align: center; font-family: Verdana, Arial, Helvetica, sans-serif; color: #336; }",
                         "h3 { text-align: center; font-family: Verdana, Arial, Helvetica, sans-serif; color: blue; }",
                         "   p { color: green; }", "	</style>", "</head> ", "<body>",
                         "			<h2>{}</h2>".format(header), '\n',
                         "    <section id=\"docs\" style=\"margin: 5%;\">"]
        # Список строк для формирования окончания отчета
        string_after = ["    </section>", "</body>", "</html> "]

        if flg == 'begin':
            # Имя файла, получаемого в результате работы функции
            self.filename = str('jiraReport' + datetime.now().ctime() + '.html').replace(' ', '_').replace(':', '')
            # Открываем файл
            self.file = open(self.filename, 'w')
            for line in string_before:
                self.file.write(line)
        else:
            # Закрываем файл
            for line in string_after:
                self.file.write(line)
            self.file.close()
            
            # Если установлен флаг отправки на почту
            if send_email:
                # Отправляем файл по почте
                self.send_email(self.filename)
            else:
                # Иначе открываем файл отчета в браузере
                webbrowser.open_new_tab(self.filename)

    def write_label_data(self, i, l):
        self.file.write("<div><a href=\"" + "https://jira.zyfra.com/browse/" + str(
            i) + "\" target=\"new\">" + str(i) + ". Указаны метки: " + (' ,').join(l) + "</a></div>")
        # self.file.write('\n\n')

    def write_data(self, i, c):
        self.file.write("\n			<div>")
        self.file.write("\n				<h3><a href=\"" + "https://jira.zyfra.com/browse/" + str(
            i) + "\" target=\"new\">" + i.fields.summary + "</a></h3>")
        self.file.write("\n				<p>" + dateutil.parser.isoparse(c.created).ctime() + "</p>")
        self.file.write("\n				<p>" + c.author.displayName + "</p>")
        self.file.write("\n				<p>" + c.body + "</p>")
        self.file.write('\n' + '=' * 100 + '\n')

    def non_tp_last_comment(self):
        """
        Функция для нахождения последнего комментария, автором которого не является сотрудник 1й линии.
        """
        # Заполняем "шапку" в файле
        self.file_begins_ends('begin', header='Последний комментарий, где автор не является сотрудником ТП')

        # Получаем список задач
        issues = self.get_issues(project='VISTHELP2')
        # Листаем задачи
        for i in issues:
            # Получаем объект задачи из джиры
            issue = self.jira.issue(str(i))
            # Если есть комментарии в задаче
            if len(issue.fields.comment.comments) != 0:
                # Берем последний комментарий задачи
                lastcomment = issue.fields.comment.comments[-1]
                # Проверяем, имеются ли авторами последних комментариев сотрудники ТП
                if lastcomment.author.displayName not in self.tp_names_list:
                    # Если комментарий не старше определенного при инициализации количества дней delta
                    if dateutil.parser.isoparse(lastcomment.created) > self.utc.localize(
                            datetime.today() - self.delta):
                        # Вызываем функцию записи в файл
                        self.write_data(issue, lastcomment)

        # Заполняем окончание файла, сохраняем
        self.file_begins_ends('end')

    def check_comments(self):
        """
        Функция для получения последнего комментария по всем задачам, удовлетворяющим поисковому запросу
        :return: Функция ничего не возвращает, результатом работы функции является html-файл, который можно открыть в
        браузере.
        """

        # Заполняем "шапку" в файле
        self.file_begins_ends('begin', header="Проверка комментариев")

        # Получаем список задач
        issues = self.get_issues(project='VISTHELP2')

        # Листаем задачи
        for i in issues:
            # Получаем объект задачи из джиры
            issue = self.jira.issue(str(i))
            # Если есть комментарии в задаче
            if len(issue.fields.comment.comments) != 0:
                # Берем последний комментарий задачи
                lastcomment = issue.fields.comment.comments[-1]
                # Если комментарий не старше определенного при инициализации количества дней delta
                if dateutil.parser.isoparse(lastcomment.created) > self.utc.localize(datetime.today() - self.delta):
                    # Вызываем функцию записи в файл
                    self.write_data(issue, lastcomment)

        # Заполняем окончание файла, сохраняем
        self.file_begins_ends('end')

    def find_lost_labels(self, project=None):
        """
        Получение списка заявок, в которых не указаны метки, либо отсутствует метка 'support'
        :param project: название проекта, в котором проверяем. По-умолчанию: 'VISTHELP'
        :return: Функция не возвращает значений. В результате работы функции форминуется html-файл
        со списком задач, где не указаны метки.
        """

        # Если явно задан проект, в котором смотреть метки
        if project:
            #  то список задач получаем из указанного явно проекта
            issues = self.get_issues(project=project)
        # Ииначе
        else:
            #  получаем список задач дефолтным запросом
            issues = self.get_issues()

        pbar = ProgressBar(maxval=len(issues))
        pbar.start()

        # Заполняем "шапку" в файле
        self.file_begins_ends('begin', header="Не указаны метки в заявках:")

        # Листаем заявки, полученные запросом выше
        for i, iss in enumerate(issues):
            pbar.update(i)
            # Получаем объект заявки из Jira
            issue = self.jira.issue(iss)
            # Если среди меток отсутствует support или количество меток меньше, чем 2
            if 'support' not in issue.fields.labels or len(issue.fields.labels) < 2:
                # Вызываем функцию записи в файл
                self.write_label_data(issue, issue.fields.labels)

        pbar.finish()

        # Заполняем окончание файла, сохраняем
        self.file_begins_ends('end')

    def find_lost_answers(self, to_send_or_not_to_send=False):
        """
        Проверка, имеются ли упущенные комментарии на второй линии,
        то есть такие, после которых движение задачи на первой линии не было возобновлено
        :return: Функция создает html-файл со списком упущенных задач второй линии
        """

        # Заполняем "шапку" в файле
        self.file_begins_ends('begin', header='Упущенные комментарии на 2 и 3 линиях')

        # Вызываем функцию, получающую список задач из джиры
        issues = self.get_issues()

        pbar = ProgressBar(maxval=len(issues))
        pbar.start()

        # Начинаем перебирать заявки, полученные в списке фунцией get.issues()
        for i, iss in enumerate(issues):
            # Получаем объект "Заявка" из джиры
            issue = self.jira.issue(str(iss))
            pbar.update(i)
            # print(issue)
            # input()
            # Проверяем список присоединенных задач к заявке
            for issue_link in issue.fields.issuelinks:
                # Проверяем, есть ли аттрибут с именем inwardIssue
                if hasattr(issue_link, 'inwardIssue'):
                    # Если есть, то получаем объект заявки, присоединенной к задаче
                    linked_issue = self.jira.issue(issue_link.inwardIssue.key)
                # Иначе проверяем, есть ли аттрибут с именем outwardIssue
                elif hasattr(issue_link, 'outwardIssue'):
                    # Если есть, то получаем объект заявки, присоединенной к задаче
                    linked_issue = self.jira.issue(issue_link.outwardIssue.key)
                # В противном случае переходим к следующей итерации цикла
                else:
                    continue

                # Проверяем несколько условий.
                # Первое - равно ди название проекта текущей заявки проекту присоединенной задачи?
                # Второе - имеются ли комментарии в присоединенной задаче?
                # Третье - проверяем, есть ли более свежие комментарии присоединённой задачи по отношению к проверяемой?
                # Четвертое - не является ли автором комментария присоединенной задачи сотрудником ТП?
                if issue.fields.project != linked_issue.fields.project \
                        and len(linked_issue.fields.comment.comments) != 0 \
                        and issue.fields.updated < linked_issue.fields.comment.comments[-1].created \
                        and linked_issue.fields.comment.comments[-1].author.displayName not in self.tp_names_list \
                        and dateutil.parser.isoparse(issue.fields.comment.comments[-1].created) > self.utc.localize(
                    datetime.today() - self.delta):
                    # Вызываем функцию записи в файл
                    self.write_data(linked_issue, linked_issue.fields.comment.comments[-1])

        pbar.finish()

        # Заполняем окончание файла, сохраняем
        self.file_begins_ends('end',send_email=to_send_or_not_to_send)


    def check_watchers(self):
        """
        Функция для проверки, установлены ли наблюдателями сотрудники 1й линии в задачах на второй.
        При отсутствии сотрудника в наблюдателях, ошибка исправляется.
        """

        # Вызываем функцию, получающую список задач из джиры
        issues = self.get_issues(project='VISTHELP2')

        # Словарь сотрудников ТП на 1 линии
        # visthelp2_watchers = self.visthelp_persons

        # Идем по списку открытых задач в жире и ищем отсутствующих наблюдателей, исправляем
        for issue in issues:
            # Получаем список наблюдателей к задаче (используется электронная почта наблюдателя)
            wemaillist = [watcher.emailAddress for watcher in self.jira.watchers(issue).watchers]
            # Для каждого наблюдателя из словаря выше
            for wemail in self.visthelp_persons.values():
                # Проверяем, имеется ли он среди наблюдателей в задаче
                if wemail not in wemaillist:
                    # При отсутствии наблюдателя - добавляем его
                    self.jira.add_watcher(issue,wemail)
                    # Выводим в консоль
                    print("{}: В задачу {} добавлен наблюдатель {}".format(datetime.now(),issue,wemail))
                    # Записываем в файл
                    with open('scripts.log', 'a', encoding='utf-8') as g:
                        print(datetime.now(),": В задачу ", issue, " добавлен наблюдатель ", wemail,file=g)
    

    def send_email(self, report_file):
    
        dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
        if os.path.exists(dotenv_path):
            load_dotenv(dotenv_path)
            addr_from = os.getenv("JIRA_LOGIN_VIST")
            password = os.getenv("JIRA_PASS_VIST")
        else:
            addr_from = input('Введи логин учетной записи почты: ')
            password = input('Введи пароль: ')

        host = "smtp.office365.com"
        addr_to   = self.visthelp_persons.values()
        # addr_to = ['anton.nagovitsin@zyfra.com']
        msg_text = """
        На текущий момент времени имеются задачи на 2 и 3 линиях, 
        где был предоставлен комментарий, но никто на него не отреагировал.
        Во вложении находится html-файл, в котором перечислены задачи и ссылки на них.
        Возможно, некоторые комментарии и не заслуживают ответа, 
        но всё же бОльшая часть из них должна быть рассмотрена и предприняты какие-либо действия.
        """

        msg = MIMEMultipart()
        msg['From']    = addr_from
        msg['To']      = (',').join(addr_to)
        msg['Subject'] = "Задачи без ответа"

        file = report_file
        self.process_attachement(msg, file)

        msg.attach(MIMEText(msg_text, 'plain'))                     # Добавляем в сообщение текст

        #======== Этот блок настраивается для каждого почтового провайдера отдельно ===============================================
        server = smtplib.SMTP(host, 587)        # Создаем объект SMTP
        server.starttls()                                      # Начинаем шифрованный обмен по TLS
        # server.set_debuglevel(True)                            # Включаем режим отладки, если не нужен - можно закомментировать
        server.login(addr_from, password)                       # Получаем доступ
        server.send_message(msg)                                # Отправляем сообщение
        server.quit()                                           # Выходим
        #==========================================================================================================================

    def process_attachement(self, msg, file):                        # Функция по обработке списка, добавляемых к сообщению файлов
        if os.path.isfile(file):                               # Если файл существует
            self.attach_file(msg,file)                              # Добавляем файл к сообщению

    def attach_file(self, msg, filepath):                             # Функция по добавлению конкретного файла к сообщению
        filename = os.path.basename(filepath)                   # Получаем только имя файла
        ctype, encoding = mimetypes.guess_type(filepath)        # Определяем тип файла на основе его расширения
        if ctype is None or encoding is not None:               # Если тип файла не определяется
            ctype = 'application/octet-stream'                  # Будем использовать общий тип
        maintype, subtype = ctype.split('/', 1)                 # Получаем тип и подтип
        if maintype == 'text':                                  # Если текстовый файл
            with open(filepath) as fp:                          # Открываем файл для чтения
                file = MIMEText(fp.read(), _subtype=subtype)    # Используем тип MIMEText
                fp.close()                                      # После использования файл обязательно нужно закрыть
        elif maintype == 'image':                               # Если изображение
            with open(filepath, 'rb') as fp:
                file = MIMEImage(fp.read(), _subtype=subtype)
                fp.close()
        elif maintype == 'audio':                               # Если аудио
            with open(filepath, 'rb') as fp:
                file = MIMEAudio(fp.read(), _subtype=subtype)
                fp.close()
        else:                                                   # Неизвестный тип файла
            with open(filepath, 'rb') as fp:
                file = MIMEBase(maintype, subtype)              # Используем общий MIME-тип
                file.set_payload(fp.read())                     # Добавляем содержимое общего типа (полезную нагрузку)
                fp.close()
                encoders.encode_base64(file)                    # Содержимое должно кодироваться как Base64
        file.add_header('Content-Disposition', 'attachment', filename=filename) # Добавляем заголовки
        msg.attach(file)                                        # Присоединяем файл к сообщению

    # def find_comments(self):
    #     """
    #     Функция для поиска комментариев с упоминанием слова или словосочетания по всем задачам, удовлетворяющим поисковому запросу
    #     :return: Функция ничего не возвращает, результатом работы функции является html-файл, который можно открыть в
    #     браузере.
    #     """

    #     # Заполняем "шапку" в файле
    #     self.file_begins_ends('begin', header="Проверка комментариев")

    #     # Получаем список задач
    #     issues = self.get_issues(project='VISTHELP2')

    #     # Листаем задачи
    #     for i in issues:
    #         # Получаем объект задачи из джиры
    #         issue = self.jira.issue(str(i))
    #         # Если есть комментарии в задаче
    #         if len(issue.fields.comment.comments) != 0:
                
    #             for comment in issue.fields.comment.comments:
    #                 tmp = re.find(text, comment)
    #                 if tmp.
    #             if dateutil.parser.isoparse(lastcomment.created) > self.utc.localize(datetime.today() - self.delta):
    #                 # Вызываем функцию записи в файл
    #                 self.write_data(issue, lastcomment)

    #     # Заполняем окончание файла, сохраняем
    #     self.file_begins_ends('end')


    def find_lost_answers2(self, to_send_or_not_to_send=False):
        """
        Проверка, имеются ли упущенные комментарии на второй линии,
        то есть такие, после которых движение задачи на первой линии не было возобновлено
        :return: Функция создает html-файл со списком упущенных задач второй линии
        """

        # Заполняем "шапку" в файле
        self.file_begins_ends('begin', header='Упущенные комментарии на 2 и 3 линиях')

        # Вызываем функцию, получающую список задач из джиры
        issues = self.get_issues(project='VISTHELP2')

        pbar = ProgressBar(maxval=len(issues))
        pbar.start()

        # Начинаем перебирать заявки, полученные в списке фунцией get.issues()
        for i, iss in enumerate(issues):
            # Получаем объект "Заявка" из джиры
            issue = self.jira.issue(str(iss))
            pbar.update(i)
            # Проверяем список присоединенных задач к заявке
            for issue_link in issue.fields.issuelinks:
                # Проверяем, есть ли аттрибут с именем inwardIssue
                if hasattr(issue_link, 'inwardIssue'):
                    # Если есть, то получаем объект заявки, присоединенной к задаче
                    linked_issue = self.jira.issue(issue_link.inwardIssue.key)
                # Иначе проверяем, есть ли аттрибут с именем outwardIssue
                elif hasattr(issue_link, 'outwardIssue'):
                    # Если есть, то получаем объект заявки, присоединенной к задаче
                    linked_issue = self.jira.issue(issue_link.outwardIssue.key)
                # В противном случае переходим к следующей итерации цикла
                else:
                    continue

                # Проверяем несколько условий.
                # Первое - равно ди название проекта текущей заявки проекту присоединенной задачи?
                # Второе - имеются ли комментарии в присоединенной задаче?
                # Третье - проверяем, есть ли более свежие комментарии присоединённой задачи по отношению к проверяемой?
                # Четвертое - не является ли автором комментария присоединенной задачи сотрудник ТП?
                if issue.fields.project != linked_issue.fields.project \
                        and len(linked_issue.fields.comment.comments) != 0 \
                        and issue.fields.updated < linked_issue.fields.comment.comments[-1].created \
                        and linked_issue.fields.comment.comments[-1].author.displayName not in self.tp_names_list \
                        and dateutil.parser.isoparse(issue.fields.created) > self.utc.localize(
                    datetime.today() - self.delta):
                    # Вызываем функцию записи в файл
                    self.write_data(linked_issue, linked_issue.fields.comment.comments[-1])

        pbar.finish()

        # Заполняем окончание файла, сохраняем
        self.file_begins_ends('end',send_email=to_send_or_not_to_send)
