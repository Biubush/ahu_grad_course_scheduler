import json
from datetime import datetime

# 关键词处理函数字典
keyword_handlers = {}
course_schedule = {}


def keyword_handler(keyword):
    def decorator(func):
        keyword_handlers[keyword] = func
        return func

    return decorator


def get_current_week(config_file: str = "config.json"):
    """
    初始化函数，加载课程表
    """
    load_courses()
    try:
        with open(config_file, "r", encoding="utf-8") as file:
            config = json.load(file)
            current_week = config.get("current_week", 1)
            return current_week
    except Exception as e:
        raise


def load_courses(course_file: str = "courses.json"):
    """
    加载课程文件，获取课程安排
    """
    try:
        with open(course_file, "r", encoding="utf-8") as file:
            global course_schedule
            course_schedule = json.load(file)
    except Exception as e:
        raise


@keyword_handler("你好")
def handle_hello(content, msg):
    return f"你好, {msg['from_user']}!"


@keyword_handler("帮助")
def handle_help(content, msg):
    instructions = "目前支持的命令有：\n"
    for keyword in keyword_handlers.keys():
        instructions += f"     {keyword}\n"
    return instructions


@keyword_handler("今天")
def handle_schedule(content, msg):
    load_courses()
    current_day_of_week = datetime.now().weekday() + 1
    today_courses = []
    current_week = get_current_week()
    for course in course_schedule:
        if course["start_week"] > current_week or course["end_week"] < current_week:
            continue
        if course["day_of_week"] != current_day_of_week:
            continue
        today_courses.append(course)
    if len(today_courses) == 0:
        return "今天没有课程哦！"
    else:
        rt_msg = "今天有以下课程：\n"
        # 取索引和值
        for index, course in enumerate(today_courses):
            rt_msg += f"{index+1}.{course['course_name']}\n    课程时间：{course['start_time']}~{course['end_time']}\n    位置：{course['location']}\n    老师：{course['instructor_name']}\n"
        return rt_msg


@keyword_handler("明天")
def handle_schedule(content, msg):
    load_courses()
    current_day_of_week = datetime.now().weekday() + 1
    tomorrow_day_of_week = current_day_of_week + 1 if current_day_of_week < 7 else 1
    tomorrow_courses = []
    target_week = get_current_week()

    if tomorrow_day_of_week == 1:
        target_week += 1

    for course in course_schedule:
        if course["start_week"] > target_week or course["end_week"] < target_week:
            continue
        if course["day_of_week"] != tomorrow_day_of_week:
            continue
        tomorrow_courses.append(course)
    if len(tomorrow_courses) == 0:
        return "明天没有课程哦！"
    else:
        rt_msg = "明天有以下课程：\n"
        for index, course in enumerate(tomorrow_courses):
            rt_msg += f"{index+1}.{course['course_name']}\n    课程时间：{course['start_time']}~{course['end_time']}\n    位置：{course['location']}\n    老师：{course['instructor_name']}\n"
        return rt_msg


@keyword_handler("本周")
def handle_schedule(content, msg):
    load_courses()
    week_courses = []
    current_week = get_current_week()
    for course in course_schedule:
        if course["start_week"] > current_week or course["end_week"] < current_week:
            continue
        week_courses.append(course)
    if len(week_courses) == 0:
        return "本周没有课程哦！"
    else:
        rt_msg = f"本周(第{current_week}周)有以下课程：\n"
        weeks = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
        # 按星期顺序输出各个课程
        for i in range(1, 8):
            day_courses = []
            for course in week_courses:
                if course["day_of_week"] == i:
                    day_courses.append(course)
            if len(day_courses) == 0:
                continue
            rt_msg += f"【{weeks[i-1]}】有以下课程：\n"
            for index, course in enumerate(day_courses):
                rt_msg += f"{index+1}.{course['course_name']}\n    课程时间：{course['start_time']}~{course['end_time']}\n    位置：{course['location']}\n    老师：{course['instructor_name']}\n"
        return rt_msg


@keyword_handler("下周")
def handle_schedule(content, msg):
    load_courses()
    week_courses = []
    current_week = get_current_week()
    target_week = current_week + 1
    for course in course_schedule:
        if course["start_week"] > target_week or course["end_week"] < target_week:
            continue
        week_courses.append(course)
    if len(week_courses) == 0:
        return "下周没有课程哦！"
    else:
        rt_msg = f"下周(第{target_week}周)有以下课程：\n"
        weeks = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
        # 按星期顺序输出各个课程
        for i in range(1, 8):
            day_courses = []
            for course in week_courses:
                if course["day_of_week"] == i:
                    day_courses.append(course)
            if len(day_courses) == 0:
                continue
            rt_msg += f"【{weeks[i-1]}】有以下课程：\n"
            for index, course in enumerate(day_courses):
                rt_msg += f"{index+1}.{course['course_name']}\n    课程时间：{course['start_time']}~{course['end_time']}\n    位置：{course['location']}\n    老师：{course['instructor_name']}\n"
        return rt_msg


