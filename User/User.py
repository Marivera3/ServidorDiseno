import mongoengine as me
import datetime


class PersonRasp(me.Document):
    # Se replica al servidor

    idrasp              = me.StringField(unique=True, required=True) # propuesta por la BD
    created_at          = me.DateTimeField(default=datetime.datetime.utcnow)
    name                = me.StringField(max_length=255, default='')
    surname             = me.StringField(max_length=255, default='')
    last_in             = me.DateTimeField()
    last_out            = me.DateTimeField()
    is_recognized       = me.BooleanField(default=False)
    seralize_pic        = me.StringField() #
    picture             = me.StringField() # RGB picture in bytes(?)
    likelihood          = me.DecimalField()
    is_trained          = me.BooleanField(default=False)
    # mail_sent           = me.BooleanField(default=False)
    # mail_recieved       = me.BooleanField(default=False)
    # waiting_response    = me.BooleanField(default=False)




class PersonServ(me.Document):

    #idrasp              = me.StringField(unique=True, required=True)
    idlist              = me.ListField(default=[])
    name                = me.StringField(max_length=255, default='')
    surname             = me.StringField(max_length=255, default='')
    created_at          = me.DateTimeField(default=datetime.datetime.utcnow)
    last_update_at      = me.DateTimeField(default=datetime.datetime.utcnow)
    hist_mov            = me.ListField() # It is a list of tuples that has (in, out) mov
    is_recognized       = me.BooleanField(default=False)
    seralize_pic        = me.StringField() #
    picture             = me.StringField() # RGB picture in bytes(?)
    mail_sent           = me.BooleanField(default=False)
    mail_recieved       = me.BooleanField(default=False)
    waiting_response    = me.BooleanField(default=False)
    likelihood          = me.ListField()
    is_added            = me.BooleanField(default=False)
    is_waiting_cam      = me.BooleanField(default=False)
    waiting_since       = me.DateTimeField()
#
#
# class RegisteredUser(me.Document):
#
#     idrasps             = me.ListField() # list of idhrasp gave
#     name                = me.StringField(max_length=255, default='')
#     surname             = me.StringField(max_length=255, default='')
#     seralize_pic        = me.ListField() #
