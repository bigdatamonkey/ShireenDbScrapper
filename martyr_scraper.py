from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import csv
from urllib.parse import urljoin

def scrape_martyrs(url, output_csv, max_pages):
    # Initialize the service and WebDriver with headless mode
    options = Options()
    options.add_argument('--headless')  # Run in headless mode

    driver = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()), options=options)

    try:
        driver.get(url)

        # Use WebDriverWait instead of time.sleep() for page load waiting
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.myrcard')))

        with open(output_csv, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['ID','Martyr Type', 'Martyr Name','Martyr Age' ,'Martyr Location', 'Martyr Date']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            total_martyrs_found = 0  # Track the total number of martyrs found

            for page_number in range(max_pages):
                print(f"Scraping Page {page_number + 1}")
                soup = BeautifulSoup(driver.page_source, 'html.parser')
                martyr_cards = soup.find_all('div', class_='myrcard')

                if not martyr_cards:
                    print("No more pages to scrape.")
                    break  # No more pages

                for card_index, card in enumerate(martyr_cards, start=1):
                    martyr_id = card.get('data-id')
                    martyr_type = card.find('span').text
                    martyr_name = card.find('div', class_='mname').text
                    martyr_info = card.find('div', class_='martSubInfo').text
                    martyr_date = card.find('div', class_='martSubInfoDate').text
                    # Extracting location and age using a different approach
                    location, _, age_part = martyr_info.partition(',')
                    martyr_age = age_part.split()[0] if age_part else None
                    
                    writer.writerow({
                        'ID': martyr_id,
                        'Martyr Type': martyr_type,
                        'Martyr Name': martyr_name,
                        'Martyr Age': martyr_age,
                        'Martyr Location': location.strip(),
                        'Martyr Date': martyr_date
                    })

                    total_martyrs_found += 1
                    print(f"Martyr {total_martyrs_found} - Type: {martyr_type}, Name: {martyr_name}, Location: {location.strip()}, Date: {martyr_date}")

                try:
                    # Increase the page number in the URL
                    next_page_url = urljoin(url, f'#page-{page_number + 2}')
                    driver.get(next_page_url)

                    # Use WebDriverWait to wait for the presence of myrcard elements on the new page
                    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.myrcard')))
                except NoSuchElementException as e:
                    print(f"Failed to navigate to the next page: {e}")
                    break
                except TimeoutException:
                    print("Timed out waiting for myrcard elements on the new page.")
                    break

    finally:
        print(f"Total Martyrs Found: {total_martyrs_found}")

        # Remember to close the WebDriver when done
        driver.quit()

# Replace 'your_url_here' with the actual URL of the website
# Replace 'output.csv' with the desired output CSV file name
website_url = 'https://www.shireen.ps/martyrs/year/2024#page-1'
output_csv = 'output_test.csv'
max_pages = 1  # Pass max_pages as an integer
scrape_martyrs(website_url, output_csv, max_pages)