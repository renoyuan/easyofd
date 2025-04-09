#!/usr/bin/env python
# -*- coding: utf-8 -*-
# PROJECT_NAME:  file_ofd_parser.py
# CREATE_TIME: 2025/3/28 11:45
# E_MAIL: renoyuan@foxmail.com
# AUTHOR: reno
# NOTE: 解析OFD
from .file_parser_base import FileParserBase

class OFDFileParser(FileParserBase):
    """
    Parser OFD 文件
    /xml_dir/OFD.xml
    """
    def __call__(self):
        info = {}
        # DocRoot
        doc_root: list = []
        doc_root_key = "ofd:DocRoot"
        # print(self.xml_obj,doc_root)
        self.recursion_ext(self.xml_obj, doc_root, doc_root_key)
        info["doc_root"] = doc_root

        signatures: list = []
        signatures_key = "ofd:Signatures"
        self.recursion_ext(self.xml_obj, signatures, signatures_key)
        info["signatures"] = signatures

        # ofd:Creator
        creator: list = []
        creator_key = "ofd:Creator"
        self.recursion_ext(self.xml_obj, creator, creator_key)
        info["creator"] = creator

        # ofd:CreationDate
        reation_date: list = []
        creation_date_key = "ofd:CreationDate"
        self.recursion_ext(self.xml_obj, reation_date, creation_date_key)
        info["creationDate"] = reation_date

        return info