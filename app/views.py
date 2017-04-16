import time
import math
import random
import json
from flask import render_template, request, redirect
from app import app
from pymongo import MongoClient
from flask.helpers import send_from_directory

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


@app.route('/')
def origin():
    return render_template('start_page.html')


@app.route('/welcome', methods=['POST'])
def user_rating():

    student_id = request.form['text_square']
    print student_id
    Log[student_id] = {}
    Log[student_id]['studentID'] = student_id

    Log[student_id]['shopping_intent'] = request.form['options3']
    Log[student_id]['description'] = request.form['text_square']

    tmpTime = time.strftime(timeFormat, time.localtime())

    Log[student_id]['user_rating_list'] = {}
    Log[student_id]['timestamp'] = [tmpTime]
    match = []
    tmp_list = []
    random.shuffle(id_list)
    keynum = 0
    for id in id_list:
        keynum += 1
        if keynum > 10:
            break
        tmp_list.append(products.find_one({'itemID': id}))
        Log[student_id]['user_rating_list'][id] = 0
        if keynum % 5 == 0:
            random.shuffle(tmp_list)
            match.append(tmp_list)
            tmp_list = []
    return render_template('user_rating_1.html', match=match, student_id=student_id)


@app.route('/second rating', methods=['POST'])
def second_rating():
    student_id = request.form['student_id']
    print student_id
    tmpTime = time.strftime(timeFormat, time.localtime())
    Log[student_id]['timestamp'].append(tmpTime)
    for item_id in Log[student_id]['user_rating_list'].keys():
        try:
            r = request.form[item_id]
            Log[student_id]['user_rating_list'][item_id] = int(r)
        except:
            pass
    match = []
    tmp_list = []
    random.shuffle(id_list)
    keynum = 0
    for id in id_list:
        keynum += 1
        if keynum > 10:
            break
        tmp_list.append(products.find_one({'itemID': id}))
        Log[student_id]['user_rating_list'][id] = 0
        if keynum % 5 == 0:
            random.shuffle(tmp_list)
            match.append(tmp_list)
            tmp_list = []
    return render_template('user_rating_2.html', match=match, student_id=student_id)


@app.route('/list rating', methods=['POST'])
def list_rating():
    student_id = request.form['student_id']
    print student_id
    tmpTime = time.strftime(timeFormat, time.localtime())
    Log[student_id]['timestamp'].append(tmpTime)
    for item_id in Log[student_id]['user_rating_list'].keys():
        try:
            r = request.form[item_id]
            Log[student_id]['user_rating_list'][item_id] = int(r)
        except:
            pass

    Log[student_id]['match'] = []
    Log[student_id]['BPRMF'] = BPRMF(Log[student_id]['user_rating_list'])
    Log[student_id]['UserKNN'] = UserKNN(Log[student_id]['user_rating_list'])
    Log[student_id]['ItemKNN'] = ItemKNN(Log[student_id]['user_rating_list'])
    Log[student_id]['AdaBPR'] = AdaBPR(Log[student_id]['user_rating_list'])
    Log[student_id]['Borda'] = Borda(Log[student_id]['user_rating_list'])
    Log[student_id]['Random'] = Random()
    Log[student_id]['ItemKNN_pro'] = ItemKNN_pro(Log[student_id]['ItemKNN'], Log[student_id]['AdaBPR'])
    Log[student_id]['match'].append({'rec_method': 'BPRMF', 'list': Log[student_id]['BPRMF']})
    Log[student_id]['match'].append({'rec_method': 'UserKNN', 'list': Log[student_id]['UserKNN']})
    Log[student_id]['match'].append({'rec_method': 'ItemKNN', 'list': Log[student_id]['ItemKNN']})
    Log[student_id]['match'].append({'rec_method': 'AdaBPR', 'list': Log[student_id]['AdaBPR']})
    Log[student_id]['match'].append({'rec_method': 'Borda', 'list': Log[student_id]['Borda']})
    Log[student_id]['match'].append({'rec_method': 'Random', 'list': Log[student_id]['Random']})
    Log[student_id]['match'].append({'rec_method': 'ItemKNN_pro', 'list': Log[student_id]['ItemKNN_pro']})
    random.shuffle(Log[student_id]['match'])

    for i in range(7):
        Log[student_id]['match'][i]['list_id'] = i+1
    return render_template('recommendations.html', match=Log[student_id]['match'], student_id=student_id)


