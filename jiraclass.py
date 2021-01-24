import os
from jira import JIRA
from dotenv import load_dotenv

# Получаем текущую директорию
path = os.path.dirname(__file__)

class Jira:

    def get_issues(self, jira_query=None, username='VIST'):
        """
        Функция для получения списка задач и переменной jira
        :param jira_query: jql-запрос в виде строки. По умолчанию - None
        :param username: пользователь, логин/пароль которого будет взят из файла .env
        :return:
        """

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

        return jira, issues