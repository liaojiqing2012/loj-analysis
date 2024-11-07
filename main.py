import requests
from bs4 import BeautifulSoup
import time
import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

BASE_URL = "https://loj.ac/p?page={}"

# Configure Selenium WebDriver
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

def get_problem_list(page_number):
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(BASE_URL.format(page_number))
    
    # Check the page source to see if it's loaded properly
    time.sleep(5)  # Increase static wait to ensure the page has enough time to load
    print(f"Page {page_number}: Loading page source...")
    
    try:
        # Wait until the problem rows are loaded
        WebDriverWait(driver, 20).until(
            EC.visibility_of_element_located((By.CLASS_NAME, "_row_15kiv_90"))
        )
    except Exception as e:
        print(f"Error loading problem list page {page_number}:", e)
        driver.quit()
        return []
    
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    problem_rows = soup.find_all("tr", class_="_row_15kiv_90")
    
    problems = []
    for row in problem_rows:
        title_tag = row.find("a", href=True)
        submission_count_tag = row.find_all("td")[2]
        acceptance_rate_tag = row.find_all("td")[3]
        
        if title_tag and submission_count_tag and acceptance_rate_tag:
            problem_name = title_tag.text.strip()
            submission_count = submission_count_tag.text.strip()
            acceptance_rate = acceptance_rate_tag.text.strip()
            problems.append({
                "name": problem_name,
                "submission_count": submission_count,
                "acceptance_rate": acceptance_rate
            })
    
    driver.quit()
    return problems

def main():
    all_problem_details = []
    
    # Loop through all 67 pages
    for page_number in range(1, 68):
        problems = get_problem_list(page_number)
        all_problem_details.extend(problems)
        time.sleep(1)  # To avoid overwhelming the server with requests
    
    # Save the data to a CSV file
    with open("loj_problems_details.csv", "w", newline='', encoding='utf-8-sig') as csvfile:
        fieldnames = ["name", "submission_count", "acceptance_rate"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for detail in all_problem_details:
            writer.writerow(detail)

if __name__ == "__main__":
    main()
