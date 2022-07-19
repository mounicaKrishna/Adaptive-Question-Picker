from asyncio.windows_events import NULL
from xmlrpc.client import boolean
from flask import Flask, redirect, request, render_template,url_for
from flask import session 
import requests
import pymongo
from trial import store_session_start_info, evaluate_answer, get_difficulty_level,get_question_list_algebra
import random
import json
import time
import datetime
from basic import add_questions_from_excel_to_db,create_excel_final_json_structure
import pandas as pd
import glob
import math
import itertools

app = Flask(__name__)
app.secret_key = 'abc'

app.config["MONGO_DBNAME"] = 'dm-focus'
app.config["MONGO_URI"] = "mongodb+srv://elaimte:Hknudxnt143@focusedumatics.b3ue9.mongodb.net/test"

client = pymongo.MongoClient("mongodb+srv://elaimte:Hknudxnt143@focusedumatics.b3ue9.mongodb.net/test")

# Database
Database = client.get_database('Grade5_Q')
# Documents
Questions_doc = Database.Questions
session_doc = Database.session
algebra_doc = Database.algebra
# time_bonus = 0.5
# streak_bonus = 0.5

# getting excel files from Directory Desktop
# path =r"C:\Users\duvvuru.mounika\Desktop\Workspace\HS Algebra_excels_only"

# # read all the files with extension .xlsx i.e. excel 
# filenames = glob.glob(path + "\*.xlsx")

# final_json= create_excel_final_json_structure()
# for file in filenames:
#     # print("file",file)
#     df = pd.read_excel(file)
#     df.columns = df.columns.str.strip()
#     final_structure = add_questions_from_excel_to_db(df,final_json)
# algebra_doc.insert_one(final_structure)


#Question picker API
@app.route('/question_picker/<S_id>/<T_id>/<D_L>', methods=['POST'])
def question_picker(S_id, T_id, D_L):
    session_qp = request.get_json(force=True)
    question_list = get_question_list_algebra(algebra_doc, D_L)
    P_Q_ID = session_qp['P_Q_ID']
    # print("P_Q_ID",P_Q_ID)
    if P_Q_ID == NULL:
        random_question = random.choice(question_list)
        while random_question["question_id"] in session_qp['q_id_l']:
            # print("random question is in s_q_id")
            random_question = random.choice(question_list)
        session_qp['q_id_l'].append(random_question["question_id"])
        # print("R Q", random_question)
        return random_question
    
    else:
        diffiulty_level = session_qp['Difficulty_level']
        # print("P_Q_ID",P_Q_ID)
        #from that previous question get sub question array question ids
        total_doc = algebra_doc.find_one({"Topic_id":"MA_Algebra"})
        session_qp['q_id_l'].append(P_Q_ID)
        dicts_basedon_dl = total_doc["Questions"][diffiulty_level]
        for one_dictionary in dicts_basedon_dl:
            if one_dictionary["question_id"]==P_Q_ID:
                if 'sub-question' in one_dictionary:
                    s_q_array = one_dictionary['sub-question']
                    print("s_q_array",s_q_array)
                    # s_q_id_l = []
                    #Getting sub questions ids to iterate
                    for sub_question in s_q_array:
                        # s_q_id_l.append(sub_question['question_id'])
                        # for q_id in s_q_id_l: 
                        if sub_question['question_id'] in session_qp['q_id_l']:
                            continue
                        else:
                            session_qp['q_id_l'].append(sub_question['question_id'])
                            random_question= sub_question
                            print("random_question",random_question)
                            return random_question
                    session_qp['P_Q_ID']= NULL
                    random_question = random.choice(question_list)
                    while random_question["question_id"] in session_qp['q_id_l']:
                        random_question = random.choice(question_list)
                    session_qp['q_id_l'].append(random_question["question_id"])
                    return random_question
                else:
                    random_question = random.choice(question_list)
                    while random_question["question_id"] in session_qp['q_id_l']:
                        random_question = random.choice(question_list)
                    session_qp['q_id_l'].append(random_question["question_id"])
                    return random_question
        # return random_question
