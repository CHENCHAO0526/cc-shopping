# -*- coding: utf-8 -*-
import os

import configparser


class Config(object):

    def __init__(self, config_file='config.ini'):
        self.__path = os.path.join(os.getcwd(), config_file)
        if not os.path.exists(self.__path):
            raise FileNotFoundError("No such file: config.ini")
        self.__config = configparser.ConfigParser()
        self.__config.read(self.__path, encoding='utf-8')

    def get_section_config(self, section_name):
        s = self.__config[section_name]
        return s

    def get(self, section, name, strip_blank=True, strip_quote=True):
        s = self.__config.get(section, name)
        if strip_blank:
            s = s.strip()
        if strip_quote:
            s = s.strip('"').strip("'")
        return s

    def getboolean(self, section, name):
        return self.__config.getboolean(section, name)


global_config = Config()
