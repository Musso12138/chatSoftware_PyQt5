# 单个用户类
class user():

    def __init__(self, user_id="", user_password="", user_name="", user_friend=[], user_group=[]):
        self.user_info = {}
        self.user_info["id"] = user_id
        self.user_info["password"] = user_password
        self.user_info["name"] = user_name
        self.user_info["friend"] = user_friend
        self.user_info["group"] = user_group
        self.user_info["unread"] = 0
        # self.user_info["time"] = 0


# 所有用户的类
class users():

    def __init__(self):
        self.user_list = []

    # 根据id查找user
    def findUser(self, user_id):
        for x in self.user_list:
            if x.user_info["id"] == user_id:
                return x.user_info

    # 根据id查找user昵称
    def getUserName(self, user_id):
        for x in self.user_list:
            if x.user_info["id"] == user_id:
                return x.user_info["name"]

    # 添加未读消息数
    def addUnread(self, user_id):
        for x in self.user_list:
            if x.user_info["id"] == user_id:
                x.user_info["unread"] += 1

    # 减少未读消息数
    def decUnread(self, user_id):
        for x in self.user_list:
            if x.user_info["id"] == user_id:
                x.user_info["unread"] -= 1

    # 有未读消息
    def haveUnread(self, user_id):
        for x in self.user_list:
            if x.user_info["id"] == user_id:
                if x.user_info["unread"] > 0:
                    return True
                else:
                    return False
        return False

    # 根据id查找好友
    def getFriends(self, user_id):
        for x in self.user_list:
            if x.user_info["id"] == user_id:
                user_friends = []
                for friend in x.user_info["friend"]:
                    friend_id = friend
                    friend_info = self.findUser(friend)
                    friend_name = friend_info["name"]
                    user_friends.append((friend_name, friend_id))
                return user_friends
        return False

    # 根据id查找群组
    def getGroups(self, user_id):
        for x in self.user_list:
            if x.user_info["id"] == user_id:
                user_groups = []
                for group in x.user_info["group"]:
                    group_id = group
                    group_name = grouplist.findGroup(group_id)["name"]
                    user_groups.append((group_name, group_id))
                return user_groups

    # 根据id查找user是否在线
    # def isOnline(self, user_id):
    #     for x in self.user_list:
    #         if x.user_info["id"] == user_id:
    #             if x.user_info["time"] > 0:
    #                 return True
    #     return False

    # 输入登录user的id、ip、port将其设置为在线
    # def online(self, user_id):
    #     for x in self.user_list:
    #         if x.user_info["id"] == user_id:
    #             x.user_info["time"] = 10
    #             return
    #     return

    # 根据id、ip、port设置user的IP和端口
    # def setSock(self, user_id, user_ip, user_port):
    #     for x in self.user_list:
    #         if x.user_info["id"] == user_id:
    #             x.user_info["ip"] = user_ip
    #             x.user_info["port"] = user_port
    #             return
    #     return

    # 将用户下线
    # def offline(self, user_id):
    #     for x in self.user_list:
    #         if x.user_info["id"] == user_id:
    #             x.user_info["time"] = -1
    #             return
    #     return

    # 在users中新加user
    def appendUser(self, x: user):
        self.user_list.append(x)



class group():

    def __init__(self, group_id, group_name, group_admin=[], group_mem=[]):
        self.group_info = {}
        self.group_info["id"] = group_id
        self.group_info["name"] = group_name
        self.group_info["admin"] = group_admin
        self.group_info["members"] = group_mem



class groups():

    def __init__(self):
        self.grouplist = []

    # 根据群id获取群成员
    def getGroupMems(self, groupid):
        for x in self.grouplist:
            if x.group_info["id"] == groupid:
                return x.group_info["members"]

    # 根据群id获取群名称
    def getGroupName(self, groupid):
        for x in self.grouplist:
            if x.group_info["id"] == groupid:
                return x.group_info["name"]

    # 根据id获取群管理员
    def getGroupAdmins(self, groupid):
        for x in self.grouplist:
            if x.group_info["id"] == groupid:
                return x.group_info["admin"]

    # 根据群id查找群
    def findGroup(self, groupid):
        for x in self.grouplist:
            if x.group_info["id"] == groupid:
                return x.group_info

    # 添加新群组
    def appendGroup(self, x: group):
        self.grouplist.append(x)


group1 = group("1", "管理员群", ["musso", "admin"], ["musso", "admin"])
group2 = group("2", "群组1", ["musso"], ["musso", "123456", "1234567"])
group3 = group("3", "群组2", ["musso"], ["musso", "1234567", "12345678"])

grouplist = groups()
group_reg_list = [group1, group2, group3]
for x in group_reg_list:
    grouplist.appendGroup(x)

user1 = user("admin", "admin", "超级管理员", ["musso"], ["1"])
user2 = user("musso", "musso", "Musso", ["admin", "123456"], ["1", "2", "3"])
user3 = user("123456", "123456", "用户1", ["musso", "1234567", "12345678"], ["2"])
user4 = user("1234567", "123456", "用户2", ["123456", "12345678"], ["2", "3"])
user5 = user("12345678", "123456", "用户3", ["123456", "1234567"], ["3"])

userlist = users()
user_reg_list = [user1, user2, user3, user4, user5]
for x in user_reg_list:
    userlist.appendUser(x)


