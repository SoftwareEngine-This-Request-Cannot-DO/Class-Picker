import pandas as pd
import json

#讀入Json檔案
def read_json_file(filename):
    data = {}
    try:
        with open(filename, 'r') as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        print("ERROR: 找不到 " + filename + " 檔案。")
        return None

def write_json_file(filename, new_data):
    try:
        with open(filename, 'w') as f:
            json.dump(new_data, f, indent = 2)
        return True
    except FileNotFoundError:
        print("ERROR: 找不到 " + filename + " 檔案。")
        return FileNotFoundError
    except FileExistsError:
        print("ERROR: " + filename + " 檔案存在錯誤。")
        return FileExistsError

def search_course(course_id):
    course_info = read_json_file("Course.json")
    if course_id in course_info:
        return course_info[course_id]
    else:
        return None

def write_curriculum(student_id, course_id):
    filename = student_id + ".json"

    try:
        if (verify(student_id, course_id) and not is_over_credit(student_id, course_id) and not is_same_course(student_id, course_id)):
            with open(filename, 'r') as f:
                data = json.load(f)

            new_key = len(data) + 1
            if new_key < 10:
                new_key = "0" + str(new_key)
            else:
                new_key = str(new_key)

            data[new_key] = {
                "Course_ID" : course_id
            }
            write_json_file(filename, data)
            return True
    except FileNotFoundError:
        print("ERROR: " + student_id +"檔案不存在")
        return False

def is_same_course(student_id, course_id):
    filename = student_id + ".json"
    curriculum = read_json_file(filename)

    curriculum_ = []
    for key, data in curriculum.items():
        curriculum_.append(data["Course_ID"])

    if course_id in curriculum_:
        return True
    else:
        return False
        

# 是否超過學分
def is_over_credit(student_id, course_id):
    filename = student_id + ".json"
    curriculum = read_json_file(filename)
    course_info = read_json_file("Course.json")
    course_credit = course_info[course_id]["Credit"]

    student_credit = 0
    for key, data in curriculum.items():
        temp = search_course(data["Course_ID"])
        credit = temp["Credit"]
        student_credit += credit

    max_credit = 10
    if student_credit + course_credit > max_credit:
        return True
    else:
        return False

# 核實是否衝堂
def verify(student_id, course_id):
    filename = student_id + ".json"
    curriculum = read_json_file(filename)
    course_info = read_json_file("Course.json")

    if curriculum is None:
        return False

    if course_id in course_info:
        course_time = course_info[course_id]["Time"]
    else:
        return False
    time1 = []
    for key, data in curriculum.items():
        arr = search_course(data["Course_ID"])
        if arr is None:
            return False
        time1.append(arr["Time"]["Week"])
        time1.append(arr["Time"]["Class"])
        time1.append(arr["Time"]["Duration"])

    time2 = []
    time2.append(course_time["Week"])
    time2.append(course_time["Class"])
    time2.append(course_time["Duration"])

    if time1[0] == time2[0]:
        if is_duplicate(time1, time2) == True:
            return False
        else:
            return True
    else:
        return True

# 是否重複
def is_duplicate(time1, time2):
    times = 0
    arr1 = generate_value(time1)
    arr2 = generate_value(time2)
    
    for v1 in arr1:
        if v1 in arr2:
            times += 1
    if times == 0:
        return False
    else:
        return True

# 生成計算值
def generate_value(arr):
    value = []
    min_ = arr[1]
    max_ = min_ + arr[2]
    for i in range(min_, max_):
        value.append(i)
    return value

# testing only
course = read_json_file("Course.json")
student_id = "F001"
class_id = "A003"
result = write_curriculum(student_id, class_id)
if result:
    print("Success")
else:
    print("Error")