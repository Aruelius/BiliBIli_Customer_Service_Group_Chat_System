import json
import time
from threading import Thread

import requests


class 群聊系统(object):
    def __init__(self):
        self.群聊人数 = 5
        self.消息池 = []
        self.客服列表 = []
        self.分组号 = "5764e62b72924e8a9814b79cc62ae69c"
        self.系统序号 = "102d1b48515346ec8e9fb543b54ec454"
        self.初始化链接 =   "https://service.bilibili.com/v2/chat/user/init.action"
        self.接入客服链接 = "https://service.bilibili.com/v2/chat/user/chatconnect.action"
        self.接收消息链接 = "https://service.bilibili.com/v2/chat/user/msg.action"
        self.发送消息链接 = "https://service.bilibili.com/v2/chat/user/chatsend.action"


    @staticmethod
    def 打印(*消息):
        print(*消息)

    def 初始化(self, 用户名):
        响应 = requests.post(
            url=self.初始化链接,
            data={
                'ack': '1',
                'sysNum': self.系统序号,
                'source': '0',
                'tranFlag': '0',
                "groupId": self.分组号,
                "uname": 用户名,
                "visitUrl": "https://member.bilibili.com/v2",
                "realname": 用户名,
                'isReComment': '1'
            }
        ).json()
        self.打印(用户名, 响应["uid"])
        return 响应["uid"], 响应["cid"]

    def 睡(self, 秒: int):
        time.sleep(秒)

    def 发送消息(self,客服昵称: str, 消息: str):
        for 客服 in self.客服列表:
            if 客服["客服昵称"] != 客服昵称:
                requests.post(
                    url=self.发送消息链接,
                    data={
                        "puid": 客服["客服编号"],
                        "cid": 客服["聊天编号"],
                        "uid": 客服["用户编号"],
                        "content": 消息
                    },
                    headers={"Cookie": 客服["曲奇饼"]}
                )
                # self.打印(f"给 {客服['客服昵称']} 发送了 {消息}")

    def 分发客服(self):
        任务列表 = []
        for 序号 in range(1, self.群聊人数):
            用户编号, 聊天编号 = self.初始化(f"呷哺呷哺用户{序号}")
            任务列表.append(
                Thread(target=self.接入客服, args=(用户编号, 聊天编号))
            )
        for 任务 in 任务列表:
            任务.start()
        for 任务 in 任务列表:
            任务.join()

    def 接收消息(self):
        任务列表 = []
        def 接收消息_子任务(客服: dict):
            令牌 = int(time.time()*1000)
            真 = True
            while 真:
                try:
                    响应 = requests.get(
                        url=self.接收消息链接,
                        params={
                            "puid": 客服["客服编号"],
                            "uid": 客服["用户编号"],
                            "token": 令牌
                        },
                        headers={"Cookie": 客服["曲奇饼"]}
                    )
                    响应字典 = 响应.json()
                    if 响应字典:
                        消息字典 = json.loads(响应字典[0])
                        if 消息字典["type"] == 202 and 消息字典['content'] not in self.消息池:
                            self.消息池.append(消息字典['content'])
                            客服昵称 = 消息字典["aname"]
                            消息 = f"{客服昵称}: {消息字典['content']}"
                            self.打印(消息)
                            self.发送消息(客服昵称, 消息)
                except KeyboardInterrupt:
                    self.打印("正在给客服发送再见~，完成后会自动退出")
                    self.发送消息("呷哺呷哺", "会话断开，再见！")
                except: pass
                self.睡(1)

        for 客服 in self.客服列表:
            任务列表.append(Thread(target=接收消息_子任务, args=(客服,)))
        for 任务 in 任务列表:
            任务.start()
        for 任务 in 任务列表:
            任务.join()

    def 接入客服(self, 用户编号, 聊天编号):
        真 = True
        while 真:
            响应 = requests.post(
                url=self.接入客服链接,
                data={
                    'sysNum': self.系统序号,
                    'uid': 用户编号,
                    'tranFlag': '0',
                    'way': '1',
                    'current': 'false',
                    'groupId': self.分组号
                }
            )
            响应字典 = 响应.json()
            if "排队中" in 响应.text:
                self.打印(f"排队中，目前位置：{响应字典['count']}")
                self.睡(10)
            else:
                self.打印(f"接入客服：{响应字典['aname']}")
                self.客服列表.append({
                    "客服昵称": 响应字典["aname"],
                    "客服编号": 响应字典['puid'],
                    "用户编号": 用户编号,
                    "聊天编号": 聊天编号,
                    "曲奇饼": f"{self.系统序号}_u={用户编号}"
                })
                self.接收消息()
                return 响应字典['puid'], 用户编号, 聊天编号
        
if __name__ == "__main__":
    群聊 = 群聊系统()
    群聊.分发客服()
