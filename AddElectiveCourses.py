import json

#讀入Json檔案
def read_json_file(filename):
    data = {}
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        print("ERROR: 找不到 " + filename + " 檔案。")
        return None

def write_json_file(filename, new_data):
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(new_data, f, indent = 2)
        return True
    except FileNotFoundError:
        print("ERROR: 找不到 " + filename + " 檔案。")
        return FileNotFoundError
    except FileExistsError:
        print("ERROR: " + filename + " 檔案存在錯誤。")
        return FileExistsError

def search_course(course_id):
    course_info = read_json_file("course.json")
    if course_id in course_info:
        return course_info[course_id]
    else:
        return None

def write_curriculum(student_id, course_id):
    filename = "student.json"
    data = read_json_file(filename)
    course_info = read_json_file("course.json")

    try:
        # 確認剩餘人數
        if course_info[course_id]["Remaining"] == 0:
            return [False, "沒有剩餘名額"]

        wrong_msg = ""

        # 確認是否課程名稱重複
        if is_same_course(student_id, course_id):
            wrong_msg += "課程名稱不能重複, "

        # 確認學分與衝堂
        if is_over_credit(student_id, course_id):
            wrong_msg += "超過學分上限, "

        # 確認衝堂
        if (not verify(student_id, course_id)):
            wrong_msg += "衝堂, "
        
        if len(wrong_msg) > 0:
            return [False, wrong_msg[:-2]]
        
        data[student_id]["classes"]["normal"].append(course_id)
        data[student_id]['credit'] += course_info[course_id]["Credit"]
        course_info[course_id]["Remaining"] -= 1
        course_info[course_id]["Student List"].append(data[student_id]['name'])
        write_json_file("student.json", data)
        write_json_file("course.json", course_info)

    except FileNotFoundError:
        print("ERROR: " + filename +"檔案不存在")
    return [True]

# 核實是否衝堂
def verify(student_id, course_id):
    filename = "student.json"
    curriculum = read_json_file(filename)
    course_info = read_json_file("course.json")

    if curriculum is None:
        return False

    if course_id in course_info:
        course_time = course_info[course_id]["Time"]
    else:
        return False

    my_time = []
    for other_course_id in curriculum[student_id]["classes"]["normal"]:
        # Week, Class, Duration
        my_time.append(course_info[other_course_id]["Time"])
    
    for other_course_id in curriculum[student_id]["classes"]["required"]:
        # Week, Class, Duration
        my_time.append(course_info[other_course_id]["Time"])

    for time in my_time:
        if is_duplicate(course_time, time):
            return False

    return True

# 是否重複
def is_duplicate(course_time, my_time):
    if course_time["Week"] != my_time["Week"]: return False

    times = 0
    course_time_array = generate_value(course_time)
    my_time_arry = generate_value(my_time)
    
    for v1 in course_time_array:
        if v1 in my_time_arry:
            return True
    return False

# 是否課程名稱相同
def is_same_course(student_id, course_id):
    student_data = read_json_file("student.json")
    course_data = read_json_file("course.json")
    curriculum = student_data[student_id]['classes']['normal'] + student_data[student_id]['classes']['required']
    for index, id in enumerate(curriculum):
        curriculum[index] = course_data[id]["Name"]
    course_name = course_data[course_id]["Name"]
    if course_name in curriculum:
        return True
    else:
        return False

# 是否超過學分
def is_over_credit(student_id, course_id):
    student_data = read_json_file("student.json")
    course_data = read_json_file("course.json")
    student_credit = student_data[student_id]["credit"]
    course_credit = course_data[course_id]["Credit"]

    max_credit = 20
    if student_credit + course_credit > max_credit:
        return True
    else:
        return False

# 生成計算值
def generate_value(time):
    value = []
    min_ = time["Class"]
    max_ = min_ + time["Duration"]
    for i in range(min_, max_):
        value.append(i)
    return value

# testing only
if __name__ == '__main__':
    course = read_json_file("course.json")
    student_id = "F001"
    class_id = "B001"
    result = write_curriculum(student_id, class_id)
    if result:
        print("Success")
    else:
        print("Error")