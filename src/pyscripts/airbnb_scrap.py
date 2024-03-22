import time 
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from selenium.common.exceptions import TimeoutException

TIMEOUT=30


def check_div_exists(driver, div1, div2):
    try:
        # Check for the preferred div first
        WebDriverWait(driver, TIMEOUT).until(
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
            return None, None  # Neither div exists


def fetch_properties(driver, div1, div2):
    """Fetches both price and title if one of the divs exists."""
    div_found, listing_soup = check_div_exists(driver, div1, div2)

    price = None
    title = None
    visit_num = None
    beds = None
    bedrooms = None

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
            visit_num = listing_soup.findAll('li', class_='l7n4lsf atm_9s_1o8liyq_keqd55 dir dir-ltr')[0]
            visit_num = visit_num.text if visit_num else None
        except Exception:
            pass

        try:
            beds = listing_soup.findAll('li', class_='l7n4lsf atm_9s_1o8liyq_keqd55 dir dir-ltr')[2]
            beds = beds.text if beds else None
        except Exception:
            pass

        try:
            bedrooms = listing_soup.findAll('li', class_='l7n4lsf atm_9s_1o8liyq_keqd55 dir dir-ltr')[1]
            bedrooms = bedrooms.text if bedrooms else None
        except Exception:
            pass

        try:
            baths = listing_soup.findAll('li', class_='l7n4lsf atm_9s_1o8liyq_keqd55 dir dir-ltr')[3]
            baths = baths.text if baths else None
        except Exception:
            pass

        try:
            isGuestFav = listing_soup.find('div', class_='lbjrbi0 atm_le_1y44olf atm_lk_1y44olf atm_ll_1y44olf dir dir-ltr')
            isGuestFav = isGuestFav.text if isGuestFav else None
        except Exception:
            pass

        try:
            isSuperhost = listing_soup.findAll('li', class_='l7n4lsf atm_9s_1o8liyq_keqd55 dir dir-ltr')[4]
            isSuperhost = isSuperhost.text if 'Superhost' in isSuperhost else None
        except Exception:
            pass

        

    return price, title, visit_num, beds, bedrooms, baths, isGuestFav, isSuperhost


def listing_wrapper(driver, div1, div2):
    price, title, visit_num, beds, bedrooms, baths, isGuestFav, isSuperhost = fetch_properties(driver, div1, div2)
    print(f"Price: {price}")
    print(f"Title: {title}")
    print(f"Visitors: {visit_num}")
    print(f"Beds: {beds}")
    print(f"Bedrooms: {bedrooms}")
    print(f"Baths: {baths}")
    print(f"Guest Favorite : {isGuestFav}")
    print(f"Superhost : {isSuperhost}")



def scrape_airbnb_listings():
    driver = webdriver.Chrome()
    base_url = "https://www.airbnb.com/s/Thessaloniki/homes"  # Replace with your target search
    driver.get(base_url)
    time.sleep(5)

    current_page = 0

    while True:  # Loop through pages
        if current_page == 2:
            break
        current_page += 1
        print(f"Scraping page: {current_page}")

        # Wait for listings to load 
        WebDriverWait(driver, TIMEOUT).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".atm_9s_1txwivl"))
        )

        html_source = driver.page_source
        soup = BeautifulSoup(html_source)

        listings = soup.find_all('div', class_='atm_dz_1osqo2v')  # Adjust selector if needed
        print(len(listings))

        # Remove first instance as it is not listing
        listings.pop(0)

        for listing in listings:
            print("=====================================================================================")
            listing_url = listing.find('a', class_='atm_uc_glywfm_18zk5v0_pynvjw')['href']  # Adjust if needed 
            absolute_url = f"https://www.airbnb.com{listing_url}" 
            print(f"Fetching: {absolute_url}")

            driver.get(absolute_url)

            # Single WebDriverWait and fetch properties
            try:
                WebDriverWait(driver, TIMEOUT).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'span._tyxjp1, span._1y74zjx'))
                    # Check for either the price or title element
                )
                listing_wrapper(driver, 'span._tyxjp1', 'span._1y74zjx')

            except TimeoutException:
                print(f"Listing details not found: {absolute_url}")

            driver.back()  # Go back to the listings page

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
