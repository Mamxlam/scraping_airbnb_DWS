import pandas as pd
import numpy as np
import os,sys, json
from copy import deepcopy
import openpyxl
from store_data_in_mongo import store_data_to_mongo




# MY_DIR = os.path.dirname(os.path.abspath(__file__))
MY_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = 'C:/Users/Nikolas/OneDrive/Υπολογιστής/Scrape_data_with_titles/pre_translated_data'
# print(len(os.listdir(DATA_DIR)),"\n and",os.listdir(DATA_DIR))
# sys.exit()
characters_list_name,proper_name_list =[],[]
copy_data_list =[]
for js_file in os.listdir(DATA_DIR):
    with open(f'{DATA_DIR }/{js_file}') as d_file:
        data = json.load(d_file)
    copied_data = deepcopy(data)
    copied_data['telework'] = False #  'Ideal for teleworking. WiFi with 50 Mbps, along with a special workplace.',
    copied_data['fast_wifi'],copied_data['arr_exp'],copied_data['location'],copied_data['check_in'],copied_data['exp_host'] = False,False,False,False,False
    copied_data['pets'],copied_data['com'],copied_data["cancel"],copied_data["parking"] = False,False,False,False

    try:
        copied_data["final_price_per_night"]=float(copied_data["final_price_per_night"])
    except:
        raise  ValueError(f'Inside exception {copied_data["final_price_per_night"]} and file {js_file} with host_name {copied_data["host_name"]}')
    if isinstance(copied_data["total_rating"],str):
        if 'Δεν υπάρχουν κριτικές' in copied_data["total_rating"] or copied_data["total_rating"] =='':
            copied_data["total_rating"] = 0.0
    #Organizing charcteristics
    copied_data['num_characteristics']= len(copied_data["characteristics"])
    for val in copied_data['characteristics']:
        if 'check-in' in val.lower() or 'check in' in val.lower():
            copied_data['check_in'] = True
        elif 'location' in val.lower():
            copied_data['location'] = True
        elif 'pets' in val.lower():
            copied_data['pets'] = True
        elif 'cancellation' in val.lower():
            copied_data['cancel'] = True
        elif 'parking' in val.lower():
            copied_data["parking"] = True
        elif 'fast wifi' in val.lower() and 'mbps' in val.lower():
            copied_data["fast_wifi"] = True
        elif 'communication' in val.lower():
            copied_data['com'] =True
        elif 'for other spaces' in val.lower():
            copied_data['exp_host'] =True
        if 'special workplace' in val.lower() or 'teleworking' in val.lower() or 'telecommunication' in val.lower():
            copied_data['telework'] =True
        if 'arrival experience' in val.lower():
            copied_data['arr_exp'] = True
    copied_data["beds"],copied_data["bathrooms"],copied_data["visitors"],copied_data["baths"],copied_data["bedrooms"],copied_data['studio'] = 0,0,0,0,0,False
    for val_1 in copied_data['properties']:
        # print(val_1,'and splitted version is', val_1.split(" ")[0])
        if 'beds' in val_1.lower() or 'bed' in val_1.lower():
            copied_data["beds"] =val_1.split(" ")[0]
        if 'bathrooms' in val_1.lower():
            copied_data["bathrooms"] =val_1.split(" ")[0]
        if 'visitors' in val_1.lower():
            copied_data["visitors"] =val_1.split(" ")[0] # Φτάνει μέχρι 16+
        if 'baths' in val_1.lower() or 'bath' in val_1.lower() :
            copied_data["baths"] =val_1.split(" ")[0]
        if 'bedrooms' in val_1.lower() or 'bedroom' in val_1.lower():
            copied_data["bedrooms"] =val_1.split(" ")[0]
        if 'studio' in val_1.lower():
            copied_data['studio'] = True
    splitted_js = js_file.split("_")
    if len(splitted_js) ==3:
        copied_data['region'] = 'Menemeni/Ampelokipoi'
        copied_data['page'] = splitted_js[0][4:]  # 1-15
        copied_data['n_prop'] = splitted_js[2].split(".")[0] # 1-18
    else: # is equal to 4
        copied_data['n_prop'] = splitted_js[3].split(".")[0]
        if 'sta' in js_file.lower():
            copied_data['search_region'] = 'Stavropoli'
            copied_data['page'] = splitted_js[2][4:]
        elif 'evo' in js_file.lower():
            copied_data['search_region']= 'Evosmos'
            copied_data['page'] = splitted_js[2][4:]

    del copied_data['characteristics']
    del copied_data['properties']
    copy_data_list.append(copied_data)

#------------------------ Remove duplicated values -------------------------------------#
df= pd.DataFrame(copy_data_list)
print('before',len(df)) # 440 values and 360 in total values
# ERASE THE DUPLICATED VALUES
subset_for_dropping_cols = ['superhost', 'guest_favorite', 'total_rating', 'total_reviews',
       'host_name', 'final_price_per_night', 'coordinates', 'telework',
       'fast_wifi', 'arr_exp', 'location', 'check_in', 'exp_host', 'pets',
       'com', 'cancel', 'parking', 'num_characteristics', 'beds', 'bathrooms',
       'visitors', 'baths', 'bedrooms', 'studio']

dupi_mask = df.duplicated(subset=subset_for_dropping_cols)
duplicated_rows = df[dupi_mask]
wanted_index = duplicated_rows.index

for w in sorted(wanted_index,reverse=True):
    copy_data_list.pop(w)


store_data_to_mongo(copy_data_list)






