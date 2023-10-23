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
from io import BytesIO,StringIO 
import string
from uuid import uuid1
import random
import traceback
import logging

import numpy as np
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

from easyofd.draw import  FONTS

logger = logging.getLogger("root")



class FontTool(object):
    FONTS = FONTS
    
    def __init__(self):
        # 初始支持字体
        # 字体检测
        pass
    
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
            try:
                with open(file_name,"wb") as f: 
                    f.write(base64.b64decode(font_b64))
                
                pdfmetrics.registerFont(TTFont(FontName, font_b64))
                self.FONTS.append(FontName)
                
            except Exception as e:
                traceback.print_exc()
                logger.error(f"register_font_error:\n{e}")
            
            finally:
                if os.path.exists(file_name):
                        os.remove(file_name)
        
    
    
