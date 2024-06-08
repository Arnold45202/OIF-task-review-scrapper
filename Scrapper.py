import csv
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# define my needed variables such as the name and the total number of reviews you would want to scrape 
path_to_csv = "qantas_reviews.csv"
path_to_json = "qantas_reviews.json"
reviews_to_scrape = 1000
reviews_per_page = 5

# this is the formula to count how many pages we would want to scrape
pages_to_scrape = (reviews_to_scrape + reviews_per_page - 1) // reviews_per_page
url = "https://www.tripadvisor.com.au/Airline_Review-d8729133-Reviews-Qantas#REVIEWS"

# set up the chrome driver where it would open up another google chrome 
driver = webdriver.Chrome()  
driver.get(url)

# this is the list for hte json files
reviews_data = []

# this would open up the csv file 
with open(path_to_csv, 'w', encoding="utf-8") as csvFile:
    # for the csv i would have to have an header at the top which is this 
    csvWriter = csv.writer(csvFile)
    csvWriter.writerow(["Date", "Rating", "Title", "Review", "Legroom", "In-flight Entertainment", "Value for Money", "Check-in and Boarding", "Seat Comfort", "Customer Service", "Cleanliness", "Food and Beverage"])

    scraped_reviews = 0
    # iterate through the number of pages of reviews i have to scrape
    for i in range(pages_to_scrape):
        time.sleep(2)

        # this would open up the button to read more to see the individual ratings and see 
        # the whole content review if its really long, this would wait at most 10 seconds
        try:
            expand_buttons = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.XPATH, ".//div[contains(@data-test-target, 'expand-review')]"))
            )
            for button in expand_buttons:
                driver.execute_script("arguments[0].click();", button)
        except Exception as e:
            print(f"Error expanding review: {e}")

        # for the whole page it would find the whole blocks of review containers 
        reviews = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, "//div[@data-reviewid]"))
        )

        # since it is separated we can iterate through the reviews
        for review in reviews:
            if scraped_reviews >= reviews_to_scrape:
                break
            try:
                # extra the part based on their span and the class  and the data-test-target
                rating = review.find_element(By.XPATH, ".//span[contains(@class, 'ui_bubble_rating')]").get_attribute("class").split("_")[3]
                title = review.find_element(By.XPATH, ".//div[@data-test-target='review-title']//span/span").text
                review_text = review.find_element(By.XPATH, ".//span[@data-test-target='review-text']/span").text.replace("\n", "  ")
                date_parent = review.find_element(By.XPATH, ".//span[contains(@class, 'teHYY _R Me S4 H3')]")
                date_text = date_parent.get_attribute("innerText").replace("Date of travel: ", "").strip()
                
                # intialise as each indivudal rating as None 
                legroom = None
                inflight_entertainment = None
                value_for_money = None
                checkin_boarding = None
                seat_comfort = None
                customer_service = None
                cleanliness = None
                food_beverage = None

                # Extract individual ratings
                individual_ratings = review.find_elements(By.XPATH, ".//div[contains(@class, 'hemdC')]")
                for ir in individual_ratings:
                    label = ir.find_element(By.XPATH, ".//span[2]").text
                    rating_value = ir.find_element(By.XPATH, ".//span[contains(@class, 'ui_bubble_rating')]").get_attribute("class").split("_")[3]
                    if label == "Legroom":
                        legroom = rating_value
                    elif label == "In-flight Entertainment":
                        inflight_entertainment = rating_value
                    elif label == "Value for money":
                        value_for_money = rating_value
                    elif label == "Check-in and boarding":
                        checkin_boarding = rating_value
                    elif label == "Seat comfort":
                        seat_comfort = rating_value
                    elif label == "Customer service":
                        customer_service = rating_value
                    elif label == "Cleanliness":
                        cleanliness = rating_value
                    elif label == "Food and Beverage":
                        food_beverage = rating_value

                # this would 
                csvWriter.writerow([date_text, rating, title, review_text, legroom, inflight_entertainment, value_for_money, checkin_boarding, seat_comfort, customer_service, cleanliness, food_beverage])

                # this would append the data that is fetched to load onto the reviews data json file
                reviews_data.append({
                    "Date": date_text,
                    "Rating": rating,
                    "Title": title,
                    "Review": review_text,
                    "ExtraRating": 
                    {
                        "Legroom": legroom,
                        "In-flight Entertainment": inflight_entertainment,
                        "Value for Money": value_for_money,
                        "Check-in and Boarding": checkin_boarding,
                        "Seat Comfort": seat_comfort,
                        "Customer Service": customer_service,
                        "Cleanliness": cleanliness,
                        "Food and Beverage": food_beverage
                    }
                })
                scraped_reviews += 1

            except Exception as e:
                print(f"Error extracting review data: {e}")

        if scraped_reviews >= reviews_to_scrape:
            break

        # this would allow it to navigate to the next page after it has been scraped
        # it would wait at most ten seconds for it to load
        try:
            next_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, './/a[contains(@class, "ui_button nav next primary ")]'))
            )
            driver.execute_script("arguments[0].click();", next_button)
        except Exception as e:
            print(f"Error navigating to next page: {e}")
            break

driver.quit()

# this would write the json list into this json file
with open(path_to_json, 'w', encoding="utf-8") as jsonFile:
    json.dump(reviews_data, jsonFile, ensure_ascii=False, indent=4)
