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

# 配置 Selenium WebDriver
chrome_options = Options()
chrome_options.add_argument("--headless")  # 无头模式，不显示浏览器界面
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

def get_problem_list(page_number):
    # 启动 WebDriver
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(BASE_URL.format(page_number))
    
    # 检查页面是否正确加载
    #time.sleep(1)  # 增加静态等待时间，确保页面有足够时间加载
    print(f"第 {page_number} 页：正在加载页面内容...")
    
    try:
        # 等待问题行加载完成
        WebDriverWait(driver, 20).until(
            EC.visibility_of_element_located((By.CLASS_NAME, "_row_15kiv_90"))
        )
    except Exception as e:
        print(f"第 {page_number} 页加载问题列表时出错：", e)
        driver.quit()
        return []
    
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    problem_rows = soup.find_all("tr", class_="_row_15kiv_90")
    
    problems = []
    for row in problem_rows:
        td_elements = row.find_all("td")
        #print(td_elements)
        id_tag = td_elements[0].find("b")  # 提取问题 ID
        title_tag = td_elements[1].find("a", href=True)  # 提取问题名称
        submission_count_tag = td_elements[2]  # 提取提交数量
        acceptance_rate_tag = td_elements[3]  # 提取通过率
        
        if id_tag and title_tag and submission_count_tag and acceptance_rate_tag:
            problem_id = id_tag.text.strip()  # 提取问题 ID
            problem_name = title_tag.text.strip()  # 提取问题名称
            submission_count = submission_count_tag.text.strip()  # 提取提交数量
            acceptance_rate = acceptance_rate_tag.text.strip()  # 提取通过率
            problems.append({
                "id": problem_id,
                "name": problem_name,
                "submission_count": submission_count,
                "acceptance_rate": acceptance_rate
            })
    
    driver.quit()
    return problems

def main():
    all_problem_details = []
    
    # 遍历所有 67 页
    for page_number in range(1, 68):
        problems = get_problem_list(page_number)
        all_problem_details.extend(problems)
       # time.sleep(1)  # 避免对服务器造成过大请求压力
    
    # 将数据保存到 CSV 文件
    with open("loj_problems_details.csv", "w", newline='', encoding='utf-8-sig') as csvfile:
        fieldnames = ["id", "name", "submission_count", "acceptance_rate"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for detail in all_problem_details:
            writer.writerow(detail)

if __name__ == "__main__":
    main()
