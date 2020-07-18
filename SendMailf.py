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
import numpy as np
from tabulate import tabulate


class SendMailf(threading.Thread):


    def __init__(self, user, password, receiver, col):
        super().__init__()
        self.user           = user
        self.__pass         = password
        self.receiver_email = receiver
        self.id             = id
        self.subject        = ''
        self.collection     = col
        # self.body          doc.last_in = [[doc.name, doc.surname, doc.last_in, doc.last_out]
        # for doc in self.collection.find({})]
        self.filename       = ''
        self.message        = None
        self.smtp_server    = "smtp.gmail.com"
        self.port           = 465



    def setmessage(self):
        self.subject = "Oficina-1: PNID"
        self.message = MIMEMultipart()
        self.message["Subject"] = self.subject
        self.message["From"] = self.user
        self.message["To"] = self.receiver_email
        self.body = []
        for doc in self.collection.find({}):
            keysx = doc.keys()
            l_long = ""
            if "hist_mov" in keysx:
                mov = doc["hist_mov"]
                for ent in mov:
                    l_in = ent[0]
                    l_out = ent[1]

                    if l_in:
                        if l_in.day == datetime.datetime.now().day:
                            l_in = l_in - datetime.timedelta(hours=4)

                            if l_out == "":
                                l_out = "-"
                                l_long = "-"
                            else:
                                l_out = l_out - datetime.timedelta(hours=4)
                                l_long = l_out - l_in

                            try:
                                # print(l_in)
                                self.body.append([doc["name"], doc["surname"], l_in.strftime("%H:%M") , l_out.strftime("%H:%M"), (l_long).strftime("%H:%m")  ])

                            except:
                                # print(l_in)
                                self.body.append([doc["name"], doc["surname"],  l_in.strftime("%H:%M")  , l_out, l_long])


        headers = ["Nombre", "Apellido", "Hora ingreso", "Hora salida", "Duración dentro"]
        table = tabulate(self.body, headers, tablefmt="html", stralign="center")
        # print(table)
        texto = '<font face="Courier New, Courier, monospace">' + table + '</font>'
        with open("Templates/mailfinal.html", "r") as file:
            f = file.read()
            self.message.attach(MIMEText(f.format(fecha=datetime.datetime.now().strftime(" %d/%m/%Y ") ,mail=texto), "html"))



    def connect(self):
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(self.smtp_server, self.port, context=context) as server:
            server.login(self.user, self.__pass)
            server.sendmail(self.user, self.receiver_email, self.message.as_string())
            if server.noop()[0] == 250:
                print(f'Final Mail sent...')


    def run(self):
        self.setmessage()
        self.connect()
