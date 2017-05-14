# coding=utf-8
import time
from flask import render_template, request
from app import app
import pandas as pd

from algorithm import *
import json

DEBUG = True
Log = {}


def __init_log(student_id):
    """
        initialize log by student_id
    """
    Log[student_id] = {}
    Log[student_id]['studentID'] = student_id
    Log[student_id]['timestamps'] = {}
    Log[student_id]['Gaze'] = {}
    Log[student_id]['click'] = {}
    Log[student_id]['user_info'] = {}


def log_time(student_id, pagebegin):
    """
        log current_time to student_id
    """
    Log[student_id]['timestamps'][pagebegin] = time.time()


def log_gaze(student_id, nowpage, np_param, lastpage, gazedata):
    """
        initialize log for nowpage, fill gaze data into lastpage's log
    """
    if lastpage:
        assert lastpage in Log[student_id]['Gaze']
        Log[student_id]['Gaze'][lastpage]['gazedata'] = json.loads(gazedata)

    if nowpage:
        Log[student_id]['Gaze'][nowpage] = {"param": np_param, "gazedata": {}}


def log_click(student_id, lastpage, clickdata):
    if clickdata:
        Log[student_id]["click"][lastpage] = json.loads(clickdata)
    else:
        Log[student_id]["click"][lastpage] = []


@app.route('/')
def origin():
    """
    登录页面(origin) -> 眼动校准页面（cam_cal）
    """
    if DEBUG:
        return render_template("00_start_page.html")
    return render_template('01_start_page.html')


@app.route('/cam_cal', methods=['POST'])
def cam_cal():
    """
    登录页面(start_page) -> *摄像头校准页面(cam_cal) -> 眼动校准页面(gaze_cal)
    """
    # -------------- start_page --------------- #

    student_id = request.form['student_id']
    __init_log(student_id)

    Log[student_id]['user_info']['shopping_intent'] = request.form['shopping_intent']
    if Log[student_id]['user_info']['shopping_intent'] == "4":
        Log[student_id]['user_info']['reason'] = request.form['reason']
    else:
        Log[student_id]['user_info']['reason'] = ""

    log_time(student_id, "cam_cal")  # 1
    return render_template('02_cam_calibration.html', student_id=student_id)


@app.route('/gaze_cal', methods=['POST'])
def gaze_cal():
    """
    摄像头校准页面(cam_cal) -> *眼动校准页面(gaze_cal) -> 采集评分页面（welcome）
    """
    student_id = request.form['student_id']
    log_time(student_id, "gaze_cal")  # 2
    return render_template('03_gaze_calibration.html', student_id=student_id)


# -------------------------- 采集眼动信息 --------------------------- #
@app.route('/welcome', methods=['POST'])
def user_rating():
    """
    眼动校准页面（gaze_cal）-> *商品评分页面1 -> 商品评分收集页面2
    """
    student_id = request.form['student_id']
    if DEBUG:
        __init_log(student_id)

    Log[student_id]['Temp_ids'] = random.sample(id_list, 20)
    Log[student_id]['user_rating_list'] = dict([(tid, 0) for tid in Log[student_id]['Temp_ids']])

    match = [[products.find_one({'itemID': tid}) for tid in Log[student_id]['Temp_ids'][:5]],
             [products.find_one({'itemID': tid}) for tid in Log[student_id]['Temp_ids'][5:10]]]

    log_gaze(student_id, "user_rating_1", {"match": match, "student_id": student_id}, None, None)

    log_time(student_id, "user_rating_1")  # 3
    return render_template('04_user_rating_1.html', basehtml="GAZE_MODULE_Tobii.html", match=match,
                           student_id=student_id)


@app.route('/second rating', methods=['POST'])
def second_rating():
    """
    商品评分收集页面1 -> *商品评分收集页面2 -> 列表评分页面(list_rating)
    """
    student_id = request.form['student_id']
    log_click(student_id, "user_rating_1", request.form['clickdata'])

    for item_id in Log[student_id]['user_rating_list'].keys():
        try:
            r = request.form[item_id]
            Log[student_id]['user_rating_list'][item_id] = int(r)
        except:
            pass

    match = [[products.find_one({'itemID': tid}) for tid in Log[student_id]['Temp_ids'][10:15]],
             [products.find_one({'itemID': tid}) for tid in Log[student_id]['Temp_ids'][15:20]]]

    del Log[student_id]['Temp_ids']

    log_gaze(student_id, "user_rating_2", {"match": match, "student_id": student_id}, "user_rating_1",
             request.form['gazedata'])

    log_time(student_id, "user_rating_2")  # 4
    return render_template('05_user_rating_2.html', basehtml="GAZE_MODULE_Tobii.html", match=match,
                           student_id=student_id)