#Score API
@app.route('/score_api/<student_response>/<q_id>', methods=['POST'])
def score1_func(student_response,q_id):
    session1 = request.get_json(force=True)
    time_bonus=0.5
    streak_bonus=0.5
    response_start_time = time.time()
    response_end_time = time.time()
    response_time = str(response_end_time - response_start_time)
    # Evaluate the answer 
    correct_answers = ["A","a"]
    ans_match = evaluate_answer(student_response,correct_answers)
    print("ans match eval 13", ans_match)
    if session1['P_Q_ID'] == NULL:
        # Scoring
        if ans_match:
            print('ans match',ans_match)
            question_points = 2
            session_last_score_temp = session1['last_session_score']
            print("session_last_score_temp",session_last_score_temp)
            total_points_scored = session_last_score_temp + question_points + time_bonus + streak_bonus
            # print("total_points_scored",total_points_scored)
            result = "correct answer"
        else: 
            print('No ans match',ans_match)
            result = "wrong answer"
            question_points = -1
            time_bonus=0
            streak_bonus=0
            session_last_score_temp = session1['last_session_score']
            total_points_scored = session_last_score_temp + question_points
            print("The answer you have given is incorrect.. please try the next question")
    else:
        print("121 Executing sub questions ****")
        result = "Sub-question-answer"
        time_bonus=0
        streak_bonus=0
        question_points = 0
        session_last_score_temp = session1['last_session_score']
        total_points_scored = session_last_score_temp + question_points
    # level Changing based on total_points_scored
    Difficulty_level, complete_status = get_difficulty_level(total_points_scored)  
    response_dict = {}
    response_dict["session_questions_responses_data"] = dict()
    response_dict["session_questions_responses_data"]["question_Difficulty_level"] = session1['Difficulty_level']
    response_dict["session_questions_responses_data"]["Q_no"] = q_id
    response_dict["session_questions_responses_data"]["Response"] = student_response
    response_dict["session_questions_responses_data"]["Result"] = result
    response_dict["session_questions_responses_data"]["T_bonus"] = time_bonus
    response_dict["session_questions_responses_data"]["S_bonus"] = streak_bonus
    response_dict["session_questions_responses_data"]["Points_Scored"] = question_points
    response_dict["session_questions_responses_data"]["Response_Time"] = response_time
    response_dict["points_earned_total"] = total_points_scored  
    response_dict["complete_status"] = complete_status
    response_dict["Difficulty_level"] = Difficulty_level
    response_dict["ans_match"] = ans_match
    response_dict['session_last_score_temp']=session_last_score_temp
    # print("response_dict",response_dict)
    return response_dict

def session_func(score_api_resp):
    session_doc.update_one({'session_id':session['response']},{'$push':{'session_questions_responses_data':score_api_resp["session_questions_responses_data"]}},upsert=True)
    session_doc.update_one({'session_id':session['response']},{'$set':{'session_student_exit_level':score_api_resp["session_questions_responses_data"]["question_Difficulty_level"],'session_final_score':score_api_resp["points_earned_total"] ,'session_topic_complete':score_api_resp["complete_status"]}})

@app.route('/topic_list', methods=['GET'])
def all_topic_list():
    for doc in Questions_doc.find():
        all_topic_names = doc["topic_name"]
    return render_template('home.html',topic_list= all_topic_names, S_id="1")

@app.route('/close/<session_id>')
def end_time(session_id):
    final_op = session_doc.update_one({'session_id':session_id}, {'$set':{'session_end_date_time':str(datetime.datetime.now())}})
    session.pop('response')
    return 'close'
  
def is_main_question(id):
    main_q = False
    try:
        id.split('_')[1]
    except IndexError:
        main_q = True
    return main_q

