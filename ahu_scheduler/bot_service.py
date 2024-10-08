import json
import logging
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from functools import partial
from .web_driver import get_courses
import os

from WeworkBot import *

class CourseReminderBot:
    def __init__(
        self,
        config_file: str = "config.json",
        course_file: str = "courses.json",
        log_file: str = "course_reminder.log",
    ):
        """
        初始化课程提醒机器人实例

        :param config_file: 配置文件路径
        :param course_file: 课程文件路径
        :param log_file: 日志文件路径
        """
        self.setup_logging(log_file)
        self.load_config(config_file)
        self.course_file = course_file
        if not os.path.exists(course_file):
            logging.error("课程文件不存在，开始获取课程信息")
            get_courses(self.student_id, self.password, course_file)
            logging.info(f"课程信息获取成功，保存到 {course_file}")
        self.scheduler = BackgroundScheduler()
        self.load_courses()
        self.schedule_weekly_update()
        setup_msg=(
            f"主人，您的课程管家已上线！\n"
            f"当前周数：{self.current_week}\n"
            f"提前提醒分钟数：{self.reminder_minutes}\n"
            f"已加载 {len(self.course_schedule)} 门课程\n"
            f"请耐心等待课程提醒消息，竭诚为您服务！"
        )
        msg_server.send_text_message("JiYuan",setup_msg)

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
        logging.getLogger("flask").setLevel(logging.WARNING)
        logging.getLogger("werkzeug").setLevel(logging.WARNING)

    def load_config(self, config_file):
        """
        加载配置文件，获取机器人信息和当前周数

        :param config_file: 配置文件路径
        """
        try:
            with open(config_file, "r", encoding="utf-8") as file:
                config = json.load(file)
                self.webhook_urls = config.get("webhook_urls", [])
                self.current_week = config.get("current_week", 1)
                self.reminder_minutes = config.get("reminder_minutes", 30)
                self.student_id = config.get("student_id", "")
                self.password = config.get("password", "")
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
                f"主人，您有一门课即将开始：\n"
                f"- 课程名称：{course['name']}\n"
                f"- 上课时间：{course['start_time']} - {course['end_time']}\n"
                f"- 上课地点：{course['location']}\n"
                f"- 任课教师：{course['teacher']}\n\n"
                f"请及时参加课程，祝学习愉快！"
            )
            if msg_server.send_text_message("JiYuan",content):
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
        with open("config.json", "r", encoding="utf-8") as file:
            config = json.load(file)
            config["current_week"] = self.current_week
        with open("config.json", "w", encoding="utf-8") as file:
            json.dump(config, file, ensure_ascii=False, indent=4)
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
        except (KeyboardInterrupt, SystemExit):
            self.scheduler.shutdown()
            logging.info("调度器已关闭")


def start_bot_server():
    """
    启动服务
    """
    reminder_bot = CourseReminderBot()
    reminder_bot.run()
    msg_server.start_server()

# 使用示例
if __name__ == "__main__":
    start_bot_server()