@app.route('/list rating', methods=['POST', 'GET'])
def list_rating():
    """
    商品评分收集页面2 -> *推荐列表评分 -> 推荐列表多样性评分
    """

    student_id = request.form['student_id']
    log_click(student_id, "user_rating_2", request.form['clickdata'])

    for item_id in Log[student_id]['user_rating_list'].keys():
        try:
            r = request.form[item_id]
            Log[student_id]['user_rating_list'][item_id] = int(r)
        except:
            pass

    Log[student_id]['BPRMF'] = {"items": BPRMF(Log[student_id]['user_rating_list'])}
    Log[student_id]['UserKNN'] = {"items": UserKNN(Log[student_id]['user_rating_list'])}
    Log[student_id]['ItemKNN'] = {"items": ItemKNN(Log[student_id]['user_rating_list'])}
    Log[student_id]['AdaBPR'] = {"items": AdaBPR(Log[student_id]['user_rating_list'])}
    Log[student_id]['Borda'] = {"items": Borda(Log[student_id]['user_rating_list'])}
    Log[student_id]['Random'] = {"items": Random()}
    Log[student_id]['ItemKNN_pro'] = {"items": ItemKNN_pro(Log[student_id]['ItemKNN'], Log[student_id]['AdaBPR'])}

    Log[student_id]['rec_lists'] = [
        {'rec_method': 'BPRMF', 'list': Log[student_id]['BPRMF']['items']},
        {'rec_method': 'UserKNN', 'list': Log[student_id]['UserKNN']['items']},
        {'rec_method': 'ItemKNN', 'list': Log[student_id]['ItemKNN']['items']},
        {'rec_method': 'AdaBPR', 'list': Log[student_id]['AdaBPR']['items']},
        {'rec_method': 'Borda', 'list': Log[student_id]['Borda']['items']},
        {'rec_method': 'Random', 'list': Log[student_id]['Random']['items']},
        {'rec_method': 'ItemKNN_pro', 'list': Log[student_id]['ItemKNN_pro']['items']}
    ]
    random.shuffle(Log[student_id]['rec_lists'])

    for i in range(7):
        Log[student_id]['rec_lists'][i]['list_id'] = i + 1

    log_gaze(student_id, "recommendations", {"match": Log[student_id]['rec_lists'], "student_id": student_id},
             "user_rating_2", request.form['gazedata'])

    log_time(student_id, "recommendations")  # 5
    return render_template('06_recommendations.html', basehtml="GAZE_MODULE.html",
                           match=Log[student_id]['rec_lists'],
                           student_id=student_id)


@app.route('/list diversity', methods=['POST'])
def list_diversity():
    """
    推荐列表评分 -> *推荐列表多样性评分 -> 商品喜好标注页面
    """
    student_id = request.form['student_id']
    log_click(student_id, "recommendations", request.form['clickdata'])

    Log[student_id]['BPRMF']['rating'] = request.form['BPRMF']
    Log[student_id]['UserKNN']['rating'] = request.form['UserKNN']
    Log[student_id]['ItemKNN']['rating'] = request.form['ItemKNN']
    Log[student_id]['AdaBPR']['rating'] = request.form['AdaBPR']
    Log[student_id]['Borda']['rating'] = request.form['Borda']
    Log[student_id]['Random']['rating'] = request.form['Random']
    Log[student_id]['ItemKNN_pro']['rating'] = request.form['ItemKNN_pro']

    log_gaze(student_id, "diversity", {"match": Log[student_id]['rec_lists'], "student_id": student_id},
             "recommendations",
             request.form['gazedata'])

    log_time(student_id, "diversity")  # 6
    return render_template('07_diversity.html', basehtml="GAZE_MODULE_Tobii.html", match=Log[student_id]['rec_lists'],
                           student_id=student_id)


@app.route('/user click', methods=['POST'])
def user_click():
    """
    推荐列表多样性评分 -> *商品喜好标注页面 -> 列表选择页面
    """
    student_id = request.form['student_id']
    log_click(student_id, "diversity", request.form['clickdata'])

    Log[student_id]['BPRMF']['diversity'] = request.form['BPRMF']
    Log[student_id]['UserKNN']['diversity'] = request.form['UserKNN']
    Log[student_id]['ItemKNN']['diversity'] = request.form['ItemKNN']
    Log[student_id]['AdaBPR']['diversity'] = request.form['AdaBPR']
    Log[student_id]['Borda']['diversity'] = request.form['Borda']
    Log[student_id]['Random']['diversity'] = request.form['Random']
    Log[student_id]['ItemKNN_pro']['diversity'] = request.form['ItemKNN_pro']

    log_gaze(student_id, "user_click", {"match": Log[student_id]['rec_lists'], "student_id": student_id}, "diversity",
             request.form['gazedata'])

    log_time(student_id, "user_click")  # 7
    return render_template('08_user_click.html', basehtml="GAZE_MODULE_Tobii.html", match=Log[student_id]['rec_lists'],
                           student_id=student_id)


