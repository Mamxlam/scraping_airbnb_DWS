import time 
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
from selenium.common.exceptions import TimeoutException
import time
import pandas as pd
import numpy as np
import logging
import sys
import os
from datetime import datetime
import re

script_path = os.path.abspath(sys.argv[0])
print(f"The path of the currently executing script is: {script_path}")
# Go up three levels
parent_directory = os.path.dirname(script_path)
for _ in range(2):
    parent_directory = os.path.dirname(parent_directory)

# Configure logging
current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
logging.basicConfig(filename=parent_directory+f'/logs/scrapapp_{current_time}.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Create a handler for writing log messages to the standard output (console)
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)

# Create a formatter for the console handler
console_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

# Add the formatter to the console handler
console_handler.setFormatter(console_formatter)

# Add the console handler to the root logger
logging.getLogger('').addHandler(console_handler)

logging.info(f"Logfile will be saved at path: {parent_directory+f'/logs/scrapapp_{current_time}.log'}")
logging.info(f"Data will be saved at path: {parent_directory+f"/data/listing_data_{current_time}.csv"}")

TIMEOUT=30
PAGE_TO_BREAK=30
COLUMNS = [
    'Price', 'Title', 'Visitors', 'Beds', 'Bedrooms', 'Baths', 
    'Guest Favorite', 'Superhost', 'Review Index', 'Number of reviews', 
    'Host Name', 'Characteristics', 'Latitude', 'Longitude'
]

listing_data_df = pd.DataFrame(columns=COLUMNS)

# Helper function to extract numbers from text
def extract_number(text):
    """
    Extract numerical value from text using regular expression.
    
    Parameters:
    text (str): Text containing numerical value.
    
    Returns:
    int or None: Extracted numerical value or None if no match.
    """
    match = re.search(r'\d+', str(text))
    return int(match.group()) if match else None

def post_proc(df):
    """
    Post-processing function to clean and transform the input dataframe.
    
    Parameters:
    df (DataFrame): Input dataframe containing raw data.
    
    Returns:
    DataFrame: Processed dataframe ready for modeling.
    """
    
    # Price: remove currency symbol and convert to numeric
    df['Price'] = df['Price'].str.replace('€', '').str.strip().astype(float)
    df['Host Name'] = df['Host Name'].str.replace('Hosted by ', '')

    # Extract numerical values from text columns
    df['Visitors'] = df['Visitors'].apply(extract_number)
    df['Beds'] = df['Beds'].apply(extract_number)
    df['Bedrooms'] = df['Bedrooms'].apply(extract_number)
    df['Baths'] = df['Baths'].apply(extract_number)
    df['Number of reviews'] = df['Number of reviews'].apply(extract_number)

    # Convert Review Index to float
    df['Review Index'] = df['Review Index'].apply(extract_number).astype(float)

    # Convert categorical columns to binary
    df['Guest Favorite'] = df['Guest Favorite'].astype(str).apply(lambda x: 1 if 'favorite' in x else 0)
    df['Superhost'] = df['Superhost'].astype(str).apply(lambda x: 1 if 'Superhost' in x else 0)

    # Assuming Latitude and Longitude are already in numeric format
    # If not, convert them to numeric here

    # Characteristics processing
    characteristics_to_track = ['Superhost', 'Free cancellation', 'Fast wifi', 'Dedicated workspace', 'Great location', 'Furry friends', 'Highly rated', 'Self check-in', 'Great check-in', 'remote work']

# Create new columns for each characteristic and set binary values
    for char in characteristics_to_track:
        # Check for NaN values in 'Characteristics' column
        if not df['Characteristics'].isna().all():
            df['char_' + char.lower().replace(' ', '_')] = df['Characteristics'].str.contains(char, na=False).astype(int)
        else:
            df['char_' + char.lower().replace(' ', '_')] = 0

    # Drop the original 'Characteristics' column
    df.drop('Characteristics', axis=1, inplace=True)

    return df

def export_data():
    global current_time
    global listing_data_df
    listing_data_df.to_csv(parent_directory+f"/data/listing_data_{current_time}.csv")
    listing_data_df = post_proc(listing_data_df)
    listing_data_df.to_csv(parent_directory+f"/data/listing_data_postproc_{current_time}.csv")

def find_geoloc(driver):
    while True:
        try:
            PATTERN = 'google.com/maps/@'
            soup = BeautifulSoup(driver.page_source, 'html.parser')

            # Find the Google Maps href
            google_maps_links = []

            for link in soup.find_all('a', {'href': True}):
                if PATTERN in link['href']:
                    google_maps_links.append(link['href'])

            if len(google_maps_links) == 1:
                lat = google_maps_links[0].split('@')[1].split(',')[0]
                lng = google_maps_links[0].split('@')[1].split(',')[1]
                return lat, lng
            else:
                logging.error("Found multiple google maps links")
                logging.info(google_maps_links)
                return None,None

        except:
            logging.error("Geoloc could not be identified.")
            pass

