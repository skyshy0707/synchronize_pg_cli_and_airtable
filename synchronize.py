# -*- coding: utf-8 -*-
"""
Created on Tue Feb 16 16:53:01 2021

@author: SKY_SHY
"""



import json
import requests


from variables import *



class Therapists_inCloud():
    
    def __init__(self,):
        self.headers = {'Authorization': 'Bearer {}'.format(api_key)}
        self.params = {"offset": 0, 
                       "filterByFormula":
                           "AND(NOT({Имя} = ''), " + 
                           "NOT({Фотография} = ''), " + 
                           "NOT({Методы} = ''))"
                           }
        self.therapists = []

    

    def set_params(self, rec_id):
        if rec_id:
            return {}
        return self.params
    
    
    def get_raw_data_fromPage(self, rec_id=''):
        return requests.get('https://api.airtable.com/v0/{}/Psychotherapists/{}'.\
                            format(
                                airtable_baseid, 
                                rec_id
                                ),
                            headers=self.headers,
                            params=self.set_params(rec_id),
                            )
            
    def get_json(self, raw_data):
        return json.loads(raw_data.text)
    
    
    def get_data(self,rec_id=''):
        raw_data = self.get_raw_data_fromPage(rec_id)
        return self.get_json(raw_data)
    
    
    def page_over(self,data_json):
        try:
            self.params.update({"offset": data_json["offset"]
                                }
                               )
        except KeyError:
            return True
    
    
    def get_raw_data(self,):
        
        while True:
            data_json = self.get_data()
            self.therapists.append(data_json)
            if self.page_over(data_json):
                break
        if 'error' in self.therapists[0]:
            raise KeyError("Неверная комбинация параметров REST API Airtable: "\
                           "BaseId={}, api_key={}".format(
                               airtable_baseid, 
                               api_key
                               )
                           )
            
            
responce_airtable = Therapists_inCloud()
responce_airtable.get_raw_data()
therapists = responce_airtable.therapists



from sqlalchemy import create_engine, Table, Column, Integer, String,\
    MetaData, Text, JSON, DateTime, Sequence, exc


class CreateNewDB():
    
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.engine = None
        self.conn = None
        
    
    def create_connection(self, db_name='postgres'):
        return create_engine('postgresql://{}:{}@localhost:{}/{}'.\
                             format(
                               self.username, 
                               self.password,
                               port,
                               db_name,
                               )
                            )
            
    def connect(self,):
        try:
            conn = self.engine.connect()
            conn.execute("COMMIT")
        except exc.OperationalError as e:
            pass
        else:
            return conn
        
    
    def set_default_connection(self,):
        self.engine = self.create_connection()
        self.conn = self.connect()
    
    def set_new_connection(self, db_name):
        self.engine = self.create_connection(db_name)
        self.conn = self.connect()


    def create_new_db(self, db_name):
        self.set_default_connection()
        try:
            self.conn.execute("CREATE DATABASE %s" % db_name)
            self.conn.execute("COMMIT")
        except exc.DatabaseError:
            pass
        except AttributeError:
            pass
            




class Therapist(object):
    def __init__(self, rec_id, photo, FIO, methods):
        self.rec_id = rec_id
        self.photo = photo
        self.FIO = FIO
        self.methods = methods
    
    def __repr__(self):
        return "<Therapist('%s', '%s', '%s', '%s')>" % (self.rec_id, 
                                                        self.photo, 
                                                        self.FIO, 
                                                        self.methods
                                                        )
    
class RWD_Therapists_Airtable(object):
    def __init__(self, received_data, date_run,):
        self.received_data = received_data
        self.date_run = date_run

    
    def __repr__(self):
        return "<RWD_Therapists_Airtable('%s', '%s')>" % (self.received_data, 
                                                          self.date_run, 
                                                          )
    
  
from sqlalchemy.orm import mapper, sessionmaker    
db = CreateNewDB(username, password)

db.create_new_db(db_name)
db.set_new_connection(db_name)

