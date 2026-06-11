#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""测试签章解析器 SignaturesFileParser & SignatureFileParser"""

import pytest
from easyofd.parser_ofd.file_signature_parser import (
    SignaturesFileParser,
    SignatureFileParser,
)


class TestSignaturesFileParser:
    """测试 SignaturesFileParser（签章总文件解析）"""

    def test_empty_xml(self):
        """空 xml 应返回空字典"""
        parser = SignaturesFileParser({"ofd:Signatures": {}})
        result = parser()
        assert result == {}

    def test_single_signature(self):
        """单个签章解析"""
        xml_obj = {
            "ofd:Signatures": {
                "ofd:Signature": {
                    "@ID": "s0",
                    "@BaseLoc": "Doc_0/Signs/Signature_0/Signature.xml",
                    "@Type": "Seal",
                }
            }
        }
        parser = SignaturesFileParser(xml_obj)
        result = parser()
        assert "s0" in result
        assert result["s0"]["BaseLoc"] == "Doc_0/Signs/Signature_0/Signature.xml"
        assert result["s0"]["Type"] == "Seal"

    def test_multiple_signatures(self):
        """多个签章解析"""
        xml_obj = {
            "ofd:Signatures": {
                "ofd:Signature": [
                    {
                        "@ID": "s0",
                        "@BaseLoc": "Doc_0/Signs/Signature_0/Signature.xml",
                        "@Type": "Seal",
                    },
                    {
                        "@ID": "s1",
                        "@BaseLoc": "Doc_0/Signs/Signature_1/Signature.xml",
                        "@Type": "Electronic",
                    },
                ]
            }
        }
        parser = SignaturesFileParser(xml_obj)
        result = parser()
        assert len(result) == 2
        assert result["s0"]["Type"] == "Seal"
        assert result["s1"]["Type"] == "Electronic"

    def test_missing_optional_fields(self):
        """签章可选字段缺失"""
        xml_obj = {
            "ofd:Signatures": {
                "ofd:Signature": {
                    "@ID": "s0",
                    "@BaseLoc": "Doc_0/Signs/Signature_0/Signature.xml",
                }
            }
        }
        parser = SignaturesFileParser(xml_obj)
        result = parser()
        assert "s0" in result
        assert result["s0"].get("Type") is None


class TestSignatureFileParser:
    """测试 SignatureFileParser（单签章文件解析）"""

    def test_empty_xml(self):
        """空 xml 应返回空字典"""
        parser = SignatureFileParser({"ofd:Signature": {}})
        result = parser()
        assert result == {}

    def test_stamp_annot_with_signed_value(self):
        """含签名值的签章解析"""
        xml_obj = {
            "ofd:Signature": {
                "ofd:StampAnnot": {
                    "@PageRef": "p0",
                    "@Boundary": "87.50 8.50 30 20",
                    "@ID": "177",
                },
                "ofd:SignedValue": "SignedValue.dat",
            }
        }
        parser = SignatureFileParser(xml_obj)
        result = parser(prefix="Doc_0/Signs/Signature_0")
        assert result.get("PageRef") == "p0"
        assert result.get("Boundary") == "87.50 8.50 30 20"
        assert "SignedValue" in result
        assert result["SignedValue"].endswith("SignedValue.dat")

    def test_stamp_annot_without_signed_value(self):
        """无签名值的签章，使用默认路径"""
        xml_obj = {
            "ofd:Signature": {
                "ofd:StampAnnot": {
                    "@PageRef": "p0",
                    "@Boundary": "0 0 100 100",
                    "@ID": "178",
                }
            }
        }
        parser = SignatureFileParser(xml_obj)
        result = parser(prefix="Doc_0/Signs/Signature_0")
        assert result.get("PageRef") == "p0"
        assert result.get("Boundary") == "0 0 100 100"
        assert result.get("SignedValue") == "Doc_0/Signs/Signature_0/SignedValue.dat"