def check_div_exists(driver, div1, div2):
    while True:
        try:
            # Check for the preferred div first
            WebDriverWait(driver, TIMEOUT-10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, div1))
            )
            listing_soup = BeautifulSoup(driver.page_source, 'html.parser')
            return div1, listing_soup  # Preferred div exists

        except TimeoutException:
            try:
                # If the first one doesn't exist, check the other
                WebDriverWait(driver, TIMEOUT-10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, div2))
                )
                listing_soup = BeautifulSoup(driver.page_source, 'html.parser')
                return div2, listing_soup  # Alternative div exists

            except TimeoutException:
                logging.error("No Div Found!! Retrying...")
                pass

def infolist_eval(room_info, infotype, exceptCheck=None):
    if exceptCheck is None:
        infoTxtList = [info.text for _, info in enumerate(room_info) if infotype in info.text]
    else:
        # Catch case with bed and bedroom
        infoTxtList = [info.text for _, info in enumerate(room_info) if infotype in info.text and not exceptCheck in info.text]
    return infoTxtList[0] if len(infoTxtList) > 0 else None

def fetch_properties(driver, div1, div2):
    """Fetches both price and title if one of the divs exists."""
    # Div found tells us if discounted price or not. It has to do with price
    div_found, listing_soup = check_div_exists(driver, div1, div2)

    price = None
    title = None
    guestNum = None
    beds = None
    bedrooms = None
    reviewIndex = None
    characteristics = None

    if div_found:
        try:
            price_element = listing_soup.find('span', class_=div_found.split('.')[1])
            price = price_element.text if price_element else None
        except Exception:  # Be more specific with exception types if needed
            pass  # Handle potential errors during price extraction

        try:
            # Check for the title div only if the first div wasn't found
            title_element = listing_soup.find('h1', class_='atm_9s_1nu9bjl')
            title = title_element.text if title_element else None
        except Exception:
            pass

        try:
            isGuestFav = listing_soup.find('div', class_='lbjrbi0 atm_le_1y44olf atm_lk_1y44olf atm_ll_1y44olf dir dir-ltr')
            isGuestFav = isGuestFav.text if isGuestFav else None
        except Exception:
            pass

        # l7n4lsf atm_9s_1o8liyq_keqd55 dir dir-ltr has multiple information without a specific order. 
        # Needs to be adjusted and with regex identify each cell if it has keyword
        try: 
            room_info = listing_soup.findAll('li', class_='l7n4lsf atm_9s_1o8liyq_keqd55 dir dir-ltr')

            isSuperhost = infolist_eval(room_info, 'Superhost')
            guestNum = infolist_eval(room_info, 'guest')
            bedrooms = infolist_eval(room_info, 'bedroom')
            beds = infolist_eval(room_info, 'bed', 'bedroom')
            baths = infolist_eval(room_info, 'bath')
        except:
            pass

        try:
            if isGuestFav:
                # Find div that includes the guest favorite container
                reviewIndex = listing_soup.find('div', class_ = 'a8jhwcl atm_c8_exq1xd atm_g3_1pezo5y atm_fr_7aerd4 atm_9s_1txwivl atm_ar_1bp4okc atm_h_1h6ojuz atm_cx_t94yts atm_le_14y27yu atm_c8_8nb4eg__14195v1 atm_g3_1dpnnv7__14195v1 atm_fr_11dsdeo__14195v1 atm_cx_1l7b3ar__14195v1 atm_le_1l7b3ar__14195v1 dir dir-ltr').find_all()[1]
            else:
                reviewIndex = listing_soup.find('div', class_='r1lutz1s atm_c8_o7aogt atm_c8_l52nlx__oggzyc dir dir-ltr')

            # None can also be valid when few reviews have been reported
            reviewIndex = reviewIndex.text if reviewIndex else None
        except:
            logging.error('except')
            pass

        try:
            if isGuestFav:
                # Find div that includes the guest favorite container
                reviewNum = listing_soup.find('div', class_ = 'r16onr0j atm_c8_exq1xd atm_g3_1pezo5y atm_fr_7aerd4 atm_gq_myb0kj atm_vv_qvpr2i atm_c8_8nb4eg__14195v1 atm_g3_1dpnnv7__14195v1 atm_fr_11dsdeo__14195v1 atm_gq_idpfg4__14195v1 dir dir-ltr')
            else:
                reviewNum = listing_soup.find('a', class_='l1ovpqvx atm_1y33qqm_1ggndnn_10saat9 atm_17zvjtw_zk357r_10saat9 atm_w3cb4q_il40rs_10saat9 atm_1cumors_fps5y7_10saat9 atm_52zhnh_1s82m0i_10saat9 atm_jiyzzr_1d07xhn_10saat9 b1uxatsa atm_c8_1kw7nm4 atm_bx_1kw7nm4 atm_cd_1kw7nm4 atm_ci_1kw7nm4 atm_g3_1kw7nm4 atm_9j_tlke0l_1nos8r_uv4tnr atm_7l_1kw7nm4_pfnrn2 atm_rd_8stvzk_pfnrn2 c1qih7tm atm_1s_glywfm atm_26_1j28jx2 atm_3f_idpfg4 atm_9j_tlke0l atm_gi_idpfg4 atm_l8_idpfg4 atm_vb_1wugsn5 atm_7l_ujz1go atm_rd_8stvzk atm_5j_mlmjl2 atm_cs_qo5vgd atm_r3_1kw7nm4 atm_mk_h2mmj6 atm_kd_glywfm atm_9j_13gfvf7_1o5j5ji atm_7l_ujz1go_v5whe7 atm_rd_8stvzk_v5whe7 atm_7l_h5wwlf_1nos8r_uv4tnr atm_rd_8stvzk_1nos8r_uv4tnr atm_7l_xgd4j5_4fughm_uv4tnr atm_rd_8stvzk_4fughm_uv4tnr atm_rd_8stvzk_xggcrc_uv4tnr atm_7l_1eisd1c_csw3t1 atm_rd_8stvzk_csw3t1 atm_3f_glywfm_jo46a5 atm_l8_idpfg4_jo46a5 atm_gi_idpfg4_jo46a5 atm_3f_glywfm_1icshfk atm_kd_glywfm_19774hq atm_7l_ujz1go_1w3cfyq atm_rd_8stvzk_1w3cfyq atm_uc_x37zl0_1w3cfyq atm_70_1ocnt96_1w3cfyq atm_uc_glywfm_1w3cfyq_1rrf6b5 atm_7l_ujz1go_18zk5v0 atm_rd_8stvzk_18zk5v0 atm_uc_x37zl0_18zk5v0 atm_70_1ocnt96_18zk5v0 atm_uc_glywfm_18zk5v0_1rrf6b5 atm_7l_xgd4j5_1o5j5ji atm_rd_8stvzk_1o5j5ji atm_rd_8stvzk_1mj13j2 dir dir-ltr')

            # None can also be valid when few reviews have been reported
            reviewNum = reviewNum.text if reviewNum else None
        except:
            logging.error('except2')
            pass

        try:
            # Find hostname 
            hostname = listing_soup.find('div', class_='t1pxe1a4 atm_c8_8ycq01 atm_g3_adnk3f atm_fr_rvubnj atm_cs_qo5vgd dir dir-ltr')
            hostname = hostname.text if hostname else None
        except Exception:
            pass

        try: 
            char_info_container = listing_soup.find('div', class_='i1jq8c6w atm_9s_1txwivl atm_ar_1bp4okc atm_cx_1tcgj5g dir dir-ltr')

            char_info = char_info_container.findAll('h3', class_='hpipapi atm_7l_1kw7nm4 atm_c8_1x4eueo atm_cs_1kw7nm4 atm_g3_1kw7nm4 atm_gi_idpfg4 atm_l8_idpfg4 atm_kd_idpfg4_pfnrn2 dir dir-ltr')
            char_info = [info.text for _, info in enumerate(char_info)]
            characteristics = ", ".join(char_info) if len(char_info)>0 else None
        except:
            pass

        # Catch longtitude, latitude
        try:
            lat, lng = find_geoloc(driver)
        except:
            pass

    return price, title, guestNum, beds, bedrooms, baths, isGuestFav, isSuperhost, reviewIndex, reviewNum, hostname, characteristics, lat, lng


