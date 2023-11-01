#!/usr/bin/env python
#-*- coding: utf-8 -*-
#PROJECT_NAME: F:\code\easyofd\test
#CREATE_TIME: 2023-10-23 
#E_MAIL: renoyuan@foxmail.com
#AUTHOR: reno 
#note:  批量测试 查看效果

import sys
import os
import base64
from PIL import Image
import traceback
import numpy as np

from easyofd.ofd import OFD

if __name__ == "__main__":
    output_path = "F:\code\ofd2pdf"
    path  = "F:\code\OFD样本"
    files = os.listdir(path)
    ofd = OFD()
    error_file = []
    for file in files:
        
        with open(os.path.join(path,file),"rb") as f:
            ofdb64 = str(base64.b64encode(f.read()),"utf-8")
        
        ofd.read(ofdb64) # 读取ofd
        # print(ofd.data)
        # pdf_bytes = ofd.to_pdf() # 转pdf
        try:
            img_np = ofd.to_jpg() # 转图片
            ofd.del_data()
            # with open(os.path.join(output_path,os.path.splitext(file)[0] )+".pdf","wb") as f:
            #     f.write(pdf_bytes)
            for idx, img in enumerate(img_np):
                im = Image.fromarray(img)
                im.save(os.path.join(output_path,os.path.splitext(file)[0] )+f"_{idx}.jpg")
        except:
            error_file.append(file)
            traceback.print_exc()
    print(error_file)