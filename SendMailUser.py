import threading
import smtplib
import ssl
import getpass
import email
import datetime
from pymongo import MongoClient
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


class SendMailUser(threading.Thread):


    def __init__(self, user, password, receiver):
        super().__init__()
        self.user           = user
        self.__pass         = password
        self.receiver_email = receiver
        self.subject        = ''
        self.body           = ''
        self.filename       = ''
        self.message        = None
        self.smtp_server    = "smtp.gmail.com"
        self.port           = 465
        # print(instancia)


    def setcontent(self, file):
        with open("contentuser.txt", "r", encoding='utf-8') as f:
            self.body= f.read()

    def setmessage(self, body):
        self.setcontent(body)
        self.subject = "Oficina-1: PNID"
        self.message = MIMEMultipart()
        self.message["Subject"] = self.subject
        self.message["From"] = self.user
        self.message["To"] = self.receiver_email
        self.message.attach(MIMEText(self.body, "plain"))


    def connect(self):
        context = ssl.create_default_context()
        # print("t1")
        with smtplib.SMTP_SSL(self.smtp_server, self.port, context=context) as server:
            # print("t2")
            server.login(self.user, self.__pass)
            server.sendmail(self.user, self.receiver_email, self.message.as_string())
            if server.noop()[0] == 250:
                print(f'Mail sent to user...')
            # print(server.noop())



    def run(self):

        self.connect()
