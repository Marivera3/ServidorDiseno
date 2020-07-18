from SendMail import SendMail
from SendMailUser import SendMailUser
from SendMailf import SendMailf
from ReceiveMail import ReceiveMail
from pymongo import MongoClient, ReadPreference
from User.User import PersonServ
import threading
import time
import datetime
import hashlib
import io
import pickle
import codecs
import numpy
import mongoengine as me
import matplotlib.pyplot as plt
import json
import base64
# User
user = 'disenouc20g14@gmail.com'
# password = getpass.getpass()
password = 'DisenoUCg14'
# admin
receiver_email = 'max.rivera.figueroa@gmail.com'

## Connect to DBs
# Connection to pymongo DB Rasp
mongo_client_Rasp = MongoClient('mongodb://server4diseno.duckdns.org:1226')
db_Rasp = mongo_client_Rasp["Rasp"]
col_Rasp = db_Rasp["person_rasp"].with_options(read_preference=ReadPreference.SECONDARY)
print(f"[INFO] Conecting to DB Rasp with:{col_Rasp.read_preference}...")

# Conection to DB Server pymongo
mongo_client_Server = MongoClient('mongodb://127.0.0.1:27018')
db_Server = mongo_client_Server["server"]
col_Server = db_Server["person_serv"]

## Connect to mongoengine
me.connect('server', host='127.0.0.1', port=27018)
# PersonServ(name="Max3", surname="Rivera3", is_recognized=True).save()
print("[INFO] Conecting to DB Sever...")

## Start receiving emails

receive = ReceiveMail(user=user, password=password, time=1)
receive.start()


## Functions

def readrxbuffer(rx, col):
    if len(rx.list_msg) > 0:
        for i in rx.list_msg:
            print(f'RX = Name: {i.name}, Surname: {i.surname}, mail: {i.mail}, ID: {i.id}')
            # enviar mail
            doc = [x for x in col.find({}) if i.id in x["idlist"]]

            # print(i.mail)


            if doc:
                doc = doc[0]
                if doc:
                    if doc["mail_recieved"] == True:
                        print("mail ya enviado al usuario")
                    else:
                        mail1 = SendMailUser(user, password, i.mail)
                        mail1.setmessage('contentuser.txt')
                        mail1.start()

                        doc["name"] =  i.name.lower()
                        doc["surname"] =  i.surname.lower()
                        doc["last_update_at"] = datetime.datetime.utcnow()
                        doc["is_recognized"] = True
                        doc["mail_recieved"] = True
                        doc["waiting_response"] = False
                        col.save(doc)

        rx.clear_msg()

def addperson2dbserver(x):
    keysx = x.keys()
    if "last_out" in keysx:
        l_out = x["last_out"]
    else:
        l_out = ""

    if "seralize_pic" in keysx:
        s_pic = x["seralize_pic"]
    else:
        s_pic = ""

    if "picture" in keysx:
        pic= x["picture"]
    else:
        pic = ""

    PersonServ(idlist=[x["idrasp"]],name=x["name"], surname=x["surname"],
                hist_mov=[[x["last_in"], l_out]],
                is_recognized=x["is_recognized"],
                seralize_pic=s_pic, picture=pic,
                likelihood=[x["likelihood"]]).save()

def sendfinalemail(col):
    mail1 = SendMailf(user=user, password=password,
                    receiver=receiver_email, col=col).start()

def sendmailfromserver(x, col):
        mail1 = SendMail(user=user, password=password,
                        receiver=receiver_email, id=x["idrasp"], col=col)
        mail1.setmessage('content.txt')

        keysx = x.keys()
        # print(keysx)
        # buffer = io.BytesIO()
        if "picture" in keysx:

            ser_pic = x["picture"]
            # print(ser_pic)
            # unpickled = pickle.loads(codecs.decode(ser_pic.encode(), "base64"))
            unpickled = base64.b64decode(ser_pic)
            # plt.imsave(buffer, unpickled)
        else:
            ser_pic = ""
        mail1.attach_bytes(unpickled, 'unknown.png')
        mail1.start()

def isdocnotrepeated(docser, docrasp, cond=1):
    keysx = docrasp.keys()
    if "last_out" in keysx:
        l_out = docrasp["last_out"]
    else:
        l_out = ""

    if cond == 0:
        # caso sin nombre
        idrasp = docrasp["idrasp"]
        index = docser["idlist"].index(idrasp)
        mov = docser[index]
        if docrasp["last_in"] == mov[0] and l_out == mov[1]:
            return False
        else:
            return True

    if cond == 1:
        # caso con nombre
        pass

# data = pickle.loads(open('imagen.pickle', "rb").read())
# print([doc["name"] for doc in col_Server.find({})])

# print("cleaning DB")
# me.connect('server', host='127.0.0.1', port=27018)
# for doc in PersonServ.objects():
#     if doc.surname == "":
#         doc.delete()


