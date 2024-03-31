'''
Όταν το δημιουργεί locally και το push-άρεις τότε δημιουργείται αυτόματα

Όταν διαγράφεις branch είτε το κάνεις locally και remode

git branch -d branch_name

git push origin --delete branch_name

'''
import copy
from googletrans import Translator
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import selenium.common.exceptions
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import  Keys
import json,sys,os,time,requests
from pprint import pprint
from copy import deepcopy
# We do this for lin
#Aύριο προσπάθησε να βρεις επιλογή επισκεπτών και latitude και longtitude
# ---------------------------------------------  Selenium setup --------------------------------------------------------#
chrome_opts = webdriver.ChromeOptions()
Chrome_opts = chrome_opts.add_experimental_option('detach',True)
dr = webdriver.Chrome(options=Chrome_opts)


#---------------------------------------------- Beautifoul soup setup --------------------------------------------------#

#---------------------------------------------------- Functions ------------------------------------------------------- #
def extract_room_attributes(html_text,nested_dict):
    official_translator = Translator()
    is_superhost, is_guest_favorite = False, False
    overall_rating, more_about_google_api = '', ''
    mutable_soup = BeautifulSoup(html_text, 'html.parser')
    # ---------------------------------- Room pricing code ---------------------------------------------#
    try:
        price_per_night = mutable_soup.find(name='div', class_='_1jo4hgw').text # TODO ADD SOME VALIADATION IF FINDS NONE TYPE
    except:
        print('No price found')
        price_per_night=""
    count_euros, blank_reject = 0, False
    final_price_per_night = ''
    if price_per_night.count('€') == 2:
        for num in range(len(price_per_night)):
            if blank_reject:
                final_price_per_night += price_per_night[num:num + 3]
                break
            if count_euros == 2:
                blank_reject = True
                continue
            if '€' == price_per_night[num]:
                count_euros += 1
    elif price_per_night.count('€') == 1:
        for num in range(len(price_per_night)):
            if blank_reject:
                final_price_per_night += price_per_night[num:num + 3]
                break
            if count_euros == 1:
                blank_reject = True
                continue
            if '€' == price_per_night[num]:
                count_euros += 1

    else:
        final_price_per_night = ''
    # print(f'The final price per night is {final_price_per_night}')
    # print(f"Price per night is {price_per_night}")
    # ------------------------------- Host name code --------------------------------------------------#
    host_name = mutable_soup.select(selector='.to1hkqq .t1pxe1a4')
    # print(host_name[0].text)
    if len(host_name) == 1:
        if ':' in host_name[0].text:  # Οικοδεσπότης: Beatrix
            final_host_name = host_name[0].text.split(":")[1].replace(" ", "")
        elif 'Μείνετε' in host_name[0].text:  # Μείνετε με τον/την Fowzia
            final_host_name = host_name[0].text.split(" ")[3]
    # -------------------------------- Superhost code that will be deleted because it overlaps with another code#
    # superhost_or_not = mutable_soup.select(selector='.s1l7gi0l ol')
    # pre_superhost =[el.find(name='li') for el in superhost_or_not]
    # ----------------------------- Characteristics  ---------------------------------------------------------#
    pre_character = mutable_soup.select(selector='.c1yo0219 .i1jq8c6w ._wlu9uw')

    first_heads = [pre.select(selector='._sg8691 h3') for pre in pre_character]

    second_head = [prev.select(selector='._1dmhz6v') for prev in pre_character]

    final_char_list = []
    for f_el_init, sec_el_init in zip(first_heads, second_head):
        final_char_list.append(f_el_init[0].text + '.' + sec_el_init[0].text)
    # print(f' Host name is {final_host_name} \n with final characteristics {final_char_list} ')
    # --------------------------- Number of guests/beds/bedrooms/baths $Properties$ ------------------------#
    pre_general = mutable_soup.select(selector='.lgx66tx .l7n4lsf')
    if len(pre_general) > 1:
        pre_general.pop()  # The last element refere to the name of superhosts so pop it
    pre_general_copy = deepcopy(pre_general)
    for el in pre_general_copy:
        extract_text = el.text
        # print(f'the extracted text looks like these {extract_text}')
        if 'Superhost' in extract_text:
            is_superhost = True
            # pop_index = pre_general.index('Superhost')
            # print(pre_general,pop_index)
            pre_general.remove(el)
        if 'οικοδεσπότης' in extract_text:  # Είχα θέμα 3 επισκέπτες ·  · Στούντιο ·  · 2 κρεβάτια ·  · 1 μπάνιο · 5 χρόνια εμπειρίας ως οικοδεσπότηςΜέλος από: Δεκέμβριος 2018 ·
            pre_general.remove(el)
        if 'Μέλος' in extract_text:
            pre_general.remove(el)
    general_info = [el.text for el in pre_general]
    room_properties = ''.join(general_info)
    pre_final_room_properties1 = room_properties.split('·')  # .replace("·",",").split(',')
    # print()
    final_room_properties2 = [p for p in pre_final_room_properties1 if ',' not in p]
    final_room_properties = [p1 for p1 in final_room_properties2 if
                             '  ' not in p1]  # ['1 διπλό κρεβάτι ', '  ', ' Ιδιωτικό μπάνιο εντός δωματίου']
    # print(f'All the properties can be sum int this {final_room_properties}  \n and the superhost {is_superhost}')
    # sys.exit()

    # ----------------------------------------- GUEST FAVORITES WITH REVIEW NUMBER AND OVERALL RATING  ------------------#
    pre_guest_favorite_tme = mutable_soup.select_one(selector='._gpz5gq ._16e70jgn .c1yo0219 .m209l21')  # a .m209l21
    # print(pre_guest_favorite_tme,'\n',len(pre_guest_favorite_tme))
    # print(type(pre_guest_favorite_tme)) --> It is a bs4.element.Tag
    if pre_guest_favorite_tme is not None:
        # Βρες  μου τα στοιχεία που αφορούν την επιλογή επισκεπτών
        # print('this place is guest favorite')
        guest_favorite_tag = pre_guest_favorite_tme.select_one(
            selector='.geb1krl .c139f2ip .lbjrbi0')  # ['Επιλογή', 'επισκεπτών']
        # print(guest_favorite_tag)
        if len(guest_favorite_tag.text.split('\n')) != 0:
            is_guest_favorite = True
            preoverall_rating = pre_guest_favorite_tme.select_one(
                selector='.a8jhwcl .a8jt5op').text  # Βαθμολογήθηκε με 4,97 στα 5 αστέρια για αυτό θέλω το στοιχείο
            overall_rating = preoverall_rating.split(" ")[2]
            # print(f' Number of reviews with guest favorite {overall_rating}')
            number_of_ratings = pre_guest_favorite_tme.select_one(selector='.rddb4xa .r16onr0j').text
            # print('With number of ratings', number_of_ratings)
    else:
        review_number_init = mutable_soup.select(
            selector='.rk4wssy .l1ovpqvx')  # Αυτό μπορεί να υπάρχει στα νέα συστήματα, αλλά μπορείς και όχι

        overall_rating_init = mutable_soup.select(
            selector='.rk4wssy .r1lutz1s')  # Αυτό σίγουρα δεν υπάρχει στα νέα συστήματα
        if len(overall_rating_init) != 0:
            # print(f'Without guest favorites we have that OVERALL RATING IS {overall_rating_init}')
            overall_rating = overall_rating_init[0].text
            # overall_rating = float(overall_rating_init[0].text.replace(",", "."))
            # print(f'Final outocmes without guest favorite tab from overall rating {overall_rating}')
            if 'Νέο' in overall_rating:
                # print(' New Home with no overall rating')
                overall_rating ='Νέο'
        else:
            print(f'No overall rating found for this category')
        if len(review_number_init) != 0:  # NEO ΧΩΡΙΣ αριθμό κριτικών
            # print(f'Without guest favorites we have that REVIEW NUMBER {review_number_init}')
            number_of_ratings = review_number_init[0].text.split(" ")[0]
            # print(f'Final outocmes without guest favorite tab from reviews number {number_of_ratings}')
        else:
            # print('Not available number of reviews for this room')
            number_of_ratings =''
    nested_dict['superhost'] = is_superhost
    nested_dict['guest_favorite'] = is_guest_favorite
    nested_dict['total_rating'] = overall_rating
    nested_dict['total_reviews'] = number_of_ratings
    nested_dict['host_name'] = final_host_name.split(" ")[0]

    # nested_dict['characteristics'] = [official_translator.translate(el,src='el', dest='en').text for el in final_char_list]
    nested_dict['characteristics'] = final_char_list
    # nested_dict['properties'] = [official_translator.translate(el,src='el', dest='en').text for el in final_room_properties]
    nested_dict['properties'] =final_room_properties
    nested_dict['final_price_per_night'] = final_price_per_night.split(" ")[0]
    return nested_dict

