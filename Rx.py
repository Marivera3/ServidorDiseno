class Rxmsg:


    def __init__(self, name=None, surname=None, mail=None, ID=None):

        self.name = name
        self.surname = surname
        self.mail = mail
        self.id = ID

    def readsubject(self, subj):
        self.id = subj.strip().split('-')[-1].strip().split(';')[1].split()[0]

    def readbody(self, body):
        # rx = body.strip().split(';')[0].strip('[').strip(']').split(',')

        rx = body.strip().split(';')[0].split('\n')
        # print(rx)
        for att in rx:
            attaux = att.strip().split(':')
            if attaux[0] == 'Nombre':
                self.name = attaux[1].strip("\r").split()[0]

            elif attaux[0] == 'Apellido':
                self.surname = attaux[1].strip("\r").split()[0]
            elif attaux[0] == 'Mail' or attaux[0] == 'mail':
                self.mail = attaux[1].strip("\r").split()[0]
                # print(self.mail)
            elif attaux[0] == 'ID':
                self.id = attaux[1].strip("\r").strip(".").split()[0]
