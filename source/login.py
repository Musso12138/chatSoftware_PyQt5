import random
import sys
from socket import *
from tools import *
import chat
from PyQt5 import QtWidgets, QtCore, QtGui


class Ui_MainWindow(QtWidgets.QMainWindow):

    def setupUi(self, MainWindow):
        # 主窗
        self.MainWindow = MainWindow
        self.MainWindow.setObjectName("MainWindow")
        self.MainWindow.resize(1000, 700)
        self.MainWindow.setMinimumSize(QtCore.QSize(540, 410))
        self.MainWindow.setMaximumSize(QtCore.QSize(540, 410))
        # 设置主窗图标
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("../source/image_basic/mainwindow_icon.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.MainWindow.setWindowIcon(icon)
        self.MainWindow.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        # 加入用户名输入栏
        self.lineEdit_account = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit_account.setGeometry(QtCore.QRect(100, 215, 340, 45))
        self.lineEdit_account.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.lineEdit_account.setText("")
        self.lineEdit_account.setMaxLength(1000)
        self.lineEdit_account.setPlaceholderText("请输入用户名")
        self.lineEdit_account.setFont(QtGui.QFont("微软雅黑 Light", 11))
        self.lineEdit_account.setObjectName("lineEdit_account")
        self.lineEdit_account.setStyleSheet("border:none")
        # 加入密码输入栏
        self.lineEdit_password = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit_password.setGeometry(QtCore.QRect(100, 265, 340, 45))
        self.lineEdit_password.setInputMask("") # 密码输入时不可见
        self.lineEdit_password.setText("")
        self.lineEdit_password.setMaxLength(1000)
        self.lineEdit_password.setEchoMode(QtWidgets.QLineEdit.Password)
        self.lineEdit_password.setCursorPosition(0)
        self.lineEdit_password.setFont(QtGui.QFont("微软雅黑 Light", 11))
        self.lineEdit_password.setObjectName("lineEdit_password")
        self.lineEdit_password.setPlaceholderText("请输入密码")
        self.lineEdit_password.setStyleSheet("border:none")
        # 加入登录按钮
        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton.setGeometry(QtCore.QRect(100, 315, 340, 45))
        self.pushButton.setStyleSheet("background-color: rgb(7, 85, 240);\n"
                                      "color: rgb(255, 255, 255);")
        self.pushButton.setFont(QtGui.QFont("微软雅黑 Light", 10))
        self.pushButton.setObjectName("pushButton")
        self.pushButton.clicked.connect(self.login) # 绑定请求登录函数

        self.formFrame = QtWidgets.QFrame(self.centralwidget)
        self.formFrame.setGeometry(QtCore.QRect(0, -1, 540, 211))
        self.formFrame.setStyleSheet("border-color: rgb(0, 85, 255);\n"
                                     "background-image: url(../source/image_basic/login_background.jpg);")
        self.formFrame.setObjectName("formFrame")
        self.formLayout = QtWidgets.QFormLayout(self.formFrame)
        self.formLayout.setObjectName("formLayout")
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.MainWindow.setWindowTitle(_translate("MainWindow", "myChat登录"))
        self.pushButton.setText(_translate("MainWindow", "登录"))

    # 点击登录按钮调用方法
    def login(self):
        # 获取输入的用户名、密码
        user_id = self.lineEdit_account.text()
        user_password = self.lineEdit_password.text()
        # 检查是否输入用户名
        if not user_id:
            QtWidgets.QMessageBox.information(self.MainWindow, '提示', '用户名不能为空!',
                                              QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Close,
                                              QtWidgets.QMessageBox.Close)
        else:
            # 检查是否输入密码
            if not user_password:
                QtWidgets.QMessageBox.information(self.MainWindow, '提示', '密码不能为空!',
                                                  QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Close,
                                                  QtWidgets.QMessageBox.Close)
            # 用户名密码都正常输入
            else:
                # 构建登录请求消息
                req_msg = {
                    "type": "login_req",
                    "args": {
                        "account": user_id,
                        "password": user_password,
                        "time": get_time(),
                    }
                }
                try:
                    # 创建socket，并主动连接服务器
                    self.client_socket = socket(AF_INET, SOCK_STREAM)
                    host_socket = ("127.0.0.1", 5544)
                    self.client_socket.connect(host_socket)
                    send_data(self.client_socket, req_msg)
                    print("[{}] 发出登录请求:".format(get_time()))
                    print(req_msg)
                    # 接收服务器返回的登录响应消息
                    recv_rsp = receive(self.client_socket)
                    if recv_rsp["type"] == "login_res":
                        # 登录成功
                        if recv_rsp["args"]["login_status"]:
                            print("[{}] 收到登录成功响应:".format(get_time()))
                            print(recv_rsp)
                            user_info = recv_rsp["args"]["user_info"]
                            friend_list = recv_rsp["args"]["friend_list"]
                            group_list = recv_rsp["args"]["group_list"]
                            client_socket = self.client_socket
                            # 打开聊天框，并关闭登录窗口，将对应的客户端socket等信息传入聊天窗口
                            ui_chat = chat.Ui_Chat_MainWindow(client_socket, user_info, friend_list, group_list)
                            self.MainWindow.close()
                        # 登录失败
                        else:
                            print("[{}] 收到登录失败响应:".format(get_time()))
                            print(recv_rsp)
                            # 弹窗显示失败信息
                            error_msg = recv_rsp["args"]["res_msg"]
                            QtWidgets.QMessageBox.information(self, 'error', error_msg)
                            self.client_socket.close()
                # 服务器连接失败，抛出异常
                except Exception as e:
                    QtWidgets.QMessageBox.information(self, 'error', '连接服务器失败')
                    self.client_socket.close()

if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    widget = QtWidgets.QWidget()
    ui = Ui_MainWindow()
    ui.setupUi(widget)
    ui.retranslateUi()
    widget.show()

    sys.exit(app.exec_())
