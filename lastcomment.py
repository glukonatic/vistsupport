import jiraclass
import htmlcreate
import pytz


def lastcomment():
    html = htmlcreate.htmlcreate()

    # Время в UTC
    utc = pytz.UTC

    # query = 'project = VISTHELP AND status not in (Resolved, Closed, Done, Declined, Canceled)'
    query = 'project = VISTHELP AND status in (Developing, Pending, Analisis)'

    # Заполняем "шапку" в файле
    html.file_begins_ends('begin',
                          header="Проверка комментариев (по {} задачам на 1 линии в статусах Анализ, Разработка и Ожидание)".format(len(query)))

    # Вызываем объект класса, получающего список задач и переменную jira
    j = jiraclass.Jira()

    # Получаем переменную jira и список задач
    jira, issues = j.get_issues(username='ANTON',jira_query=query)

    tp_persons_list = ["anton.mulenkov@zyfra.com",
                        "andrey.zhuk@zyfra.com",
                        "anton.nagovitsin@zyfra.com",
                        "pavel.khromov@zyfra.com",
                        "aleksey.polyakov@zyfra.com",
                        "sergey.kondratyev@zyfra.com",
                        "mikhail.serba@zyfra.com",
                        "yuriy.likhanov@zyfra.com",
                         "vistsupport24@zyfra.com"]

    # Листаем задачи
    for iss in issues:

        i, c = None, None
        iss2, iss3 = None, None

        # Получаем объект задачи из джиры
        # iss = jira.issue(str(i))
        # Если есть комментарии в задаче

        # Проверяем список присоединенных задач к заявке
        for issue_link1 in iss.fields.issuelinks:
            # Проверяем, есть ли аттрибут с именем inwardIssue
            if hasattr(issue_link1, 'inwardIssue'):
                # Если есть, то получаем объект заявки, присоединенной к задаче
                linked_issue1 = jira.issue(issue_link1.inwardIssue.key)
            # Иначе проверяем, есть ли аттрибут с именем outwardIssue
            elif hasattr(issue_link1, 'outwardIssue'):
                # Если есть, то получаем объект заявки, присоединенной к задаче
                linked_issue1 = jira.issue(issue_link1.outwardIssue.key)
            # В противном случае переходим к следующей итерации цикла
            else:
                continue

            # Если есть связанная задача, и она - на второй линии
            if linked_issue1 and 'VISTHELP2' in str(linked_issue1):
                # Запрашиваем задачу с сервера
                iss2 = jira.issue(str(linked_issue1))
                if iss2.fields.status.name not in ('Resolved', 'Closed', 'Done', 'Declined', 'Canceled') and \
                        len(iss2.fields.comment.comments) != 0 and \
                        iss2.fields.comment.comments[-1].author.emailAddress not in tp_persons_list:
                    # Берем последний комментарий задачи
                    i = iss2
                    c = i.fields.comment.comments[-1]
                # Проверяем список присоединенных задач к заявке
                for issue_link2 in iss2.fields.issuelinks:
                    # Проверяем, есть ли аттрибут с именем inwardIssue
                    if hasattr(issue_link2, 'inwardIssue'):
                        # Если есть, то получаем объект заявки, присоединенной к задаче
                        linked_issue2 = jira.issue(issue_link2.inwardIssue.key)
                    # Иначе проверяем, есть ли аттрибут с именем outwardIssue
                    elif hasattr(issue_link2, 'outwardIssue'):
                        # Если есть, то получаем объект заявки, присоединенной к задаче
                        linked_issue2 = jira.issue(issue_link2.outwardIssue.key)
                    # В противном случае переходим к следующей итерации цикла
                    else:
                        continue

                    # Если имеется ссылка на задачу на 3 линии
                    if linked_issue2 and 'VISTV8' in str(linked_issue2):
                        # Запрашиваем задачу с сервера
                        iss3 = jira.issue(linked_issue2)
                        if iss3.fields.status.name not in ('Resolved', 'Closed', 'Done', 'Declined', 'Canceled') and \
                            len(iss3.fields.comment.comments) != 0 and \
                            iss3.fields.comment.comments[-1].author.emailAddress not in tp_persons_list:
                            # Берем последний комментарий задачи
                            i = iss3
                            c = i.fields.comment.comments[-1]

        # Вызываем функцию записи в файл
        if i and c:
            html.write_data(i, c)

    # Заполняем окончание файла, сохраняем
    filename = html.file_begins_ends('end')

    return filename