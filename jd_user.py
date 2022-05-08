import functools
import json
import os
import pickle
import random
import time
import requests
import re
from bs4 import BeautifulSoup
from jd_user_account import JDUserAccount
from exception import CCShoppingException
from log import logger
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5 as Cipher_pkcs1_v1_5
from base64 import b64encode
import json

from util import (
    open_image,
    parse_json,
    get_tag_value,
)

DEFAULT_QR_FILE = "browser_rubbish/QRcode.png"
DEFAULT_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36"

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.1 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2226.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.4; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2225.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2225.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2224.3 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.93 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.124 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2049.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 4.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2049.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.67 Safari/537.36",
    "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.67 Safari/537.36",
    "Mozilla/5.0 (X11; OpenBSD i386) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1944.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.3319.102 Safari/537.36",
    "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.2309.372 Safari/537.36",
    "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.2117.157 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36",
    "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1866.237 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.137 Safari/4E423F",
    "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.116 Safari/537.36 Mozilla/5.0 (iPad; U; CPU OS 3_2 like Mac OS X; en-us) AppleWebKit/531.21.10 (KHTML, like Gecko) Version/4.0.4 Mobile/7B334b Safari/531.21.10",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.517 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1667.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1664.3 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1664.3 Safari/537.36",
    "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.16 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1623.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/30.0.1599.17 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/29.0.1547.62 Safari/537.36",
    "Mozilla/5.0 (X11; CrOS i686 4319.74.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/29.0.1547.57 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/29.0.1547.2 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1468.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1467.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1464.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1500.55 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.93 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.93 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.93 Safari/537.36",
    "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.93 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.93 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.93 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.90 Safari/537.36",
    "Mozilla/5.0 (X11; NetBSD) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.116 Safari/537.36",
    "Mozilla/5.0 (X11; CrOS i686 3912.101.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.116 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.60 Safari/537.17",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_2) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1309.0 Safari/537.17",
    "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.15 (KHTML, like Gecko) Chrome/24.0.1295.0 Safari/537.15",
    "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.14 (KHTML, like Gecko) Chrome/24.0.1292.0 Safari/537.14"
]
LOGIN_URL = "https://passport.jd.com/new/login.aspx"
QR_CODE_URL = "https://qr.m.jd.com/show"
QR_CHECK_URL = "https://qr.m.jd.com/check"
QR_TICKET_VALIDATE_URL = "https://passport.jd.com/uc/qrCodeTicketValidation"
USER_INFO_URL = "https://passport.jd.com/user/petName/getUserInfoForMiniJd.action"
LIST_URL = "https://order.jd.com/center/list.action"
STOCK_URL = "https://c0.3.cn/stock"
CANCEL_ALL_ITEM_URL = "https://cart.jd.com/cancelAllItem.action"
CART_ACTION_URL = 'https://cart.jd.com/cart_index'
CART_URL = 'https://cart.jd.com'
CHANGE_NUM_URL = "https://cart.jd.com/changeNum.action"


# browser的static方法
def _save_image(resp, image_file):
    with open(image_file, "wb") as f:
        for chunk in resp.iter_content(chunk_size=1024):
            f.write(chunk)


def _get_random_useragent():
    """生成随机的UserAgent
    :return: UserAgent字符串
    """
    return random.choice(USER_AGENTS)


def _get_response_status(resp):
    if resp.status_code != requests.codes.OK:
        logger.info("Status: %u, Url: %s" % (resp.status_code, resp.url))
        return False
    return True


def _check_login(func):
    """用户登陆态校验装饰器。若用户未登陆，则调用扫码登陆"""

    @functools.wraps(func)
    def new_func(self, *args, **kwargs):
        if not self.is_login:
            logger.info("{0} 需登陆后调用，开始扫码登陆".format(func.__name__))
            self.login_by_QRcode()
        return func(self, *args, **kwargs)

    return new_func


def _parse_sku_id(sku_ids):
    """将商品id字符串解析为字典

    商品id字符串采用英文逗号进行分割。
    可以在每个id后面用冒号加上数字，代表该商品的数量，如果不加数量则默认为1。

    例如：
    输入  -->  解析结果
    '123456' --> {'123456': '1'}
    '123456,123789' --> {'123456': '1', '123789': '1'}
    '123456:1,123789:3' --> {'123456': '1', '123789': '3'}
    '123456:2,123789' --> {'123456': '2', '123789': '1'}

    :param sku_ids: 商品id字符串
    :return: dict
    """
    if isinstance(sku_ids, dict):  # 防止重复解析
        return sku_ids

    sku_id_list = list(filter(bool, map(lambda x: x.strip(), sku_ids.split(','))))
    result = dict()
    for item in sku_id_list:
        if ':' in item:
            sku_id, count = map(lambda x: x.strip(), item.split(':'))
            result[sku_id] = count
        else:
            result[item] = '1'
    return result


def _parse_area_id(area):
    """解析地区id字符串：将分隔符替换为下划线 _
    :param area: 地区id字符串（使用 _ 或 - 进行分割），如 12_904_3375 或 12-904-3375
    :return: 解析后字符串
    """
    area_id_list = list(map(lambda x: x.strip(), re.split('_|-', area)))
    area_id_list.extend((4 - len(area_id_list)) * ['0'])
    return '_'.join(area_id_list)

def _get_tag_value(tag, key='', index=0):
    if key:
        value = tag[index].get(key)
    else:
        value = tag[index].text
    return value.strip(' \t\r\n')

RSA_PUBLIC_KEY = """-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDC7kw8r6tq43pwApYvkJ5lalja
N9BZb21TAIfT/vexbobzH7Q8SUdP5uDPXEBKzOjx2L28y7Xs1d9v3tdPfKI2LR7P
AzWBmDMn8riHrDDNpUpJnlAGUqJG9ooPn8j7YNpcxCa1iybOlc2kEhmJn5uwoanQ
q+CA6agNkqly2H4j6wIDAQAB
-----END PUBLIC KEY-----"""

def _encrypt_pwd(password, public_key=RSA_PUBLIC_KEY):
    rsa_key = RSA.importKey(public_key)
    encryptor = Cipher_pkcs1_v1_5.new(rsa_key)
    cipher = b64encode(encryptor.encrypt(password.encode('utf-8')))
    return cipher.decode('utf-8')

def _encrypt_payment_pwd(payment_pwd):
    return ''.join(['u3' + x for x in payment_pwd])

