import xlrd

def load_file(path):
    wb = xlrd.open_workbook(path)
    sh = wb.sheet_by_index(0)
    return sh

def create_questions_list(sh):
    Question_list = []
    for rownum in range(1, sh.nrows):
        Question = dict()
        row_values = sh.row_values(rownum)
        Question['Question_type'] = row_values[0]
        Question['Question_tag'] = row_values[1]
        Question['Question'] = row_values[2]
        Question['Question_Option1'] = row_values[3]
        Question['Question_Option2'] = row_values[4]
        Question['Question_Option3'] = row_values[5]
        Question['Question_Option4'] = row_values[6]
        Question_list.append(Question)
    return Question_list

def question_id(topic_id, q_tag, count):
    q_id = topic_id+"_"+q_tag["Difficulty"]+str(count)
    return q_id

def create_question_format(question, q_tag, topic_id, count):
    quest_format = dict()
    quest_format["question_id"] = question_id(topic_id, q_tag, count)
    quest_format["question_type"] = question["Question_type"]
    quest_format["question_data"] = question["Question"]
    quest_format["Options"] = dict()
    quest_format["Options"]["option_1"] = question["Question_Option1"]
    quest_format["Options"]["option_2"] = question["Question_Option2"]
    quest_format["Options"]["option_3"] = question["Question_Option3"]
    quest_format["Options"]["option_4"] = question["Question_Option4"]
    quest_format["Correct_ans"] = "A"
    quest_format["probable_ans"] = "a"
    quest_format["DOK_Level"] = q_tag["DepthOfKnowledge"]
    quest_format["Bloom_Level"] = q_tag["Blooms"]
    return quest_format

def create_final_json_struc(topic_id, topic_name):
    final_json = dict()
    final_json["topic_id"]= topic_id
    final_json["topic_name"] = topic_name
    final_json["Questions"] = dict()
    final_json["Questions"]["Easy"] = []
    final_json["Questions"]["Medium"] = []
    final_json["Questions"]["Hard"] = []
    return final_json

def create_final_json_frm_q_list(Question_list,final_json, topic_id):
    easy_count= 1
    medium_count= 1
    hard_count= 1
    for question in Question_list: 
        Question_tag = question['Question_tag'].split('#$#')
        # print("Question_tag",Question_tag)
        #Question_tag ['MaxPoints: 1.00', 'DepthOfKnowledge: 2', 'Blooms: Understanding', 'item_createdby: Certica Solutions', 'item_districtid: ALL', 'Scope: Classroom', 'Difficulty: M', 'Subject: MATH']
        while '' in Question_tag:
            Question_tag.remove('')
            # print("Question_tag",type(Question_tag))
        Question_tag = dict(tag.split(': ') for tag in Question_tag)
        if "Difficulty" in Question_tag.keys():
            if(Question_tag["Difficulty"] == 'E'):
                question_dict = create_question_format(question,Question_tag, topic_id, easy_count)
                easy_count = easy_count+1
                final_json["Questions"]["Easy"].append(question_dict)
            elif(Question_tag["Difficulty"] == 'M'):
                question_dict = create_question_format(question,Question_tag, topic_id, medium_count)
                medium_count = medium_count+1
                final_json["Questions"]["Medium"].append(question_dict)
            elif(Question_tag["Difficulty"] == 'H'):
                question_dict = create_question_format(question,Question_tag, topic_id, hard_count)
                hard_count = hard_count+1
                final_json["Questions"]["Hard"].append(question_dict)
    return Question_tag,final_json
