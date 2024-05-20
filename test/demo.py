#!/usr/bin/env python
#-*- coding: utf-8 -*-
#PROJECT_NAME: F:\code\easyofd\test
#CREATE_TIME: 2023-10-18 
#E_MAIL: renoyuan@foxmail.com
#AUTHOR: reno 
#note:  use demo
import sys,os
import base64
import json
from PIL import Image
project_dir = os.path.join(os.path.dirname(os.getcwd()),"easyofd")
pkg_dir = os.path.dirname(os.getcwd())
print(project_dir)
print(pkg_dir)
sys.path.insert(0,project_dir)
sys.path.insert(0,pkg_dir)
import numpy as np
import cv2
from easyofd.ofd import OFD


# 
def test_img2():
    """
    jpg2ofd 
    jpg2pfd
    """
    img_path = os.path.join(".", r"test\Doc_0\Res") # 多页排序问题
    imgs_p = os.listdir(img_path)
    imgs = []
    for img_p in imgs_p:
        imgs.append(cv2.imread(os.path.join(img_path,img_p)))
    ofdbytes = ofd = OFD().jpg2ofd(imgs)
    pdfbytes = ofd = OFD().jpg2pfd(imgs)
    with open(r"img2test.pdf","wb") as f:
        f.write(pdfbytes)
    with open(r"img2test.ofd","wb") as f:
        f.write(ofdbytes)
        
def test_ofd2():
    """
    ofd2pdf
    ofd2img
    """
    # with open(r"0e7ff724-1011-4544-8464-ea6c025f6ade.ofd","rb") as f:
    with open(r"F:\code\easyofd\test\测试.ofd","rb") as f:
        ofdb64 = str(base64.b64encode(f.read()),"utf-8")
    ofd = OFD() # 初始化OFD 工具类
    ofd.read(ofdb64,save_xml=True, xml_name="testxml") # 读取ofdb64
    # print("ofd.data", ofd.data) # ofd.data 为程序解析结果
    pdf_bytes = ofd.to_pdf() # 转pdf
    img_np = ofd.to_jpg() # 转图片
    ofd.del_data()
    
    with open(r"test1.pdf", "wb") as f:
        f.write(pdf_bytes)
        
    for idx, img in enumerate(img_np):
        im = Image.fromarray(img)
        im.save(f"test_img{idx}.jpg")
        
def test_pdf2():
    """
    pdf2ofd
    pdf2img
    """
    with open(r"F:\code\easyofd\test\test.pdf", "rb") as f:
        pdfb64 = f.read()
    ofd = OFD()
    ofd_bytes = ofd.pdf2ofd(pdfb64, optional_text=True)  # 转ofd # optional_text 生成可操作文本 True
    img_np = ofd.pdf2img(pdfb64)
    ofd.del_data()
    with open(r"test.ofd", "wb") as f:
        f.write(ofd_bytes)
    for idx, img in enumerate(img_np):
        im = Image.fromarray(img)
        im.save(f"test_img{idx}.jpg")


if __name__ == "__main__":
    if sys.argv[1] =="ofd2":
        test_ofd2()
    elif sys.argv[1] =="pdf2":
        test_pdf2()
    elif sys.argv[1] =="img2":
        test_img2()
    else:
        test_ofd2()

    # data = ofd.data
    # json.dump(data,open("data.json","w",encoding="utf-8"),ensure_ascii=False,indent=4)
    # print(ofd.data)
    
    



       