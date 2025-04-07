#!/usr/bin/env python
# -*- coding: utf-8 -*-
# PROJECT_NAME:  file_doc_parser.py
# CREATE_TIME: 2025/3/28 11:46
# E_MAIL: renoyuan@foxmail.com
# AUTHOR: reno
# NOTE: 解析document

import  re

from .file_parser_base import FileParserBase



class DocumentFileParser(FileParserBase):
    """
    Document 为doc内的根节点 包含：
    1 文件的路径 2 doc的size
    """

    def loc2page_no(self, loc, idx):
        pg_no = re.search(r"\d+", loc)
        if pg_no:
            pg_no = int(pg_no.group())
        else:
            pg_no = idx
        return pg_no

    def __call__(self):
        document_info = {}

        # size
        physical_box: list = []
        physical_box_key = "ofd:PhysicalBox"
        self.recursion_ext(self.xml_obj, physical_box, physical_box_key)
        document_info["size"] = physical_box[0] if physical_box else ""

        # ofd:PublicRes路径 包含字体路径信息
        public_res: list = []
        public_res_key = "ofd:PublicRes"
        self.recursion_ext(self.xml_obj, public_res, public_res_key)
        document_info["public_res"] = public_res

        # ofd:DocumentRes路径  包含静态资源图片
        document_res: list = []
        document_res_key = "ofd:DocumentRes"
        self.recursion_ext(self.xml_obj, document_res, document_res_key)
        document_info["document_res"] = document_res

        # ofd:Page 正文
        page: list = []
        page_id_map = {}
        apage_key = "ofd:Page"
        self.recursion_ext(self.xml_obj, page, apage_key)
        if page:
            page_id_map = {
                i.get("@ID"): self.loc2page_no(i.get("@BaseLoc"), idx)
                for idx, i in enumerate(page)
            }
            page = [i.get("@BaseLoc") if isinstance(i, dict) else i for i in page]

        document_info["page"] = page
        document_info["page_id_map"] = page_id_map

        tpls: list = []
        template_page_key = "ofd:TemplatePage"
        self.recursion_ext(self.xml_obj, tpls, template_page_key)
        if tpls:
            tpls = [i.get("@BaseLoc") if isinstance(i, dict) else i for i in tpls]
        document_info["tpls"] = tpls

        return document_info






