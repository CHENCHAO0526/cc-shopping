



# jd账号信息及登录处理
class JDUserAccount(object):
    def __init__(self, nickname="unknown", phone_number="", pay_password=""):
        self.__nickname = nickname
        self.__phone_number = phone_number
        self.__pay_password = pay_password
        self.__cookie_file = ""
        self.__is_login = False

    def set_nickname(self, nick_name):
        self.__nickname = nick_name

    def get_nickname(self):
        return self.__nickname

    def get_payment(self):
        return self.__pay_password

    def is_login(self):
        return self.__is_login

    def set_login(self, is_login):
        self.__is_login = is_login



    def __repr__(self):
        return "JDUserAccount{{\n    nick_name: {0}\n    phone_number: {1}}}".format(self.__nickname,self.__phone_number)