engine = db.engine
conn = db.conn
Session = sessionmaker(bind=engine)
session = Session()



metadata = MetaData()
therapists_tab = Table("therapist", metadata,
                       Column('rec_id', String, primary_key=True),
                       Column('photo', Text, nullable=False),
                       Column('FIO', String, nullable=False),
                       Column('methods', JSON, nullable=False),
                       )


rwd_therapists_airtable_tab = Table('rawdata', metadata,
                                Column('id', Integer, 
                                       Sequence('rawdata_id_seq'),
                                       primary_key=True,
                                       ),
                                Column('received_data', JSON, nullable=False),
                                Column('date_run', DateTime, nullable=False),
                                )


try:
    metadata.create_all(engine)
except exc.OperationalError:
    pass


mapper(Therapist, therapists_tab)
mapper(RWD_Therapists_Airtable, rwd_therapists_airtable_tab)

from datetime import datetime


class SaveData():
    
    
    def received_data(self,):
        received_data, date_run = (therapists, datetime.now())
        return RWD_Therapists_Airtable(received_data, date_run)
    
    def add_received_data(self,):
        session.add(self.received_data())


class Synchronize_pg_with_airtable():
    
    
    def __init__(self, therapists):
        self.pks_from_airtable = self.get_current_pks_from_airtable()
        
    
    def get_fields(self, rec):
        return (rec['id'], 
                rec['fields']['Фотография'][0]['url'], 
                rec['fields']['Имя'], 
                rec['fields']['Методы']
                )
    
    def create_therapist(self, rec):
        rec_id, photo, FIO, methods = self.get_fields(rec)
        return Therapist(rec_id, photo, FIO, methods)
    

    def get_rec_id_as_row(self, rec):
        return (self.create_therapist(rec).rec_id,)
        
    
    def get_current_pks_from_airtable(self,):
        ids = []
        for page in therapists:
            for rec in page['records']:#try to catch KeyError
                ids.append(self.get_rec_id_as_row(rec))
        return ids
    
        
    def deleting_rows_by_pk(self):
        return set(session.query(Therapist.rec_id).all()).\
            difference(set(self.pks_from_airtable))
    
    def del_rows(self,):
        for row in self.deleting_rows_by_pk():
            del_ = therapists_tab.delete().\
                where(therapists_tab.c.rec_id==row[0])
            conn.execute(del_)
        
    def updating_rows_by_pk(self):
        return set(session.query(Therapist.rec_id).all()).\
            intersection(set(self.pks_from_airtable))
            
    def upd_rows(self,):
        for row in self.updating_rows_by_pk():
            _, photo, FIO, methods = self.get_fields(
                self.get_raw_therapist(row[0])
                )
            upd = therapists_tab.update().\
                where(therapists_tab.c.rec_id==row[0]).\
                    values({"photo": photo, "FIO": FIO, "methods": methods})
            conn.execute(upd)
            
    
    def adding_rows(self,):
        return set(self.pks_from_airtable).\
            difference(set(session.query(Therapist.rec_id).all()))

    def get_raw_therapist(self, rec_id):
        return responce_airtable.get_data(rec_id)
    
    def add_rows(self,):
        for row in self.adding_rows():
            session.add(self.create_therapist(self.get_raw_therapist(row[0])))
            
         
    def synchronize(self,):
        try:
            self.del_rows()
            self.upd_rows()
            self.add_rows()
            session.commit()
            session.close()
            print("Синхронизация данных airtable\\{}\\Psychotherapists c"\
                  " {}.therapist прошла успешно".format(
                      airtable_baseid,
                      db_name,
                      )
                  )
        except exc.OperationalError:
            print("Неверная комбинация параметров подключения к postgres: "\
                  "username={}, password={}, port={}".format(
                      username, 
                      password, 
                      port
                      )
                  )

if __name__ == "__main__":
    saveData = SaveData()
    saveData.add_received_data()
    
    synchronize = Synchronize_pg_with_airtable(therapists)
    synchronize.synchronize()