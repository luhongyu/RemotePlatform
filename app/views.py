# coding=utf-8
import time
from flask import render_template, request, redirect
from app import app
from flask.helpers import send_from_directory

from algorithm import *


def __init_log(student_id):
    """
        initialize log by student_id
    """
    Log[student_id] = {}
    Log[student_id]['studentID'] = student_id
    Log[student_id]['timestamp'] = []
    Log[student_id]['Gaze'] = {}


def log_time(student_id):
    """
        log current_time to student_id
    """
    tmpTime = time.strftime(timeFormat, time.localtime())
    Log[student_id]['timestamp'].append(tmpTime)


def log_gaze(student_id, nowpage, np_param, lastpage, gazedata):
    """
        initialize log for nowpage, fill gaze data into lastpage's log
    """
    if lastpage:
        assert lastpage in Log[student_id]['Gaze']
        Log[student_id]['Gaze'][lastpage]['gazelist'] = gazedata

    if nowpage:
        Log[student_id]['Gaze'][nowpage] = {"param": np_param, "gazedata": {}}


@app.route('/')
def origin():
    """
    登录页面(origin) -> 眼动校准页面（cam_cal）
    """
    return render_template('start_page.html')


@app.route('/cam_cal', methods=['POST'])
def cam_cal():
    """
    登录页面(start_page) -> *摄像头校准页面(cam_cal) -> 眼动校准页面(gaze_cal)
    """
    # -------------- start_page --------------- #

    student_id = request.form['text_square']
    __init_log(student_id)

    Log[student_id]['shopping_intent'] = request.form['options3']
    Log[student_id]['description'] = request.form['text_square']

    # -------------- cam_calibration --------------- #
    log_time(student_id)  # 1
    return render_template('cam_calibration.html', student_id=student_id)


@app.route('/gaze_cal', methods=['POST'])
def gaze_cal():
    """
    摄像头校准页面(cam_cal) -> *眼动校准页面(gaze_cal) -> 采集评分页面（welcome）
    """
    student_id = request.form['student_id']
    log_time(student_id)  # 2
    return render_template('gaze_calibration.html', student_id=student_id)


@app.route('/welcome', methods=['POST'])
def user_rating():
    """
    眼动校准页面（gaze_cal）-> *商品评分页面1 -> 商品评分收集页面2
    """
    student_id = request.form['student_id']
    log_time(student_id)  # 3

    Log[student_id]['user_rating_list'] = {}

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

    log_gaze(student_id, "user_rating_1", {"match": match, "student_id": student_id}, None, None)
    return render_template('user_rating_1.html', match=match, student_id=student_id)


@app.route('/second rating', methods=['POST'])
def second_rating():
    """
    商品评分收集页面1 -> *商品评分收集页面2 -> 列表评分页面(list_rating)
    """
    student_id = request.form['student_id']
    log_time(student_id)  # 4

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

    log_gaze(student_id, "user_rating_2", {"match": match, "student_id": student_id}, "user_rating_1",
             request.form['gazedata'])
    return render_template('user_rating_2.html', match=match, student_id=student_id)


@app.route('/list rating', methods=['POST'])
def list_rating():
    """
    商品评分收集页面2 -> *推荐列表评分 -> 推荐列表多样性评分
    """

    student_id = request.form['student_id']
    log_time(student_id)  # 5

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
        Log[student_id]['match'][i]['list_id'] = i + 1

    log_gaze(student_id, "recommendations", {"match": Log[student_id]['match'], "student_id": student_id},
             "user_rating_2",
             request.form['gazedata'])

    return render_template('recommendations.html', match=Log[student_id]['match'], student_id=student_id)


@app.route('/list diversity', methods=['POST'])
def list_diversity():
    """
    推荐列表评分 -> *推荐列表多样性评分 -> 商品喜好标注页面
    """
    student_id = request.form['student_id']
    log_time(student_id)  # 6

    Log[student_id]['BPRMF_rating'] = request.form['BPRMF']
    Log[student_id]['UserKNN_rating'] = request.form['UserKNN']
    Log[student_id]['ItemKNN_rating'] = request.form['ItemKNN']
    Log[student_id]['AdaBPR_rating'] = request.form['AdaBPR']
    Log[student_id]['Borda_rating'] = request.form['Borda']
    Log[student_id]['Random_rating'] = request.form['Random']
    Log[student_id]['ItemKNN_pro_rating'] = request.form['ItemKNN_pro']

    log_gaze(student_id, "diversity", {"match": Log[student_id]['match'], "student_id": student_id}, "recommendations",
             request.form['gazedata'])
    return render_template('diversity.html', match=Log[student_id]['match'], student_id=student_id)


@app.route('/user click', methods=['POST'])
def user_click():
    """
    推荐列表多样性评分 -> *商品喜好标注页面 -> 列表选择页面
    """
    student_id = request.form['student_id']
    log_time(student_id)  # 7

    Log[student_id]['BPRMF_diversity'] = request.form['BPRMF']
    Log[student_id]['UserKNN_diversity'] = request.form['UserKNN']
    Log[student_id]['ItemKNN_diversity'] = request.form['ItemKNN']
    Log[student_id]['AdaBPR_diversity'] = request.form['AdaBPR']
    Log[student_id]['Borda_diversity'] = request.form['Borda']
    Log[student_id]['Random_diversity'] = request.form['Random']
    Log[student_id]['ItemKNN_pro_diversity'] = request.form['ItemKNN_pro']

    log_gaze(student_id, "user_click", {"match": Log[student_id]['match'], "student_id": student_id}, "diversity",
             request.form['gazedata'])

    return render_template('user_click.html', match=Log[student_id]['match'], student_id=student_id)


@app.route('/like dislike', methods=['POST'])
def list_select():
    student_id = request.form['student_id']
    log_time(student_id)  # 8

    methods = ['BPRMF', 'UserKNN', 'ItemKNN', 'AdaBPR', 'Borda', 'Random', 'ItemKNN_pro']
    for each_method in methods:
        for each in Log[student_id][each_method]:
            Log[student_id][each_method + each['itemID']] = request.form[each_method + each['itemID']]

    log_gaze(student_id, None, None, "user_click", request.form['gazedata'])

    return render_template('list_select.html', match=Log[student_id]['match'], student_id=student_id)


@app.route('/gender survey', methods=['POST'])
def gender_survey():
    student_id = request.form['student_id']
    print student_id
    log_time(student_id)  # 9

    Log[student_id]['Mostdiverse'] = request.form['options1']
    Log[student_id]['Leastdiverse'] = request.form['options2']
    print Log[student_id]['Mostdiverse'], Log[student_id]['Leastdiverse']
    return render_template('gender_survey.html', student_id=student_id)


@app.route('/finish', methods=['POST'])
def final():
    student_id = request.form['student_id']
    log_time(student_id)  # 10

    try:
        Log[student_id]['gender'] = request.form['options1']
        Log[student_id]['shopping_time'] = request.form['options2']
        # Log[student_id]['shopping_intent_re'] = request.form['options3']
        # Log[student_id]['description'] = request.form['text_square']
        print Log[student_id]['gender'], Log[student_id]['shopping_time'], Log[student_id]['studentID']
        log_data.insert(Log[student_id])
        del Log[student_id]
    except:
        pass
    return render_template('final.html', image={
        "url": "https://ss1.bdstatic.com/70cFvXSh_Q1YnxGkpoWK1HF6hhy/it/u=586527107,661330562&fm=23&gp=0.jpg"})
