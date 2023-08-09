#!/usr/bin/env python
#-*- coding: utf-8 -*-
#PROJECT_NAME: D:\code\easyofd\easyofd
#CREATE_TIME: 2023-07-27 
#E_MAIL: renoyuan@foxmail.com
#AUTHOR: reno 
#NOTE: 字体处理逻辑  

from __future__ import print_function, division, absolute_import
from fontTools.ttLib import TTFont as ttLib_TTFont
from fontTools.pens.basePen import BasePen
from reportlab.graphics.shapes import Path
from reportlab.lib import colors
from reportlab.graphics import renderPM
from reportlab.graphics.shapes import Group, Drawing, scale

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



try:
    import cv2
except :
    logging.warning("缺少cv2 若需要处理图片文件必不可少")
    



class FontParser(object):
    def __init__(self):
        # 初始支持字体
        self.FONTS = ['宋体',"SWPMEH+SimSun",'SimSun','KaiTi','楷体',
        "STKAITI","SWLCQE+KaiTi",'Courier New','STSong-Light',"CourierNew",
        "SWANVV+CourierNewPSMT","CourierNewPSMT","BWSimKai","hei","黑体","SimHei",
        "SWDKON+SimSun","SWCRMF+CourierNewPSMT","SWHGME+KaiTi"]
         
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
                print(f"register_font_error:\n{e}")
            
            finally:
                if os.path.exists(file_name):
                        os.remove(file_name)
        
    
    
