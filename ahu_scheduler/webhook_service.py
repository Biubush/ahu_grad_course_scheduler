import json
import logging
import time
import requests
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from functools import partial
import os
from .web_driver import get_courses


class WeChatBot:
    """
    企业微信群机器人客户端，只可以发送文本消息

    :param webhook_urls: webhook URL的列表，可以传入一个或多个webhook URL。
    """

    def __init__(self, webhook_urls):
        if isinstance(webhook_urls, str):
            # 如果只传入一个webhook URL，将其转换为列表
            self.webhook_urls = [webhook_urls]
        else:
            self.webhook_urls = webhook_urls

    def send_text(self, content, mentioned_list=None, mentioned_mobile_list=None):
        """
        发送文本消息。

        :param content: 消息内容。
        :param mentioned_list: 要@的成员ID列表。
        :param mentioned_mobile_list: 要@的成员手机号列表。
        """
        data = {
            "msgtype": "text",
            "text": {
                "content": content,
                "mentioned_list": mentioned_list or [],
                "mentioned_mobile_list": mentioned_mobile_list or [],
            },
        }
        return self._send(data, "text")

    def _send(self, data, msg_type, webhook_url=None):
        """
        发送消息到指定的webhook URL。

        :param data: 要发送的消息数据。
        :param msg_type: 消息类型。
        :param webhook_url: 要发送的webhook URL，如果不指定，则发送到所有webhook URLs。
        """
        if webhook_url is None:
            webhooks = self.webhook_urls
        else:
            webhooks = [webhook_url]

        for webhook in webhooks:
            headers = {"Content-Type": "application/json"}
            response = requests.post(webhook, headers=headers, data=json.dumps(data))
            if response.status_code != 200 or response.json()["errcode"] != 0:
                print(f"Error sending {msg_type} message: {response.json()}")
                return False
        return True


