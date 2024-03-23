import time 
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from selenium.common.exceptions import TimeoutException
import time

TIMEOUT=30


def check_div_exists(driver, div1, div2):
    try:
        # Check for the preferred div first
        WebDriverWait(driver, TIMEOUT-20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, div1))
        )
        listing_soup = BeautifulSoup(driver.page_source, 'html.parser')
        return div1, listing_soup  # Preferred div exists

    except TimeoutException:
        try:
            # If the first one doesn't exist, check the other
            WebDriverWait(driver, TIMEOUT).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, div2))
            )
            listing_soup = BeautifulSoup(driver.page_source, 'html.parser')
            return div2, listing_soup  # Alternative div exists

        except TimeoutException:
            print("No Div Found!!")
            return None, None  # Neither div exists

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
            # guestFavBehave = True if isGuestFav is not None else False

            if isGuestFav:
                # Find div that includes the guest favorite container
                reviewIndex = listing_soup.find('div', class_ = 'a8jhwcl atm_c8_exq1xd atm_g3_1pezo5y atm_fr_7aerd4 atm_9s_1txwivl atm_ar_1bp4okc atm_h_1h6ojuz atm_cx_t94yts atm_le_14y27yu atm_c8_8nb4eg__14195v1 atm_g3_1dpnnv7__14195v1 atm_fr_11dsdeo__14195v1 atm_cx_1l7b3ar__14195v1 atm_le_1l7b3ar__14195v1 dir dir-ltr').find_all()[1]
            else:
                reviewIndex = listing_soup.find('div', class_='r1lutz1s atm_c8_o7aogt atm_c8_l52nlx__oggzyc dir dir-ltr')

            # None can also be valid when few reviews have been reported
            reviewIndex = reviewIndex.text if reviewIndex else None

        except:
            print('except')
            pass

    return price, title, guestNum, beds, bedrooms, baths, isGuestFav, isSuperhost, reviewIndex


def listing_wrapper(driver, div1, div2):
    price, title, visit_num, beds, bedrooms, baths, isGuestFav, isSuperhost, reviewIndex = fetch_properties(driver, div1, div2)
    print(f"Price: {price}")
    print(f"Title: {title}")
    print(f"Visitors: {visit_num}")
    print(f"Beds: {beds}")
    print(f"Bedrooms: {bedrooms}")
    print(f"Baths: {baths}")
    print(f"Guest Favorite : {isGuestFav}")
    print(f"Superhost : {isSuperhost}")
    print(f"Review Index : {reviewIndex}")



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
        if current_page == 2:
            break

        print(f"Scraping page: {current_page}")

        # Wait for listings to load 
        WebDriverWait(driver, TIMEOUT).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".atm_dz_1osqo2v"))
        )

        html_source = driver.page_source
        soup = BeautifulSoup(html_source, features="lxml")

        listings = soup.find_all('div', class_='atm_dz_1osqo2v')  # Adjust selector if needed

        # Remove first instance as it is not listing
        listings.pop(0)

        print(f"Number of listings found in page {current_page} : {len(listings)}")

        for listing in listings:
            time.sleep(1.5)
            print("=====================================================================================")
            try: 
                listing_url = listing.find('a', class_='atm_uc_glywfm_18zk5v0_pynvjw')['href']  # Adjust if needed 
            except:
                print("Increase time wait at initial page fetching.")
                break
            absolute_url = f"https://www.airbnb.com{listing_url}" 
            print(f"Fetching: {absolute_url}")

            driver.get(absolute_url)

            # Single WebDriverWait and fetch properties
            try:
                # _1y74zjx is used when in Guest Favorite mode
                listing_wrapper(driver, 'span._tyxjp1', 'span._1y74zjx')

            except TimeoutException:
                print(f"Listing details not found: {absolute_url}")

            driver.back()  # Go back to the listings page

        print(f"Page fetching time : {time.time() - start_pg_time} seconds. ")

        # Find and click on the "next" button (if it exists)
        try:
            next_button = driver.find_element(By.CSS_SELECTOR, '[aria-label="Next"]')
            next_button.click()
            time.sleep(2)  # Small delay to allow page to load
        except:
            print("Reached the end of the listings!")
            break

    driver.quit()

scrape_airbnb_listings()
