import smtplib 
from email.mime.text import MIMEText
from email.header import Header
from email.utils import parseaddr,formataddr

def send_mail(account, password, dst_email, mailhost, content):
    def _format_addr(s):
        s = parseaddr(s)
        return formataddr(s)

    qqmail = smtplib.SMTP()
    qqmail.connect(mailhost,25)
    qqmail.login(account,password)

    message = MIMEText(content, 'html', 'utf-8')
    subject = "Recommend by your to watch list"
    #输入你的邮件主题，为字符串格式
    message['Subject'] = Header(subject, 'utf-8')
    message['From'] = _format_addr("wt_from <%s>" % account)
    message['To'] =  _format_addr("wt_to <%s>" % account)

    try:
        qqmail.sendmail(account, dst_email, message.as_string())
        print ('send email success')
    except Exception as e:
        print ('send email failure', e)
    qqmail.quit()