import jiraclass

def check_levels():

    query = 'project = VISTHELP AND status not in (Resolved, Closed, Canceled)'

    # Вызываем объект класса, получающего список задач и переменную jira
    j = jiraclass.Jira()

    # Получаем переменную jira и список задач
    jira, issues = j.get_issues(username='ANTON',jira_query=query)

    iss_list = []

    # Листаем задачи
    for iss in issues:
        if iss.fields.customfield_12507.value == "Консультации по работе АСД":
            iss_list.append("Зачада {}: {}".format(iss, iss.fields.customfield_12507.value))

    # Заполняем окончание файла, сохраняем

    return ('\n').join(iss_list)