# -------------------------------- 停止采集 ------------------------------ #
@app.route('/like dislike', methods=['POST'])
def list_select():
    student_id = request.form['student_id']
    log_click(student_id, "user_click", request.form['clickdata'])

    methods = ['BPRMF', 'UserKNN', 'ItemKNN', 'AdaBPR', 'Borda', 'Random', 'ItemKNN_pro']
    for each_method in methods:
        Log[student_id][each_method]["likes"] = {}
        for each in Log[student_id][each_method]['items']:
            Log[student_id][each_method]["likes"][each['itemID']] = request.form[each_method + each['itemID']]

    log_gaze(student_id, None, None, "user_click", request.form['gazedata'])

    log_time(student_id, "list_select")  # 8
    return render_template('09_list_select.html', match=Log[student_id]['rec_lists'], student_id=student_id)


@app.route('/gender survey', methods=['POST'])
def gender_survey():
    student_id = request.form['student_id']

    Log[student_id]["verification"] = {}
    Log[student_id]["verification"]['Mostdiverse'] = request.form['options1']
    Log[student_id]["verification"]['Leastdiverse'] = request.form['options2']

    log_time(student_id, "gender_survey")  # 9
    return render_template('10_gender_survey.html', student_id=student_id)


@app.route('/finish', methods=['POST'])
def final():
    student_id = request.form['student_id']
    log_time(student_id, "final")  # 10

    Log[student_id]['user_info']['gender'] = request.form['options1']
    Log[student_id]['user_info']['shopping_time'] = request.form['options2']

    print "------------ Finish Notification ------------ "
    print "StudentID: ", Log[student_id]['studentID']
    print "Gender:    ", Log[student_id]['user_info']['gender']
    print "Number:    ", log_data.find().count()

    log_data.insert(Log[student_id])
    del Log[student_id]

    return render_template('11_final.html', image={
        "url": "https://ss1.bdstatic.com/70cFvXSh_Q1YnxGkpoWK1HF6hhy/it/u=586527107,661330562&fm=23&gp=0.jpg"})


@app.route("/show_gaze", methods=['POST', 'GET'])
def show_gaze():
    return render_template("12_show_gaze.html")


@app.route("/show_gaze_page", methods=['POST', 'GET'])
def show_gaze_page():
    student_id = request.form['student_id']
    page = request.form['page']
    mode = request.form['mode']
    tlog = log_data.find({"studentID": student_id})
    if tlog:
        tlog = tlog[0]
    else:
        print "error! can't find studentID"

    param = tlog['Gaze'][page]['param']
    gaze_data = tlog['Gaze'][page]['gazedata']

    scale_width = float(gaze_data['pagesize']['width'])
    scale_height = float(gaze_data['pagesize']['height'])

    print mode
    gaze_list = []
    if mode == "tobii":
        def getscroll(t_time):
            last_scroll = (0, 0)
            for trec in gaze_data['scrollrecs']:
                if t_time >= trec['timestamp']:
                    last_scroll = (trec['scrollTop'], trec['scrollLeft'])
                    continue
                else:
                    break
            return last_scroll[0], last_scroll[1]

        df_fixation = pd.read_pickle("tobii_0507_fixation.pkl")

        mintime, maxtime = gaze_data['gazelist'][0]['time'], gaze_data['gazelist'][-1]['time']

        offset_top = gaze_data['windowrange']['offsettop']
        offset_left = gaze_data['windowrange']['offsetleft']

        for screenx, screeny, timestamp in zip(df_fixation['screen_x'], df_fixation['screen_y'],
                                               df_fixation['timestamp']):
            if mintime <= timestamp <= maxtime:
                scrolltop, scrollleft = getscroll(timestamp)
                x = screenx - offset_left + scrollleft
                y = screeny - offset_top + scrolltop
                gaze_list.append({"x": x / scale_width, "y": y / scale_height, "value": 1})

    else:

        offset_top = gaze_data['pagesize']['offsetTop']
        offset_left = gaze_data['pagesize']['offsetLeft']

        gaze_list = [
            {"x": (tg['px'] - offset_left) / scale_width, "y": (tg['py'] - offset_top) / scale_height, "value": 1}
            for tg in gaze_data['gazelist']]

    print gaze_list
    page_dic = {
        'user_rating_1': "04_user_rating_1.html",
        'user_rating_2': "05_user_rating_2.html",
        'recommendations': "06_recommendations.html",
        'diversity': "07_diversity.html",
        'user_click': "08_user_click.html"
    }
    return render_template(page_dic[page], basehtml="HEATMAP_MODULE.html", gazelist=gaze_list, match=param['match'],
                           student_id=param['student_id'])
