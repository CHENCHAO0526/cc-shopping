from jd_user import JdUser
from config import Config
from interface import RushGUI
from log import logger


if __name__ == '__main__':
    global_config = Config()
    chenchao = JdUser(global_config)
    chenchao_gui = RushGUI(chenchao)

