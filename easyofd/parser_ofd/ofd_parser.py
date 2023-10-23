#!/usr/bin/env python
#-*- coding: utf-8 -*-
#PROJECT_NAME: D:\code\easyofd\easyofd\parser
#CREATE_TIME: 2023-07-27 
#E_MAIL: renoyuan@foxmail.com
#AUTHOR: reno 
#NOTE: ofd解析主流程

import sys
import os
import logging
sys.path.insert(0,"..")

import traceback
import base64
import re
from typing import Any

from loguru import logger
from .file_deal import FileRead
from .file_parser import OFDFileParser, DocumentFileParser, ContentFileParser,DocumentResFileParser,PublicResFileParser



class OFDParser(object):
    """
    OFDParser 解析
    1 解压文件 创建文件映射表 释放文件
    2 解析 xml 逐级去 收集需要信息  结构文本 以及 资源
    2 调用font 注册 字体
    """
    def __init__(self, ofdb64):
        self.ofdb64 = ofdb64
        self.file_tree = None
        self.jbig2dec_path = r"C:/msys64/mingw64/bin/jbig2dec.exe"
      
    
    # 获得xml 对象
    def get_xml_obj(self, label):
        assert label
        for abs_p in self.file_tree:
            # 统一符号，避免win linux 路径冲突
            abs_p_compare = abs_p.replace("\\","-").replace("/","-")  
            label_compare = label.replace("\\","-").replace("/","-") 
            if label_compare in abs_p_compare:
                return self.file_tree[abs_p]
    
    def jb22png(self, img_d:dict):
        """
        jb22png
        没有安装 jbig2dec 无法操作 
        """          
        if not os.path.exists(self.jbig2dec_path):
            logger.warning(f"未安装jbig2dec，无法处理jb2文件")
            return
        
        # todo ib2 转png C:/msys64/mingw64/bin/jbig2dec.exe -o F:\code\easyofd\test\image_80.png F:\code\easyofd\test\image_80.jb2
        fileName = img_d["fileName"]
        new_fileName = img_d['fileName'].replace(".jb2",".png")
        with open(fileName, "wb") as f:
            f.write(base64.b64decode(img_d["imgb64"]))
        
        command = "{} -o {} {}"
        res=os.system(command.format(self.jbig2dec_path, new_fileName ,fileName))
        if res != 0:
            logger.warning(f"jbig2dec处理失败")
        if  os.path.exists(fileName):
            os.remove(fileName)
        if  os.path.exists(new_fileName):
            logger.info(f"jbig2dec处理成功{fileName}>>{new_fileName}")
            img_d["fileName"] = new_fileName
            img_d["suffix"] = "png"
            img_d["format"] = "png"
            with open(new_fileName,"rb") as f:
                data = f.read()
                img_d["imgb64"] =  str(base64.b64encode(data),encoding="utf-8") 
               
            os.remove(new_fileName)
        
    def parser(self, ):
        """
        解析流程
        """
        # 默认只有 doc_0 一层有多层后面改
        page_size = []
        doc_list = []       
        ofd_xml_obj = self.get_xml_obj(self.file_tree["root_doc"])  # OFD.xml xml 对象 

        if ofd_xml_obj:
            doc_root_name = OFDFileParser(ofd_xml_obj)().get("doc_root")
        else:
            # 考虑根节点丢失情况
            doc_root_name = ["Doc_0/Document.xml"]
        
        doc_root_xml_obj = self.get_xml_obj(doc_root_name[0])
        doc_root_info = DocumentFileParser(doc_root_xml_obj)()
        doc_size = doc_root_info.get("size")
        
        if doc_size:
            try:
                page_size = [float(pos_i) for pos_i in doc_size.split(" ") if re.match("[\d\.]",pos_i)] 
            except:
                traceback.print_exc()
        
        # 字体信息
        font_info = {}
        public_res_name:list = doc_root_info.get("public_res")
        if public_res_name: 
            public_xml_obj = self.get_xml_obj(public_res_name[0])
            font_info = PublicResFileParser(public_xml_obj)()
            
            # 注册字体
            for font_id,font_v in font_info.items():    
                file_name = font_v.get("FontFile")
                if file_name:
                    font_b64 = self.get_xml_obj(file_name)
                    if font_b64:
                        font_v["font_b64"] = font_b64
                        
                
        
        # 图片资源
        document_res_name:list = doc_root_info.get("document_res")
        if document_res_name:
            document_res_xml_obj = self.get_xml_obj(document_res_name[0])
            
            img_info = DocumentResFileParser(document_res_xml_obj)()
            # 找到图片b64
            for img_id,img_v in img_info.items(): 
                img_v["imgb64"] = self.get_xml_obj(img_v.get("fileName"))
                if img_v["suffix"] == 'jb2': # todo ib2 转png C:/msys64/mingw64/bin/jbig2dec.exe -o F:\code\easyofd\test\image_80.png F:\code\easyofd\test\image_80.jb2
                    self.jb22png(img_v)
        
        # 正文信息 会有多页 情况
        page_name:list = doc_root_info.get("page")
        
        page_info_d = {}
        if page_name:
            for index,_page in enumerate(page_name):
                page_xml_obj = self.get_xml_obj(_page)
                # 重新获取页面size
                try:
                    page_size_new = [float(pos_i) for pos_i in page_xml_obj.get('ofd:Page',{}).get("ofd:Area",{}).get("ofd:PhysicalBox","").split(" ") if re.match("[\d\.]",pos_i)] 
                    if page_size_new and len(page_size_new)>=2:
                        page_size = page_size_new
                except Exception as e:
                    traceback.print_exc()
                  
                page_info = ContentFileParser(page_xml_obj)()
                pg_no = re.search(r"\d+",_page) 
                if pg_no:
                    pg_no = int(pg_no.group())
                else:
                    pg_no = index
                page_info_d[pg_no] = page_info
                
        # 模板信息
        tpls_name:list = doc_root_info.get("tpls")
        if tpls_name:
            for index,_tpl in enumerate(tpls_name):
                tpl_xml_obj = self.get_xml_obj(_tpl)
                tpl_info = ContentFileParser(tpl_xml_obj)()
                tpl_no = re.search(r"\d+",_tpl)
            
                if tpl_no:
                    tpl_no = int(tpl_no.group())
                else:
                    tpl_no = index
                    
                if tpl_no in page_info_d:
                    page_info_d[pg_no]["text_list"].extend(tpl_info["text_list"])
                    page_info_d[pg_no]["text_list"].sort(key=lambda pos_text:  (float(pos_text.get("pos")[1]),float(pos_text.get("pos")[0])))
                    page_info_d[pg_no]["img_list"].extend(tpl_info["img_list"])
                    page_info_d[pg_no]["img_list"].sort(key=lambda pos_text:  (float(pos_text.get("pos")[1]),float(pos_text.get("pos")[0])))
                else:
                    page_info_d[tpl_no] = tpl_info
                    page_info_d[tpl_no].sort(key=lambda pos_text:  (float(pos_text.get("pos")[1]),float(pos_text.get("pos")[0])))

            page_ID = 0 # 没遇到过doc多个的情况
            doc_list.append({
                "pdf_name": self.file_tree["pdf_name"],
                "doc_no":page_ID,
                "images":img_info,
                "page_size":page_size,
                "fonts":font_info,
                "page_info":page_info_d        
                            })
            return doc_list
               
    def __call__(self, *args: Any, **kwds: Any) -> Any:
        """
        输出ofd解析结果
        """
        self.file_tree = FileRead(self.ofdb64)()
        return self.parser()
    
if __name__ == "__main__":
        with open(r"E:\code\easyofd\test\增值税电子专票5.ofd","rb") as f:
            ofdb64 = str(base64.b64encode(f.read()),"utf-8")
        print(OFDParser(ofdb64)())