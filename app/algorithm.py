# -*- coding:utf-8 -*-
import time
import math
import random
from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017')
products = client.test.products_xs
log_data = client.test.log_2
images = client.test.image
image_id_list = []
for each in images.find():
    image_id_list.append(each['_id'])

id_list = []
for each in products.find():
    id_list.append(each['itemID'])
print len(id_list)
Log = {}
timeFormat = '%Y-%m-%d %X'


def Random():
    rec_list = []
    random.shuffle(id_list)
    for i in range(6):
        rec_list.append(products.find_one({'itemID': id_list[i]}))
    return rec_list


def BPRMF(user_rating_list):
    return Random()


def UserKNN(user_rating_list):
    return Random()


def ItemKNN(user_rating_list):
    return Random()


def ItemKNN_pro(ori_list, add_list):
    return Random()


def AdaBPR(user_rating_list):
    return Random()


def Borda(user_rating_list):
    return Random()