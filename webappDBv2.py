import tornado.web
from tornado.ioloop import IOLoop
from tornado import gen
from tornado.concurrent import run_on_executor
from concurrent.futures import ThreadPoolExecutor   # `pip install futures` for python2
from pymongo import MongoClient
import json
import datetime
import tornado.httpserver
import socket
import threading
MAX_WORKERS = 16

class TestHandler(tornado.web.RequestHandler):
    executor = ThreadPoolExecutor(max_workers=MAX_WORKERS)

    """
    In below function goes your time consuming task
    """

    @run_on_executor
    def background_task(self):
        mongo_client_Server = MongoClient('mongodb://127.0.0.1:27018')
        db_Server = mongo_client_Server["server"]
        col_Server = db_Server["person_serv"]
        l = []
        for doc in col_Server.find({}):
            aux_dic = dict({})
            if "unknown" not in doc["name"]:
                aux_dic["name"] = doc["name"]
                aux_dic["surname"] = doc["surname"]
                aux_dic["idlist"] = doc["idlist"]
                l.append(aux_dic)


        return json.dumps(l)

    @tornado.gen.coroutine
    def get(self):
        """ Request that asynchronously calls background task. """
        res = yield self.background_task()
        self.write(res)

class TestHandler2(tornado.web.RequestHandler):
    executor = ThreadPoolExecutor(max_workers=MAX_WORKERS)

    @run_on_executor
    def background_task(self):
        mongo_client_Server = MongoClient('mongodb://127.0.0.1:27018')
        db_Server = mongo_client_Server["server"]
        col_Server = db_Server["person_serv"]
        l = []
        for doc in col_Server.find({}):
            aux_dic = dict({})
            if "unknown" not in doc["name"]:
                aux_dic["name"] = doc["name"]
                aux_dic["surname"] = doc["surname"]
                aux_dic["idlist"] = doc["idlist"]
                l.append(aux_dic)


        return l

    @tornado.gen.coroutine
    def get(self):
        res = yield self.background_task()
        self.write(str(len(res)))


class SolicitudHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('indexcam.html')


class ExitoHandler(tornado.web.RequestHandler):
    def post(self):
        self.render('exito.html')

class IngresoHandler(tornado.web.RequestHandler):
    executor = ThreadPoolExecutor(max_workers=MAX_WORKERS)

    @run_on_executor
    def getDB(self):
        mongo_client_Server = MongoClient('mongodb://127.0.0.1:27018')
        db_Server = mongo_client_Server["server"]
        col_Server = db_Server["person_serv"]
        return col_Server

    @tornado.gen.coroutine
    def post(self):
        col_Server = yield self.getDB()

        name = self.get_argument('name').lower()
        surname = self.get_argument('surname').lower()
        docs = [doc for doc in col_Server.find({}) if doc["name"] == name and doc["surname"] == surname]
        if docs:
            auxdoc = docs[0]
            # print(auxdoc)
            if not auxdoc["is_waiting_cam"]:
                c = 0
                while c < 5:
                    try:
                        host = "grupo14.duckdns.org"
                        port = 1299
                        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        s.connect((host, port))
                        c = 10

                        print("Coneccion Exitosa")
                        self.render('ingreso.html')
                        auxdoc["is_waiting_cam"] = True
                        auxdoc["waiting_since"] = datetime.datetime.now()
                        col_Server.save(auxdoc)
                    except Exception as e:
                        print(e)
                        print("error")
                        # connected = False
                        c += 1
                    finally:
                        s.close()

                if c < 10:
                    self.render('error.html')
                # threading.Thread(target=self.makeconnection).start()
                # while not auxdoc["is_added"]:
                #     col_Server = yield self.getDB()
                #     docs = [doc for doc in col_Server.find({}) if doc["name"] == name and doc["surname"] == surname]
                #     auxdoc = docs[0]
                # self.write("Exito")
            else:
                self.render('error_esperando.html')
        else:
            self.render('error.html')
        # print(auxdoc)
        # si esta en la base de datos, render ingreso, si no render error
    def makeconnection(self):
        host = "grupo14.duckdns.org"
        port = 1299
        connected = False
        while not connected:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect((host, port))
                connected = True
                print("Coneccion Exitosa")
            except Exception as e:
                print(e)
                print("error")
                connected = False
            finally:
                s.close()



class WaitingRoom(tornado.web.RequestHandler):
    executor = ThreadPoolExecutor(max_workers=MAX_WORKERS)

    """
    In below function goes your time consuming task
    """

    @run_on_executor
    def getDB(self):
        mongo_client_Server = MongoClient('mongodb://127.0.0.1:27018')
        db_Server = mongo_client_Server["server"]
        col_Server = db_Server["person_serv"]

        return col_Server

    @tornado.gen.coroutine
    def get(self):
        """ Request that asynchronously calls background task. """
        col_Server = yield self.getDB()
        res = [{"name":doc["name"], "surname":doc["surname"],
                "idlist":doc["idlist"],
                "waiting_since":doc["waiting_since"].__str__()
                } for doc in col_Server.find({}) if doc["is_waiting_cam"] == True]
        sorted(res, key = lambda x: x["waiting_since"])
        self.write(json.dumps(sorted(res, key = lambda x: x["waiting_since"], reverse=True)))


app = tornado.web.Application(
    handlers=[(r"/DB", TestHandler),
            (r"/Number", TestHandler2),
            (r'/Solicitud', SolicitudHandler),
            (r'/Ingreso', IngresoHandler),
            (r'/Waitingroom', WaitingRoom),
            (r'/Exito', ExitoHandler)
            ],
            template_path="./Templates/"
            )

http_server = tornado.httpserver.HTTPServer(app)
http_server.listen(8000, address="192.168.0.248")
IOLoop.instance().start()
