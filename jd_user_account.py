



# jd账号信息及登录处理
class JDUserAccount(object):
    def __init__(self, nickname="unknown", phone_number="", pay_password=""):
        self.__nickname = nickname
        self.__phone_number = phone_number
        self.__pay_password = pay_password
        self.__cookie_file = ""
        self.__is_logined = False

    def set_nickname(self, nick_name):
        self.__nickname = nick_name

    def get_nickname(self):
        return self.__nickname

    def get_payment(self):
        return self.__pay_password

    def get_login_status(self):
        return self.__is_logined

    def set_login_status(self, is_login):
        self.__is_logined = is_login



    def __repr__(self):
        return "JDUserAccount{{\n    nick_name: {0}\n    phone_number: {1}}}".format(self.__nickname,self.__phone_number)
