# -*- coding:utf-8 -*-
import math
import random
from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017')
products = client.test.products_xs
log_data = client.test.log_2
images = client.test.image

image_id_list = [t['_id'] for t in images.find()]
id_list = [t['itemID'] for t in products.find()]


def Random():
    rec_list = []
    for item_id in random.sample(id_list, 6):
        rec_list.append(products.find_one({'itemID': item_id}))
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
