import jiraclass
from datetime import datetime as dt
import pandas as pd


def report(query=None):

    # Вызываем объект класса, получающего список задач и переменную jira
    j = jiraclass.Jira()

    # Получаем переменную jira и список задач
    jira, issues = j.get_issues(jira_query=query)

    df = pd.DataFrame()

    # Начинаем перебирать заявки, полученные в списке фунцией get.issues()
    for iss1 in issues:

        iss2, iss3 = None, None
        s1, s2, s3 = None, None, None
        all_times = None
        work_time1, work_time2, work_time3 = None, None, None

        if iss1.fields.customfield_12507:
            level = iss1.fields.customfield_12507.value
        else:
            level = ''

        priority = iss1.fields.priority.name
        status = iss1.fields.status.name

        # Проверяем список присоединенных задач к заявке
        for issue_link1 in iss1.fields.issuelinks:
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
            if not iss2 and linked_issue1 and 'VISTHELP2' in str(linked_issue1):
                # Запрашиваем задачу с сервера
                iss2 = jira.issue(str(linked_issue1))

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
                    if not iss3 and linked_issue2 and 'VISTV8' in str(linked_issue2):
                        # Запрашиваем задачу с сервера
                        iss3 = jira.issue(linked_issue2)

        now = dt.strptime(dt.now().strftime("%d.%m.%Y %H:%M"), "%d.%m.%Y %H:%M")

        if iss1.fields.resolutiondate:
            work_time1 = dt.fromisoformat(iss1.fields.resolutiondate[:-9]) - dt.fromisoformat(iss1.fields.created[:-9])
        else:
            work_time1 = now - dt.fromisoformat(iss1.fields.created[:-9])

        if iss2 and iss1.fields.resolutiondate:
            work_time2 = dt.fromisoformat(iss1.fields.resolutiondate[:-9]) - dt.fromisoformat(iss2.fields.created[:-9])
        elif iss2:
            work_time2 = now - dt.fromisoformat(iss2.fields.created[:-9])
        else:
            work_time2 = None

        if iss3 and iss2.fields.resolutiondate:
            work_time3 = dt.fromisoformat(iss2.fields.resolutiondate[:-9]) - dt.fromisoformat(iss3.fields.created[:-9])
        elif iss3 and iss1.fields.resolutiondate:
            work_time3 = dt.fromisoformat(iss1.fields.resolutiondate[:-9]) - dt.fromisoformat(iss3.fields.created[:-9])
        elif iss3:
            work_time3 = now - dt.fromisoformat(iss3.fields.created[:-9])
        else:
            work_time3 = None

        if work_time1 and work_time2:
            s1 = work_time1 - work_time2
        else:
            s1 = work_time1

        if work_time2 and work_time3:
            s2 = work_time2 - work_time3
        else:
            s2 = work_time2

        if work_time3:
            s3 = work_time3

        if s1 and s2 and s3:
            all_times = s1 + s2 + s3
        elif s1 and s2:
            all_times = s1 + s2
        else:
            all_times = s1

        df[str(iss1)] = [level,
                      priority,
                      (dt.fromisoformat(iss1.fields.created[:-9])).strftime("%d.%m.%Y %H:%M"),
                      (dt.fromisoformat(iss2.fields.created[:-9])).strftime("%d.%m.%Y %H:%M") if iss2 else None,
                      (dt.fromisoformat(iss2.fields.resolutiondate[:-9])).strftime(
                          "%d.%m.%Y %H:%M") if iss2 and iss2.fields.resolutiondate else None,
                      (dt.fromisoformat(iss3.fields.created[:-9])).strftime("%d.%m.%Y %H:%M") if iss3 else None,
                      (dt.fromisoformat(iss3.fields.resolutiondate[:-9])).strftime(
                          "%d.%m.%Y %H:%M") if iss3 and iss3.fields.resolutiondate else None,
                      str(s1) if s1 else None, str(s2) if s2 else None, str(s3)  if s3 else None,
                         str(all_times) if all_times else None,
                      (dt.fromisoformat(iss1.fields.resolutiondate[:-9])).strftime(
                          "%d.%m.%Y %H:%M") if iss1.fields.resolutiondate else None,
                      status,
                      ''
                      ]

    df.index = ['Уровень',
                'Приоритет',
                'Дата и время создания на 1-й линии ТП',
                'Дата и время создания на 2-й линии',
                'Дата и время решения на 2-й линии',
                'Дата и время создания на 3-й линии',
                'Дата и время решения на 3-й линии',
                'Время решения на 1-й линии',
                'Время решения на 2-й линии',
                'Время решения на 3-й линии',
                'Время решения',
                'Дата и время решения',
                'Статус',
                'Комментарий']

    df = df.T
    df = df.fillna('')
    filename = str('SLA_report_old_' + dt.now().ctime() + '.xlsx').replace(' ', '_').replace(':', '')
    df.to_excel(filename)

    return filename