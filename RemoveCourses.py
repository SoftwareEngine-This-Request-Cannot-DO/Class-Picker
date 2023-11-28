import json

def read_json_file(filename):
    data = {}
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        print("ERROR: 找不到 " + filename + " 檔案。")
        return None

async def write_json_file(filename, new_data):
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

async def removeClass(student_id, course_id):
    students_data = read_json_file("student.json")
    course_data = read_json_file("course.json")

    # 確認必修
    if course_id in students_data[student_id]["classes"]["required"]:
        return [False, "不能退必修"]

    # 確認學分
    if students_data[student_id]["credit"] - course_data[course_id]["Credit"] < 10:
        return [False, "低於學分下限"]
    
    students_data[student_id]["credit"] -= course_data[course_id]["Credit"]
    students_data[student_id]["classes"]["normal"].remove(course_id)
    course_data[course_id]["Remaining"] += 1
    await write_json_file("student.json", students_data)
    await write_json_file("course.json", course_data)
    return [True]
    