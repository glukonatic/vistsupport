import checklevels
import mailsend

out = checklevels.check_levels()

out = "В следующих задачах уровень остался \"Консультации по работе АСД\"\nМожет быть, можно его изменить:\n\n" + out

mboxes_list = ["anton.mulenkov@zyfra.com",
                "andrey.zhuk@zyfra.com",
                "anton.nagovitsin@zyfra.com",
                "pavel.khromov@zyfra.com",
                "aleksey.polyakov@zyfra.com",
                "yuriy.likhanov@zyfra.com"]

m = mailsend.mail(mailboxes=mboxes_list)

m.send_email(msg_txt=out)
