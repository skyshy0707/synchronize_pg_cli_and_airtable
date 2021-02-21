# -*- coding: utf-8 -*-
"""
Created on Sat Feb 20 00:06:17 2021

@author: SKY_SHY
"""


import configparser
config = configparser.ConfigParser()
config.read("config.ini") 

username = config["pgs_db"]["USERNAME"]
password = config["pgs_db"]["PASSWORD"]
db_name = config["pgs_db"]["NAME"]  
port = config["pgs_db"]["PORT"] 
airtable_baseid = config["airtable_db"]["AIRTABLE_BASEID"] 
api_key = config["airtable_db"]["API_KEY"]




    
import argparse


def is_key_api(key_api):
    if key_api.startswith("key"):
        return key_api
    raise argparse.ArgumentTypeError("Неверный формат api_key\n"\
                                     "api_key следует задать в след. формате: "\
                                         "keyXXXXXXXXXXXXXX")
    

def is_baseid(baseid):
    if baseid.startswith("app"):
        return baseid
    raise argparse.ArgumentTypeError("Неверный формат baseid\n"\
                                     "baseid следует задать в след. формате: "\
                                         "appXXXXXXXXXXXXXX"
                                         )

parser = argparse.ArgumentParser(description = 'sync_airtable', 
                                 formatter_class=argparse.RawTextHelpFormatter)


parser.add_argument("--username", help="имя пользователя", default=username)
parser.add_argument("--password", help="пароль", default=password)
parser.add_argument("--port", help="порт", default=port)
parser.add_argument("--dbname", help="база данных", default=db_name)
parser.add_argument("--baseid", type=is_baseid, help="BaseId airtable", 
                    default=airtable_baseid
                    )
parser.add_argument("--api_key", type=is_key_api, help="api_key", 
                    default=api_key
                    )


args = parser.parse_args()


username = args.username
password = args.password
db_name = args.dbname
port = args.port
airtable_baseid = args.baseid   
api_key = args.api_key