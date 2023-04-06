from pony.orm import *
from datetime import datetime
import os
import numpy as np
db = Database()
db.bind(provider='sqlite', filename='data/database.sqlite', create_db=True)


class mydb(object):
    def __init__(self):
        pass

    @db_session
    def insertFeature(self, userid , feature):
        feature = Features(user=userid,features=feature)
        commit()
        return feature
    @db_session
    def getAllFeature(self):
        x=select(s for s in Features)
        mylist=[]
        for p in x:
            mylist.append(p)
        return mylist
    @db_session
    def deleteAllFeature(self):
        x=select(s for s in Features)
        for i in x:
            i.delete()
            commit()
        return True
    @db_session
    def getUserid(self, id):
        return Users.get(id=id)
    @db_session
    def getUser(self, username):
        return Users.get(username=username)
    @db_session
    def deleteUser(self,id):
        Users[id].delete()
        commit()
    @db_session
    def insertUser(self, username):
        user = Users.get(username=username)
        if (user == None):
            user = Users(username=username)
        commit()
        return user
    @db_session
    def insertAttendance(self, userid , name , cam ,datetime,direction):
        attend = Attendance(user=userid,name=name,cam=cam,datetime=datetime,direction=direction)
        commit()
        return attend
    @db_session
    def getAttendance(self,userid):  
        x=select(s for s in Attendance if s.user == userid)#Attendance.get(user=userid)
        mylist=[]
        for p in x:
            mylist.append(p)
        return mylist
    @db_session
    def getAllUsers(self):
        x=select(s for s in Users)
        mylist=[]
        for p in x:
            mylist.append(p)
        return mylist
    @db_session
    def getuserinout(self,userid,startdate,enddate):
        userins =select(s for s in Attendance if s.user==userid and s.direction=="IN" and s.datetime>=startdate and s.datetime <=enddate)
        userouts=select(s for s in Attendance if s.user==userid and s.direction=="OUT" and s.datetime>=startdate and s.datetime <=enddate)
        # print(userins)
        # print(userouts)
        mini=None
        c=0
        for p in userins:
            # print('p in user in ',p)
            if(c == 0):
                mini=p
                c=c+1
            else:
                if(p.datetime < mini.datetime):
                    mini=datetime
        # print('mini is ',mini)
        if mini == None:
            return None,None
        maxi = None
        c=0
        for p in userouts:
            # print('p in user out',p)
            if(c == 0):
                maxi=p
                c=c+1
            else:
                if(p.datetime > mini.datetime):
                    maxi = datetime
        return mini,maxi
        
    @db_session
    def getAllAttendance(self):
        x=select(s for s in Attendance)
        mylist=[]
        for p in x:
            mylist.append(p)
        return mylist
    @db_session
    def getattendancedt(self,starttime,endtime):
        x=select(s for s in Attendance if s.datetime >= starttime and s.datetime <= endtime)
        mylist=[]
        for p in x:
            mylist.append(p)
        return mylist
    

class Users(db.Entity):
    id = PrimaryKey(int, auto=True)
    username = Required(str)
class Attendance(db.Entity):
    id          = PrimaryKey(int,auto=True)
    user        = Required(int)
    name        = Required(str)
    direction   = Required(str)
    cam         = Required(str)
    datetime    = Required(datetime)
class Features(db.Entity):
    user = Required(int)
    features = Required(FloatArray)

def PurgeDatabase():
    db.drop_all_tables(with_all_data=True)
    db.create_tables()

db.generate_mapping(create_tables=True)
