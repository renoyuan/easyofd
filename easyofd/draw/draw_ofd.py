#!/usr/bin/env python
#-*- coding: utf-8 -*-
#PROJECT_NAME: F:\code\easyofd\easyofd\draw
#CREATE_TIME: 2023-10-26 
#E_MAIL: renoyuan@foxmail.com
#AUTHOR: reno 
#note:  写入 xml 目录并打包成ofd 文件 

from io import BytesIO

import xmltodict
from PIL import Image
from .pdf_parse import DPFParser
from .ofdtemplate import OFDTemplate,DocumentTemplate,DocumentResTemplate,PulicResTemplate,ContentTemplate,OFDStructure


class OFDWrite(object):
    def __init__(self,):
        tlp = {"ofd:xml":{"@version":"1.0","@encoding":"utf-8"},
                "ofd:OFD" :{}               
               }
    def build_pulic_res(self):
        font = [
                {
                    "@ID": "69",
                    "@FontName": "STSong",
                    "@FamilyName": "SimSun",
                    "@Serif": "true",
                    "@FixedWidth": "true",
                    "@Charset": "prc"
                }
            ]
        pulic_res=PulicResTemplate(Font=font)
        return pulic_res
    
    def build_document_res(self,img_len):
        MultiMedia = []
        for num in range(img_len): 
            MultiMedia.append({
                            "@ID": f"9100{num}",
                            "@Type": "Image",
                            "ofd:MediaFile": f"Image_{num}.jpg"
                        })
                    
                
                
        
        document_res=DocumentResTemplate(MultiMedia=MultiMedia)
        return document_res
    
    def build_content_res(self,pil_img_list):
        """一张图片是一页"""
        content_res_list = []
        for idx, pil_img in enumerate(pil_img_list):
            print(idx,pil_img[1],pil_img[2])
            PhysicalBox = f"0 0 {pil_img[1]} {pil_img[2]}"
            ImageObject = [{
                                "@ID": f"110{idx}",
                                "@CTM": f"{pil_img[1]} 0 0 {pil_img[2]} 0 0",
                                "@Boundary": f"0 0 {pil_img[1]} {pil_img[2]}",
                                "@ResourceID": f"9100{idx}"
                            }]
            
            conten = ContentTemplate(PhysicalBox=PhysicalBox, ImageObject=ImageObject,CGTransform=[],PathObject=[],TextObject=[])
            print(conten)
            content_res_list.append(conten)
        return content_res_list
    
    def build_document(self,img_len):
        pages = []

        for idx in range(img_len):
            pages.append(
                 {
                "@ID": f"{idx+1}",
                "@BaseLoc": f"Pages/Page_{idx}/Content.xml"
            }
            )
        document=DocumentTemplate(Page=pages)
        return document
    
    def pil_2_bytes(self, image):
        # 创建一个 BytesIO 对象
        img_bytesio = BytesIO()

        # 将图像保存到 BytesIO 对象
        image.save(img_bytesio, format='PNG')  # 你可以根据需要选择其他图像格式

        # 获取 BytesIO 对象中的字节
        img_bytes = img_bytesio.getvalue()

        # 关闭 BytesIO 对象
        img_bytesio.close()
        return img_bytes
    
    def __call__(self,pdf_bytes):
        # 读取 pdf 转图片 
        pdf_obj = DPFParser()
        img_list = pdf_obj.to_img(pdf_bytes)
        pil_img_list = [(self.pil_2_bytes(Image.frombytes("RGB", [_img.width, _img.height], _img.samples)),_img.width,_img.height) for _img in img_list]
        document = DocumentTemplate()
        pulic_res = self.build_pulic_res()
        document_res = self.build_document_res(len(pil_img_list))
        document = self.build_document(len(pil_img_list))
        content_res_list = self.build_content_res(pil_img_list)
        
        res_static = {} # 图片资源
        for idx, pil_img_tuple in enumerate(pil_img_list):
            res_static[f"Image_{idx}.jpg"] = pil_img_tuple[0]
        
        ofd_byte = OFDStructure("123",document = document,pulic_res=pulic_res,document_res=document_res,content_res=content_res_list,res_static=res_static)()
        return ofd_byte
        
if  __name__ == "__main__":
    
    pdf_p = r"D:\renodoc\技术栈\GBT_33190-2016_电子文件存储与交换格式版式文档.pdf"
    with open(pdf_p,"rb") as f:
        content = f.read()
    
    ofd_content = OFDWrite()(content)
    
    with open("ofd.ofd","wb") as f:
        f.write(ofd_content)
    
    