def listing_wrapper(driver, div1, div2):
    price, title, visit_num, beds, bedrooms, baths, isGuestFav, isSuperhost, reviewIndex, reviewNum, hostname, characteristics, lat, lng = fetch_properties(driver, div1, div2)
    logging.info(f"Price: {price}")
    logging.info(f"Title: {title}")
    logging.info(f"Visitors: {visit_num}")
    logging.info(f"Beds: {beds}")
    logging.info(f"Bedrooms: {bedrooms}")
    logging.info(f"Baths: {baths}")
    logging.info(f"Guest Favorite : {isGuestFav}")
    logging.info(f"Superhost : {isSuperhost}")
    logging.info(f"Review Index : {reviewIndex}")
    logging.info(f"Number of reviews : {reviewNum}")
    logging.info(f"Host Name : {hostname}")
    logging.info(f"Characteristics : {characteristics}")
    logging.info(f"Latitude : {lat}")
    logging.info(f"Longitude : {lng}")

    global listing_data_df
    listing_data_df = listing_data_df._append({
        'Price': price,
        'Title': title,
        'Visitors': visit_num,
        'Beds': beds,
        'Bedrooms': bedrooms,
        'Baths': baths,
        'Guest Favorite': isGuestFav,
        'Superhost': isSuperhost,
        'Review Index': reviewIndex,
        'Number of reviews': reviewNum,
        'Host Name': hostname,
        'Characteristics': characteristics,
        'Latitude': lat,
        'Longitude': lng
    }, ignore_index=True)



