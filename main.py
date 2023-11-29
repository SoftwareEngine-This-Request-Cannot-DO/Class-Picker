from flask import Flask, render_template, request, redirect, url_for
from flask_cors import CORS
import json, copy
import AddElectiveCourses as addCourses
import RemoveCourses as removeCourses
app = Flask(__name__)
CORS(app)

user, courses, time = {}, [], {}
islogin = [False, ""]

@app.route('/', methods=['GET'])
def home():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    global user
    # POST 請求用於表單繳交
    username = request.form['username']
    password = request.form['password']

    # 檢查帳號是否輸入
    if not username:
        return f"<script>alert('請輸入帳號');history.back();</script>"

    # 檢查密碼是否輸入
    if not password:
        return f"<script>alert('請輸入密碼');history.back();</script>"
    
    with open("student.json", encoding='utf-8') as f:
        user = json.load(f).get(username)
    
    # 檢查是否有此帳號
    if not user:
        return f"<script>alert('帳號錯誤');history.back();</script>"
    
    # 檢查密碼是否正確
    if user['password'] != password:
        return f"<script>alert('密碼錯誤');history.back();</script>"

    if user and user['password'] == password:
        # 登入成功，重定向到用戶頁面
        global islogin
        islogin = [True, username]
        return redirect(url_for('user_profile', username=username))
    else:
        # 登入失敗
        return f"<script>alert('登入失敗');history.back();</script>"

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
    global user, courses, time, islogin
    if not islogin[0] or islogin[1] != username:
        return f"<script>alert('你想幹麻，滾開');history.back();</script>"

    # 個別用戶資料頁面
    with open("student.json", encoding='utf-8') as f:
        user = json.load(f).get(username)

    with open("course.json", encoding='utf-8') as f:
        raw_courses = json.load(f)

    time = createTimeTable()
    # 身分為學生
    if user["role"] == 'Student':
        credits = 0
        for class_ in user["classes"]["normal"]:
            credits += raw_courses[class_]["Credit"]
            class_time = raw_courses[class_]["Time"]
            for i in range(class_time["Duration"]):
                time["class"][int(class_time["Class"]) - 1 + i]["content"][int(class_time["Week"]) - 1] = raw_courses[class_]
            
        for class_ in user["classes"]["required"]:
            credits += raw_courses[class_]["Credit"]
            class_time = raw_courses[class_]["Time"]
            for i in range(class_time["Duration"]):
                time["class"][int(class_time["Class"]) - 1 + i]["content"][int(class_time["Week"]) - 1] = raw_courses[class_]
        user["credit"] = credits

        courses = []
        copy_courses = copy.deepcopy(raw_courses)
        for course_key, course_val in copy_courses.items():
            course_val["Time"]["Week"] = time["days"][course_val["Time"]["Week"] - 1] 
            course_obj = {
                "id": course_key, 
                "info": course_val, 
                "check": course_key in user["classes"]["normal"] or course_key in user["classes"]["required"],
                "required": course_key in user["classes"]["required"]
            }
            courses.append(course_obj)
    
    # 該身分為教師
    if user['role'] == 'Teacher':
        courses = []
        for course_id in user['classes']:
            raw_courses[course_id]["Time"]["Week"] = time["days"][raw_courses[course_id]["Time"]["Week"] - 1] 
            course_obj = {
                "id": course_id,
                "info": raw_courses[course_id]
            }
            courses.append(course_obj)

    if user:
        if user['role'] == 'Student':
            return render_template('student.html', user=user, time=time, courses=courses)
        if user['role'] == 'Teacher':
            return render_template('teacher.html', user=user, courses=courses)
    else:
        return f"<script>alert('該用戶不存在');history.back();</script>"
    
@app.route('/add/<classid>', methods=['POST'])
def addClass(classid):
    global user
    res = addCourses.write_curriculum(user['id'], classid)
    if res[0]:         
        return redirect(url_for('user_profile', username=user['id']))
    return f"<script>alert('{res[1]}');history.back();</script>"

@app.route('/remove/<classid>', methods=['POST'])
def removeClass(classid):
    global user
    res = removeCourses.removeClass(user['id'], classid)
    if res[0]:
        return redirect(url_for('user_profile', username=user['id']))
    return f"<script>alert('{res[1]}');history.back();</script>"

@app.route('/details/<classid>', methods=['Post'])
def details(classid):
    with open("course.json", encoding='utf-8') as f:
        raw_courses = json.load(f)
    course = raw_courses[classid]
    class_ = {"user": user['id'], "name": course["Name"], "info": []}
    class_["info"].append({ "key": "課程 ID", "value": classid })
    class_["info"].append({ "key": "學分", "value": course["Credit"]})
    class_["info"].append({ "key": "上課時間", "value": time["days"][course["Time"]["Week"] - 1] + " 第" + str(course["Time"]["Class"]) + "-" + str(course["Time"]["Class"] + course["Time"]["Duration"] - 1) + "節"})
    class_["info"].append({ "key": "上課地點", "value": course["Place"]})
    class_["info"].append({ "key": "指導教師", "value": course["Teacher"]})
    class_["info"].append({ "key": "開辦系辦", "value": course["Depart"]})
    if user['role'] == 'Student':
        class_["info"].append({ "key": "剩餘名額 / 開放人數", "value": str(course["Remaining"]) + " / " + str(course["Total peopl"])})
    if user['role'] == 'Teacher':
        last = course["Total peopl"] - course["Remaining"] - len(course["Student List"])
        for i in range(last):
            course["Student List"].append(f"學生 {i + 1}")
        class_["info"].append({"key": "已加選人數 / 開放人數", "value": str(course["Total peopl"] - course["Remaining"]) + " / " + str(course["Total peopl"])})
        class_["info"].append({"key": "已加選學生名單", "value": course["Student List"]})

    class_["info"].append({ "key": "課程內容", "value": course["Content"]})
    return render_template("details.html", class_=class_)

@app.route('/previous_page/<username>', methods=['POST'])
def previous_page(username):
    return redirect(url_for('user_profile', username=username))


@app.route('/logout')
def logout():
    global islogin, user, courses, time
    islogin = [False, ""]
    user = {}
    courses = []
    time = {}
    return redirect('/')

if __name__ == "__main__":
    app.run("0.0.0.0", port=5000, debug=True)