class CourseReminderBot:
    def __init__(
        self,
        config_file: str = "config.json",
        course_file: str = "courses.json",
        log_file: str = "course_scheduler.log",
    ):
        """
        初始化课程提醒机器人实例

        :param config_file: 配置文件路径
        :param course_file: 课程文件路径
        :param log_file: 日志文件路径
        """
        self.config_file = config_file
        self.setup_logging(log_file)
        self.load_config(config_file)
        self.course_file = course_file
        if not os.path.exists(course_file):
            logging.error("课程文件不存在，开始获取课程信息")
            get_courses(self.student_id, self.password, course_file)
            logging.info(f"课程信息获取成功，保存到 {course_file}")

        self.bot = WeChatBot(self.webhook_urls)
        self.scheduler = BackgroundScheduler()
        self.load_courses()
        self.schedule_weekly_update()
        setup_msg=(
            f"少爷，您的课程管家已上线！\n"
            f"当前周数：{self.current_week}\n"
            f"提前提醒分钟数：{self.reminder_minutes}\n"
            f"已加载 {len(self.course_schedule)} 门课程\n"
            f"请耐心等待课程提醒消息，竭诚为您服务！"
        )
        weeks_list=['一','二','三','四','五','六','日']
        # 按照星期排序courses_msg
        courses_msg=""
        for i in range(1,8):
            courses_msg+=f"{'——'*7}\n星期{weeks_list[i-1]}\n"
            exist=False
            for course in self.course_schedule:
                if course['day_of_week']==i:
                    courses_msg+=f"{'-'*30}\n课程名称：{course['name']}\n上课周数：{course['start_week']} - {course['end_week']}\n上课时间：{course['start_time']} - {course['end_time']}\n上课地点：{course['location']}\n任课教师：{course['teacher']}\n"
                    exist=True
            if not exist:
                courses_msg+="无课程\n"
        self.bot.send_text(setup_msg)
        self.bot.send_text(f"载入的课程数据如下：\n"+courses_msg)

    def setup_logging(self, log_file):
        """
        设置日志记录配置

        :param log_file: 日志文件路径
        """
        logging.basicConfig(
            filename=log_file,
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            encoding="utf-8",
        )
        logging.getLogger("apscheduler").setLevel(logging.WARNING)

    def load_config(self, config_file):
        """
        加载配置文件，获取机器人信息和当前周数

        :param config_file: 配置文件路径
        """
        try:
            with open(config_file, "r", encoding="utf-8") as file:
                config = json.load(file)
                self.student_id = config.get("student_id", "")
                self.password = config.get("password", "")
                self.webhook_urls = config.get("webhook_urls", [])
                self.current_week = config.get("current_week", 1)
                self.reminder_minutes = config.get("reminder_minutes", 30)
                logging.info(
                    f"当前周数：{self.current_week}，提醒分钟数：{self.reminder_minutes}"
                )
        except Exception as e:
            logging.error(f"加载配置失败: {e}")
            raise

    def load_courses(self):
        """
        加载课程文件，获取课程安排
        """
        try:
            with open(self.course_file, "r", encoding="utf-8") as file:
                self.course_schedule = json.load(file)
        except Exception as e:
            logging.error(f"加载课程失败: {e}")
            raise

    def remind_course(self, course):
        """
        发送课程提醒消息

        :param course: 课程信息字典
        """
        current_day_of_week = datetime.now().weekday() + 1
        if self.current_week < course["start_week"] or self.current_week > course["end_week"]:
            logging.info(f"课程 {course['name']} 不在上课周内，不发送提醒消息")
            return

        if course["day_of_week"] != current_day_of_week:
            logging.info(f"课程 {course['name']} 的上课日与当前日不同，不发送提醒消息")
            return
        
        try:
            content = (
                f"少爷，您有一门课即将开始：\n"
                f"- 课程名称：{course['name']}\n"
                f"- 上课时间：{course['start_time']} - {course['end_time']}\n"
                f"- 上课地点：{course['location']}\n"
                f"- 任课教师：{course['teacher']}\n\n"
                f"请及时参加课程，祝学习愉快！"
            )
            if self.bot.send_text(content):
                logging.info(f"已发送提醒消息：{course['name']} 的课程即将开始")
            else:
                logging.error(f"发送提醒消息失败：{course['name']} 的课程即将开始")
        except Exception as e:
            logging.error(f"发送提醒消息时发生错误: {e}")

    def schedule_courses(self):
        """
        根据课程安排设置提醒任务
        """
        for course in self.course_schedule:
            try:
                start_time_str = course["start_time"]
                if (
                    not isinstance(start_time_str, str)
                    or len(start_time_str.split(":")) != 2
                ):
                    logging.error(
                        f"课程 {course.get('name', '未知课程')} 的开始时间格式不正确"
                    )
                    continue

                start_time = datetime.strptime(start_time_str, "%H:%M").time()
                reminder_minutes = (
                    start_time.minute - self.reminder_minutes
                )  # 使用实例属性
                reminder_hour = (
                    start_time.hour if reminder_minutes >= 0 else start_time.hour - 1
                )
                reminder_minute = (
                    reminder_minutes % 60
                    if reminder_minutes >= 0
                    else (reminder_minutes + 60) % 60
                )

                time_stamp = datetime.now().timestamp()
                job_id = f"{course['name'].replace(' ', '_')}_{start_time_str.replace(':', '_')}_{time_stamp}"

                if self.scheduler.get_job(job_id):
                    self.scheduler.reschedule_job(
                        job_id,
                        trigger="cron",
                        hour=reminder_hour % 24,
                        minute=reminder_minute,
                    )
                    logging.info(f"重新安排了课程 {course['name']} 的提醒任务")
                else:
                    self.scheduler.add_job(
                        func=partial(self.remind_course, course),
                        trigger="cron",
                        hour=reminder_hour % 24,
                        minute=reminder_minute,
                        id=job_id,
                        name=f"{course['name']} 的课程提醒任务",
                    )
                    logging.info(f"为课程 {course['name']} 设置了提醒任务")
            except KeyError as e:
                logging.error(f"课程信息缺失: {e}")
            except Exception as e:
                logging.error(f"设置任务时发生错误: {e}")

    def update_current_week(self):
        """
        更新当前周数，并保存到配置文件
        """
        self.current_week += 1
        tmp_data=None
        with open(self.course_file, "r", encoding="utf-8") as file:
            tmp_data=json.load(file)
        tmp_data["current_week"]=self.current_week
        with open(self.course_file, "w", encoding="utf-8") as file:
            json.dump(tmp_data,file,ensure_ascii=False,indent=4)
        logging.info(f"当前周数已更新为：{self.current_week}")

    def schedule_weekly_update(self):
        """
        设置每周一凌晨1点更新当前周数的任务
        """
        self.scheduler.add_job(
            func=self.update_current_week,
            trigger="cron",
            day_of_week='mon',
            hour=1,
            minute=0,
            name="每周一更新当前周数任务",
        )


    def run(self):
        """
        启动调度器，并持续运行
        """
        self.schedule_courses()
        try:
            self.scheduler.start()
            logging.info("调度器已启动")
            while True:
                time.sleep(1)
        except (KeyboardInterrupt, SystemExit):
            self.scheduler.shutdown()
            logging.info("调度器已关闭")


# 使用示例
if __name__ == "__main__":
    reminder_bot = CourseReminderBot()
    reminder_bot.run()
