#!/usr/bin/env python
#-*- coding: utf-8 -*-
#PROJECT_NAME: F:\code\easyofd\test
#CREATE_TIME: 2023-10-18 
#E_MAIL: renoyuan@foxmail.com
#AUTHOR: reno 
#note:  use demo
import sys
import os
project_dir = os.path.join(os.path.dirname(os.getcwd()),"easyofd")
pkg_dir = os.path.dirname(os.getcwd())

# print(project_dir)
print(pkg_dir)
# sys.path.insert(0,project_dir)
sys.path.insert(0,pkg_dir)
import base64
from PIL import Image

import numpy as np

from easyofd.ofd import OFD

if __name__ == "__main__":
    with open(r"增值税电子专票5.ofd","rb") as f:
        ofdb64 = str(base64.b64encode(f.read()),"utf-8")
    ofd = OFD()
    ofd.read(ofdb64) # 读取ofd
    # print(ofd.data)
    pdf_bytes = ofd.to_pdf() # 转pdf
    img_np = ofd.to_jpg() # 转图片
    ofd.del_data()
    with open(r"test.pdf","wb") as f:
        f.write(pdf_bytes)
    for idx, img in enumerate(img_np):
        im = Image.fromarray(img)
        im.save(f"test_img{idx}.jpg")
       