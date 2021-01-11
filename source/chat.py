from socket import *
from tools import *
import threading
from simulate_database import *
import base64
from PyQt5 import QtWidgets, QtCore, QtGui


class Ui_Chat_MainWindow(QtWidgets.QMainWindow):

    def __init__(self, client_socket, user_info, friend_list, group_list):
        self.client_socket = client_socket
        self.user_info = user_info
        self.friend_list = friend_list
        self.group_list = group_list
        self.msg_type = "g_msg"
        self.from_user_id = self.user_info["id"]
        self.from_user_name = self.user_info["name"]
        self.to_id = ""
        self.default_url = "../source/recv_files/"  # 默认文件存储路径
        self.default_image_url = "../source/recv_image/"    # 默认图片存储路径
        super(Ui_Chat_MainWindow, self).__init__()
        widget = QtWidgets.QWidget()
        self.setupUi(widget)
        self.retranslateUi()
        self.MainWindow.show()
        self.run()

    def setupUi(self, MainWindow):
        # 新建主窗
        self.MainWindow = MainWindow
        self.MainWindow.setObjectName("MainWindow")
        self.MainWindow.resize(1230, 715)
        self.MainWindow.setMinimumSize(QtCore.QSize(1230, 715))
        self.MainWindow.setMaximumSize(QtCore.QSize(1230, 715))
        self.MainWindow.setStyleSheet("background-color: rgb(231, 237, 238);")
        # 设置主窗图标
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("../source/image_basic/mainwindow_icon.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.MainWindow.setWindowIcon(icon)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        # 创建列表左边栏
        self.listWidget = QtWidgets.QListWidget(self.centralwidget)
        self.listWidget.setGeometry(QtCore.QRect(0, 50, 250, 665))
        self.listWidget.setObjectName("list")
        self.listWidget.setStyleSheet("border:none")
        self.listWidget.setFont(QtGui.QFont("微软雅黑 Light", 12))
        self.listWidget.setStyleSheet("background-color: rgb(161, 182, 187);")
        # 添加群组列表
        for group in self.group_list:
            item = QtWidgets.QListWidgetItem()
            item.setSizeHint(QtCore.QSize(246, 50))
            item.setText(group[0])
            item.setWhatsThis("group")
            self.listWidget.addItem(item)
        # 添加好友列表
        for friend in self.friend_list:
            item = QtWidgets.QListWidgetItem()
            item.setSizeHint(QtCore.QSize(246, 50))
            item.setText(friend[0])
            item.setWhatsThis("friend")
            self.listWidget.addItem(item)
        self.listWidget.currentRowChanged.connect(self.swichLog)
        # 添加顶部当前对方框
        self.lineEdit = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit.setObjectName("topLine")
        self.lineEdit.setReadOnly(True)
        self.lineEdit.setFont(QtGui.QFont("微软雅黑 Light", 14))
        self.lineEdit.setText(self.friend_list[0][0])
        self.lineEdit.setAlignment(QtCore.Qt.AlignCenter)
        self.lineEdit.setStyleSheet("background-color: rgb(161, 182, 187);border:none")
        self.lineEdit.setGeometry(QtCore.QRect(0, 0, 1230, 50))
        # 添加对话窗口显示框
        self.stackedWidget = QtWidgets.QStackedWidget(self.centralwidget)
        self.stackedWidget.setGeometry(QtCore.QRect(250, 50, 970, 490))
        self.stackedWidget.setStyleSheet("background-color: rgb(231, 237, 238);border:none")
        for i in range(self.listWidget.count()):
            text = self.listWidget.item(i).text()
            msg_log = QtWidgets.QTextEdit(self.centralwidget)
            msg_log.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
            msg_log.setReadOnly(True)
            msg_log.setFont(QtGui.QFont("微软雅黑 Light", 11))
            self.stackedWidget.addWidget(msg_log)
        # 添加输入框
        self.textEdit_send = QtWidgets.QTextEdit(self.centralwidget)
        self.textEdit_send.setGeometry(QtCore.QRect(250, 570, 970, 145))
        self.textEdit_send.setStyleSheet("background-color: rgb(231, 237, 238);border:none")
        self.textEdit_send.setText("")
        self.textEdit_send.setPlaceholderText("请输入内容...")
        self.textEdit_send.setFont(QtGui.QFont("微软雅黑 Light", 11))
        self.textEdit_send.setObjectName("textEdit_send")
        # 添加发送按钮
        self.pushButton_send = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_send.setGeometry(QtCore.QRect(1110, 664, 105, 34))
        self.pushButton_send.setStyleSheet("background-color: rgb(161,181,186);\n"
                                      "color: rgb(0,0,0);border:none")
        self.pushButton_send.setFont(QtGui.QFont("微软雅黑 Light", 10))
        self.pushButton_send.setObjectName("pushButton_send")
        self.pushButton_send.clicked.connect(self.sendMsg)
        # 添加图片按钮
        self.pushButton_image = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_image.setGeometry(QtCore.QRect(260, 540, 30, 30))
        self.pushButton_image.setIcon(QtGui.QIcon("../source/image_basic/image_button.png"))
        self.pushButton_image.setIconSize(QtCore.QSize(30, 30))
        self.pushButton_image.setStyleSheet("border: none")
        self.pushButton_image.clicked.connect(self.loadImage)
        # 添加文件传输按钮
        self.pushButton_file = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_file.setGeometry(QtCore.QRect(300, 540, 30, 30))
        self.pushButton_file.setIcon(QtGui.QIcon("../source/image_basic/file_button.png"))
        self.pushButton_file.setIconSize(QtCore.QSize(30, 30))
        self.pushButton_file.setStyleSheet("border: none")
        self.pushButton_file.clicked.connect(self.loadFile)

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.MainWindow.setWindowTitle(_translate("MainWindow", "myChat"))
        self.pushButton_send.setText(_translate("MainWindow", "发送"))

    # 改变显示区域，并获取对应的id及应发消息类型
    def swichLog(self, index):
        self.stackedWidget.setCurrentIndex(index)
        self.listWidget.setCurrentRow(index)
        group_num = len(self.group_list)
        if index < group_num:
            self.to_id = self.group_list[index][1]
            self.msg_type = "g_msg"
            self.lineEdit.setText(self.group_list[index][0])
        else:
            self.to_id = self.friend_list[index - group_num][1]
            self.msg_type = "u_msg"
            self.lineEdit.setText((self.friend_list[index-group_num][0]))
        # 监控打印当前的消息类型、接收方id
        print("当前消息类型: " + self.msg_type)
        print("目的接收人id: " + self.to_id)

    # 图片发送方法
    def loadImage(self):
        print("load--image")
        # 弹出文件选择框，过滤条件为文件扩展名.jpg .jpeg .png .gif
        fname = QtWidgets.QFileDialog.getOpenFileName(self, "选择图片", "../source/test_files", "Image files(*.jpg *.jpeg *.gif *.png)")
        # 获取图片路径、图片名并打印
        file_url = fname[0]
        file_name = fname[0].split("/")[-1]
        print("URL: " + file_url)
        print("FILENAME: " + file_name)
        # 检查文件名、防止点击取消按键file_name为空导致崩溃
        if file_name:
            with open(file_url, "rb") as f:
                    file_content = f.read()
            # 利用base64将字节流转换为可以直接使用json进行序列化的形式
            file_str = base64.encodebytes(file_content).decode("utf-8")
            # 构建发送消息
            msg_time = get_time()
            msg_type = self.msg_type
            msg_from = self.from_user_id
            msg_to = self.to_id
            msg_args_type = "image"
            # 发送消息不能为空
            msg = {
                "type": msg_type,
                "args": {
                    "from_id": msg_from,
                    "from_name": self.user_info["name"],
                    "to_id": msg_to,
                    "type": msg_args_type,
                    "data": {
                        "file_name": file_name,
                        "file_content": file_str,
                    },
                    "time": msg_time,
                }
            }
            send_data(self.client_socket, msg)
            print("[{}] 成功发送图片: " + file_url)
            # 在对话区域显示图片
            log = self.stackedWidget.currentWidget()
            # 设置对话区域指针
            cursor = log.textCursor()
            cursor.movePosition(QtGui.QTextCursor.End)
            log.setTextCursor(cursor)
            log.insertPlainText("我" + ":   " + msg_time + "\n")
            # 利用QImage从路径处获取图片
            src_image = QtGui.QImage(file_url)
            src_image.scaled(300, 250, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
            # 将图片加入到聊天区域中显示
            cursor.insertImage(src_image)
            log.insertPlainText("\n\n")
            cursor.movePosition(QtGui.QTextCursor.End)

    # 文件发送方法
    def loadFile(self):
        print("load--file")
        # 弹出文件选择框，过滤条件为所有类型文件，获取文件路径、文件名并打印
        fname = QtWidgets.QFileDialog.getOpenFileName(self, "选择文件", "../source/test_files", "All Files(*)")
        file_url = fname[0]
        print("URL: " + file_url)
        file_name = file_url.split("/")[-1]
        print("FILENAME: " + file_name)
        # 检查文件名，防止文件名为空导致崩溃
        if file_name:
            # 目前只支持一对一传输文件，群组文件可以通过取消本条if语句实现
            # 考虑到服务器端对文件、图片类型消息依旧已消息完整形式加入未读消息库
            # 防止缓存占用过大，可扩展服务器功能，将文件、图片类型消息写入"server_file_buff/"改善此问题
            if self.msg_type == "u_msg":
                with open(file_url, "rb") as f:
                        file_content = f.read()
                # 利用base64将文件读取的字节流转换为可直接利用json序列化的形式
                file_str = base64.encodebytes(file_content).decode("utf-8")
                # 构建消息
                msg_time = get_time()
                msg_type = self.msg_type
                msg_from = self.from_user_id
                msg_to = self.to_id
                msg_args_type = "file"
                # 发送消息不能为空
                msg = {
                    "type": msg_type,
                    "args": {
                        "from_id": msg_from,
                        "from_name": self.user_info["name"],
                        "to_id": msg_to,
                        "type": msg_args_type,
                        "data": {
                            "file_name": file_name,
                            "file_content": file_str,
                        },
                        "time": msg_time,
                    }
                }
                send_data(self.client_socket, msg)
                print("[{}] 成功发送文件: " + file_url)
                # 设置对应的对话区域
                log = self.stackedWidget.currentWidget()
                # 设置对话区域鼠标指针
                cursor = log.textCursor()
                cursor.movePosition(QtGui.QTextCursor.End)
                log.setTextCursor(cursor)
                # 在聊天区域显示对应信息
                log.insertPlainText("我" + ":   " + msg_time + "\n")
                log.insertPlainText("成功发送文件: " + file_name)
                log.insertPlainText("\n\n")
                cursor.movePosition(QtGui.QTextCursor.End)

    # 发送消息输入区域消息方法
    def sendMsg(self):
        msg_data = self.textEdit_send.toPlainText()
        msg_time = get_time()
        msg_type = self.msg_type
        msg_from = self.from_user_id
        msg_to = self.to_id
        msg_args_type = "text"
        # 发送消息不能为空
        if not msg_data:
            QtWidgets.QMessageBox.information(self.MainWindow, '提示', '发送消息不能为空!',
                                              QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Close,
                                              QtWidgets.QMessageBox.Close)
            return
        # 构建发送消息
        msg = {
            "type": msg_type,
            "args": {
                "from_id": msg_from,
                "from_name": self.user_info["name"],
                "to_id": msg_to,
                "type": msg_args_type,
                "data": msg_data,
                "time": msg_time,
            }
        }
        # 待扩展功能
        # 如果拖动文件进入输入框，识别获取并发送
        # if msg_data[0:8] == "file:///":
        #     msg["args"]["type"] = "file"
        #     file_url = msg_data[8:]
        #     file_name = file_url.split("/")[-1]
        #     file_content = []
        #     line_content = ""
        #     with open(file_url, "r") as f:
        #         for line in f.readlines():
        #             line_content = line
        #             file_content.append(line_content)
        #     msg["args"]["data"] = {
        #         "file_name": file_name,
        #         "file_content": file_content,
        #     }
        #     # print("构建文件类型消息:")
        #     # print(msg)
        #     # msg = json.dumps(msg).encode()
        #     # print(msg)
        #     # print(str(len(msg)).ljust(30).encode())
        # else:
        #     msg["args"]["type"] = "text"
        send_data(self.client_socket, msg)
        print("[{}] 发送消息: ".format(get_time()))
        print(msg)
        # 发送消息后操作
        # 清空消息输入框
        self.textEdit_send.setPlainText("")
        # 设置对应对话显示框
        log = self.stackedWidget.currentWidget()
        # 设置鼠标指针
        cursor = log.textCursor()
        cursor.movePosition(QtGui.QTextCursor.End)
        log.setTextCursor(cursor)
        # 在聊天区域显示对应消息
        log.insertPlainText("我" + ":   " + msg_time + "\n")
        log.insertPlainText(msg_data)
        log.insertPlainText("\n\n")
        cursor.movePosition(QtGui.QTextCursor.End)

    # 接收消息线程
    def recvMsg(self):
        try:
            while True:
                recv_msg = receive(self.client_socket)
                # 收到一对一消息
                if recv_msg["type"] == "u_msg":
                    print("[{}] 收到一对一消息:".format(get_time()))
                    msg_from = recv_msg["args"]["from_id"]
                    msg_from_name = recv_msg["args"]["from_name"]
                    msg_time = recv_msg["args"]["time"]
                    for i in list(range(len(self.friend_list))):
                        if self.friend_list[i][1] == msg_from:
                            self.swichLog(i+len(self.group_list))
                            break
                    # 处理文本类型消息
                    if recv_msg["args"]["type"] == "text":
                        msg_data = recv_msg["args"]["data"]
                        print("文本消息: " + msg_data)
                        # 设置对话显示区域
                        log = self.stackedWidget.currentWidget()
                        cursor = log.textCursor()
                        cursor.movePosition(QtGui.QTextCursor.End)
                        log.setTextCursor(cursor)
                        log.insertPlainText(msg_from_name + ":   " + msg_time + "\n")
                        log.insertPlainText(msg_data)
                        log.insertPlainText("\n\n")
                        cursor.movePosition(QtGui.QTextCursor.End)
                    # 处理文件类型消息
                    elif recv_msg["args"]["type"] == "file":
                        # 获取文件名，设置默认路径
                        file_name = recv_msg["args"]["data"]["file_name"]
                        file_url = self.default_url + file_name
                        print("收到文件: " + file_name)
                        print("可到路径: " + file_url + "查看")
                        file_str = recv_msg["args"]["data"]["file_content"]
                        # 利用base64反向转换获取文件的字节流形式
                        file_content = file_str.encode("utf-8")
                        file_content = base64.decodebytes(file_content)
                        # 打开默认路径，将字节流写入文件
                        with open(file_url, 'wb+') as f:
                            f.write(file_content)
                        # 设置对话显示区域
                        log = self.stackedWidget.currentWidget()
                        cursor = log.textCursor()
                        cursor.movePosition(QtGui.QTextCursor.End)
                        log.setTextCursor(cursor)
                        log.insertPlainText(msg_from_name + ":   " + msg_time + "\n")
                        log.insertPlainText("收到文件: " + file_name + "\n")
                        log.insertPlainText("可到文件路径: " + file_url + " 查看收到内容")
                        log.insertPlainText("\n\n")
                        cursor.movePosition(QtGui.QTextCursor.End)
                    # 处理图片类型消息
                    elif recv_msg["args"]["type"] == "image":
                        # 获取图片名，设置默认路径
                        file_name = recv_msg["args"]["data"]["file_name"]
                        file_url = self.default_image_url + file_name
                        print("收到图片: " + file_name)
                        print("可到路径: " + file_url + "查看")
                        file_str = recv_msg["args"]["data"]["file_content"]
                        # 利用base64反向转换获取图片的字节流形式
                        file_content = file_str.encode("utf-8")
                        file_content = base64.decodebytes(file_content)
                        # 打开默认路径，将字节流写入文件
                        with open(file_url, 'wb+') as f:
                            f.write(file_content)
                        # 设置对话显示区域
                        log = self.stackedWidget.currentWidget()
                        cursor = log.textCursor()
                        cursor.movePosition(QtGui.QTextCursor.End)
                        log.setTextCursor(cursor)
                        log.insertPlainText(msg_from_name + ":   " + msg_time + "\n")
                        # 利用QImage从路径处获取图片
                        src_image = QtGui.QImage(file_url)
                        src_image.scaled(300, 250, QtCore.Qt.IgnoreAspectRatio, QtCore.Qt.SmoothTransformation)
                        # 将图片加入到聊天区域中显示
                        cursor.insertImage(src_image)
                        # log.insertPlainText("\n")
                        # log.insertPlainText("可到图片路径: " + file_url + " 查看收到内容")
                        log.insertPlainText("\n\n")
                        cursor.movePosition(QtGui.QTextCursor.End)
                # 收到群组消息
                elif recv_msg["type"] == "g_msg":
                    print("[{}] 收到群组消息:".format(get_time()))
                    msg_from = recv_msg["args"]["from_id"]
                    msg_from_name = recv_msg["args"]["from_name"]
                    # msg_data = recv_msg["args"]["data"]
                    msg_time = recv_msg["args"]["time"]
                    for i in list(range(len(self.group_list))):
                        if msg_from == self.group_list[i][1]:
                            self.swichLog(i)
                            break
                    # 处理文本类型消息
                    if recv_msg["args"]["type"] == "text":
                        msg_data = recv_msg["args"]["data"]
                        print("文本消息: " + msg_data)
                        # 设置对话显示区域
                        log = self.stackedWidget.currentWidget()
                        cursor = log.textCursor()
                        cursor.movePosition(QtGui.QTextCursor.End)
                        log.setTextCursor(cursor)
                        log.insertPlainText(msg_from_name + ":   " + msg_time + "\n")
                        log.insertPlainText(msg_data)
                        log.insertPlainText("\n\n")
                        cursor.movePosition(QtGui.QTextCursor.End)
                    # 处理图片类型消息
                    elif recv_msg["args"]["type"] == "image":
                        # 获取图片名，设置默认路径
                        file_name = recv_msg["args"]["data"]["file_name"]
                        file_url = self.default_image_url + file_name
                        print("收到图片: " + file_name)
                        print("可到路径: " + file_url + "查看")
                        file_str = recv_msg["args"]["data"]["file_content"]
                        # 利用base64反向转换获取图片的字节流形式
                        file_content = file_str.encode("utf-8")
                        file_content = base64.decodebytes(file_content)
                        # 打开默认路径，将字节流写入文件
                        with open(file_url, 'wb+') as f:
                            f.write(file_content)
                        # 设置对话显示区域
                        log = self.stackedWidget.currentWidget()
                        cursor = log.textCursor()
                        cursor.movePosition(QtGui.QTextCursor.End)
                        log.setTextCursor(cursor)
                        log.insertPlainText(msg_from_name + ":   " + msg_time + "\n")
                        # 利用QImage从路径处获取图片
                        src_image = QtGui.QImage(file_url)
                        src_image.scaled(300, 250, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
                        # 将图片加入到聊天区域中显示
                        cursor.insertImage(src_image)
                        # log.insertPlainText("\n")
                        # log.insertPlainText("可到图片路径: " + file_url + " 查看收到内容")
                        log.insertPlainText("\n\n")
                        cursor.movePosition(QtGui.QTextCursor.End)
        # 抛出线程中止异常
        except Exception as e:
            print("[{}] recv_thread 异常，被迫中止".format(get_time()))
            self.client_socket.close()
            self.close()

    # 设置默认启动线程
    def run(self):
        recv_thread = threading.Thread(target=self.recvMsg)
        recv_thread.start()


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    # mainWindow = QtWidgets.QMainWindow()
    # mainWindow.show()

    client_socket = socket(AF_INET, SOCK_STREAM)
    test_user = userlist.findUser("123456")
    widget = QtWidgets.QWidget()
    ui = Ui_Chat_MainWindow(client_socket, test_user, [("Musso", "musso"), ("用户2", "1234567"), ("用户3", "12345678")], test_user["group"])
    ui.setupUi(widget)
    ui.retranslateUi()
    widget.show()

    sys.exit(app.exec_())


