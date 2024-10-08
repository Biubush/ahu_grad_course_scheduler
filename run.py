from ahu_scheduler import *

if __name__ == "__main__":
    reminder_bot = CourseReminderBot()
    reminder_bot.run()
    msg_server.start_server()