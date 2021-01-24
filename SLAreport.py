from datetime import timedelta
from datetime import datetime as dt
import jiraclass
import pandas as pd

class SLA_rep:

    def wdhms(self,td):
        """
        Функция преобразования интервала в милисекундах в недели, дни, часы, минуты
        """
        weeks = td.days // 7
        days = td.days % 7
        hours = td.seconds // (60 * 60)
        minutes = (td.seconds // 60) % 60
        seconds = td.seconds % 60

        out = ''

        if minutes != 0:
            out = '{}м'.format(minutes)
        if hours != 0:
            out = '{}ч '.format(hours) + out
        if days != 0:
            out = '{}д '.format(days) + out
        if weeks != 0:
            out = '{}нед '.format(weeks) + out

        if out == '':
            out = '0м'

        return out.rstrip()


    def broken_SLA(self,priority, td):
        """
        Функция для определения, нарушело СЛА или нет
        """

        SLA_t = {'Low': 1456, 'Medium': 156, 'High': 18, 'Highest': 8}
        hours = td.seconds // (60 * 60) + td.days * 24

        if SLA_t[priority] - hours >= 0:
            return('Нет')
        else:
            return('Да')

    def get_report(self, query):
        # Переменная, в которой будет вся таблица сохранена
        df = pd.DataFrame()

        # Вызываем объект класса, получающего список задач и переменную jira
        j = jiraclass.Jira()

        # Получаем переменную jira и список задач
        jira, issues = j.get_issues(jira_query = query)

        # Начинаем перечислять задачи
        for bar, iss in enumerate(issues):

            # Инициализируем переменные SLA нулями
            SLA1, SLA2, SLA3 = 0, 0, 0

            # Получаем предприятие (если не определено - пустая строка)
            if len(iss.fields.customfield_10403) > 0:
                enterprise = iss.fields.customfield_10403[0].name
            else:
                enterprise = ''

            if iss.fields.customfield_12507:
                level = iss.fields.customfield_12507.value
            else:
                level = ''

            # Получаем длительность работы над заявкой на разных линиях
            if len(iss.fields.customfield_12527.completedCycles) > 0:
                SLA1 += iss.fields.customfield_12527.completedCycles[0].elapsedTime.millis
            if hasattr(iss.fields.customfield_12527, 'ongoingCycle'):
                SLA1 += iss.fields.customfield_12527.ongoingCycle.elapsedTime.millis
            if len(iss.fields.customfield_12528.completedCycles) > 0:
                SLA2 += iss.fields.customfield_12528.completedCycles[0].elapsedTime.millis
            if hasattr(iss.fields.customfield_12528, 'ongoingCycle'):
                SLA2 += iss.fields.customfield_12528.ongoingCycle.elapsedTime.millis
            if len(iss.fields.customfield_12529.completedCycles) > 0:
                SLA3 += iss.fields.customfield_12529.completedCycles[0].elapsedTime.millis
            if hasattr(iss.fields.customfield_12529, 'ongoingCycle'):
                SLA3 += iss.fields.customfield_12529.ongoingCycle.elapsedTime.millis

            # Сохраняем построчно таблицу отчета
            df[str(iss)] = [level, enterprise,
                            iss.fields.priority.name,
                            iss.fields.status.name,
                            (dt.fromisoformat(iss.fields.created[:-9])).strftime("%d.%m.%Y %H:%M"),
                            self.wdhms(timedelta(milliseconds=SLA1)),
                            self.wdhms(timedelta(milliseconds=SLA2)),
                            self.wdhms(timedelta(milliseconds=SLA3)),
                            self.wdhms(timedelta(milliseconds=SLA1 + SLA2 + SLA3)),
                            self.broken_SLA(iss.fields.priority.name,
                                                  timedelta(milliseconds=SLA1 + SLA2 + SLA3))]

        # Определяем названия индексам
        df.index = ['Уровень', 'Предприятие', 'Приоритет', 'Статус', 'Создано',
                    'SLA 1 линии', 'SLA 2 линии', 'SLA 3 линии', 'Общее время', 'Нарушено SLA']

        # Транспонируем
        df = df.T

        # Сортируем
        df = df.sort_index()

        # Сохраняем в файл
        filename = str('SLA_report_' + dt.now().ctime() + '.xlsx').replace(' ', '_').replace(':', '')
        df.to_excel(filename)

        return filename
