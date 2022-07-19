from os import remove
import random

def create_question_format(question_df,is_main_question):
   question_df1 = question_df.to_dict('records')[0]
   quest_format = dict()
   quest_format["question_type"] = "Q&A"
   quest_format["Breakup_of_Main_question"] = question_df1['Breakup of Main question']
   quest_format["question_data"] = question_df1['Question']
   quest_format["Correct_ans"] = question_df1['Correct Answer']
   quest_format["probable_ans"] = question_df1['Probable Answers'] 
   if question_df1['Breakup of Main question'].is_integer():
      Difficulty_level_list = ["Easy","Medium","Hard"]
      quest_format["Difficulty_level"] = random.choice(Difficulty_level_list)
      Bloom_level_list = ["Creating","evaluating","Analyzing","Applying","Understanding","Remembering"]
      quest_format["Bloom_level"] =  random.choice(Bloom_level_list)
      Depth_Of_Knowledge_list = ["DOK_1","DOK_2","DOK_3","DOK_4"]
      quest_format["Depth_Of_Knowledge"] =random.choice(Depth_Of_Knowledge_list)
      quest_format["question_id"] = str(int(question_df1['Question_id']))
   if is_main_question:
      quest_format["sub-question"] = []
   return quest_format
 
def create_excel_final_json_structure():
   final_json = dict()
   final_json["Excel_name"] = "HS ALG.1.E.2.BOT AI DEMO_Distributing and Like Terms"
   final_json["Topic_id"]= "MA_Algebra"
   final_json["Questions"] = dict()
   final_json["Questions"]["Easy"]=[]
   final_json["Questions"]["Medium"]=[]
   final_json["Questions"]["Hard"]=[]
   return final_json

def create_db_question_structure(question_df,is_main_question, question_json):
   if is_main_question:
      question_json = create_question_format(question_df, is_main_question)
   else:
      question_json["sub-question"].append(create_question_format(question_df, is_main_question))
   return question_json

def add_questions_from_excel_to_db(df,final_json):
   unique_main_questions = df['Main Q.NO'].dropna().unique()
   for main_question in unique_main_questions:
      main_question_df = df[df['Main Q.NO']==main_question].reset_index()
      q_json = dict()
      main_q_info = dict()
      for i in range(0,len(main_question_df)):
         is_main_question = False
         if main_question_df['Breakup of Main question'][i] == main_question:
            is_main_question = True
         q_json = create_db_question_structure(main_question_df[main_question_df['Breakup of Main question']==main_question_df['Breakup of Main question'][i]].reset_index(),is_main_question,q_json)         
         if is_main_question:
            main_q_info["question_id"] = q_json["question_id"]
            main_q_info["Difficulty_level"]= q_json["Difficulty_level"]
            main_q_info["Bloom_level"] = q_json["Bloom_level"]
            main_q_info["Depth_Of_Knowledge"] = q_json["Depth_Of_Knowledge"]
            main_q_info["sub-question"]= q_json["sub-question"]
         else:
            q_json["sub-question"][i-1]["Difficulty_level"]= main_q_info["Difficulty_level"]
            q_json["sub-question"][i-1]["Bloom_level"]= main_q_info["Bloom_level"]
            q_json["sub-question"][i-1]["Depth_Of_Knowledge"]= main_q_info["Depth_Of_Knowledge"]
            q_json["sub-question"][i-1]["question_id"] = main_q_info["question_id"]+"_"+str(i)
         q_json.update(q_json)
      #if there are no sub-questions in Sub-question array
      if main_q_info["sub-question"] == []:
            q_json.pop("sub-question")
      if q_json["Difficulty_level"]=="Easy":
         final_json["Questions"]["Easy"].append(q_json)
      elif q_json["Difficulty_level"]=="Medium":
         final_json["Questions"]["Medium"].append(q_json)
      elif q_json["Difficulty_level"]=="Hard":
         final_json["Questions"]["Hard"].append(q_json)
   return final_json

