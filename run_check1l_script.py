import checkissuesfirstline as check
import mailsend


template_text_begin = """\
<html>
  <body>

"""

template_text_end = """\
  </body>
</html>
"""

r = check.comments()
l = check.levels()
o = check.organizations()

main_text = ''

if r:
    main_text += '<h3>В заявках есть комментарии от клиентов, после которых не последовало ответа:</h3>'

    for k, v in r.items():
        main_text += '<p><a href="https://jira.zyfra.com/browse/{}">{}</a>: {}</p>'.format(k, k, v)

if l:
    main_text += '<h3>В следующих заявках остался уровень "Консультации по работе АСД":</h3>'

    for issue in l:
        main_text += '<p><a href="https://jira.zyfra.com/browse/{}">{}</a>: {}</p>'.format(issue, issue,
                                                                                           issue.fields.customfield_12507.value)

if o:
    main_text += '<h3>В следующих заявках не указана организация:</h3>'

    for issue in o:
        main_text += '<p><a href="https://jira.zyfra.com/browse/{}">{}</a></p>'.format(issue, issue)

all_text = template_text_begin + main_text + template_text_end if r or l or o else None

if all_text:
    mboxes_list = ["anton.mulenkov@zyfra.com",
                       "andrey.zhuk@zyfra.com",
                       "anton.nagovitsin@zyfra.com",
                       "pavel.khromov@zyfra.com",
                       "aleksey.polyakov@zyfra.com",
                       "yuriy.likhanov@zyfra.com"]
    m = mailsend.mail(mailboxes=mboxes_list)
    m.send_email(html_text=all_text)