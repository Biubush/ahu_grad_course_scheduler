# 说明

【此版本为webhook版】

一个微信推送机器人，用于推送【安徽大学】【研究生】的课表信息

项目特性如下：

- √自动根据你的课表信息生成一套计划，在每一堂课开始的前若干分钟，向你的微信推送开课消息

- √可识别当前周数对应课表，如：4~11周开展的课不会在第3周通知

- √可自定义提前多少分钟通知

- √课表的生成全程自动化

效果图：
![](https://github.com/Biubush/ahu_grad_course_scheduler/blob/main/src/picture1.jpg?raw=true)

# 部署

## 企业微信创建

用电脑打开[企业微信官网](https://work.weixin.qq.com/)，注册一个企业

## 机器人添加

在企业内部创建一个群聊

1. 电脑端

电脑端内部群聊->右上方三个点->添加群机器人，可以新建机器人，图标和名称自定义

![](https://github.com/Biubush/ahu_grad_course_scheduler/blob/main/src/picture2.png?raw=true)

2. 手机端

手机端内部群聊->右上角三个点->添加群机器人

![](https://github.com/Biubush/ahu_grad_course_scheduler/blob/main/src/picture3.png?raw=true)

获取webhook地址

1. 电脑端

进入群聊->群成员列表->右键对应机器人->查看资料->Webhook地址

![](https://github.com/Biubush/ahu_grad_course_scheduler/blob/main/src/picture5.png?raw=true)

2. 手机端

进入群聊->右上角三个点->群机器人->点击对应机器人->Webhook地址

![](https://github.com/Biubush/ahu_grad_course_scheduler/blob/main/src/picture4.png?raw=true)

**记录下这个webhook地址，等会需要填进配置**

## 部署环境搭建

首先克隆仓库并进入文件夹

```
git clone https://github.com/Biubush/ahu_grad_course_scheduler.git
cd ahu_grad_course_scheduler
```

其次创建虚拟环境（可选），这里省略

然后安装三方库

```
pip install -r requirements.txt
```

现在，把config.json.example文件重命名为config.json

按照以下规则更改你的各个字段：
```
"student_id":"填你的学号",
"password":"你的密码",
"current_week": 当前周数,
"reminder_minutes":提前多少分钟提醒上课,
"webhook_urls": [
    "你之前保存的webhook地址"
]
```

## 运行项目

```
python run.py
```

运行成功就会在群里发通知

> 注意，程序停止运行就没法继续通知了，建议使用24h运行的服务器