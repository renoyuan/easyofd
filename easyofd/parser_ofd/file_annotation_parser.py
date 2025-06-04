#!/usr/bin/env python
# -*- coding: utf-8 -*-
# PROJECT_NAME:  file_annotation_parser.py
# CREATE_TIME: 2025/3/28 14:12
# E_MAIL: renoyuan@foxmail.com
# AUTHOR: reno
# NOTE: 注释解析
from loguru import logger
from .file_parser_base import FileParserBase

class AnnotationsParser(FileParserBase):
    """
    Parser Annotations
    注释信息-总
    /xml_dir/Doc_0/Pages/Page_0/Content.xml
    """

    def __call__(self):
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
                info[page_id] = {
                    "FileLoc": file_Loc,
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
            "type": "Highlight"
        }
    }

    def __call__(self):
        info = {}
        public_res: list = []
        public_res_key = "ofd:Page"
        self.recursion_ext(self.xml_obj, public_res, public_res_key)

        if public_res:
            for i in public_res:
                info[i.get("@ID")] = {
                    "FontName": self.normalize_font_name(i.get("@FontName")),
                    "FontNameORI": i.get("@FontName"),
                    "FamilyName": self.normalize_font_name(i.get("@FamilyName")),
                    "FamilyNameORI": i.get("@FamilyName"),
                    "Bold": i.get("@Bold"),
                    "Serif": i.get("@Serif"),
                    "FixedWidth": i.get("@FixedWidth"),
                    "FontFile": i.get("ofd:FontFile"),
                }
        return info

