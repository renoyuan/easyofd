#!/usr/bin/env python
#-*- coding: utf-8 -*-
#PROJECT_NAME: D:\code\easyofd\easyofd\parser
#CREATE_TIME: 2023-07-27 
#E_MAIL: renoyuan@foxmail.com
#AUTHOR: reno 
#NOTE:  文件处理
import os
import base64
import shutil
from typing import Any
from uuid import uuid1

import xmltodict
import zipfile
from loguru import logger

from .path_parser import PathParser


class FileRead(object):
    """
    文件读取，清除
    'root': OFD.xml 
    "root_doc" Doc_0/Document.xml
    xml_path : xml_obj
    other_path : b64string
    """
    def __init__(self, ofdb64:str):

        self.ofdbyte = base64.b64decode(ofdb64) 
        pid=os.getpid()
        self.name = f"{pid}_{str(uuid1())}.ofd"
        self.pdf_name = self.name.replace(".ofd",".pdf")
        self.zip_path = f"{os.getcwd()}/{self.name}"
        self.unzip_path = ""
        self.file_tree = {}
    
    def unzip_file(self):
        """
        :param zip_path: ofd格式文件路径
        :param unzip_path: 解压后的文件存放目录
        :return: unzip_path
        """
        with open(self.zip_path,"wb") as f:
            f.write(self.ofdbyte)
        self.unzip_path = self.zip_path.split('.')[0]
        with zipfile.ZipFile(self.zip_path, 'r') as f:
            for file in f.namelist():
                f.extract(file, path=self.unzip_path)
        if self.save_xml:
            print("saving xml {}".format(self.xml_name))
            with zipfile.ZipFile(self.zip_path, 'r') as f:
                for file in f.namelist():
                    f.extract(file, path=self.xml_name)
       
    def buld_file_tree(self):
        "xml读取对象其他b64"
        self.file_tree["root"] = self.unzip_path
        self.file_tree["pdf_name"] = self.pdf_name
        for root, dirs, files in os.walk(self.unzip_path):
            for file in files:
                
                abs_path = os.path.join(root,file)
                # 资源文件 则 b64 xml 则  xml——obj
                self.file_tree[abs_path] = str(base64.b64encode(open(f"{abs_path}","rb").read()),"utf-8")  \
                    if "xml" not in file else xmltodict.parse(open(f"{abs_path}" , "r", encoding="utf-8").read())
        self.file_tree["root_doc"] = os.path.join(self.unzip_path,"OFD.xml") if os.path.join(self.unzip_path,"OFD.xml") in self.file_tree else ""
  
        if os.path.exists(self.unzip_path):
            shutil.rmtree(self.unzip_path)
       
        if os.path.exists(self.zip_path):
            os.remove(self.zip_path)
                   
    def __call__(self, *args: Any, **kwds: Any) -> Any:
        self.save_xml=kwds.get("save_xml",False)
        self.xml_name=kwds.get("xml_name")
    
        self.unzip_file()
        self.buld_file_tree()
        return self.file_tree 

if __name__ == "__main__":
    with open(r"D:/code/easyofd/test/增值税电子专票5.ofd","rb") as f:
        ofdb64 = str(base64.b64encode(f.read()),"utf-8")
    a = FileRead(ofdb64)()
    print(list(a.keys()))