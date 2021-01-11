from socket import *
from simulate_database import *
from tools import *
import json
import threading
import time
import queue

# <-----------自构数据库----------->
# 获取用户列表
user_list = userlist
# 获取群组列表
group_list = grouplist


class Server():

    def __init__(self):
        self.host_ip = "127.0.0.1"
        self.host_port = 5544   # 服务器开放的端口
        self.server_sock = socket(AF_INET, SOCK_STREAM)
        self.server_sock.bind((self.host_ip, self.host_port))
        self.server_sock.listen(3)  # 服务器socket被动接受的最大连接数
        self.lock = threading.Lock()
        self.msg_queue = queue.Queue()  # 服务器未处理消息队列
        self.unread_msgs = []   # 所有用户的未读消息列表
        self.online_users = dict()  # 当前在线用户字典

    # 监听登录线程
    def login_thread(self):
        while True:
            client_sock, client_address = self.server_sock.accept() # 接受连接并获取客户端socket、IP和端口
            print("[{}] 主机: ".format(get_time()) + str(client_address) + " 已接入")
            recv_msg = receive(client_sock) # 接收来自新连接socket的消息（一定是登录请求）
            print("[{}] 收到登录请求:".format(get_time()))
            print(recv_msg)
            self.put_msg(client_sock, recv_msg) # 将收到的消息放入未处理消息队列

    # 将消息放入未处理消息队列
    def put_msg(self, client_sock, recv_msg):
        self.lock.acquire()
        self.msg_queue.put((client_sock, recv_msg))
        self.lock.release()

    # 消息结构:
    # "login_req"为客户端登录请求，"login_res"为服务器对登录请求响应
    # "req"为客户端请求数据，"res"为服务器响应结果
    # "u_msg"为一对一消息
    # "g_msg"为群发消息
    # 封装消息
    # msg = {
    #     "type": ,
    #     "args": {
    #           "from_id": user_id,
    #           "from_name": ,
    #           "to_id": user_id,
    #           "type": "text""image""file",
    #           "data": ,
    #           "time": ,
    #     }
    #}
    # 服务器发送线程（处理消息的线程）
    def send_thread(self):
        while True:
            # 若消息队列非空，从消息队列中获取消息
            if not self.msg_queue.empty():
                client_sock, recv_msg = self.msg_queue.get()
                # 消息类型为登录请求，进行登录控制
                if recv_msg["type"] == "login_req":
                    # 获取登录的用户名、密码、时间
                    login_account = recv_msg["args"]["account"]
                    login_password = recv_msg["args"]["password"]
                    login_time = recv_msg["args"]["time"]
                    # 查询数据库中是否有该用户名
                    if user_list.findUser(login_account):
                        print("[{}] 用户请求登录:".format(get_time()))
                        login_user = user_list.findUser(login_account)
                        print(login_user)
                        # 密码正确且该用户不在线，登录成功
                        if (login_password == login_user["password"]) and (login_user["id"] not in self.online_users.keys()):
                            print("[{}] Success login: 用户 {} 已登录".format(get_time(), login_user["id"]))
                            # 成功登录的加入在线名单
                            self.online_users[login_account] = client_sock
                            print("[{}] 当前在线用户: ".format(get_time()))
                            print(self.online_users)
                            # 构建客户端响应信息
                            user_info = user_list.findUser(login_account)
                            user_name = user_info["name"]
                            user_friends = user_list.getFriends(login_account)
                            user_groups = user_list.getGroups(login_account)
                            res_msg = {
                                "type": "login_res",
                                "args": {
                                    "login_status": True,   # 登录成功标志
                                    "res_msg": "用户登录成功！",
                                    "user_id": login_account,
                                    "user_name": user_name,
                                    "user_info": user_info,
                                    "friend_list": user_friends,
                                    "group_list": user_groups,
                                    "time": get_time()
                                }
                            }
                            # 发送登录成功响应
                            send_data(client_sock, res_msg)
                            print("[{}] 已发送登录响应:".format(get_time()))
                            print(res_msg)
                            # 检查登录用户是否有未读消息，有则发送
                            if user_list.haveUnread(login_account):
                                i = 0
                                while user_list.haveUnread(login_account):
                                    print("Number of Unread messages: " + str(user_info["unread"]))
                                    print("登录用户有未读消息，正在准备发送")
                                    unread_msg = self.unread_msgs[i]
                                    if unread_msg[0] == login_account:  # 检查每个消息的应收id是不是本次登录用户的id
                                        # 引入小延时防止消息过多线程崩溃
                                        time.sleep(0.5)
                                        # if unread_msg[1]["type"] == "u_msg":
                                        #     self.put_msg(client_sock, unread_msg[1])
                                        # else:
                                        #     send_data(client_sock, unread_msg[1])
                                        send_data(client_sock, unread_msg[1])
                                        user_list.decUnread(login_account)
                                        self.unread_msgs.remove(unread_msg)
                                    else:
                                        i += 1
                            # 为登录用户新开线程监听来自此用户的消息
                            t = threading.Thread(target=self.recv_thread, name="recv_thread_for_{}".format(login_account), args=(client_sock,))
                            t.start()

                        # 密码错误，登录失败
                        elif login_password != login_user["password"]:
                            print("[{}] Failed login request: 密码错误: {}".format(login_time, login_password))
                            res_msg = {
                                "type": "login_res",
                                "args": {
                                    "login_status": False,  # 登录失败标志
                                    "res_msg": "用户名或密码错误！", # 登录失败错误信息
                                    "time": get_time(),
                                }
                            }
                            send_data(client_sock, res_msg)
                        # 检查到用户已经在线，登录失败
                        elif login_account in self.online_users.keys():
                            print("[{}] Failed login request: 用户重复登录: {}".format(login_time, login_account))
                            res_msg = {
                                "type": "login_res",
                                "args": {
                                    "login_status": False,  # 登录失败标志
                                    "res_msg": "用户在线，请勿重复登录！",  # 登录失败错误信息
                                    "time": get_time(),
                                }
                            }
                            send_data(client_sock, res_msg)
                    # 用户名错误，登录失败
                    else:
                        print("[{}] Failed login request: 账号错误: {}".format(login_time, login_account))
                        # 客户端响应信息
                        res_msg = {
                            "type": "login_res",
                            "args": {
                                "login_status": False,  # 登录失败标志
                                "res_msg": "用户名或密码错误！", # 登录失败错误信息
                                "time": get_time(),
                            }
                        }
                        send_data(client_sock, res_msg)

                # 消息类型为一对一消息
                elif recv_msg["type"] == "u_msg":
                    print("[{}] 收到一对一消息:".format(get_time()))
                    print(recv_msg)
                    # 获取所有可以先获取的信息
                    from_user_id = recv_msg["args"]["from_id"]
                    from_user_name = recv_msg["args"]["from_name"]
                    to_user_id = recv_msg["args"]["to_id"]
                    user_msg_data = recv_msg["args"]["data"]
                    from_time = recv_msg["args"]["time"]
                    msg_args_type = recv_msg["args"]["type"]
                    # 用户在线则发送给目的用户
                    if to_user_id in self.online_users.keys():
                        # 构建响应消息
                        res_msg = {
                            "type": "u_msg",
                            "args": {
                                "from_id": from_user_id,
                                "from_name": from_user_name,
                                "to_id": to_user_id,
                                # "to_name": to_user_name,
                                "type": msg_args_type,
                                "data": user_msg_data,
                                "time": from_time,
                            }
                        }
                        to_user_sock = self.online_users[to_user_id]    # 按照用户id从在线用户字典获取socket
                        send_data(to_user_sock, res_msg)
                        print("[{}] 成功发送: 发送人id:{} 昵称:{} ==> 接收人id:{} 昵称:{} : {}".format(get_time(),
                                                                                      from_user_id,
                                                                                      user_list.getUserName(from_user_id),
                                                                                      to_user_id,
                                                                                      user_list.getUserName(to_user_id),
                                                                                      user_msg_data))
                    # 用户不在线则送入未读消息，并将用户未读数+1
                    else:
                        self.unread_msgs.append((to_user_id, recv_msg))
                        user_list.addUnread(to_user_id)
                        print("[{}] 对方不在线，存入未读消息: 发送人id:{} 昵称:{} ==> 接收人id:{} 昵称:{} : {}".format(get_time(),
                                                                                 from_user_id,
                                                                                 user_list.getUserName(from_user_id),
                                                                                 to_user_id,
                                                                                 user_list.getUserName(to_user_id),
                                                                                 user_msg_data))

                # 消息类型为群组消息
                elif recv_msg["type"] == "g_msg":
                    print("[{}] 收到群聊消息:".format(get_time()))
                    print(recv_msg)
                    # 先获取所有可以获得的信息
                    from_user_id = recv_msg["args"]["from_id"]
                    from_user_name = recv_msg["args"]["from_name"]
                    group_msg_type = recv_msg["args"]["type"]
                    group_msg_data = recv_msg["args"]["data"]
                    group_msg_time = recv_msg["args"]["time"]
                    to_group_id = recv_msg["args"]["to_id"]
                    # 获取群组中成员id列表
                    to_group_mems = group_list.getGroupMems(to_group_id)
                    # 逐个检查群组成员，若在线则发送，否则加入未读
                    for group_mem in to_group_mems:
                        res_msg = {
                            "type": "g_msg",
                            "args": {
                                "from_id": to_group_id,
                                "from_name": from_user_name,
                                "to_id": group_mem,
                                "type": group_msg_type,
                                "data": group_msg_data,
                                "time": group_msg_time,
                            }
                        }
                        print(res_msg)
                        if group_mem == from_user_id:
                            continue
                        # 如果群组成员在线则发送
                        if group_mem in list(self.online_users.keys()):
                            send_data(self.online_users[group_mem], res_msg)
                        # 如果群组成员不在线，则存入未读
                        else:
                            self.unread_msgs.append((group_mem, res_msg))
                            user_list.addUnread(group_mem)

    # 为每个客户端建立的监听线程
    def recv_thread(self, client_sock):
        try:
            while True:
                recv_content = receive(client_sock)
                self.put_msg(client_sock, recv_content)
        except:
            print("[{}] Connection lost: 连接已断开 {}".format(get_time(), client_sock))
            # 从在线用户中删除断开连接的用户
            for online_client_id, online_client_socket in self.online_users.items():
                if online_client_socket == client_sock:
                    self.online_users.pop(online_client_id)
            # 释放连接
            client_sock.close()

    # 创建时启动线程表，起始时启动登录监听线程和消息处理线程
    def run(self):
        login_thread = threading.Thread(target=self.login_thread)
        login_thread.start()
        send_thread = threading.Thread(target=self.send_thread)
        send_thread.start()
        print("<-----------服务器启动成功----------->")

if __name__ == '__main__':
    Server().run()
