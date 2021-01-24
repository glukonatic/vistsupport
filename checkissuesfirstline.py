import jiraclass
from collections import defaultdict
import re


def clean_text(text):
    text = re.sub(r"\n", " ", text)

    return text


def comments(interval="13h"):
    query = 'project = VISTHELP AND created >= -{}'.format(interval)

    # Вызываем объект класса, получающего список задач и переменную jira
    j = jiraclass.Jira()

    # Получаем переменную jira и список задач
    jira, issues = j.get_issues(username='VIST', jira_query=query)

    tp_persons_list = ["anton.mulenkov@zyfra.com",
                       "andrey.zhuk@zyfra.com",
                       "anton.nagovitsin@zyfra.com",
                       "pavel.khromov@zyfra.com",
                       "aleksey.polyakov@zyfra.com",
                       "sergey.kondratyev@zyfra.com",
                       "mikhail.serba@zyfra.com",
                       "yuriy.likhanov@zyfra.com",
                       "vistsupport24@zyfra.com"]

    comments = defaultdict()

    # Листаем задачи
    for iss in issues:

        c = None

        # Получаем объект задачи из джиры
        iss = jira.issue(str(iss))

        # Если есть комментарии в задаче
        if len(iss.fields.comment.comments) > 0 \
                and iss.fields.comment.comments[-1].author.emailAddress not in tp_persons_list:
            c = iss.fields.comment.comments[-1]
            comments[str(iss)] = clean_text(c.body) if len(c.body) < 100 else clean_text(c.body[:100] + '...')

    return comments if len(comments) > 0 else None


def levels():
    query = 'project = VISTHELP AND status not in (Resolved, Closed, Canceled)'

    # Вызываем объект класса, получающего список задач и переменную jira
    j = jiraclass.Jira()

    # Получаем переменную jira и список задач
    jira, issues = j.get_issues(username='ANTON', jira_query=query)

    levels = []

    # Листаем задачи
    for iss in issues:
        if hasattr(iss.fields.customfield_12507, "value") and \
                iss.fields.status.name not in ('Решен', 'Закрыт', 'Отменен') and \
                iss.fields.customfield_12507.value == "Консультации по работе АСД":
            levels.append(iss)

    return levels if len(levels) > 0 else None


def organizations(interval="4d"):
    query = 'project = VISTHELP AND created >= -{}'.format(interval)

    # Вызываем объект класса, получающего список задач и переменную jira
    j = jiraclass.Jira()

    # Получаем переменную jira и список задач
    jira, issues = j.get_issues(username='VIST', jira_query=query)

    orgs = []

    # Листаем задачи
    for iss in issues:
        if len(iss.fields.customfield_10403) == 0:
            orgs.append(iss)

    return orgs if len(orgs) > 0 else None