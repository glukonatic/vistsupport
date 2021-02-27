import os
from jira import JIRA
from dotenv import load_dotenv
from datetime import datetime, timedelta
import dateutil.parser
import pytz
import logging
import pandas as pd
from collections import defaultdict


def func():

    # При указании запроса следует иметь в виду следующие факторы:
    #  1. Запрос из проекта VISTHELP
    #  2. Окно выборки делать не более 1 месяца, чтобы не превысить лимит выборки заявок
    #  3. Исполнитель в заявках должен быть указан vistsupport24@zyfra.com
    # Примерный образец jql-запроса должен выглядеть следующим образом (при реальной работе по задачам следует закомментировать!!!):
    jira_query = 'project = VISTHELP AND created >= 2020-10-03 AND created <= 2020-10-04 AND assignee in ("vistsupport24@zyfra.com") ORDER BY created ASC'

    # Отработанные запросы:
    # jira_query = 'project = VISTHELP AND created >= 2020-10-01 AND created <= 2020-10-31 AND assignee in ("vistsupport24@zyfra.com") ORDER BY created ASC'
    # jira_query = 'project = VISTHELP AND created >= 2020-11-01 AND created <= 2020-11-30 AND assignee in ("vistsupport24@zyfra.com") ORDER BY created ASC'
    # jira_query = 'project = VISTHELP AND created >= 2020-12-01 AND created <= 2020-12-31 AND assignee in ("vistsupport24@zyfra.com") ORDER BY created ASC'

    # В ожидании запуска:

    # Пользователь, от имени которого будет осуществляться выборка и логаться время в задачах
    username='ANTON'

    # Опции подключения к Джире
    jira_options = {'server': 'https://jira.zyfra.com'}

    # Файл окружения, в котором хранятся логины и пароли
    dotenv_path = '.env'

    # Логин и пароль - либо из файла окружения, либо вводим вручную
    if os.path.exists(dotenv_path):
        load_dotenv(dotenv_path)
        jira_login = os.getenv("JIRA_LOGIN_{}".format(username))
        jira_pass = os.getenv("JIRA_PASS_{}".format(username))
    else:
        jira_login = input('Введи логин пользователя Jira (учетка {}): '.format(username))
        jira_pass = input('Введи пароль: ')

    # Получение списка задач из Джиры запросом и переменной jira
    jira = JIRA(options=jira_options, basic_auth=(jira_login, jira_pass))
    issues = jira.search_issues(jira_query, maxResults=1000)

    # Возвращаем список задач и переменную jira
    return issues, jira


def logtime(df):

    # Получаем список задач и переменную jira для работы с задачами
    issues, jira = func()

    # Словарь заявок-задач, где требуется логать время:
    issues_to_logtime = defaultdict()
    issues_to_logtime['Nagovitsin'] = jira.issue('VGTS0192-2')
    issues_to_logtime['Polyakov'] = jira.issue('VGTS0192-3')
    issues_to_logtime['Zhuk'] = jira.issue('VGTS0192-4')
    issues_to_logtime['Mulenkov'] = jira.issue('VGTS0192-5')
    issues_to_logtime['Likhanov'] = jira.issue('VGTS0192-6')
    issues_to_logtime['Khromov'] = jira.issue('VGTS0192-7')

    # Стартовое время, от которого начнут отсчитываться смены (в UTC формате (+00))
    start_quarter_utc = datetime(2020, 10, 1, 4, 00, 00)
    # start_quarter_utc = datetime(2021, 2, 12, 4, 00, 00)

    # Дельта - время рабочей смены сотрудника
    delta = timedelta(hours=12, minutes=0)

    utc = pytz.UTC
    tz = pytz.timezone('Europe/Moscow')

    # Начинаем идти по сменам, отсчитываем 200 смен от начала отсчета (start_quarter_utc)
    for mul in range(0, 200):
        # Начало очередной смены
        start_interval = utc.localize(start_quarter_utc + delta * mul).astimezone(tz)
        # Конец очередной смены
        stop_interval = utc.localize(start_quarter_utc + delta * (mul + 1)).astimezone(tz)
        # Счетчик заявок (можно и без него обойтись, но уже некогда дебажить код)
        counter = 0
        # Список заявок, поданных за текущую (очередную) смену
        issues_list = []

        # Листаем все полученные запросом заявки
        for issue in issues:
            # Если заявка попала в интервал, определенный началом и концом текущей (очередной) смены,
            if start_interval <= dateutil.parser.isoparse(issue.fields.created) < stop_interval:
                # то добавляем заявку в список
                issues_list.append(issue)
                # и увеличиваем счетчик на 1
                counter += 1

        # Общее время рабочей смены в минутах
        tm = 12 * 60
        # Заполняем список времён работы над задачами, поделив время рабочей смены на (число заявок - 1)
        worklog = [round(tm / (counter + 1)) for _ in range(counter - 1)]
        # Последней заявке указываем время, оставшееся "неотработанным" с учетом уже заполненного списка времён worklog
        worklog.append(tm - sum(worklog))

        # Если список заявок не пуст
        if len(issues_list) > 0:
            # Выводим в консоль информацию по обрабатываемой смене
            print(mul, start_interval, stop_interval, counter, sum(worklog), worklog)
            # Для каждой заявки логаем время
            for i, iss in enumerate(issues_list):
                # Логание времени для конкретного сотрудника, отработавшего текущую (очередную) смену
                jira.add_worklog(issues_to_logtime[df.loc[start_interval]['person']],
                                 timeSpent='{}m'.format(worklog[i]),
                                 comment='Работа над запросом {}'.format(iss))
                # Добавление записи в лог-файл
                logging.info(": Добавлено время работы над задачей {} сотрудником {}".format(iss, df.loc[start_interval]['person']))


# Читаем файл с перечисленными сменами, отработанными сотрудниками
df = pd.read_csv('shifts.csv')
# Преобразуем формат данных в столбце времени, создаем новый столбец
df['shifts_parsed'] = df['shifts'].apply(dateutil.parser.isoparse)
# Устанавливаем полученный столбец индексом
df = df.set_index('shifts_parsed')

# Директория для хранения файла лога
logdir = '/var/log/'
# Задаем параметры логгера
logging.basicConfig(filename=logdir + 'worklog.log', filemode='a+', level=logging.INFO, format='%(asctime)s %(message)s')
logging.info(": Запущена процедура логания времени работы над задачами")

# Основная функция
logtime(df)

logging.info(": Процедура логания времени работы над задачами завершила свою работу \n")