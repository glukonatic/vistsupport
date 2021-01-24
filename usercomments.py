import jiraclass
import htmlcreate
import re

# За какое время делаем запрос к джире
days = 10

# query = input('JQL:')
query = 'project = VISTHELP2 AND created >= -{}d'.format(days)

# Вызываем объект класса, получающего список задач и переменную jira
j = jiraclass.Jira()

# Получаем переменную jira и список задач
jira, issues = j.get_issues(username='ANTON',jira_query=query)

html = htmlcreate.htmlcreate()

# Заполняем "шапку" в файле
file = html.file_begins_ends('begin', header="Проверка комментариев")

# Листаем задачи
for iss in issues:
    # Получаем объект задачи из джиры
    iss = jira.issue(str(iss))
    # Если есть комментарии в задаче
    if len(iss.fields.comment.comments) != 0:
        # Берем последний комментарий задачи
        for comment in iss.fields.comment.comments:
            # Если автор комментария я и есть описание sql-запроса
            if comment.author.name == 'anton.nagovitsin@zyfra.com' \
                    and hasattr(re.search(r'select', comment.body.lower),'group'):
                # То пишем в файл
                html.write_data(iss, comment)

# Заполняем окончание файла, сохраняем
html.file_begins_ends('end')