@app.route('/<Student_id>/<Topic_id>', methods=['GET','POST'])
def student_session(Student_id,Topic_id):
    if 'response' in session:
        if request.method == 'POST':
            print("in post")
            student_response = request.form["Studentans"]
            if is_main_question(session['ques_id']):
                session['P_Q_ID'] = NULL
            s_url = 'http://127.0.0.1:5000/score_api/'+ student_response + '/'+ session['ques_id']
            data1 = {"last_session_score":session['last_session_score'],"Difficulty_level":session['Difficulty_level'],"P_Q_ID":session['P_Q_ID']}
            score_output= requests.post(s_url, data=json.dumps(data1)).json()
            q_id=score_output["session_questions_responses_data"]["Q_no"]
            session['ques_points']=score_output["session_questions_responses_data"]["Points_Scored"]
            session['t_bonus']= score_output["session_questions_responses_data"]["T_bonus"]
            session['s_bonus']= score_output["session_questions_responses_data"]["S_bonus"]
            session['q_id_points'].append({'ques_points':session['ques_points'],'t_bonus':session['t_bonus'],'s_bonus':session['s_bonus']})
            ans_match = score_output["ans_match"]
            if not ans_match:
                session["incorrect_attempts"] = session["incorrect_attempts"]+1
                session['P_Q_ID']= score_output["session_questions_responses_data"]["Q_no"].split("_")[0]
            else:
                session["correct_attempts"] = session["correct_attempts"]+1
            session['last_session_score']= score_output["points_earned_total"]
            session['Difficulty_level'] = score_output['Difficulty_level']
            session_func(score_output)
            return redirect('/'+Student_id+'/'+Topic_id)
        else:
            print("in get")
            session_list1 = []
            mydoc1 = session_doc.find({"user_id": Student_id, "session_topic_id": Topic_id})
            for x in mydoc1:
                session_list1.append(x) 
            session_q_id_list = []
            for y in session_list1:
                session_q_id = y.get('session_questions_responses_data',[])
                for i in session_q_id:
                    session_q_id_list.append(i['Q_no']) 
            session['q_id_l']= session_q_id_list
            D_L = session['Difficulty_level']
            #call the question picker api
            q_url = 'http://127.0.0.1:5000/question_picker/'+Student_id+'/'+Topic_id+'/'+D_L
            data11 = {"q_id_l":session['q_id_l'],"P_Q_ID":session['P_Q_ID'],"Difficulty_level":session['Difficulty_level']}
            question_picker_output= requests.post(q_url, data = json.dumps(data11)).json()
            print("question_picker_output",question_picker_output)
            session['ques_id'] = question_picker_output["question_id"]
            print("session",session)
            if 'questions' in session: 
                print("question in session if")
                print("session in questions",session['questions'])
                no_of_questions_per_session = len(session['questions'])
                for ques in session['questions']:
                    questions_in_session= dict()
                    questions_in_session["questions"]= ques
                    questions_in_session["question_points"]= ques["Points_Scored"]
                    questions_in_session["time_bonus"]=ques["T_bonus"]
                    questions_in_session["streak_bonus"]=ques["S_bonus"]
                    print("questions_in_session",questions_in_session)
                    questions_in_session["no_of_questions_per_session"]= no_of_questions_per_session
                data = []+session['data']
                print("data 113", data)
                score_list=[] 
                total_points_scored = session['data'][-1]['y_axis']
                print("session last score111",session['last_session_score'] )
                for i, ele in enumerate(session['q_id_points']):
                    q_no = len(data)+1
                    total_points_scored = total_points_scored+ele['ques_points'] + ele['t_bonus'] + ele['s_bonus']
                    data.append({'x_axis':q_no, 'y_axis':total_points_scored})
                print("data 114", data)
                
            else:
                print("question in session else")
                data = []
                score_list=[]
                print(" session['total_question_points']", session['total_question_points'])
                total_question_points = session['total_question_points']
                for i,ele in enumerate(session['q_id_points']):
                    t_question_points =  ele['ques_points'] + ele['t_bonus'] + ele['s_bonus']
                    score_list.append(int(t_question_points))
                    question_points_array= (i,score_list[-1])
                    total_question_points = total_question_points + question_points_array[1]
                    data.append({"x_axis":question_points_array[0]+1,"y_axis":total_question_points}) 
            #storing variables to send to frontend
            session_question_points= session['ques_points']
            session_q_id_l = session['q_id_l']
            total_attempts= len(session['q_id_l'])
            #for percentage calculation in the center of donut chart
            quotient = session["correct_attempts"] / total_attempts
            percent = {'x':str(int(quotient * 100))+"%"}
            donutdata= {'x':session["correct_attempts"],'y': session["incorrect_attempts"]}
            print("donutdata",donutdata)
            session_ques_id = session['ques_id']
            session_difficulty_level = session['Difficulty_level']
            session_last_score = session['last_session_score']
            session_response = session['response']
            session_topic_id =session['topic_id']
            q_data =question_picker_output['question_data']
            incorrect_attempts=session["incorrect_attempts"]
            correct_attempts=session["correct_attempts"]
            return render_template('user_page.html', q_data=q_data,data=data,donutdata=donutdata,percent=percent,incorrect_attempts=incorrect_attempts,correct_attempts=correct_attempts,session_question_points=session_question_points,total_attempts= total_attempts,session_topic_id=session_topic_id,session_q_id_l = session_q_id_l,session_ques_id = session_ques_id,session_difficulty_level = session_difficulty_level, session_last_score = session_last_score,session_response=session_response)
    #Create a New Session
    else:
        session_list=[]
        questions_list= []
        mydoc = session_doc.find({ "user_id":Student_id , "session_topic_id" : Topic_id })
        for record in mydoc:
            session_list.append(record)
            print("session list",session_list)
            if session_list != []:
                questions_data = record["session_questions_responses_data"]
                questions_list.append(questions_data)
                questions=list(itertools.chain.from_iterable(questions_list))
                session['questions'] = questions
                print("session['questions']",session['questions'])
        #for adding end_date_time for sessions
        if len(session_list)>0:
            print("entering in if part of outer else")
            # print("len of mydoc",len(session_list))
            session_end_time_list = []
            q_id_list = []
            data = []
            session['q_id_points']=[]
            total_question_points=0
            score_list_ques=[]
            correct_attempts = 0
            incorrect_attempts = 0
            for i,ele in enumerate(questions):
                t_question_points=ele['Points_Scored']+ele['T_bonus']+ele['S_bonus']
                score_list_ques.append(int(t_question_points))
                question_points_array= (i,score_list_ques[-1])
                total_question_points = total_question_points + question_points_array[1]
                data.append({"x_axis":question_points_array[0]+1,"y_axis":total_question_points})
                session['data']= data
                if ele['Points_Scored'] >0:
                    correct_attempts = correct_attempts+1
                else:
                    incorrect_attempts = incorrect_attempts+1
                session['correct_attempts'] = correct_attempts
                session['incorrect_attempts'] = incorrect_attempts
            for n in session_list:
                session_end_time = n.get('session_end_date_time')
                session_end_time_list.append(session_end_time)
                questions_list_data = n.get('session_questions_responses_data')
                for ques in questions_list_data:
                    q_id_list.append(ques['Q_no'])
            # print("session_end_time_list",session_end_time_list)
            index_recent_session_end_time = session_end_time_list.index(max(session_end_time_list))
            recent_session= session_list[index_recent_session_end_time]
            recent_session_exit_level = recent_session.get('session_student_exit_level')
            last_session_score = recent_session.get('session_final_score')
            session['last_session_score']=last_session_score
            session['total_question_points'] = total_question_points+session['last_session_score']
            recent_topic_status= recent_session.get('session_topic_complete')
            Updated_Difficulty_level = recent_session_exit_level
            print("session",session)
            session_count= len(session_list)+1
        else:
            #for creating a new session with difficulty level- Easy
            print("entering in else part of outer else")
            session_count=1
            Updated_Difficulty_level= "Easy"
            last_session_score = 0
            q_id_list = []
            data = [] 
            session['q_id_points']=[]
            data.append({"x_axis":0,"y_axis":0})
            session["correct_attempts"] = 0
            session["incorrect_attempts"] = 0
        
        session['last_session_score'] = last_session_score
        session['response'] = 'session_'+str(session_count)+'_'+Student_id+'_'+Topic_id
        session['Difficulty_level'] = Updated_Difficulty_level
        session['q_id_l'] = q_id_list
        total_attempts= len(session['q_id_l'])
        #for percentage calculation in the center of donut chart
        quotient = session["correct_attempts"] / total_attempts
        percent = {'x':str(int(quotient * 100))+"%"}
        print("percent",percent)
        donutdata= {'x':session["correct_attempts"],'y': session["incorrect_attempts"]}
        # print("donutdata",donutdata)
        session_id = session['response']
        session['P_Q_ID']= NULL
        store_session_start_data1 = store_session_start_info(Student_id,Topic_id, session_id, Updated_Difficulty_level)
        topic_id = store_session_start_data1["session_topic_id"] 
        session['topic_id']=topic_id
        session_topic_id =session['topic_id']
        session_doc.insert_one(store_session_start_data1)
        q_url ='http://127.0.0.1:5000/question_picker/'+Student_id+'/'+Topic_id+'/'+Updated_Difficulty_level
        ques_picker_data = {"q_id_l":session['q_id_l'], "P_Q_ID": session['P_Q_ID'], "Difficulty_level": session['Difficulty_level']}
        question_picker_output= requests.post(q_url, data = json.dumps(ques_picker_data)).json()
        session['ques_id'] = question_picker_output["question_id"]
        q_data = question_picker_output['question_data']
        session_last_score = session['last_session_score']
        session_response = session['response']
        session_difficulty_level = session['Difficulty_level']
        return render_template('user_page.html', q_data=q_data,data=data,donutdata=donutdata,percent=percent,incorrect_attempts=session['incorrect_attempts'],correct_attempts=session['correct_attempts'],total_attempts = total_attempts,session_topic_id = session_topic_id,session_last_score = session_last_score, session_response =session_response,session_difficulty_level = session_difficulty_level)

@app.route('/clear_session')
def clear_session():
    session.clear()
    return 'SUCCESS'

if __name__ == '__main__':
    app.run()

            
            