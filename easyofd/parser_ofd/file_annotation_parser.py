#!/usr/bin/env python
# -*- coding: utf-8 -*-
# PROJECT_NAME:  file_annotation_parser.py
# CREATE_TIME: 2025/3/28 14:12
# E_MAIL: renoyuan@foxmail.com
# AUTHOR: reno
# NOTE: 注释解析
import re 

from loguru import logger

from .file_parser_base import FileParserBase

class AnnotationsParser(FileParserBase):
    """
    Parser Annotations
    注释入口文件
    /xml_dir/Doc_0/Pages/Page_0/Content.xml
    """

    def __call__(self):
        """
        解析注释入口文件
        :return: {PageID: {"FileLoc": "ofd:FileLoc","pageNo": pageNo}}
        注释入口文件的内容
        """
        info = {}
        annotations_res: list = []
        annotations_res_key = "ofd:Page"
        self.recursion_ext(self.xml_obj, annotations_res, annotations_res_key)
        logger.debug(f"annotations_res is {annotations_res}")
        if annotations_res:
            for i in annotations_res:
                page_id =  i.get("@PageID")
                if not page_id:
                    logger.debug(f"page_id is null ")
                    continue
                file_Loc = i.get("ofd:FileLoc")
                if not file_Loc:
                    logger.debug(f"file_Loc is null ")
                    continue
                else:
                    logger.debug(f"page_id is {page_id}, file_Loc is {file_Loc}")
                    match = re.search(r'Page_(\d+)', file_Loc)
                    if match:
                        page_no = int(match.group(1))
                    else:
                        logger.debug(f"page_no is null, text is {text}")
                        page_no = 0
                    info[page_id] = {
                        "FileLoc": file_Loc,
                        "pageNo": page_no,
                    }

        return info
class AnnotationFileParser(FileParserBase):
    """
    Parser Annotation
    注释类 包含 签名注释 水印注释 信息注释
    """
    AnnoType = {
        "Watermark":{
            "name":"水印",
            "type":"Watermark"
        },
        "Link": {
            "name": "链接",
            "type": "Link"
        }
        ,
        "Path": {
            "name": "路径",
            "type": "Path"
        },
        "Highlight": {
            "name": "高亮",
            "type": "Highlight"
        },
        "Stamp": {
            "name": "签章",
            "type": "Stamp"
        }
    }

    def __call__(self):
        """
        {0: {'175': {'AnnoType': {'name': '签章', 'type': 'Stamp'}, 
        'Appearance': {'Boundary': '87.50 8.50 30 20', 'CTM': None}, 'Content': {None}, 
        'ImgageObject': {'ID': '177', 'ResourceID': '176', 'Boundary': '0 0 30 20', 'CTM': '30 0 0 20 0 0'}}}}
        """
        info = {}
        annot_res: list = []
        annot_res_key = "ofd:Annot"
        self.recursion_ext(self.xml_obj, annot_res, annot_res_key)

        if annot_res:
            for i in annot_res:
                info[i.get("@ID")] = {
                    "AnnoType": self.AnnoType.get(i.get("@Type")),
                    "Appearance": {
                        "Boundary": i.get("ofd:Appearance", {}).get("@Boundary"),
                        "CTM": i.get("ofd:Appearance", {}).get("@CTM",""),
                    },
                    "Content": i.get("ofd:Content", {}).get("@Text",""),
                    "ImgageObject": {
                        "ID": i.get("ofd:Appearance", {}).get("ofd:ImageObject", {}).get("@ID"),
                        "ResourceID": i.get("ofd:Appearance", {}).get("ofd:ImageObject", {}).get("@ResourceID"),
                        "Boundary": i.get("ofd:Appearance", {}).get("ofd:ImageObject", {}).get("@Boundary"),
                        "CTM": i.get("ofd:Appearance", {}).get("ofd:ImageObject", {}).get("@CTM"),
                    },
                    
                }
        return info

