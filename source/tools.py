import json
import threading
import time
import queue

buff_size = 1024


def receive(client_socket):
    # 获取消息总长
    msg_len = int(client_socket.recv(30).decode().rstrip())
    # 已收消息长
    recv_len = 0
    # 消息数据
    recv_data = b''

    while recv_len < msg_len:
        recv_buff = client_socket.recv(buff_size)
        if not recv_buff:
            break
        recv_len += len(recv_buff)
        recv_data += recv_buff

    recv_data = json.loads(recv_data.decode())
    return recv_data


def send_data(client_sock, msg):
    # 封装消息
    msg = json.dumps(msg).encode()
    # 获取消息长度并设置为15位左对齐
    send_msg_len = str(len(msg)).ljust(30).encode()
    # 先发数据长度，再发消息，为接收长消息做准备
    client_sock.send(send_msg_len)
    client_sock.send(msg)


def get_time():
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
