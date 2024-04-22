import time

from googletrans import Translator
import json, os, sys
from copy import deepcopy
#TODO DO THE TRANSLATE AND FILL THE EMPTY COORDINATES (LEAVE ONE SAMPLE WITH EMPTY COORDINATES FOR ILLUSTRATION PURPOSES)
'''
Translate all the characteristics and properties
'''
base_t = Translator()
INITIAL_PATH = 'C:/Users/Nikolas/OneDrive/Υπολογιστής/Scrape_data_with_titles/z_Mongo_data'
# INITIAL_PATH = './non_translated'
FINAL_TRANS_PATH = 'C:/Users/Nikolas/OneDrive/Υπολογιστής/Scrape_data_with_titles/pre_translated_data'
files_place_1 = os.listdir(f'{INITIAL_PATH}')
# print(len(files_place_1))
# sys.exit()
for f in files_place_1:
    # print(f)
    # sys.exit()
    with open(f'{INITIAL_PATH}/{f}',encoding='utf-8') as d_file:
        data = json.load(d_file)
        #properties ειναι λίστα
        #characteristics είναι λίστα
        # hostname
    copied_d = deepcopy(data)
    # print('reviews',copied_d["total_reviews"],'and  total rating',copied_d["total_rating"])
    # print(f'Money per night {copied_d["final_price_per_night"]}')

    # ------------- starting code ------------------#
    time.sleep(2)
    try:
        copied_d["host_name"] = base_t.translate(text=copied_d["host_name"],dest='en').text
        copied_d["title"] = base_t.translate(text=copied_d["title"], dest='en').text
    except Exception as e:
        print(f'Correct host name on your own {f} and host name {copied_d["host_name"]}')
        with open(f'./non_translated/{f}',"w") as datafile1:
            json.dump(copied_d,datafile1)
        continue
        time.sleep(2)

    time.sleep(3) # we have sompe problem with characteristics translation??
    for num2 in range(len(data["properties"])):
        # τρ
        # print(data["properties"][num2])
        try:
            copied_d ["properties"][num2] = base_t.translate(text=copied_d ["properties"][num2], dest='en').text
        except Exception as e:
            print(f'Correct properties your own {f} and properties {copied_d ["properties"][num2]}')
            time.sleep(1)
    time.sleep(3)
    for num1 in range(len(data["characteristics"])):
        try:
            copied_d["characteristics"][num1] = base_t.translate(text=copied_d["characteristics"][num1], dest='en').text
        except:
            print(f'Correct characteristics own {f} and properties {copied_d["properties"][num2]}')
            time.sleep(1)

    with open(f'{FINAL_TRANS_PATH}/{f}',"w") as f_d_file:
        json.dump(copied_d,f_d_file)
    # sys.exit()
    # ------------ end of starting code ----------------#
#After MASTER YOU SHOULD CONVERT THIS


#-------------------------------------------- Nikolaras validation -----------------------------------------------------#
#TODO 1 --> CREATE THE FINAL TRANSLATE and REMOVE DUPLICATE VALUES !!!
#TODO 2 --> erase Rating Νέο Δεν υπάρχουν κριτικές ακόμα and nan values, Reveiews --> replace  null with zeros, price βγάλε το \xa0
#TODO 3 --> fill the empty values of coordinate and host name hardcoded
#TODO 4 --> find THE UNIQUE VALUES for each characteristic and properties to extract coorelations

basic_translation = base_t.translate("Γειά σου",dest='en')

print(basic_translation.text)