def scrape_airbnb_listings():
    driver = webdriver.Chrome()
    base_url = "https://www.airbnb.com/s/Thessaloniki/homes"  # Replace with your target search
    driver.get(base_url)
    # Wait five secs to fetch all listings. 
    time.sleep(5)

    current_page = 0

    while True:  # Loop through pages
        current_page += 1
        start_pg_time = time.time()
        if current_page == PAGE_TO_BREAK:
            logging.info(f"Reached page {current_page}, breaking...")
            export_data()
            break

        logging.info(f"Scraping page: {current_page}")

        # Wait for listings to load 
        WebDriverWait(driver, TIMEOUT).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".atm_dz_1osqo2v"))
        )

        html_source = driver.page_source
        soup = BeautifulSoup(html_source, features="lxml")

        listings = soup.find_all('div', class_='atm_dz_1osqo2v')  # Adjust selector if needed

        # Remove first instance as it is not listing
        listings.pop(0)

        logging.info(f"Number of listings found in page {current_page} : {len(listings)}")

        for listing_num, listing in enumerate(listings):
            time.sleep(1.5)
            logging.info("=====================================================================================")
            logging.info(f"Fetching listing {listing_num+1} out of {len(listings)} listings in page {current_page}.")
            try: 
                listing_url = listing.find('a', class_='l1ovpqvx atm_1y33qqm_1ggndnn_10saat9 atm_17zvjtw_zk357r_10saat9 atm_w3cb4q_il40rs_10saat9 atm_1cumors_fps5y7_10saat9 atm_52zhnh_1s82m0i_10saat9 atm_jiyzzr_1d07xhn_10saat9 bn2bl2p atm_5j_8todto atm_9s_1ulexfb atm_e2_1osqo2v atm_fq_idpfg4 atm_mk_stnw88 atm_tk_idpfg4 atm_vy_1osqo2v atm_26_1j28jx2 atm_3f_glywfm atm_kd_glywfm atm_3f_glywfm_jo46a5 atm_l8_idpfg4_jo46a5 atm_gi_idpfg4_jo46a5 atm_3f_glywfm_1icshfk atm_kd_glywfm_19774hq atm_uc_x37zl0_1w3cfyq_oggzyc atm_70_thabx4_1w3cfyq_oggzyc atm_uc_glywfm_1w3cfyq_pynvjw atm_uc_x37zl0_pfnrn2_ivgyl9 atm_70_thabx4_pfnrn2_ivgyl9 atm_uc_glywfm_pfnrn2_61fwbc dir dir-ltr')['href']  # Adjust if needed 
            except:
                logging.error("Increase time wait at initial page fetching.")
                break
            absolute_url = f"https://www.airbnb.com{listing_url}" 
            logging.info(f"URL: {absolute_url}")

            driver.get(absolute_url)

            # Remove translate popup case
            try:
                time.sleep(2)
                popup = driver.find_element(By.XPATH, '/html/body/div[9]/div/div/section/div/div/div[2]/div')
                logging.info("Translate Popup found. Closing...")
                if popup:
                    popup.send_keys(Keys.ESCAPE)
            except:
                logging.info("Translate Popup not found.")

            # Wait to fetch screen
            time.sleep(1)
            driver.execute_script("window.scrollBy(0,4000)")
            time.sleep(1)

            # Single WebDriverWait and fetch properties
            try:
                # _1y74zjx is used when in Guest Favorite mode
                listing_wrapper(driver, 'span._tyxjp1', 'span._1y74zjx')

            except TimeoutException:
                logging.info(f"Listing details not found: {absolute_url}")

            driver.back()  # Go back to the listings page

        logging.info(f"Page fetching time : {time.time() - start_pg_time} seconds. ")

        # Find and click on the "next" button (if it exists)
        try:
            next_button = driver.find_element(By.CSS_SELECTOR, '[aria-label="Next"]')
            next_button.click()
            time.sleep(2)  # Small delay to allow page to load
        except:
            logging.info("Reached the end of the listings!")
            export_data()
            # TODO
            # DataFrame Post Processing
            break

    driver.quit()

scrape_airbnb_listings()