class JdUser(object):
    """
    京东用户进行抽象，用户的动作有登录，检查库存，结算
    """

    def __init__(self, config):
        account_config = config.get_section_config("account")
        browser_config = config.get_section_config("browser")
        rush_config = config.get_section_config("rush")
        self.__extra_config = config.get_section_config("extra")
        self.__account = JDUserAccount(**account_config)
        self.__rush_config = self.__parse_rush_config(rush_config)
        self.__user_agent = DEFAULT_USER_AGENT if not browser_config['use_random_ua'] else _get_random_useragent()
        self.__headers = {"User-Agent": self.__user_agent}
        self.sess = requests.session()
        self.__item_cat = dict()
        self.__item_vender_ids = dict()  # 记录商家id
        self.__risk_control = self.__extra_config['risk_control']

        self.rushing = True

    def __parse_rush_config(self, rush_config):
        rush_config_dict = dict()
        rush_config_dict['sku_ids'] = _parse_sku_id(rush_config["sku_ids"])
        rush_config_dict['area_id'] = _parse_area_id(rush_config['area_id'])
        rush_config_dict['wait_all'] = rush_config.getboolean('wait_all')
        rush_config_dict['stock_interval'] = rush_config.getint('stock_interval')
        rush_config_dict['submit_retry'] = rush_config.getint('submit_retry')
        rush_config_dict['submit_interval'] = rush_config.getint('submit_interval')
        rush_config_dict['timeout'] = rush_config.getint('timeout')
        return rush_config_dict

    def set_sku_ids(self, sku_ids_dict):
        self.__rush_config['sku_ids'] = sku_ids_dict

    def set_login(self, islogin):
        self.__account.set_login(islogin)

    def get_nickname(self):
        return self.__account.get_nickname()

    def set_nickname(self, nickname):
        self.__account.set_nickname(nickname)

    def is_rushing(self):
        return self.rushing

    def set_rushing(self, rushing):
        self.rushing = rushing


    def login(self, nickname='ll42883283'):
        if nickname:
            is_login = self.load_cookies(nickname)
            self.set_login(True)
            if is_login:
                return
        nickname = self.__login_by_qrcode()
        self.set_nickname(nickname)

    def __login_by_qrcode(self):
        """
        通过二维码登录
        :return:
        """
        self.__get_login_page()
        # download QR code
        if not self.__get_login_QRcode():
            raise CCShoppingException("二维码下载失败")
        # get QR code ticket
        retry_times = 85
        for _ in range(retry_times):
            ticket = self.__get_QRcode_ticket()
            if ticket:
                break
            logger.info("二维码扫描未成功")
            time.sleep(2)
        else:
            raise CCShoppingException("二维码过期，请重新获取扫描")
        # validate QR code ticket
        if not self.__validate_QRcode_ticket(ticket):
            raise CCShoppingException('二维码信息校验失败')

        nickname = self.__get_user_nickname()
        self.__save_cookies(nickname)
        logger.info('二维码登录成功')
        return nickname

    def __get_login_page(self):
        page = self.sess.get(LOGIN_URL, headers=self.__headers)
        return page

    def __get_login_QRcode(self):

        # think 这些变量是该放在离使用地方远的地方还是近的
        payload = {
            "appid": 133,
            "size": 147,
            "t": str(int(time.time() * 1000)),
        }
        headers = {
            "User-Agent": self.__user_agent,
            "Referer": LOGIN_URL,
        }
        resp = self.sess.get(url=QR_CODE_URL, headers=headers, params=payload)

        if not _get_response_status(resp):
            logger.info("获取二维码失败")
            return False

        _save_image(resp, DEFAULT_QR_FILE)
        logger.info("二维码获取成功，请打开京东APP扫描")
        open_image(DEFAULT_QR_FILE)
        return True

    def __get_QRcode_ticket(self):
        payload = {
            "appid": "133",
            "callback": "jQuery{}".format(random.randint(1000000, 9999999)),
            "token": self.sess.cookies.get("wlfstk_smdl"),
            "_": str(int(time.time() * 1000)),
        }
        headers = {
            "User-Agent": self.__user_agent,
            "Referer": LOGIN_URL,
        }
        resp = self.sess.get(url=QR_CHECK_URL, headers=headers, params=payload)

        if not _get_response_status(resp):
            logger.error("获取二维码扫描结果异常")
            return False

        resp_json = parse_json(resp.text)
        if resp_json["code"] != 200:
            logger.info("Code: %s, Message: %s", resp_json["code"], resp_json["msg"])
            return None
        else:
            logger.info("已完成手机客户端确认")
            return resp_json["ticket"]

    def __validate_QRcode_ticket(self, ticket):
        headers = {
            'User-Agent': self.__user_agent,
            'Referer': 'https://passport.jd.com/uc/login?ltype=logout',
        }
        resp = self.sess.get(url=QR_TICKET_VALIDATE_URL, headers=headers, params={'t': ticket})

        if not _get_response_status(resp):
            return False

        resp_json = json.loads(resp.text)
        if resp_json['returnCode'] == 0:
            return True
        else:
            logger.info(resp_json)
            return False

    # @check_login
    def __get_user_nickname(self):
        """获取用户信息
        :return: 用户名
        """
        payload = {
            'callback': 'jQuery{}'.format(random.randint(1000000, 9999999)),
            '_': str(int(time.time() * 1000)),
        }
        headers = {
            'User-Agent': self.__user_agent,
            'Referer': 'https://order.jd.com/center/list.action',
        }
        try:
            resp = self.sess.get(url=USER_INFO_URL, params=payload, headers=headers)
            resp_json = parse_json(resp.text)
            # many user info are included in response, now return nick name in it
            # jQuery2381773({"imgUrl":"//storage.360buyimg.com/i.imageUpload/xxx.jpg","lastLoginTime":"","nickName":"xxx","plusStatus":"0","realName":"xxx","userLevel":x,"userScoreVO":{"accountScore":xx,"activityScore":xx,"consumptionScore":xxxxx,"default":false,"financeScore":xxx,"pin":"xxx","riskScore":x,"totalScore":xxxxx}})
            return resp_json.get('nickName') or 'jd'
        except Exception:
            logger.error("获取用户信息失败")
            return 'jd'

    def __save_cookies(self, nickname):
        cookies_file = './cookies/{0}.cookies'.format(nickname)
        directory = os.path.dirname(cookies_file)
        if not os.path.exists(directory):
            os.makedirs(directory)
        with open(cookies_file, 'wb') as f:
            pickle.dump(self.sess.cookies, f)

    def load_cookies(self, nickname):
        cookies_file = './cookies/{0}.cookies'.format(nickname)
        if not os.path.exists(cookies_file):
            return False
        with open(cookies_file, 'rb') as f:
            local_cookies = pickle.load(f)
        self.sess.cookies.update(local_cookies)
        is_login = self.__validate_cookies()
        logger.info("加载cookie成功")
        return is_login

    def __validate_cookies(self):
        """验证cookies是否有效（是否登陆）
        通过访问用户订单列表页进行判断：若未登录，将会重定向到登陆页面。
        :return: cookies是否有效 True/False
        """
        payload = {
            'rid': str(int(time.time() * 1000)),
        }
        resp = self.sess.get(url=LIST_URL, params=payload, allow_redirects=False)
        if resp.status_code == requests.codes.OK:
            return True
        self.sess = requests.session()
        return False

    def buy_item_in_stock(self):
        """根据库存自动下单商品
        :return:
        """
        logger.info('下单模式：%s 所有都商品同时有货并且未下架才会尝试下单', self.__rush_config["sku_ids"])
        self._cancel_select_all_cart_item()
        while self.rushing:
            items_dict = self.__rush_config["sku_ids"]
            stock_interval = self.__rush_config["stock_interval"]
            if not self.if_item_can_be_ordered():
                logger.info('%s 不满足下单条件，%ss后进行下一次查询', items_dict, stock_interval)
                continue
            logger.info('%s 满足下单条件，开始执行', items_dict)
            cart_item_details = self._get_cart_detail()
            for (sku_id, count) in items_dict.items():
                self._add_or_change_cart_item(cart_item_details, sku_id, count)
            if self._submit_order_with_retry(self.__rush_config['submit_retry'], self.__rush_config['submit_interval']):
                return
            time.sleep(stock_interval)
        logger.info('stop rush')

    def if_item_can_be_ordered(self):
        """判断商品是否能下单
        :return: 商品是否能下单 True/False
        """
        items_dict = self.__rush_config["sku_ids"]
        area_id = self.__rush_config["area_id"]

        # 判断商品是否能下单
        if len(items_dict) > 1:
            return self.get_multi_item_stock_status(sku_ids=items_dict, area=area_id)

        sku_id, count = list(items_dict.items())[0]
        return self.get_single_item_stock_status(sku_id=sku_id, num=count, area=area_id)

    def get_single_item_stock_status(self, sku_id, num, area):
        """获取单个商品库存状态
        :param sku_id: 商品id
        :param num: 商品数量
        :param area: 地区id
        :return: 商品是否有货 True/False
        """
        area_id = _parse_area_id(area)

        cat = self.__item_cat.get(sku_id)
        vender_id = self.__item_vender_ids.get(sku_id)
        if not cat:
            page = self.__get_item_detail_page(sku_id)
            match = re.search(r'cat: \[(.*?)\]', page.text)
            cat = match.group(1)
            self.__item_cat[sku_id] = cat

            match = re.search(r'venderId:(\d*?),', page.text)
            vender_id = match.group(1)
            self.__item_vender_ids[sku_id] = vender_id

        payload = {
            'skuId': sku_id,
            'buyNum': num,
            'area': area_id,
            'ch': 1,
            '_': str(int(time.time() * 1000)),
            'callback': 'jQuery{}'.format(random.randint(1000000, 9999999)),
            'extraParam': '{"originid":"1"}',  # get error stock state without this param
            'cat': cat,  # get 403 Forbidden without this param (obtained from the detail page)
            'venderId': vender_id  # return seller information with this param (can't be ignored)
        }
        headers = {
            'User-Agent': self.__user_agent,
            'Referer': 'https://item.jd.com/{}.html'.format(sku_id),
        }

        resp_text = requests.get(url=STOCK_URL, params=payload, headers=headers,
                                 timeout=self.__rush_config['timeout']).text
        try:
            resp_text = requests.get(url=STOCK_URL, params=payload, headers=headers, timeout=self.__rush_config['timeout']).text
            resp_json = parse_json(resp_text)
            stock_info = resp_json.get('stock')
            sku_state = stock_info.get('skuState')  # 商品是否上架
            stock_state = stock_info.get('StockState')  # 商品库存状态：33 -- 现货  0,34 -- 无货  36 -- 采购中  40 -- 可配货
            return sku_state == 1 and stock_state in (33, 40)
        except requests.exceptions.Timeout:
            logger.error('查询 %s 库存信息超时(%ss)', sku_id, self.__rush_config['timeout'])
            return False
        except requests.exceptions.RequestException as request_exception:
            logger.error('查询 %s 库存信息发生网络请求异常：%s', sku_id, request_exception)
            return False
        except Exception as e:
            logger.error('查询 %s 库存信息发生异常, resp: %s, exception: %s', sku_id, resp_text, e)
            return False

    def __get_item_detail_page(self, sku_id):
        """访问商品详情页
        :param sku_id: 商品id
        :return: 响应
        """
        url = 'https://item.jd.com/{}.html'.format(sku_id)
        page = requests.get(url=url, headers=self.__headers)
        return page

    def get_multi_item_stock_status(self, sku_ids, area):
        """获取多个商品库存状态（新）

        当所有商品都有货，返回True；否则，返回False。

        :param sku_ids: 多个商品的id。可以传入中间用英文逗号的分割字符串，如"123,456"
        :param area: 地区id
        :return: 多个商品是否同时有货 True/False
        """
        items_dict = _parse_sku_id(sku_ids=sku_ids)
        area_id = _parse_area_id(area=area)

        payload = {
            'callback': 'jQuery{}'.format(random.randint(1000000, 9999999)),
            'type': 'getstocks',
            'skuIds': ','.join(items_dict.keys()),
            'area': area_id,
            '_': str(int(time.time() * 1000))
        }
        headers = {
            'User-Agent': self.__user_agent
        }

        resp_text = ''
        try:
            resp_text = requests.get(url=STOCK_URL, params=payload, headers=headers, timeout=self.__rush_config['timeout']).text
            for sku_id, info in parse_json(resp_text).items():
                sku_state = info.get('skuState')  # 商品是否上架
                stock_state = info.get('StockState')  # 商品库存状态
                if sku_state == 1 and stock_state in (33, 40):
                    continue
                else:
                    return False
            return True
        except requests.exceptions.Timeout:
            logger.error('查询 %s 库存信息超时(%ss)', list(items_dict.keys()), self.__rush_config['timeout'])
            return False
        except requests.exceptions.RequestException as request_exception:
            logger.error('查询 %s 库存信息发生网络请求异常：%s', list(items_dict.keys()), request_exception)
            return False
        except Exception as e:
            logger.error('查询 %s 库存信息发生异常, resp: %s, exception: %s', list(items_dict.keys()), resp_text, e)
            return False

    # def _cancel_select_all_cart_item(self):
    #     """取消勾选购物车中的所有商品
    #             :return: 取消勾选结果 True/False
    #             """
    #     data = {
    #         't': 0,
    #         'outSkus': '',
    #         'random': random.random()
    #         # 'locationId' can be ignored
    #     }
    #     resp = self.sess.post(CANCEL_ALL_ITEM_URL, data=data)
    #     return _get_response_status(resp)

    def _cancel_select_all_cart_item(self):
        """取消勾选购物车中的所有商品
                :return: 取消勾选结果 True/False
                """
        # body_dict = {"serInfo": {"area": "1_2800_55816_0", "user-key": "c687b7fb-9916-47a4-9fe6-d43fbdaca0fb"}}
        # data = {
        #     'functionId': 'pcCart_jc_cartCheckAll', #pcCart_jc_cartUnCheckAll
        #     'appid': 'JDC_mall_cart',
        #     'loginType': 3,
        #     'body': body_dict
        #     # 'locationId' can be ignored
        # }
        # data_json = json.dumps(data)
        headers = {
            'User-Agent': self.__user_agent,
            'Referer': 'https://cart.jd.com',
        }

        resp = self.sess.post('https://api.m.jd.com/api?functionId=pcCart_jc_cartUnCheckAll&appid=JDC_mall_cart&loginType=3&body={"serInfo":{"area":"1_2800_55816_0","user-key":"c687b7fb-9916-47a4-9fe6-d43fbdaca0fb"}}',headers=headers)
        return _get_response_status(resp)

    #@check_login
    def _get_cart_detail_old(self):
        """获取购物车商品详情
        :return: 购物车商品信息 dict
        """
        headers = {
            'User-Agent': self.__user_agent,
            'Referer': CART_URL
        }
        resp = self.sess.get(CART_ACTION_URL, headers=headers)
        soup = BeautifulSoup(resp.text, "html.parser")

        cart_detail = dict()
        for item in soup.find_all(class_='item-item'):
            try:
                sku_id = item['skuid']  # 商品id
                # 例如：['increment', '8888', '100001071956', '1', '13', '0', '50067652554']
                # ['increment', '8888', '100002404322', '2', '1', '0']
                item_attr_list = item.find(class_='increment')['id'].split('_')
                p_type = item_attr_list[4]
                promo_id = target_id = item_attr_list[-1] if len(item_attr_list) == 7 else 0

                cart_detail[sku_id] = {
                    'name': get_tag_value(item.select('div.p-name a')),  # 商品名称
                    'verder_id': item['venderid'],  # 商家id
                    'count': int(item['num']),  # 数量
                    'unit_price': get_tag_value(item.select('div.p-price strong'))[1:],  # 单价
                    'total_price': get_tag_value(item.select('div.p-sum strong'))[1:],  # 总价
                    'is_selected': 'item-selected' in item['class'],  # 商品是否被勾选
                    'p_type': p_type,
                    'target_id': target_id,
                    'promo_id': promo_id
                }
            except Exception as e:
                logger.error("某商品在购物车中的信息无法解析，报错信息: %s，该商品自动忽略。 %s", e, item)

        logger.info('购物车信息：%s', cart_detail)
        return cart_detail
    
    #@check_login
    def _get_cart_detail(self):
        """获取购物车商品详情
        :return: 购物车商品信息 dict
        """
        headers = {
            'User-Agent': self.__user_agent,
            'Referer': CART_URL
        }
        CART_DETAIL_URL = 'https://api.m.jd.com/api?functionId=pcCart_jc_getCurrentCart&appid=JDC_mall_cart&loginType=3&body={"serInfo":{"area":"4_48201_52489_0"},"cartExt":{"specialId":1}}'
        resp = self.sess.post(CART_DETAIL_URL, headers=headers)
        if _get_response_status(resp) != True:
            logger.error("请求购物车信息失败")
        resp_json = resp.json()
        if resp_json['success'] != True or resp_json['code'] != 0:
            logger.info(resp_json)
        vendors = resp_json['resultData']['cartInfo']['vendors']
        cart_item_details = {}
        for vendor in vendors:
            vendor_items = vendor['sorted']
            for item in vendor_items:
                item = item['item']
                cart_item_details[item['Id']] = item
        return cart_item_details

    def _add_or_change_cart_item(self, cart_item_details, sku_id, count):
        """添加商品到购物车，或修改购物车中商品数量

        如果购物车中存在该商品，会修改该商品的数量并勾选；否则，会添加该商品到购物车中并勾选。

        :param cart_item_details: 购物车信息 dict
        :param sku_id: 商品id
        :param count: 商品数量
        :return: 运行结果 True/False
        """
        if sku_id in cart_item_details:
            logger.info('%s 已在购物车中，调整数量为 %s', sku_id, count)
            cart_item = cart_item_details.get(sku_id)
            self._change_item_num_in_cart(
                sku_id=sku_id,
                vender_id=cart_item.get('vendorId'),
                num=count,
                p_type=cart_item.get('p_type'),
                target_id=cart_item.get('target_id'),
                promo_id=cart_item.get('promo_id')
            )
        else:
            logger.info('%s 不在购物车中，开始加入购物车，数量 %s', sku_id, count)
            self._add_item_to_cart(sku_ids={sku_id: count})

    #@check_login
    def get_checkout_page_detail(self):
        """获取订单结算页面信息

        该方法会返回订单结算页面的详细信息：商品名称、价格、数量、库存状态等。

        :return: 结算信息 dict
        """
        url = 'http://trade.jd.com/shopping/order/getOrderInfo.action'
        payload = {
            'rid': str(int(time.time() * 1000)),
        }
        resp = self.sess.get(url=url, params=payload)
        if not _get_response_status(resp):
            logger.error('获取订单结算页信息失败')
            return

        soup = BeautifulSoup(resp.text, "html.parser")
        self.__risk_control = get_tag_value(soup.select('input#riskControl'), 'value')

        order_detail = {
            'address': soup.find('span', id='sendAddr').text[5:],  # remove '寄送至： ' from the begin
            'receiver': soup.find('span', id='sendMobile').text[4:],  # remove '收件人:' from the begin
            'total_price': soup.find('span', id='sumPayPriceId').text[1:],  # remove '￥' from the begin
            'items': []
        }
        # TODO: 这里可能会产生解析问题，待修复
        # for item in soup.select('div.goods-list div.goods-items'):
        #     div_tag = item.select('div.p-price')[0]
        #     order_detail.get('items').append({
        #         'name': get_tag_value(item.select('div.p-name a')),
        #         'price': get_tag_value(div_tag.select('strong.jd-price'))[2:],  # remove '￥ ' from the begin
        #         'num': get_tag_value(div_tag.select('span.p-num'))[1:],  # remove 'x' from the begin
        #         'state': get_tag_value(div_tag.select('span.p-state'))  # in stock or out of stock
        #     })

        logger.info("下单信息：%s", order_detail)
        return order_detail
        #logger.error('订单结算页面数据解析异常（可以忽略），报错信息：%s', e)

    def _change_item_num_in_cart(self, sku_id, vender_id, num, p_type, target_id, promo_id):
        """修改购物车商品的数量
        修改购物车中商品数量后，该商品将会被自动勾选上。

        :param sku_id: 商品id
        :param vender_id: 商家id
        :param num: 目标数量
        :param p_type: 商品类型(可能)
        :param target_id: 参数用途未知，可能是用户判断优惠
        :param promo_id: 参数用途未知，可能是用户判断优惠
        :return: 商品数量修改结果 True/False
        """
        url = CHANGE_NUM_URL
        data = {
            't': 0,
            'venderId': vender_id,
            'pid': sku_id,
            'pcount': num,
            'ptype': p_type,
            'targetId': target_id,
            'promoID': promo_id,
            'outSkus': '',
            'random': random.random(),
            # 'locationId'
        }
        headers = {
            'User-Agent': self.__user_agent,
            'Referer': 'https://cart.jd.com/cart',
        }
        resp = self.sess.post(url, data=data, headers=headers)
        resp_json = resp.json()
        if resp_json['sortedWebCartResult']['achieveSevenState'] != 2 and resp_json['sortedWebCartResult']['achieveSevenState'] != 0:
            logger.error("修改购物车商品的数量数量失败, resp.text {}".format(resp.text))
        return

    #@check_login
    def _add_item_to_cart(self, sku_ids):
        """添加商品到购物车

        重要：
        1.商品添加到购物车后将会自动被勾选✓中。
        2.在提交订单时会对勾选的商品进行结算。
        3.部分商品（如预售、下架等）无法添加到购物车

        京东购物车可容纳的最大商品种数约为118-120种，超过数量会加入购物车失败。

        :param sku_ids: 商品id，格式："123" 或 "123,456" 或 "123:1,456:2"。若不配置数量，默认为1个。
        :return:
        """
        url = 'https://cart.jd.com/gate.action'
        headers = {
            'User-Agent': self.__user_agent,
        }

        for sku_id, count in _parse_sku_id(sku_ids=sku_ids).items():
            payload = {
                'pid': sku_id,
                'pcount': count,
                'ptype': 1,
            }
            resp = self.sess.get(url=url, params=payload, headers=headers)
            if CART_ACTION_URL in resp.url:  # 套装商品加入购物车后直接跳转到购物车页面
                result = True
            else:  # 普通商品成功加入购物车后会跳转到提示 "商品已成功加入购物车！" 页面
                soup = BeautifulSoup(resp.text, "html.parser")
                result = bool(soup.select('h3.ftx-02'))  # [<h3 class="ftx-02">商品已成功加入购物车！</h3>]

            if result:
                logger.info('%s x %s 已成功加入购物车', sku_id, count)
            else:
                logger.error('%s 添加到购物车失败', sku_id)

    def change_sku_num_in_cart(self):
        url = 'https://api.m.jd.com/api?functionId=pcCart_jc_changeSkuNum&appid=JDC_mall_cart&loginType=3&body={"operations":[{"TheSkus":[{"Id":"10107205060","num":5,"skuUuid":"F2sb2k1063935514318069760","useUuid":false}]}],"serInfo":{"area":"1_2800_55816_0"}}'
        headers = {
            'User-Agent': self.__user_agent,
            'Referer': 'https://cart.jd.com/cart',
        }
        resp = self.sess.post(url, headers=headers)
        return resp




    #@check_login
    def _submit_order_with_retry(self, retry=3, interval=4):
        """提交订单，并且带有重试功能
        :param retry: 重试次数
        :param interval: 重试间隔
        :return: 订单提交结果 True/False
        """
        for i in range(1, retry + 1):
            logger.info('第[%s/%s]次尝试提交订单', i, retry)
            #self.get_checkout_page_detail()
            if self._submit_order():
                logger.info('第%s次提交订单成功', i)
                return True
            else:
                if i < retry:
                    logger.info('第%s次提交失败，%ss后重试', i, interval)
                    time.sleep(interval)
        else:
            logger.info('重试提交%s次结束', retry)
            return False

    #@check_login
    def _submit_order(self):
        """提交订单

        重要：
        1.该方法只适用于普通商品的提交订单（即可以加入购物车，然后结算提交订单的商品）
        2.提交订单时，会对购物车中勾选✓的商品进行结算（如果勾选了多个商品，将会提交成一个订单）

        :return: True/False 订单提交结果
        """
        url = 'https://trade.jd.com/shopping/order/submitOrder.action'
        # js function of submit order is included in https://trade.jd.com/shopping/misc/js/order.js?r=2018070403091

        data = {
            'overseaPurchaseCookies': '',
            'vendorRemarks': '[]',
            'submitOrderParam.sopNotPutInvoice': 'false',
            'submitOrderParam.trackID': 'TestTrackId',
            'submitOrderParam.ignorePriceChange': '0',
            'submitOrderParam.btSupport': '0',
            'riskControl': self.__risk_control,
            'submitOrderParam.isBestCoupon': 1,
            'submitOrderParam.jxj': 1,
            'submitOrderParam.trackId': self.__extra_config['track_id'],  # Todo: need to get trackId
            'submitOrderParam.eid': self.__extra_config['eid'],
            'submitOrderParam.fp': self.__extra_config['fp'],
            'submitOrderParam.needCheck': 1,
        }

        # add payment password when necessary
        payment_pwd = self.__account.get_payment()
        if payment_pwd:
            data['submitOrderParam.payPassword'] = _encrypt_payment_pwd(payment_pwd)

        headers = {
            'User-Agent': self.__user_agent,
            'Host': 'trade.jd.com',
            'Referer': 'http://trade.jd.com/shopping/order/getOrderInfo.action',
        }

        self._save_invoice()
        resp = self.sess.post(url=url, data=data, headers=headers)
        resp_json = json.loads(resp.text)

        # 返回信息示例：
        # 下单失败
        # {'overSea': False, 'orderXml': None, 'cartXml': None, 'noStockSkuIds': '', 'reqInfo': None, 'hasJxj': False, 'addedServiceList': None, 'sign': None, 'pin': 'xxx', 'needCheckCode': False, 'success': False, 'resultCode': 60123, 'orderId': 0, 'submitSkuNum': 0, 'deductMoneyFlag': 0, 'goJumpOrderCenter': False, 'payInfo': None, 'scaleSkuInfoListVO': None, 'purchaseSkuInfoListVO': None, 'noSupportHomeServiceSkuList': None, 'msgMobile': None, 'addressVO': None, 'msgUuid': None, 'message': '请输入支付密码！'}
        # {'overSea': False, 'cartXml': None, 'noStockSkuIds': '', 'reqInfo': None, 'hasJxj': False, 'addedServiceList': None, 'orderXml': None, 'sign': None, 'pin': 'xxx', 'needCheckCode': False, 'success': False, 'resultCode': 60017, 'orderId': 0, 'submitSkuNum': 0, 'deductMoneyFlag': 0, 'goJumpOrderCenter': False, 'payInfo': None, 'scaleSkuInfoListVO': None, 'purchaseSkuInfoListVO': None, 'noSupportHomeServiceSkuList': None, 'msgMobile': None, 'addressVO': None, 'msgUuid': None, 'message': '您多次提交过快，请稍后再试'}
        # {'overSea': False, 'orderXml': None, 'cartXml': None, 'noStockSkuIds': '', 'reqInfo': None, 'hasJxj': False, 'addedServiceList': None, 'sign': None, 'pin': 'xxx', 'needCheckCode': False, 'success': False, 'resultCode': 60077, 'orderId': 0, 'submitSkuNum': 0, 'deductMoneyFlag': 0, 'goJumpOrderCenter': False, 'payInfo': None, 'scaleSkuInfoListVO': None, 'purchaseSkuInfoListVO': None, 'noSupportHomeServiceSkuList': None, 'msgMobile': None, 'addressVO': None, 'msgUuid': None, 'message': '获取用户订单信息失败'}
        # {"cartXml":null,"noStockSkuIds":"xxx","reqInfo":null,"hasJxj":false,"addedServiceList":null,"overSea":false,"orderXml":null,"sign":null,"pin":"xxx","needCheckCode":false,"success":false,"resultCode":600157,"orderId":0,"submitSkuNum":0,"deductMoneyFlag":0,"goJumpOrderCenter":false,"payInfo":null,"scaleSkuInfoListVO":null,"purchaseSkuInfoListVO":null,"noSupportHomeServiceSkuList":null,"msgMobile":null,"addressVO":{"pin":"xxx","areaName":"","provinceId":xx,"cityId":xx,"countyId":xx,"townId":xx,"paymentId":0,"selected":false,"addressDetail":"xx","mobile":"xx","idCard":"","phone":null,"email":null,"selfPickMobile":null,"selfPickPhone":null,"provinceName":null,"cityName":null,"countyName":null,"townName":null,"giftSenderConsigneeName":null,"giftSenderConsigneeMobile":null,"gcLat":0.0,"gcLng":0.0,"coord_type":0,"longitude":0.0,"latitude":0.0,"selfPickOptimize":0,"consigneeId":0,"selectedAddressType":0,"siteType":0,"helpMessage":null,"tipInfo":null,"cabinetAvailable":true,"limitKeyword":0,"specialRemark":null,"siteProvinceId":0,"siteCityId":0,"siteCountyId":0,"siteTownId":0,"skuSupported":false,"addressSupported":0,"isCod":0,"consigneeName":null,"pickVOname":null,"shipmentType":0,"retTag":0,"tagSource":0,"userDefinedTag":null,"newProvinceId":0,"newCityId":0,"newCountyId":0,"newTownId":0,"newProvinceName":null,"newCityName":null,"newCountyName":null,"newTownName":null,"checkLevel":0,"optimizePickID":0,"pickType":0,"dataSign":0,"overseas":0,"areaCode":null,"nameCode":null,"appSelfPickAddress":0,"associatePickId":0,"associateAddressId":0,"appId":null,"encryptText":null,"certNum":null,"used":false,"oldAddress":false,"mapping":false,"addressType":0,"fullAddress":"xxxx","postCode":null,"addressDefault":false,"addressName":null,"selfPickAddressShuntFlag":0,"pickId":0,"pickName":null,"pickVOselected":false,"mapUrl":null,"branchId":0,"canSelected":false,"address":null,"name":"xxx","message":null,"id":0},"msgUuid":null,"message":"xxxxxx商品无货"}
        # {'orderXml': None, 'overSea': False, 'noStockSkuIds': 'xxx', 'reqInfo': None, 'hasJxj': False, 'addedServiceList': None, 'cartXml': None, 'sign': None, 'pin': 'xxx', 'needCheckCode': False, 'success': False, 'resultCode': 600158, 'orderId': 0, 'submitSkuNum': 0, 'deductMoneyFlag': 0, 'goJumpOrderCenter': False, 'payInfo': None, 'scaleSkuInfoListVO': None, 'purchaseSkuInfoListVO': None, 'noSupportHomeServiceSkuList': None, 'msgMobile': None, 'addressVO': {'oldAddress': False, 'mapping': False, 'pin': 'xxx', 'areaName': '', 'provinceId': xx, 'cityId': xx, 'countyId': xx, 'townId': xx, 'paymentId': 0, 'selected': False, 'addressDetail': 'xxxx', 'mobile': 'xxxx', 'idCard': '', 'phone': None, 'email': None, 'selfPickMobile': None, 'selfPickPhone': None, 'provinceName': None, 'cityName': None, 'countyName': None, 'townName': None, 'giftSenderConsigneeName': None, 'giftSenderConsigneeMobile': None, 'gcLat': 0.0, 'gcLng': 0.0, 'coord_type': 0, 'longitude': 0.0, 'latitude': 0.0, 'selfPickOptimize': 0, 'consigneeId': 0, 'selectedAddressType': 0, 'newCityName': None, 'newCountyName': None, 'newTownName': None, 'checkLevel': 0, 'optimizePickID': 0, 'pickType': 0, 'dataSign': 0, 'overseas': 0, 'areaCode': None, 'nameCode': None, 'appSelfPickAddress': 0, 'associatePickId': 0, 'associateAddressId': 0, 'appId': None, 'encryptText': None, 'certNum': None, 'addressType': 0, 'fullAddress': 'xxxx', 'postCode': None, 'addressDefault': False, 'addressName': None, 'selfPickAddressShuntFlag': 0, 'pickId': 0, 'pickName': None, 'pickVOselected': False, 'mapUrl': None, 'branchId': 0, 'canSelected': False, 'siteType': 0, 'helpMessage': None, 'tipInfo': None, 'cabinetAvailable': True, 'limitKeyword': 0, 'specialRemark': None, 'siteProvinceId': 0, 'siteCityId': 0, 'siteCountyId': 0, 'siteTownId': 0, 'skuSupported': False, 'addressSupported': 0, 'isCod': 0, 'consigneeName': None, 'pickVOname': None, 'shipmentType': 0, 'retTag': 0, 'tagSource': 0, 'userDefinedTag': None, 'newProvinceId': 0, 'newCityId': 0, 'newCountyId': 0, 'newTownId': 0, 'newProvinceName': None, 'used': False, 'address': None, 'name': 'xx', 'message': None, 'id': 0}, 'msgUuid': None, 'message': 'xxxxxx商品无货'}

        # {"overSea":false,"outOfStock":false,"orderXml":null,"cartXml":null,"noStockSkuIds":"64602955082","reqInfo":null,"hasJxj":false,"addedServiceList":[],"sign":null,"pin":"cc42883283","overseaMerge":false,"addressVO":{"pin":null,"invalidFlag":false,"presentFlag":false,"coordType":2,"operateTime":null,"showChangeJingAddressFlag":null,"recordMark":null,"needToUploadJicc":false,"selected":true,"mobile":"13121228925","idCard":"","phone":"","email":"","provinceId":4,"appId":null,"selectedAddressType":0,"addressType":0,"cityId":48201,"countyId":52489,"townId":0,"addressDetail":"龙庭盛世小区7栋9楼，送到楼上","provinceName":"重庆","cityName":"合川区","countyName":"城区","townName":"","addressName":"陈超","areaCode":"86","nameCode":null,"postCode":"","giftSenderConsigneeName":null,"giftSenderConsigneeMobile":null,"areaName":"重庆 合川区 城区 ","longitude":1000.0,"latitude":1000.0,"paymentId":0,"pickId":0,"pickName":null,"mapUrl":null,"branchId":0,"canSelected":false,"siteType":0,"used":false,"helpMessage":null,"cabinetAvailable":true,"limitKeyword":0,"specialRemark":null,"isCod":0,"shipmentType":0,"updateTime":"2022-03-30 00:01:41","oldAddress":false,"mapping":false,"gcReliability":11,"gcReliabilitySource":3,"fullAddress":"重庆合川区城区龙庭盛世小区7栋9楼，送到楼上","freePay":false,"addressDefault":true,"selfPickAddressShuntFlag":0,"pickVOselected":false,"tipInfo":null,"siteProvinceId":0,"siteCityId":0,"siteCountyId":0,"siteTownId":0,"skuSupported":false,"addressSupported":0,"consigneeId":0,"consigneeName":null,"pickVOname":null,"selfPickMobile":null,"selfPickPhone":null,"retTag":2,"tagSource":1,"userDefinedTag":"","newProvinceId":0,"newCityId":0,"newCountyId":0,"newTownId":0,"newProvinceName":null,"newCityName":null,"newCountyName":null,"newTownName":null,"checkLevel":0,"selfPickOptimize":0,"optimizePickID":0,"pickType":0,"gcLng":106.27279319138653,"gcLat":30.00574988513638,"dataSign":0,"overseas":0,"appSelfPickAddress":0,"associatePickId":0,"associateAddressId":0,"encryptText":null,"certNum":null,"addressDefaultCancel":null,"lastOrderAddress":false,"sendMq":0,"addressMapperInfoVO":{"processAddress":null,"oldProvinceId":0,"oldCityId":0,"oldCountyId":0,"oldTownId":0,"provinceId":0,"cityId":0,"countyId":0,"townId":0,"addressDetail":null,"provinceName":null,"cityName":null,"countyName":null,"townName":null,"mapping":false,"fullAddress":null,"upStreamErrorCode":null,"resultFlag":true,"resultCode":0,"message":null},"address":null,"name":"陈超","message":null,"id":138286569,"readOnly":false,"uuid":"1011_1080193035568566286","relationMap":null},"resultCode":600158,"international":false,"success":false,"orderId":0,"submitSkuNum":0,"deductMoneyFlag":0,"orderType":0,"goJumpOrderCenter":false,"payInfo":null,"cartEmpty":true,"scaleSkuInfoListVO":null,"purchaseSkuInfoListVO":null,"commonStockSkuInfoList":null,"noSupportHomeServiceSkuList":null,"msgMobile":null,"msgUuid":null,"needCheckCode":false,"message":"安德玛官方UA库里Curry 7男子舒适灵活篮球运动鞋男鞋3021258 白色100 41商品无货！"}
        # {"overSea":false,"outOfStock":false,"orderXml":null,"cartXml":null,"noStockSkuIds":"","reqInfo":null,"hasJxj":false,"addedServiceList":null,"sign":null,"message":"您多次提交过快，请稍后再试","pin":"cc42883283","overseaMerge":false,"addressVO":{"address":null,"name":null,"message":null,"id":0,"readOnly":false,"pin":null,"selected":false,"mobile":null,"idCard":"","phone":null,"email":null,"provinceId":0,"appId":null,"selectedAddressType":0,"addressType":0,"cityId":0,"countyId":0,"townId":0,"addressDetail":null,"provinceName":null,"cityName":null,"countyName":null,"townName":null,"addressName":null,"areaCode":null,"nameCode":null,"postCode":null,"giftSenderConsigneeName":null,"giftSenderConsigneeMobile":null,"areaName":"","longitude":0.0,"latitude":0.0,"paymentId":0,"pickId":0,"pickName":null,"mapUrl":null,"branchId":0,"canSelected":false,"siteType":0,"used":false,"helpMessage":null,"cabinetAvailable":true,"limitKeyword":0,"specialRemark":null,"isCod":0,"shipmentType":0,"updateTime":null,"oldAddress":false,"mapping":false,"gcReliability":0,"gcReliabilitySource":0,"fullAddress":null,"freePay":false,"addressDefault":false,"selfPickAddressShuntFlag":0,"pickVOselected":false,"tipInfo":null,"siteProvinceId":0,"siteCityId":0,"siteCountyId":0,"siteTownId":0,"skuSupported":false,"addressSupported":0,"consigneeId":0,"consigneeName":null,"pickVOname":null,"selfPickMobile":null,"selfPickPhone":null,"retTag":0,"tagSource":0,"userDefinedTag":null,"newProvinceId":0,"newCityId":0,"newCountyId":0,"newTownId":0,"newProvinceName":null,"newCityName":null,"newCountyName":null,"newTownName":null,"checkLevel":0,"selfPickOptimize":0,"optimizePickID":0,"pickType":0,"gcLng":0.0,"gcLat":0.0,"dataSign":0,"overseas":0,"appSelfPickAddress":0,"associatePickId":0,"associateAddressId":0,"encryptText":null,"certNum":null,"addressDefaultCancel":null,"lastOrderAddress":false,"sendMq":0,"addressMapperInfoVO":null,"invalidFlag":false,"presentFlag":false,"coordType":0,"operateTime":null,"showChangeJingAddressFlag":null,"recordMark":null,"needToUploadJicc":false,"uuid":null,"relationMap":null},"resultCode":0,"international":false,"success":false,"orderId":0,"submitSkuNum":0,"deductMoneyFlag":0,"orderType":0,"goJumpOrderCenter":false,"payInfo":null,"cartEmpty":false,"scaleSkuInfoListVO":null,"purchaseSkuInfoListVO":null,"commonStockSkuInfoList":null,"noSupportHomeServiceSkuList":null,"msgMobile":null,"msgUuid":null,"needCheckCode":false}
        # 下单成功
        # '{"overSea":false,"outOfStock":false,"orderXml":null,"cartXml":null,"noStockSkuIds":"","reqInfo":null,"hasJxj":false,"addedServiceList":null,"sign":null,"needCheckCode":false,"pin":"cc42883283","overseaMerge":false,"addressVO":null,"resultCode":0,"international":false,"success":true,"orderId":243664722825,"submitSkuNum":1,"deductMoneyFlag":0,"orderType":0,"goJumpOrderCenter":false,"payInfo":null,"cartEmpty":false,"scaleSkuInfoListVO":null,"purchaseSkuInfoListVO":null,"commonStockSkuInfoList":null,"noSupportHomeServiceSkuList":null,"msgMobile":null,"msgUuid":null,"message":null}'

        if resp_json.get('success'):
            order_id = resp_json.get('orderId')
            logger.info('订单提交成功! 订单号：%s', order_id)
            #if self.send_message:
            #    self.messenger.send(text='jd-assistant 订单提交成功', desp='订单号：%s' % order_id)
            return True
        else:
            message, result_code = resp_json.get('message'), resp_json.get('resultCode')
            if result_code == 0:
                self._save_invoice()
                message += '(下单商品可能为第三方商品，将切换为普通发票进行尝试)'
                if message == "您多次提交过快，请稍后再试":
                    message += "(您多次提交过快，请稍后再试)"
                    time.sleep(5)
            elif result_code == 60077:
                message += '(可能是购物车为空 或 未勾选购物车中商品)'
            elif result_code == 60123:
                message += '(需要在config.ini文件中配置支付密码)'
            elif result_code == 600158:
                message += '抢的商品没货了'
            logger.info('订单提交失败, 错误码：%s, 返回信息：%s', result_code, message)
            logger.info(resp_json)
            return False

    def _save_invoice(self):
        """下单第三方商品时如果未设置发票，将从电子发票切换为普通发票

        http://jos.jd.com/api/complexTemplate.htm?webPamer=invoice&groupName=%E5%BC%80%E6%99%AE%E5%8B%92%E5%85%A5%E9%A9%BB%E6%A8%A1%E5%BC%8FAPI&id=566&restName=jd.kepler.trade.submit&isMulti=true

        :return:
        """
        url = 'https://trade.jd.com/shopping/dynamic/invoice/saveInvoice.action'
        data = {
            "invoiceParam.selectedInvoiceType": 1,
            "invoiceParam.companyName": "个人",
            "invoiceParam.invoicePutType": 0,
            "invoiceParam.selectInvoiceTitle": 4,
            "invoiceParam.selectBookInvoiceContent": "",
            "invoiceParam.selectNormalInvoiceContent": 1,
            "invoiceParam.vatCompanyName": "",
            "invoiceParam.code": "",
            "invoiceParam.regAddr": "",
            "invoiceParam.regPhone": "",
            "invoiceParam.regBank": "",
            "invoiceParam.regBankAccount": "",
            "invoiceParam.hasCommon": "true",
            "invoiceParam.hasBook": "false",
            "invoiceParam.consigneeName": "",
            "invoiceParam.consigneePhone": "",
            "invoiceParam.consigneeAddress": "",
            "invoiceParam.consigneeProvince": "请选择：",
            "invoiceParam.consigneeProvinceId": "NaN",
            "invoiceParam.consigneeCity": "请选择",
            "invoiceParam.consigneeCityId": "NaN",
            "invoiceParam.consigneeCounty": "请选择",
            "invoiceParam.consigneeCountyId": "NaN",
            "invoiceParam.consigneeTown": "请选择",
            "invoiceParam.consigneeTownId": 0,
            "invoiceParam.sendSeparate": "false",
            "invoiceParam.usualInvoiceId": "",
            "invoiceParam.selectElectroTitle": 4,
            "invoiceParam.electroCompanyName": "undefined",
            "invoiceParam.electroInvoiceEmail": "",
            "invoiceParam.electroInvoicePhone": "",
            "invokeInvoiceBasicService": "true",
            "invoice_ceshi1": "",
            "invoiceParam.showInvoiceSeparate": "false",
            "invoiceParam.invoiceSeparateSwitch": 1,
            "invoiceParam.invoiceCode": "",
            "invoiceParam.saveInvoiceFlag": 1
        }
        headers = {
            'User-Agent': self.__user_agent,
            'Referer': 'https://trade.jd.com/shopping/dynamic/invoice/saveInvoice.action',
        }
        resp = self.sess.post(url=url, data=data, headers=headers)
        if not _get_response_status(resp):
            logger.error("切换发票失败， resp {}".format(resp))
