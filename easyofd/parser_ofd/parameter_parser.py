#!/usr/bin/env python
# -*- coding: utf-8 -*-
# PROJECT_NAME: easyofd
# CREATE_TIME: 
# E_MAIL: renoyuan@foxmail.com
# AUTHOR: renoyuan
# note:参数解析器
from loguru import logger
from typing import List, Dict, Any, Union, Tuple, Optional


class ParameterParser(object):
    parameter = {
        "ofd:FillColor": (dict, dict),
        "ofd:StrokeColor": (dict, dict),
        "ofd:Test": ((str, int), str),
        "ofd:Font": (str, str),
        "@Value": (str, str)
    }

    def __call__(self, key, container):
        if key in ParameterParser.parameter:
            v = container.get(key, None)
            t = ParameterParser.parameter[key]
            if isinstance(v, t[0]):
                return v
            else:
                return t[1]()
        else:
            logger.warning(f"{key} not in ParameterParser")
            return None
