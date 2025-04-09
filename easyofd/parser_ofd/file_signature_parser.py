#!/usr/bin/env python
# -*- coding: utf-8 -*-
# PROJECT_NAME:  file_signature_parser.py
# CREATE_TIME: 2025/3/28 14:13
# E_MAIL: renoyuan@foxmail.com
# AUTHOR: reno
# NOTE: 签章解析

from .file_parser_base import FileParserBase

class SignaturesFileParser(FileParserBase):
    """
    Parser Signatures
    签章信息-总
    /xml_dir/Doc_0/PublicRes.xml
    """

    def __call__(self):
        info = {}
        signature_res: list = []
        signature_res_key = "ofd:Signature"
        self.recursion_ext(self.xml_obj, signature_res, signature_res_key)

        if signature_res:
            for i in signature_res:
                info[i.get("@ID")] = {
                    "BaseLoc": i.get("@BaseLoc"),
                    "Type": i.get("@Type"),
                    "ID": i.get("@ID"),

                }
        return info


class SignatureFileParser(FileParserBase):
    """
    Parser Signature
    签章信息
    """

    def __call__(self, prefix=""):
        info = {}
        StampAnnot_res: list = []
        StampAnnot_res_key = "ofd:StampAnnot"

        self.recursion_ext(self.xml_obj, StampAnnot_res, StampAnnot_res_key)

        SignedValue_res: list = []
        SignedValue_res_key = "ofd:SignedValue"
        self.recursion_ext(self.xml_obj, SignedValue_res, SignedValue_res_key)

        # print("SignedValue_res", SignedValue_res)
        # print("prefix", prefix)
        if StampAnnot_res:
            for i in StampAnnot_res:
                info = {
                    "PageRef": i.get("@PageRef"),  # page id
                    "Boundary": i.get("@Boundary"),
                    "ID": i.get("@ID"),
                    "SignedValue": f"{prefix}/{SignedValue_res[0]}" if SignedValue_res else f"{prefix}/SignedValue.dat",
                }

        return info
