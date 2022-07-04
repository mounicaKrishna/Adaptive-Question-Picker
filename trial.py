
from datetime import datetime
import json
from flask import Flask,jsonify, request
from bson import json_util


app = Flask(__name__)

#Create student
@app.route('/insert-one/<name>/<id>', methods=['POST'])
def create_user(name, id,Database):
    x=Database.SampleTable.insert_one({
        "Name": name,
        "ID": id
    });
    serailized_json = json.dumps(x)    
    # query = SampleTable.insert_one(serailized_json)
    return jsonify("SUCCESSFULLY CREATED")

#Read student
@app.route('/find', methods=['GET'])
def read_user(Database):
    cursor = [obj for obj in Database.SampleTable.find()]
    # print(cursor)
    new_dict = {item['Name']:item for item in cursor}
    # print(new_dict)
    # print(type(new_dict))
    return json.loads(json_util.dumps(new_dict))

#Update student
@app.route('/update', methods=['POST'])
def update_user(Database):
    input_json = request.get_json(force=True)
    input_Name = input_json["Name"]
    input_ID = input_json["ID"]
    updated_db =Database.SampleTable.update_one({"ID": input_ID}, {"$set": {"Name": input_Name}}, upsert=False)
    print(updated_db)
    return jsonify({"status":"Updated successfully"})

#Delete student
@app.route('/delete', methods=['DELETE'])
def delete_user(Database):
    input_json = request.get_json(force=True)
    input_ID = input_json["ID"]
    print(type(input_ID))
    res = Database.SampleTable.delete_one({"ID": input_ID})
    print("res.deleted_count",res.deleted_count)
    return jsonify({"status":"deleted successfully"})

def get_questions_lists(Questions_doc, level):
    questions_list=[]
    if Questions_doc:
        for doc in Questions_doc.find():
            ele = doc["Questions"][level]
            for k in ele:
                sep_ques = {}
                sep_ques["question_id"] = k["question_id"]
                sep_ques["question_type"] = k["question_type"]
                sep_ques["question_data"] = k["question_data"]
                sep_ques["Options"] = k["Options"]
                sep_ques["Correct_ans"] = k["Correct_ans"]
                sep_ques["probable_ans"] = k["probable_ans"]
                sep_ques["question_diff_level"] = level
                questions_list.append(sep_ques)
    return(questions_list)

def get_question_list_algebra(algebra_doc, level):
    questions_list=[]
    for doc in algebra_doc.find():
        ele = doc["Questions"][level]
        # print("ele",ele)
        for k in ele:
            sep_ques = {}
            sep_ques["question_id"] = k["question_id"]
            sep_ques["question_type"] = k["question_type"]
            sep_ques["question_data"] = k["question_data"]
            sep_ques["Breakup_of_Main_question"] = k["Breakup_of_Main_question"]
            sep_ques["Correct_ans"] = k["Correct_ans"]
            sep_ques["probable_ans"] = k["probable_ans"]
            if "sub-question" in ele:
                sep_ques["sub_question"] = k["sub_question"]
            sep_ques["question_diff_level"] = level
            questions_list.append(sep_ques)
    return questions_list


def get_question_ele_to_display(question):
    display_dict = dict()
    display_dict["question"] = question["question_picked"]["question_data"]
    display_dict["options"] = question["question_picked"]["Options"]
    display_dict["question_type"] = question["question_picked"]["question_type"]
    return display_dict

def evaluate_answer(student_answer,correct_answers):
    if student_answer in correct_answers:
        ans_match = True
    else:
        ans_match = False
    return ans_match

def get_difficulty_level(total_points_scored):
    complete_status = False
    if total_points_scored <=10:
        difficulty_level = "Easy"
    elif total_points_scored >10 and total_points_scored <= 20:
        difficulty_level = "Medium"
    elif total_points_scored >20:
        difficulty_level = "Hard"
    if total_points_scored>=30:
        complete_status= True
    return difficulty_level,complete_status

def store_session_start_info(Student_id,Topic_id, session_id, Difficulty_level = "Easy"):
    session_start_dict = {}
    session_start_dict["session_id"] = session_id
    session_start_dict["user_id"] = Student_id
    session_start_dict["session_topic_id"] = Topic_id
    session_start_dict["session_type"] = "Progress section"
    session_start_dict["session_start_date_time"] =  datetime.now().strftime("%H:%M:%S")
    session_start_dict["session_student_entry_level"] = Difficulty_level
    return session_start_dict




    
