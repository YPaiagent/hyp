
import sqlite3     # 自带数据库，不用安装
import json          # 用来存聊天记录（列表转文本）
import datetime      # 记录时间
class Use__register:
    def __init__(self):
       #创建时自动运行一次
        self.SJuku()
# 创建表格，有则存，无则过
    def SJuku(self):
        Xingxi = sqlite3.connect("user.db")     
        operate = Xingxi.cursor()        
        operate.execute('''
        CREATE TABLE IF NOT EXISTS unique_users (
            user_id TEXT PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            phone TEXT UNIQUE NOT NULL,
            chat_history TEXT,
            created_at TEXT DEFAULT (datetime('now', 'localtime')) 
        )
        ''')
        Xingxi.commit()
        Xingxi.close()  # 只关连接，不用关游标


    # 存储用户数据：用户资料只存第一次，后续只追加聊天记录，创建时间永远不变
    def save_user(self,user_id, username, phone, chat_history):
        try:
            Xingxi = sqlite3.connect("user.db")
            cursor = Xingxi.cursor()

            # 先查用户是否存在
            cursor.execute("SELECT username, phone, chat_history, created_at FROM unique_users WHERE user_id = ?", (user_id,))
            row = cursor.fetchone()

            if row:
                # 用户已存在：资料不变，只追加聊天
                username = row[0]
                phone = row[1]
                old_history = json.loads(row[2]) if row[2] else []
                chat_history = old_history + chat_history
                created_time = row[3]  # 直接用旧的创建时间，不更新！
            else:
                # 第一次创建：自动生成时间
                created_time = None

            # 关键：只有第一次才会设置 created_at，后续永远不改
            if created_time:
                cursor.execute('''
                    INSERT OR REPLACE INTO unique_users
                    (user_id, username, phone, chat_history, created_at)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    user_id,
                    username,
                    phone,
                    json.dumps(chat_history, ensure_ascii=False),
                    created_time  # 用旧时间
                ))
            else:
                cursor.execute('''
                    INSERT OR REPLACE INTO unique_users
                    (user_id, username, phone, chat_history)
                    VALUES (?, ?, ?, ?)
                ''', (
                    user_id,
                    username,
                    phone,
                    json.dumps(chat_history, ensure_ascii=False)
                ))

            Xingxi.commit()
            Xingxi.close()
            return True 
        
        except Exception as e:
            print("保存失败：", e)
            return False
        
    #忘记ID
    # 读取用户数据：根据电话号码 获取用户信息和聊天历史
    def get_phone(self,phone):
        try:
            # 连接数据库
            Xingxi = sqlite3.connect("user.db")
            cursor = Xingxi.cursor()

            # 查询用户数据
            cursor.execute('''
                SELECT user_id, username, phone, chat_history, created_at
                FROM unique_users
                WHERE phone = ?
            ''', (phone,))
            
            # 获取一条数据
            user_data = cursor.fetchone()
            Xingxi.close()

            # 如果用户不存在
            if not user_data:
                return None

            # 把 JSON 格式的聊天记录转回列表
            chat_history = json.loads(user_data[3]) if user_data[3] else []

            # 返回用户信息
            return {
                "user_id": user_data[0],
                "username": user_data[1],
                "phone": user_data[2],
                "chat_history": chat_history,
                "created_at": user_data[4]
            }

        except Exception as e:
            print("读取失败：", e)
            return None

    # 读取用户数据：根据 user_id 获取用户信息和聊天历史
    def get_user(self,user_id):
        try:
            # 连接数据库
            Xingxi = sqlite3.connect("user.db")
            cursor = Xingxi.cursor()

            # 查询用户数据
            cursor.execute('''
                SELECT user_id, username, phone, chat_history, created_at
                FROM unique_users
                WHERE user_id = ?
            ''', (user_id,))
            
            # 获取一条数据
            user_data = cursor.fetchone()
            Xingxi.close()

            # 如果用户不存在
            if not user_data:
                return None

            # 把 JSON 格式的聊天记录转回列表
            chat_history = json.loads(user_data[3]) if user_data[3] else []

            # 返回用户信息
            return {
                "user_id": user_data[0],
                "username": user_data[1],
                "phone": user_data[2],
                "chat_history": chat_history,
                "created_at": user_data[4]
            }

        except Exception as e:
            print("读取失败：", e)
            return None

    # 下一步：获取用户（有就返回，没有才创建）
    def get_or_create_user(self,user_id):


    
        # 先查询！！！
        user = self.get_user(user_id)
        
        if user:
            print("✅ 用户已存在，直接使用")
            return user  # 有就直接返回，不输入
        else:
            while True:
                new_user=input("是否为新用户（请输入‘是/否）：")
                if new_user=='是':
                    # 没有 → 才让用户输入信息
                    while True:
                        print("=== 新用户信息录入 ===")
                        idd=input("请输入您的专属ID(为4位纯数字ID):")
                        if len(idd) == 4 and idd.isdigit():
                            username = input("请输入用户名：")
                            while True:
                                phone = input("请输入手机号(为11位纯数字电话号码):")
                                if len(phone) == 11 and phone.isdigit() and phone[0]=='1':
                                    break
                                else:
                                    print("\n❌您的输入有误，请重新校验❌\n")
                                    continue
                            break
                        else:
                            print("\n❌您的输入有误，请重新校验❌\n")
                            continue
                
                    # 保存新用户
                    self.save_user(idd, username, phone, [])
                    print("🤜 新用户创建成功！🤛🏻")
                    return self.get_user(idd)
                    
                    
                    
                elif new_user=='否':
                    phone=input("若忘记ID，可通过手机号登陆，请输入您的手机号码(为11位纯数字电话号码):")
                    xin=self.get_phone(phone)
                    if xin==None:
                        print("输入有误，骗人是不是🤨")
                        continue
                    else:
                        print("🤜登录成功🤛🏻")
                        return xin
                    
                else:
                    print("输入有误❌重新输入")
my = Use__register()
user_id=input
print("🚀 程序启动成功！")

input_id = input("请输入您的4位数用户ID：")

current_user = my.get_or_create_user(input_id)

if current_user:
    print("\n 当前登录用户信息：")
    print(f"ID：{current_user['user_id']}")
    print(f"用户名：{current_user['username']}")
    print(f"手机号：{current_user['phone']}")
    print(f"创建时间：{current_user['created_at']}")
else:
    print("\n❌ 程序退出，未获取到用户")