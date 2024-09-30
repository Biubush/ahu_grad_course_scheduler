import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
from bs4 import BeautifulSoup
import re

def parse_courses(html_content:str,output_path:str):
    try:

        # 解析 HTML
        soup = BeautifulSoup(html_content, 'html.parser')
        courses = []

        time_table={
            '上午1': ["08:00", "08:45"],
            '上午2': ["08:50", "09:35"],
            '上午3': ["09:50", "10:35"],
            '上午4': ["10:40", "11:25"],
            '上午5': ["11:30", "12:15"],
            '下午6': ["14:00", "14:45"],
            '下午7': ["14:50", "15:35"],
            '下午8': ["15:50", "16:35"],
            '下午9': ["16:40", "17:25"],
            '下午10': ["17:30", "18:15"],
            '晚上11': ["19:00", "19:45"],
            '晚上12': ["19:50", "20:35"],
            '晚上13': ["20:40", "21:25"],
            '晚上14': ["21:30", "22:15"]
        }

        # 提取课程信息
        for item in soup.find_all("div", class_="listItem1"):
            course_info = {}
            
            # 提取课程基本信息
            label = item.find("ion-label")
            if label:
                course_info['name'] = label.text.split('[')[0].strip()  # 课程名称
            
            # 提取详细信息
            details = item.find("div", class_="box-y")
            if details:
                course_info['teacher'] = details.find_all("label")[0].text.split('：')[1].strip()  # 主讲
                course_info['class'] = details.find_all("label")[1].text.split('：')[1].strip()  # 班级
                
                # 提取时间并解析
                time_info = details.find_all("label")[2].text.split('：')[1].strip()
                week_match = re.findall(r'(\d+)-(\d+)周', time_info)
                if week_match:
                    course_info['start_week'] = int(week_match[0][0])  # 起始周
                    course_info['end_week'] = int(week_match[0][1])  # 结束周
                
                day_match = re.findall(r'周([一二三四五六日])', time_info)
                if day_match:
                    day_of_week_mapping = {
                        '一': 1,
                        '二': 2,
                        '三': 3,
                        '四': 4,
                        '五': 5,
                        '六': 6,
                        '日': 7
                    }
                    course_info['day_of_week'] = day_of_week_mapping[day_match[0]]  # 星期几

                # 提取时间段
                period_match = re.findall(r'([上中下]午\d+|晚上\d+)-([上中下]午\d+|晚上\d+)', time_info)
                # 补充时间段，提取time_info中day_match后的所有字符
                period_info = time_info.split('周')[-1][1:]
                if '-' in period_info:
                    start_period = period_match[0][0]
                    end_period = period_match[0][1]
                else:
                    start_period = period_info
                    end_period = period_info
                course_info['start_time'] = time_table[start_period][0]
                course_info['end_time'] = time_table[end_period][-1]
                course_info['start_period'] = start_period
                course_info['end_period'] = end_period
                course_info['location'] = details.find_all("label")[3].text.split('：')[1].strip()  # 地点

            courses.append(course_info)

        # 将数据存储为 JSON 文件
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(courses, f, ensure_ascii=False, indent=4)
    except Exception as e:
        return None

def get_courses(student_id:str,password:str,output_path:str='courses.json'):
    try:
        # 启动 undetected-chromedriver
        options = uc.ChromeOptions()
        options.add_argument("--disable-gpu")
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        driver = uc.Chrome(options=options)

        # 打开指定的 URL
        driver.get("https://gmisapp.ahu.edu.cn/SmartGmis5_0/www/index.html")

        # 等待输入框可见并输入学号
        username_xpath = (
            "/html/body/ion-app/ng-component/ion-nav/page-login/ion-content/div[2]/div[3]/input"
        )
        WebDriverWait(driver, 20).until(
            EC.visibility_of_element_located((By.XPATH, username_xpath))
        )
        driver.find_element(By.XPATH, username_xpath).send_keys(student_id)

        # 等待输入框可见并输入密码
        password_xpath = (
            "/html/body/ion-app/ng-component/ion-nav/page-login/ion-content/div[2]/div[4]/input"
        )
        WebDriverWait(driver, 20).until(
            EC.visibility_of_element_located((By.XPATH, password_xpath))
        )
        driver.find_element(By.XPATH, password_xpath).send_keys(password)

        # 点击登录按钮
        login_button_xpath = "/html/body/ion-app/ng-component/ion-nav/page-login/ion-content/div[2]/div[5]/button"
        WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, login_button_xpath))
        )
        driver.find_element(By.XPATH, login_button_xpath).click()

        # 等待页面加载完成并点击底部栏
        icon_xpath = "//*[@id='tab-t0-1']/ion-icon"
        WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, icon_xpath)))
        driver.find_element(By.XPATH, icon_xpath).click()

        # 点击指定的页面
        image_xpath = (
            "//*[@id='tabpanel-t0-1']/page-xueye/ion-content/div[2]/div[2]/div[2]/div[4]/img"
        )
        WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, image_xpath)))
        driver.find_element(By.XPATH, image_xpath).click()

        # 等待课表加载完成，获取课表部分的 HTML
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CLASS_NAME, "box-y"))
        )
        result_xpath = "/html/body/ion-app/ng-component/ion-nav/ng-component/ion-tabs/page-xkjg/ion-content/div[2]"
        outer_html = driver.find_element(By.XPATH, result_xpath).get_attribute("outerHTML")

        # 解析 HTML 并保存数据
        parse_courses(outer_html,output_path)

        # 确保浏览器被正确关闭
        driver.quit()
        return output_path
    except Exception as e:
        print(e)
        return None
    
if __name__ == "__main__":
    student_id = "YOUR_STUDENT_ID"
    password = "YOUR_PASSWORD"
    output_path = 'courses.json'
    get_courses(student_id,password,output_path)