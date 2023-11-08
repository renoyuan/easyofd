#!/usr/bin/env python
#-*- coding: utf-8 -*-
#PROJECT_NAME: F:\code\easyofd\easyofd
#CREATE_TIME: 2023-10-07 
#E_MAIL: renoyuan@foxmail.com
#AUTHOR: reno 
#note:  ofd 基础类

import base64
import os
import sys
sys.path.insert(0,os.getcwd())
sys.path.insert(0,"..")
from typing import Any

import fitz
import numpy as np
from loguru import logger

from easyofd.parser_ofd import OFDParser
from easyofd.draw import DrawPDF,OFDWrite

class OFD(object):
    """ofd对象"""
    def __init__(self,):
        self.data = None 
        
    def read(self,ofd_f,fomat="b64"):
        """_summary_

        Args:
            file (_type_): _description_
            fomat (str, optional): _description_. Defaults to "path".
            fomat in ("path","b64","binary")
        """
        if fomat == "path":
            with open(ofd_f,"rb") as f:
                ofd_f = str(base64.b64encode(f.read()),encoding="utf-8") 
        elif fomat == "b64":
            pass
        elif fomat == "binary":
            ofd_f = str(base64.b64encode(ofd_f),encoding="utf-8")
        else:
            raise "fomat Error: %s" % fomat
        
        self.data = OFDParser(ofd_f)() 
    
    def save(self,):
        """
        draw ofd xml
        初始化一个xml 文件
        self.data > file
        """
        assert self.data,f"data is None"

    def pdf2ofd(self,pdfbyte):
        """pdf转ofd"""
        ofd_byte = OFDWrite()(pdfbyte)
        return ofd_byte
    
    def to_pdf(self,):
        """return ofdbytes"""

        assert self.data,f"data is None"
        logger.info(f"to_pdf")
        return DrawPDF(self.data)()
    
    def pdf2img(self,pdfbytes):
        
        image_list = []
      
        
        doc = fitz.open(stream=pdfbytes, filetype="pdf")
      
        for page in doc:
            rotate = int(0)
            zoom_x, zoom_y = 1.6, 1.6
            mat = fitz.Matrix(zoom_x, zoom_y).prerotate(rotate)
            pix = page.get_pixmap(matrix=mat, alpha=False)
            image = np.ndarray((pix.height, pix.width, 3), dtype=np.uint8, buffer=pix.samples)
            # print(image.shape)
            # print(image[2])
            image_list.append(image)
        logger.info(f"to_jpg")
        return image_list
    
    def to_jpg(self,format="jpg"):
        """
        return numpy list
        """
        assert self.data,f"data is None"
        image_list = []
        pdfbytes = self.to_pdf()
        
        doc = fitz.open(stream=pdfbytes, filetype="pdf")
      
        for page in doc:
            rotate = int(0)
            zoom_x, zoom_y = 1.6, 1.6
            mat = fitz.Matrix(zoom_x, zoom_y).prerotate(rotate)
            pix = page.get_pixmap(matrix=mat, alpha=False)
            image = np.ndarray((pix.height, pix.width, 3), dtype=np.uint8, buffer=pix.samples)
            # print(image.shape)
            # print(image[2])
            image_list.append(image)
        logger.info(f"to_jpg")
        return image_list
    
        
    def del_data(self,):
        """销毁self.data"""
        self.data =None
        
    def __del__(self):
        del self
        
    def disposal(self,):
        """销毁对象"""
        self.__del__() 
            

if __name__ == "__main__":
    ofd = OFD()