if __name__=="__main__":
    #Menemeni-Ampelokipoi 3-10 April
    URL_PAGE_1 = 'https://www.airbnb.gr/s/Ampelokipoi~Menemeni--Greece/homes?tab_id=home_tab&refinement_paths%5B%5D=%2Fhomes&flexible_trip_lengths%5B%5D=one_week&monthly_start_date=2024-04-01&monthly_length=3&monthly_end_date=2024-07-01&price_filter_input_type=0&channel=EXPLORE&query=Ampelokipoi-Menemeni%2C%20Greece&place_id=ChIJAZMjizo6qBQRtTybGHAwKtI&date_picker_type=calendar&checkin=2024-04-03&checkout=2024-04-10&adults=3&source=structured_search_input_header&search_type=autocomplete_click'
    URL_PAGE_6 = 'https://www.airbnb.gr/s/Ampelokipoi~Menemeni--Greece/homes?tab_id=home_tab&refinement_paths%5B%5D=%2Fhomes&flexible_trip_lengths%5B%5D=one_week&monthly_start_date=2024-04-01&monthly_length=3&monthly_end_date=2024-07-01&price_filter_input_type=0&channel=EXPLORE&query=Ampelokipoi-Menemeni%2C%20Greece&place_id=ChIJAZMjizo6qBQRtTybGHAwKtI&date_picker_type=calendar&checkin=2024-04-03&checkout=2024-04-10&adults=3&source=structured_search_input_header&search_type=autocomplete_click&price_filter_num_nights=7&federated_search_session_id=ee7bec67-d7f3-4daf-92bb-4c69c5232464&pagination_search=true&cursor=eyJzZWN0aW9uX29mZnNldCI6MywiaXRlbXNfb2Zmc2V0Ijo5MCwidmVyc2lvbiI6MX0%3D'
    URL_PAGE_7 = 'https://www.airbnb.gr/s/Ampelokipoi~Menemeni--Greece/homes?tab_id=home_tab&refinement_paths%5B%5D=%2Fhomes&flexible_trip_lengths%5B%5D=one_week&monthly_start_date=2024-04-01&monthly_length=3&monthly_end_date=2024-07-01&price_filter_input_type=0&channel=EXPLORE&query=Ampelokipoi-Menemeni%2C%20Greece&date_picker_type=calendar&checkin=2024-04-03&checkout=2024-04-10&adults=3&source=structured_search_input_header&search_type=autocomplete_click&price_filter_num_nights=7&zoom_level=15&place_id=ChIJAZMjizo6qBQRtTybGHAwKtI&federated_search_session_id=23abab52-98b4-41e5-afaf-a4de606c57a2&pagination_search=true&cursor=eyJzZWN0aW9uX29mZnNldCI6MywiaXRlbXNfb2Zmc2V0IjoxMDgsInZlcnNpb24iOjF9'
    URL_PAGE_11 ='https://www.airbnb.gr/s/Ampelokipoi~Menemeni--Greece/homes?tab_id=home_tab&refinement_paths%5B%5D=%2Fhomes&flexible_trip_lengths%5B%5D=one_week&monthly_start_date=2024-04-01&monthly_length=3&monthly_end_date=2024-07-01&price_filter_input_type=0&channel=EXPLORE&query=Ampelokipoi-Menemeni%2C%20Greece&place_id=ChIJAZMjizo6qBQRtTybGHAwKtI&date_picker_type=calendar&checkin=2024-04-03&checkout=2024-04-10&adults=3&source=structured_search_input_header&search_type=autocomplete_click'
    URL_PAGE_15 ='https://www.airbnb.gr/s/Ampelokipoi~Menemeni--Greece/homes?tab_id=home_tab&refinement_paths%5B%5D=%2Fhomes&flexible_trip_lengths%5B%5D=one_week&monthly_start_date=2024-04-01&monthly_length=3&monthly_end_date=2024-07-01&price_filter_input_type=0&channel=EXPLORE&query=Ampelokipoi-Menemeni%2C%20Greece&date_picker_type=calendar&checkin=2024-04-03&checkout=2024-04-10&adults=3&source=structured_search_input_header&search_type=autocomplete_click&price_filter_num_nights=7&zoom_level=15&place_id=ChIJAZMjizo6qBQRtTybGHAwKtI&federated_search_session_id=23abab52-98b4-41e5-afaf-a4de606c57a2&pagination_search=true&cursor=eyJzZWN0aW9uX29mZnNldCI6MywiaXRlbXNfb2Zmc2V0IjoyNTIsInZlcnNpb24iOjF9'
    # TODO EAN TYXON DEN TREXOYN OI ΣΕΛΙΔΕΣ ΚΑΙ ΤΟ ΣΠΑΣΕΙΣ ΤΟΤΕ ΘΑ ΧΡΕΙΑΣΤΕΙ ΝΑ ΠΑΙΞΕΙΣ ΜΠΑΛΑ
    # Menemeni-Ampelokipoi 3-10 September
    URL_PAGE_1_MEN ='https://www.airbnb.gr/s/Ampelokipoi~Menemeni--Greece/homes?tab_id=home_tab&refinement_paths%5B%5D=%2Fhomes&flexible_trip_lengths%5B%5D=one_week&monthly_end_date=2024-07-01&price_filter_input_type=0&channel=EXPLORE&query=Ampelokipoi-Menemeni%2C%20Greece&place_id=ChIJAZMjizo6qBQRtTybGHAwKtI&date_picker_type=calendar&adults=3&source=structured_search_input_header&search_type=filter_change&price_filter_num_nights=2&checkin=2024-09-03&checkout=2024-09-10&monthly_start_date=2024-04-01&monthly_length=3'
    # Evosmos 3-10 September
    URL_PAGE_1_EVO = 'https://www.airbnb.gr/s/Evosmos--%CE%98%CE%B5%CF%83%CF%83%CE%B1%CE%BB%CE%BF%CE%BD%CE%AF%CE%BA%CE%B7/homes?tab_id=home_tab&refinement_paths%5B%5D=%2Fhomes&flexible_trip_lengths%5B%5D=one_week&monthly_end_date=2024-07-01&price_filter_input_type=0&channel=EXPLORE&query=Evosmos%2C%20%CE%98%CE%B5%CF%83%CF%83%CE%B1%CE%BB%CE%BF%CE%BD%CE%AF%CE%BA%CE%B7&date_picker_type=calendar&adults=3&source=structured_search_input_header&search_type=autocomplete_click&price_filter_num_nights=7&checkin=2024-09-03&checkout=2024-09-10&monthly_start_date=2024-04-01&monthly_length=3&place_id=ChIJl5tHov45qBQRgKS54iy9AAQ'
    #Stavropoli 3-10 September
    URL_PAGE_1_STAV ='https://www.airbnb.gr/s/Stavroupoli--%CE%95%CE%BB%CE%BB%CE%AC%CE%B4%CE%B1/homes?tab_id=home_tab&refinement_paths%5B%5D=%2Fhomes&flexible_trip_lengths%5B%5D=one_week&monthly_end_date=2024-07-01&price_filter_input_type=0&channel=EXPLORE&date_picker_type=calendar&adults=3&source=structured_search_input_header&search_type=autocomplete_click&price_filter_num_nights=7&checkin=2024-09-03&checkout=2024-09-10&monthly_start_date=2024-04-01&monthly_length=3&query=Stavroupoli%2C%20%CE%95%CE%BB%CE%BB%CE%AC%CE%B4%CE%B1&place_id=ChIJscTudt45qBQR4KW54iy9AAQ'
    #

    # pre_number_of_total_pages = dr.find_element(By.XPATH,value='//*[@id="site-content"]/div/div[3]/div/div/div/nav/div/a[4]').text
    # print(pre_number_of_total_pages)
    # print(pre_number_of_total_pages,type(pre_number_of_total_pages))
    total_number_of_pages = 15 # int(pre_number_of_total_pages) Μονο για την αρχή μας χρειάζεται
    next_butt = 0
    dictionary_for_mongo_db,my_dict = {},{}
    dr.get(URL_PAGE_1_STAV)

    for page_ in range(total_number_of_pages):
        dictionary_for_mongo_db[page_+1] ={}
        for i in range(1,19):
            dictionary_for_mongo_db[page_ + 1][i]={}
            time.sleep(3)#5
            # wait = WebDriverWait(dr,30)
            # time.sleep(2)
            room_url =dr.find_element(By.XPATH, value=f'//*[@id="site-content"]/div/div[2]/div/div/div/div/div[1]/div[{i}]/div/div[2]/div/div/div/div/div/div[1]/div/div/div[2]/div/div/div/div/a[1]')
            # room_url = wait.until(EC.element_to_be_clickable((By.XPATH,f'//*[@id="site-content"]/div/div[2]/div/div/div/div/div[1]/div[{i}]/div/div[2]/div/div/div/div/div/div[1]/div/div/div[2]/div/div/div/div/a[1]')))
            # room_url =

            time.sleep(6)
            room_url.click()


            # room_url.click()
            # time.sleep(1)
            windows_list = dr.window_handles
            dr.switch_to.window(windows_list[-1])
            # Imagine you have this
            time.sleep(3)
            new_page_source = dr.page_source
            # print(dr.window_handles)
            time.sleep(2)
            mutable_requests_text =""
            # --------------------------- Latitude / Longtitude code --------------------------------------- #
            # find the translate button
            try:
             trans_butt = dr.find_element(By.XPATH,'/html/body/div[9]/div/div/section/div/div/div[2]/div/div[1]/button')
             time.sleep(4)
             trans_butt.click()
             time.sleep(1)
             dr.execute_script("window.scrollBy(0, 3550);") # Ισως θα πρέπει να μπει 3700
            except selenium.common.exceptions.NoSuchElementException:
                dr.execute_script("window.scrollBy(0, 3550);")

            # dr.execute_script("window.scrollBy(0, 3500);") # With this code o
            time.sleep(6)
            my_dict = extract_room_attributes(html_text=new_page_source,
                                              nested_dict=dictionary_for_mongo_db[page_ + 1][i])
            try:
                google_but = dr.find_element(By.XPATH,value='//*[@id="site-content"]/div/div[1]/div[5]/div/div/div/div[2]/section/div[3]/div[4]/div/div/div/div[14]/div/a')
                wanted_coordinates_link =google_but.get_property('href').split("?")[1].split("=")[1].split(",")
                my_dict['coordinates'] = wanted_coordinates_link[0] + "," + wanted_coordinates_link[1].split('&')[0]
            except selenium.common.exceptions.NoSuchElementException:
                print('No coordinates')
                my_dict['coordinates'] =''
            # time.sleep(10)

            # my_dict['coordinates'] = wanted_coordinates_link[0] + "," + wanted_coordinates_link[1].split('&')[0]
            print(my_dict)
            # print(f"checking the page {page_}")
            mutable_soup_will_be_trasfer_to_function = BeautifulSoup(new_page_source, 'html.parser')
            # print(dr.current_window_handle)
            new_windows_list = dr.window_handles
            dr.switch_to.window(new_windows_list[0])
            # print(dr.current_window_handle)
            time.sleep(2)
            if i% 4 ==0:
                dr.execute_script("window.scrollBy(0, 850);")
                # print("screen has scrolled")
            # R
            with open(f'./results/page{page_ + 1}_property_{i}.json','w') as datafile:
                json.dump(my_dict,datafile,indent= 4)
            # print(new_windows_list)
            #//*[@id="site-content"]/div/div[1]/div[5]/div/div/div/div[2]/section/div[3]/div[4]/div/div/div/div[14]/div/a
            #href="https://maps.google.com/maps?ll=41.32119,2.01557&z=14&t=m&hl=el&gl=GR&mapclient=apiv3"
            time.sleep(2)
            # with open('')
        print(f"checking the page {page_}")
        time.sleep(3)
        print('page_switched')

        if page_ == 0:
            next_butt= dr.find_element(By.XPATH,value='//*[@id="site-content"]/div/div[3]/div/div/div/nav/div/a[5]')
        elif page_ == 14:
            break
        else:
            next_butt = dr.find_element(By.XPATH,value='//*[@id="site-content"]/div/div[3]/div/div/div/nav/div/a[6]')

        time.sleep(3)
        next_butt.click()
        time.sleep(5)