sendfinalemail(col_Server)
time.sleep(10)
c = 0
while True:
    c += 1
    time.sleep(1)
    # busco en la base de datos del Rasp si existe alguien no reconocido
    print(c)

    for x in col_Rasp.find({}):
        # print(x)
        if not x["is_trained"]:

            actual_doc_by_id = [dc for dc in col_Server.find({}) if x["idrasp"] in dc["idlist"]]
            # print(f"DOC ID:{actual_doc_by_id}")
            # Ver si tienen igual nombre para agregar el idrasp
            actual_doc_by_name = [dc for dc in col_Server.find({}) if x["name"]== dc["name"] and  x["surname"]== dc["surname"]]
            # print(f"DOC Name:{actual_doc_by_name}")
            if len(actual_doc_by_id) == 0 and len(actual_doc_by_name) == 0:
                print("caso 0")
                # Persona no esta en la base de datos del servidor, se agrega
                addperson2dbserver(x)
                if x["is_recognized"] == False:
                    # en caso de que no fue reconocido se envia mail
                    print("Send Mail to add person")
                    sendmailfromserver(x, col_Server)

            elif len(actual_doc_by_name) > 0 and len(actual_doc_by_id) == 0:
                # Vuelve a entrar
                print("Caso 2")
                auxdoc = actual_doc_by_name[0]
                last_in = x["last_in"]
                keysx = x.keys()
                if "last_out" in keysx:
                    last_out = x["last_out"]
                else:
                    last_out = ""
                hist_mov = auxdoc["hist_mov"]
                # idlist = auxdoc["idlist"]
                if [last_in, last_out] in hist_mov:
                    # Repetido
                    continue
                else:

                    auxdoc["hist_mov"].append([last_in, last_out])
                    auxdoc["idlist"].append(x["idrasp"])
                    col_Server.save(auxdoc)

            elif len(actual_doc_by_name) > 0 and len(actual_doc_by_id) > 0:
                # Ya esta en la BD, puede ser salida o repetido
                print("Caso 3")
                auxdoc = actual_doc_by_name[0]
                last_in = x["last_in"]
                keysx = x.keys()
                if "last_out" in keysx:
                    last_out = x["last_out"]
                else:
                    last_out = ""
                hist_mov = auxdoc["hist_mov"]
                if [last_in, last_out] in hist_mov:
                        print("repetido C3")
                        continue
                else:
                    for ent in range(len(hist_mov)):
                        if hist_mov[ent][0] == last_in:
                            hist_mov[ent][1] = last_out

                    col_Server.save(auxdoc)

        else:
            # Datos que ya an sidos entrenados
            actual_doc_by_name = [dc for dc in col_Server.find({}) if x["name"]== dc["name"] and  x["surname"]== dc["surname"]]
            if actual_doc_by_name:
                doc = actual_doc_by_name[0]
                if not doc["is_added"]:
                    doc["is_added"] = True
                    doc["is_waiting_cam"] = False
                    col_Server.save(doc)



        # elif len(actual_doc_by_name) == 0 and len(actual_doc_by_id) > 0:
        #     # Este caso es cuando el idrasp esta en la BD server y no esta el nombre
        #     print("case 1")
        #     pass
        #
        # elif len(actual_doc_by_name) > 0 and len(actual_doc_by_id) == 0:
        #     print("caso 2")
        #     # Estan en la bd Server, pero no se reconoce el id, e.d., ingreso nuevamente
        #     # No importa si se reconoce o no ya que ya se envio mail en el caso de que no
        #
        #
        #     actual_doc_by_name[0]["idlist"].append(x["idrasp"])
        #     # # Falta rutina para ver si es entrada o salida
        #     keysx = x.keys()
        #     if "last_out" in keysx:
        #         l_out = x["last_out"]
        #     else:
        #         l_out = ""
        #     actual_doc_by_name[0]["hist_mov"].append((x["last_in"], l_out))
        #     col_Server.save(actual_doc_by_name[0])
        #
        #
        # elif len(actual_doc_by_id) > 0 and len(actual_doc_by_name) > 0:
        #     print("caso 3")
        #     # Persona ya esta en la base de datos,
        #     if x["is_recognized"] == True:
        #         last_in = x["last_in"]
        #         last_out = x["last_out"]
        #         hist_mov = actual_doc_by_id["hist_mov"]
        #         for mv in hist_mov:
        #             if last_in in mv:
        #                 actual_doc_by_id["hist_mov"].append((last_in, last_out))
        #                 col_Server.save(actual_doc_by_id)




    readrxbuffer(receive, col_Server)
    now = datetime.datetime.now()
    if now.hour == 21:
        sendfinalemail(col_Server)
    if c == 1000:
        # sendfinalemail()
        # receive.disconnectserver()
        sendfinalemail(col_Server)
        break
