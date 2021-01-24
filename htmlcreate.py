from datetime import datetime
import dateutil.parser

class htmlcreate:

    def __init__(self):
        self.filename = None
        self.file = None
        self.bg_change = 0

    def file_begins_ends(self, flg, header='Последние комментарии', send_email=False):

        # Список строк для формирования заголовка отчета
        string_before = ["<!DOCTYPE html>",
                         "<html lang=\"ru\">",
                         "<head>",
                         "<title>Выгрузка из Джиры</title>",
                         "<meta charset=\"utf-8\">",
                         "<meta name=\"viewport\" content=\"width=device-width, "
                         "initial-scale=1.0\">",
                         "<style>",
                         "body { background-color: #F4F6F6; }",
                         "h2 { text-align: center; font-family: Verdana, Arial, Helvetica, sans-serif; color: #336; }",
                         "h3 { text-align: center; font-family: Verdana, Arial, Helvetica, sans-serif; color: blue; }",
                         "p { color: green; }",
                         "</style>",
                         "</head> ",
                         "<body>",
                         "<h2>{}</h2>".format(header),
                         '\n',
                         "<section id=\"docs\" style=\"margin: 5%;\">"]

        # Список строк для формирования окончания отчета
        string_after = ["</section>",
                        "</body>",
                        "</html> "]

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

            return self.filename

    def write_data(self, i, c):
        if self.bg_change == 0:
            bg = "#EAECEE"
            self.bg_change = 1
        else:
            bg = "#EBEDEF"
            self.bg_change = 0

        self.file.write("<section style=\"background-color: {};\">".format(bg) +
                        "<p style=\"padding-left:100px;\"><strong>" +
                        str(i) +
                        ": <a href=\"" +
                        "https://jira.zyfra.com/browse/" +
                        str(i) +
                        "\" target=\"new\"> " +
                        i.fields.summary +
                        "</a></strong> " +
                        "<p> <table width=\"100%\"><tr><td width=\"200\">" + dateutil.parser.isoparse(c.created).ctime() + "</td>"
                        "<td rowspan=\"2\">" + c.body + "</td></tr>" +
                        "<tr><td><b>" + c.author.displayName + "</b>" +
                        "</td>" +
                        "<td></td></tr></table>" +
                        "<hr>" +
                        "</section>"
                        )