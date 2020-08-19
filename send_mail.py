import smtplib
import datetime
import os


class Mail:
    def __init__(self):
        self.__timeStamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f%Z")
        self.__server = smtplib.SMTP('smtp.gmail.com', 587)

        self.__server.ehlo()
        self.__server.starttls()
        self.__server.ehlo()

        self.__server.login(os.environ.get("g_mail"), os.environ.get("g_pass"))

    def send_bug_detected(self):
        subject = 'Bug detected in Competitive Programming Score API'
        body = 'Bug detected in Competitive Programming Score API at {date}.\n'.format(date=self.__timeStamp)

        body += '\nCheck logs for more information\n'
        body += 'https://dashboard.heroku.com/apps/competitive-coding-api/logs'

        message = f'Subject : {subject}\n\n{body}\n'

        self.__server.sendmail('', ['abhijeet_abhi@live.co.uk'], message)


if __name__ == '__main__':
    mail = Mail()
    mail.send_bug_detected()