@keyword_handler("周一")
def handle_schedule(content, msg):
    load_courses()
    day_courses = []
    current_week = get_current_week()
    for course in course_schedule:
        if course["start_week"] > current_week or course["end_week"] < current_week:
            continue
        if course["day_of_week"] != 1:
            continue
        day_courses.append(course)
    if len(day_courses) == 0:
        return "周一没有课程哦！"
    else:
        rt_msg = "周一有以下课程：\n"
        # 取索引和值
        for index, course in enumerate(day_courses):
            rt_msg += f"{index+1}.{course['course_name']}\n    课程时间：{course['start_time']}~{course['end_time']}\n    位置：{course['location']}\n    老师：{course['instructor_name']}\n"
        return rt_msg


@keyword_handler("周二")
def handle_schedule(content, msg):
    load_courses()
    day_courses = []
    current_week = get_current_week()
    for course in course_schedule:
        if course["start_week"] > current_week or course["end_week"] < current_week:
            continue
        if course["day_of_week"] != 2:
            continue
        day_courses.append(course)
    if len(day_courses) == 0:
        return "周二没有课程哦！"
    else:
        rt_msg = "周二有以下课程：\n"
        # 取索引和值
        for index, course in enumerate(day_courses):
            rt_msg += f"{index+1}.{course['course_name']}\n    课程时间：{course['start_time']}~{course['end_time']}\n    位置：{course['location']}\n    老师：{course['instructor_name']}\n"
        return rt_msg


@keyword_handler("周三")
def handle_schedule(content, msg):
    load_courses()
    day_courses = []
    current_week = get_current_week()
    for course in course_schedule:
        if course["start_week"] > current_week or course["end_week"] < current_week:
            continue
        if course["day_of_week"] != 3:
            continue
        day_courses.append(course)
    if len(day_courses) == 0:
        return "周三没有课程哦！"
    else:
        rt_msg = "周三有以下课程：\n"
        # 取索引和值
        for index, course in enumerate(day_courses):
            rt_msg += f"{index+1}.{course['course_name']}\n    课程时间：{course['start_time']}~{course['end_time']}\n    位置：{course['location']}\n    老师：{course['instructor_name']}\n"
        return rt_msg


@keyword_handler("周四")
def handle_schedule(content, msg):
    load_courses()
    day_courses = []
    current_week = get_current_week()
    for course in course_schedule:
        if course["start_week"] > current_week or course["end_week"] < current_week:
            continue
        if course["day_of_week"] != 4:
            continue
        day_courses.append(course)
    if len(day_courses) == 0:
        return "周四没有课程哦！"
    else:
        rt_msg = "周四有以下课程：\n"
        # 取索引和值
        for index, course in enumerate(day_courses):
            rt_msg += f"{index+1}.{course['course_name']}\n    课程时间：{course['start_time']}~{course['end_time']}\n    位置：{course['location']}\n    老师：{course['instructor_name']}\n"
        return rt_msg


@keyword_handler("周五")
def handle_schedule(content, msg):
    load_courses()
    day_courses = []
    current_week = get_current_week()
    for course in course_schedule:
        if course["start_week"] > current_week or course["end_week"] < current_week:
            continue
        if course["day_of_week"] != 5:
            continue
        day_courses.append(course)
    if len(day_courses) == 0:
        return "周五没有课程哦！"
    else:
        rt_msg = "周五有以下课程：\n"
        # 取索引和值
        for index, course in enumerate(day_courses):
            rt_msg += f"{index+1}.{course['course_name']}\n    课程时间：{course['start_time']}~{course['end_time']}\n    位置：{course['location']}\n    老师：{course['instructor_name']}\n"
        return rt_msg


@keyword_handler("周六")
def handle_schedule(content, msg):
    load_courses()
    day_courses = []
    current_week = get_current_week()
    for course in course_schedule:
        if course["start_week"] > current_week or course["end_week"] < current_week:
            continue
        if course["day_of_week"] != 6:
            continue
        day_courses.append(course)
    if len(day_courses) == 0:
        return "周六没有课程哦！"
    else:
        rt_msg = "周六有以下课程：\n"
        # 取索引和值
        for index, course in enumerate(day_courses):
            rt_msg += f"{index+1}.{course['course_name']}\n    课程时间：{course['start_time']}~{course['end_time']}\n    位置：{course['location']}\n    老师：{course['instructor_name']}\n"
        return rt_msg


@keyword_handler("周日")
def handle_schedule(content, msg):
    load_courses()
    day_courses = []
    current_week = get_current_week()
    for course in course_schedule:
        if course["start_week"] > current_week or course["end_week"] < current_week:
            continue
        if course["day_of_week"] != 7:
            continue
        day_courses.append(course)
    if len(day_courses) == 0:
        return "周日没有课程哦！"
    else:
        rt_msg = "周日有以下课程：\n"
        # 取索引和值
        for index, course in enumerate(day_courses):
            rt_msg += f"{index+1}.{course['course_name']}\n    课程时间：{course['start_time']}~{course['end_time']}\n    位置：{course['location']}\n    老师：{course['instructor_name']}\n"
        return rt_msg
