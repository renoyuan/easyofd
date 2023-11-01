#!/usr/bin/env python
#-*- coding: utf-8 -*-
#PROJECT_NAME: F:\code\easyofd\test
#CREATE_TIME: 2023-10-26 
#E_MAIL: renoyuan@foxmail.com
#AUTHOR: reno 
#note:  json2xml 
import os
import json
import base64
import xmltodict
from pathlib import Path  
# xml_data = xmltodict.unparse({"root": {"@ID":"50",'#text': '2129.33663366337'}}, full_document=False)
# with open("test.xml","w+",encoding="utf-8") as f:
#     f.write(xml_data)
    
    
def buld_file_tree():
    

    for root, dirs, files in os.walk(r"F:\code\easyofd\test\xml"):
        for file in files:
            print(file)
            abs_path = os.path.join(root,file)
            if abs_path.endswith(".xml"):
                xmldict = xmltodict.parse(open(abs_path , "r", encoding="utf-8").read())
                json_paht = os.path.join(root,file.replace(".xml",".json"))
                print(json_paht)
                json.dump(xmldict,open(json_paht,"w",encoding="utf-8"),ensure_ascii=False,indent=4)

if __name__ == "__main__":
    buld_file_tree()