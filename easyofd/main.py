#!/usr/bin/env python
#-*- coding: utf-8 -*-
#PROJECT_NAME: D:\code\easyofd\easyofd
#CREATE_TIME: 2023-07-27 
#E_MAIL: renoyuan@foxmail.com
#AUTHOR: reno 
#NOTE:  实现入口
import base64
import os
import sys
sys.path.insert(0,"..")
from typing import Any


from parser_ofd import OFDParser
from draw import DrawPDF

class OFD2PDF(object):
    """
    OFD转PDF主要流程
    """
    def __init__(self):
        pass
    def __call__(self, ofdb64:str) -> bytes:
        """
        实现流程
        """
        data = OFDParser(ofdb64)()
        return DrawPDF(data)()
    
if __name__ == "__main__":
    print(os.getcwd())
    with open(r"E:\code\easyofd\test\增值税电子专票5.ofd","rb") as f:
        ofdb64 = str(base64.b64encode(f.read()),"utf-8")
    OFD2PDF()(ofdb64)
        
       