@app.route('/list diversity', methods=['POST'])
def list_diversity():
    student_id = request.form['student_id']
    print student_id
    tmpTime = time.strftime(timeFormat, time.localtime())
    Log[student_id]['timestamp'].append(tmpTime)
    Log[student_id]['BPRMF_rating'] = request.form['BPRMF']
    Log[student_id]['UserKNN_rating'] = request.form['UserKNN']
    Log[student_id]['ItemKNN_rating'] = request.form['ItemKNN']
    Log[student_id]['AdaBPR_rating'] = request.form['AdaBPR']
    Log[student_id]['Borda_rating'] = request.form['Borda']
    Log[student_id]['Random_rating'] = request.form['Random']
    Log[student_id]['ItemKNN_pro_rating'] = request.form['ItemKNN_pro']
    return render_template('diversity.html', match=Log[student_id]['match'], student_id=student_id)


@app.route('/user click', methods=['POST'])
def user_click():
    student_id = request.form['student_id']
    print student_id
    tmpTime = time.strftime(timeFormat, time.localtime())
    Log[student_id]['timestamp'].append(tmpTime)
    Log[student_id]['BPRMF_diversity'] = request.form['BPRMF']
    Log[student_id]['UserKNN_diversity'] = request.form['UserKNN']
    Log[student_id]['ItemKNN_diversity'] = request.form['ItemKNN']
    Log[student_id]['AdaBPR_diversity'] = request.form['AdaBPR']
    Log[student_id]['Borda_diversity'] = request.form['Borda']
    Log[student_id]['Random_diversity'] = request.form['Random']
    Log[student_id]['ItemKNN_pro_diversity'] = request.form['ItemKNN_pro']
    return render_template('user_click.html', match=Log[student_id]['match'], student_id=student_id)


@app.route('/like dislike', methods=['POST'])
def list_select():
    student_id = request.form['student_id']
    print student_id
    tmpTime = time.strftime(timeFormat, time.localtime())
    Log[student_id]['timestamp'].append(tmpTime)
    methods = ['BPRMF', 'UserKNN', 'ItemKNN', 'AdaBPR', 'Borda', 'Random', 'ItemKNN_pro']
    for each_method in methods:
        for each in Log[student_id][each_method]:
            Log[student_id][each_method+each['itemID']] = request.form[each_method+each['itemID']]
    return render_template('list_select.html', match=Log[student_id]['match'], student_id=student_id)


@app.route('/gender survey', methods=['POST'])
def gender_survey():
    student_id = request.form['student_id']
    print student_id
    tmpTime = time.strftime(timeFormat, time.localtime())
    Log[student_id]['timestamp'].append(tmpTime)
    Log[student_id]['Mostdiverse'] = request.form['options1']
    Log[student_id]['Leastdiverse'] = request.form['options2']
    print Log[student_id]['Mostdiverse'], Log[student_id]['Leastdiverse']
    return render_template('gender_survey.html', student_id=student_id)


@app.route('/finish', methods=['POST'])
def final():
    student_id = request.form['student_id']
    print student_id
    random.shuffle(image_id_list)
    try:
        tmpTime = time.strftime(timeFormat, time.localtime())
        Log[student_id]['timestamp'].append(tmpTime)
        Log[student_id]['gender'] = request.form['options1']
        Log[student_id]['shopping_time'] = request.form['options2']
        # Log[student_id]['shopping_intent_re'] = request.form['options3']
        # Log[student_id]['description'] = request.form['text_square']
        print Log[student_id]['gender'], Log[student_id]['shopping_time'], Log[student_id]['studentID']
        log_data.insert(Log[student_id])
        del Log[student_id]
    except:
        pass
    return render_template('final.html', image=images.find_one({'_id': image_id_list[0]}))


