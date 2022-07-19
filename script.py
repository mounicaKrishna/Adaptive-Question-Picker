import pymongo

from trial_2 import load_file, create_questions_list, create_final_json_frm_q_list, create_final_json_struc

client = pymongo.MongoClient("mongodb+srv://elaimte:Hknudxnt143@focusedumatics.b3ue9.mongodb.net/test")
  


def main_func(path, topic_id, topic_name):

    #load excel file
    sh = load_file(path)
    
    #create questions list from excel
    questions_list = create_questions_list(sh)

    # Create final json struc
    final_json = create_final_json_struc(topic_id, topic_name)

    # Create final_json from questions list
    final_json_created = create_final_json_frm_q_list(questions_list,final_json, topic_id)
    # print("final_json_created 632", final_json_created)
    
    
    # store it in db
    Database = client.get_database('Grade5_Q')
    Questions = Database.Questions
    Questions.insert_one(final_json_created)


path = "C:/Projects/Learnosity_Maths-data-chapter 1.xls"
topic_id = "MA_5_OA_1"
topic_name = "Operations and Arithmetics 1"

# main_func(path, topic_id, topic_name)

print(load_file(path))

