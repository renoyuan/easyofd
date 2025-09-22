#!/usr/bin/env python
#-*- coding: utf-8 -*-
#PROJECT_NAME: D:\code\easyofd\easyofd
#CREATE_TIME: 2023-07-27 
#E_MAIL: renoyuan@foxmail.com
#AUTHOR: reno 
#NOTE: 字体处理  
import time
import re
import json
import base64
import zipfile
import os
import shutil
import logging
from io import BytesIO, StringIO
import string
from uuid import uuid1
import random
import traceback
import logging


import tempfile
import xmltodict
from fontTools.ttLib import TTFont as ttLib_TTFont
from fontTools.pens.basePen import BasePen
from reportlab.graphics.shapes import Path
from reportlab.lib import colors
from reportlab.graphics import renderPM
from reportlab.graphics.shapes import Group, Drawing, scale
from reportlab import platypus
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import mm,inch
from reportlab.platypus import SimpleDocTemplate, Image
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.pdfbase.ttfonts import TTFont
from concurrent.futures import ThreadPoolExecutor
import threading
import multiprocessing
import PIL


from reportlab.lib.fonts import _tt2ps_map 
from reportlab.lib.fonts import _family_alias 

from easyofd.draw import FONTS

from loguru import logger



class FontTool(object):
    FONTS = FONTS
    def __init__(self):
        # 初始支持字体
        # 字体检测
        logger.debug("FontTool init ,read system default Font ... ")
        self.FONTS = self.get_installed_fonts()
        logger.debug(f"system default Font is \n{self.FONTS} \n{'-'*50}")


    def get_system_font_dirs(self,):
        """获取不同操作系统的字体目录"""
        system = os.name
        if system == 'nt':  # Windows
            return [os.path.join(os.environ['WINDIR'], 'Fonts')]
        elif system == 'posix':  # Linux/macOS
            return [
                '/usr/share/fonts',
                '/usr/local/share/fonts',
                os.path.expanduser('~/.fonts'),
                os.path.expanduser('~/.local/share/fonts'),
                '/Library/Fonts',  # macOS
                '/System/Library/Fonts'  # macOS
            ]
        else:
            return []

    def normalize_font_name(self, font_name):
        """将字体名称规范化，例如 'Times New Roman Bold' -> 'TimesNewRoman-Bold'"""
        # 替换空格为无，并将样式（Bold/Italic等）用连字符连接
        normalized = font_name.replace(' ', '')
        # 处理常见的样式后缀
        for style in ['Bold', 'Italic', 'Regular', 'Light', 'Medium', ]:
            if style in normalized:
                normalized = normalized.replace(style, f'-{style}')

        # todo 特殊字体名规范 后续存在需要完善
        if normalized ==  "TimesNewRoman" :
            normalized = normalized.replace("TimesNewRoman","Times-Roman")
        return normalized

    def _process_ttc_font(self, ttc_font):
        """处理ttc文件中的所有字体"""
        def judge_name(name):
            if 'http://' in name or 'https://' in name or len(name) > 50:
                return False
            else:
                return True
        font_names = set()
        try:
            # 获取所有可用的名称记录
            name_records = ttc_font['name'].names

            for idx, record in enumerate(name_records):
                try:
                    # 尝试获取中文名称（简体中文的language ID是2052）
                    if record.platformID == 3 and record.langID == 2052:
                        cn_name = record.toUnicode()
                        if judge_name(cn_name):
                            font_names.add(cn_name)



                    # 回退到英文名称（language ID 1033）
                    elif record.platformID == 3 and record.langID == 1033:
                        name = record.toUnicode()
                        if judge_name(name):
                            font_names.add(name)
                except:
                    continue
        except KeyError:
            # 如果name表不存在，跳过
            pass
        return font_names
    def get_installed_fonts(self, ):
        """获取所有已安装字体的名称和家族"""
        font_dirs = self.get_system_font_dirs()
        installed_fonts = set()
        for font_dir in font_dirs:
            if not os.path.isdir(font_dir):
                continue
            for root, _, files in os.walk(font_dir):
                for file in files:
                    if file.lower().endswith(('.ttf', '.otf','.ttc')):
                        font_path = os.path.join(root, file)

                        try:
                            if file.lower().endswith('.ttc'):
                                # 对于ttc文件，读取所有字体
                                ttc_font = ttLib_TTFont(font_path, fontNumber=0)  # 读取第一个字体
                                installed_fonts.update(self._process_ttc_font(ttc_font))
                            else:
                                with ttLib_TTFont(font_path) as font:
                                    # 提取字体全名和家族名

                                    if name_cn := font['name'].getName(4, 3, 1, 2052):
                                        installed_fonts.add(name_cn.toUnicode())
                                    # 4=Full Name, 3=Windows, 1=Unicode
                                    if name := font['name'].getName(4, 3, 1, 1033):
                                        installed_fonts.add(name.toUnicode())
                                    if family_cn := font['name'].getName(1, 3, 1, 2052):
                                        installed_fonts.add(family_cn.toUnicode())
                                    if family := font['name'].getName(1, 3, 1, 1033):  # 1=Family Name
                                        installed_fonts.add(family.toUnicode())
                        except Exception as e:
                            print(f"解析字体 {font_path} 失败: {e}")
        installed_fonts = list(installed_fonts)
        if "宋体" in installed_fonts:
            installed_fonts.remove("宋体")
            installed_fonts.insert(0, "宋体")
        return installed_fonts

    def is_font_available(self, target_font):
        """检查目标字体是否安装"""
        installed_fonts = self.get_installed_fonts()
        return target_font in installed_fonts

    
    def font_check(self):
        logger.info("f{_tt2ps_map}")
        logger.info("f{_family_alias}")
        
        for font in self.FONTS:
            if font in _tt2ps_map.values():
                logger.info(f"已注册{font}")
            else:
                logger.warning(f"-{font}-未注册可能导致写入失败")
                 
        
        
    def register_font(self,file_name,FontName,font_b64):
        
        if font_b64:
            
            file_name = os.path.split(file_name)
            # logger.error(f"file_name:{file_name}")
            # logger.info(f"file_name:{file_name}")
            if isinstance(file_name, (tuple, list)):
                    file_name = file_name[1]
            if not FontName:
                FontName = file_name.split(".")[0]

            try:
                with open(file_name, "wb") as f:
                    f.write(base64.b64decode(font_b64))
                print("FontName", FontName, "file_name", file_name)
                pdfmetrics.registerFont(TTFont(FontName, file_name))
                self.FONTS.append(FontName)
                logger.debug(f"FontTool.register_font success, name={FontName}, file={file_name}")
            except Exception as e:
                logger.error(f"register_font_error:\n{e} \n 包含不支持解析字体格式")
            finally:
                if os.path.exists(file_name):
                    os.remove(file_name)
