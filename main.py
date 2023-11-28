from flask import Flask, render_template, request, redirect, url_for
from flask_cors import CORS
import json, copy
import AddElectiveCourses as addcourses
app = Flask(__name__)
CORS(app)

user, courses, time = {}, [], {}

@app.route('/', methods=['GET'])
def home():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    global user
    # POST 請求用於表單繳交
    username = request.form['username']
    password = request.form['password']
    with open("student.json", encoding='utf-8') as f:
        user = json.load(f).get(username)

    if user and user['password'] == password:
        # 登入成功，重定向到用戶頁面
        return redirect(url_for('user_profile', username=username))
    else:
        # 登入失敗
        return "登录失败"

def createTimeTable():
    global time
    time = {
        "days": ["星期一", "星期二", "星期三", "星期四", "星期五"],
        "class":[]
    }
    minute = 10
    for i in range(8, 22):
        timestr = "{:02d}:{:02d}-{:02d}:{:02d}".format(i, minute, i + 1, (minute + 50) % 60)
        minute = (minute + 50) % 60
        if i == 17:
            minute += 30
        elif i == 18 or i == 20:
            minute += 5
        else:
            minute += 10

        row = {"time": timestr, "content": ["NULL" for _ in range(5)]}
        time["class"].append(row)
    return time
        
@app.route('/user/<username>')
def user_profile(username):
    global user, courses, time
    
    time = createTimeTable()
    # 個別用戶資料頁面
    with open("student.json", encoding='utf-8') as f:
        user = json.load(f).get(username)

    with open("Course.json", encoding='utf-8') as f:
        raw_courses = json.load(f)

    for class_ in user["classes"]:
        class_time = raw_courses[class_]["Time"]
        for i in range(class_time["Duration"]):
            time["class"][int(class_time["Class"]) - 1 + i]["content"][int(class_time["Week"]) - 1] = raw_courses[class_]

    courses = []
    copy_courses = copy.deepcopy(raw_courses)
    for course_key, course_val in copy_courses.items():
        course_val["Time"]["Week"] = time["days"][course_val["Time"]["Week"] - 1] 
        course_obj = {"id": course_key, "info": course_val, "check": course_key in user["classes"]}
        courses.append(course_obj)

    if user:
        return render_template('student.html', user=user, time=time, courses=courses)
    else:
        return '用户不存在', 404
    
@app.route('/add/<classid>', methods=['POST'])
async def addClass(classid):
    global user, time, courses

    # 增加 classid
    res = await addcourses.write_curriculum(user['id'], classid)
    if res[0]: 
        time = createTimeTable()
        # 個別用戶資料頁面
        with open("student.json", encoding='utf-8') as f:
            user = json.load(f).get(user['id'])

        with open("Course.json", encoding='utf-8') as f:
            raw_courses = json.load(f)

        for class_ in user["classes"]:
            class_time = raw_courses[class_]["Time"]
            for i in range(class_time["Duration"]):
                time["class"][int(class_time["Class"]) - 1 + i]["content"][int(class_time["Week"]) - 1] = raw_courses[class_]
        
        courses = []
        copy_courses = copy.deepcopy(raw_courses)
        for course_key, course_val in copy_courses.items():
            course_val["Time"]["Week"] = time["days"][course_val["Time"]["Week"] - 1] 
            course_obj = {"id": course_key, "info": course_val, "check": course_key in user["classes"]}
            courses.append(course_obj)
        
        return render_template('student.html', user=user, time=time, courses=courses)
    return res[1], 404

@app.route('/logout')
def logout():
    return redirect('/')

if __name__ == "__main__":
    app.run("0.0.0.0", port=5000)