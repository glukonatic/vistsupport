from datetime import timedelta, datetime
import dateutil.parser
import jiraclass
import htmlcreate
import pytz

def find_lost_answers(days=100):
    """
    Проверка, имеются ли упущенные комментарии на второй линии,
    то есть такие, после которых движение задачи на первой линии не было возобновлено
    :return: Функция создает html-файл со списком упущенных задач второй линии
    """

    html = htmlcreate.htmlcreate()

    # Заполняем "шапку" в файле
    html.file_begins_ends('begin', header="Упущенные комментарии на 2 и 3 линиях")

    tp_names_list = ['Anton Nagovitsin', 'Aleksey Polyakov', 'Pavel Khromov', 'Sergey Kondratyev',
                              'Anton Mulenkov', 'Yuriy.Likhanov', 'VIST Support', 'andrey.zhuk@zyfra.com']
    query = 'status not in (Done, Closed, Declined, Resolved) AND project = VISTHELP'

    delta = timedelta(days=days)

    # Время в UTC
    utc = pytz.UTC

    # Список тикетов, полученные запросом из Jira
    # Вызываем объект класса, получающего список задач и переменную jira
    j = jiraclass.Jira()

    # Получаем переменную jira и список задач
    jira, issues = j.get_issues(username='ANTON', jira_query=query)

    # Начинаем перебирать заявки, полученные в списке фунцией get.issues()
    for issue in issues:
        # Получаем объект "Заявка" из джиры
        issue = jira.issue(str(issue))
        # Проверяем список присоединенных задач к заявке
        for issue_link in issue.fields.issuelinks:
            # Проверяем, есть ли аттрибут с именем inwardIssue
            if hasattr(issue_link, 'inwardIssue'):
                # Если есть, то получаем объект заявки, присоединенной к задаче
                linked_issue = jira.issue(issue_link.inwardIssue.key)
            # Иначе проверяем, есть ли аттрибут с именем outwardIssue
            elif hasattr(issue_link, 'outwardIssue'):
                # Если есть, то получаем объект заявки, присоединенной к задаче
                linked_issue = jira.issue(issue_link.outwardIssue.key)
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
                    and linked_issue.fields.comment.comments[-1].author.displayName not in tp_names_list \
                    and dateutil.parser.isoparse(issue.fields.comment.comments[-1].created) > utc.localize(
                datetime.today() - delta):
                # Вызываем функцию записи в файл
                html.write_data(linked_issue, linked_issue.fields.comment.comments[-1])

    # Заполняем окончание файла, сохраняем
    filename = html.file_begins_ends('end')

    return filename