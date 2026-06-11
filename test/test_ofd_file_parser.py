#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""测试 OFDFileParser（OFD.xml 根文件解析）"""

import pytest
from easyofd.parser_ofd.file_ofd_parser import OFDFileParser


class TestOFDFileParser:
    """测试 OFDFileParser"""

    def test_empty_xml(self):
        """空 xml 应返回包含默认值的字典"""
        parser = OFDFileParser({"ofd:OFD": {}})
        result = parser()
        assert isinstance(result, dict)
        assert result.get("doc_root") == []
        assert result.get("signatures") == []
        assert result.get("creator") == []
        assert result.get("creationDate") == []

    def test_full_document(self):
        """完整 OFD.xml 解析"""
        xml_obj = {
            "ofd:OFD": {
                "ofd:DocRoot": "Doc_0/Document.xml",
                "ofd:Signatures": "Doc_0/Signs/Signatures.xml",
                "ofd:Creator": "easyofd",
                "ofd:CreationDate": "2025-01-01",
            }
        }
        parser = OFDFileParser(xml_obj)
        result = parser()
        assert "Doc_0/Document.xml" in result["doc_root"]
        assert "Doc_0/Signs/Signatures.xml" in result["signatures"]
        assert "easyofd" in result["creator"]
        assert "2025-01-01" in result["creationDate"]

    def test_only_doc_root(self):
        """仅包含 DocRoot 的解析"""
        xml_obj = {
            "ofd:OFD": {
                "ofd:DocRoot": "Doc_0/Document.xml",
            }
        }
        parser = OFDFileParser(xml_obj)
        result = parser()
        assert len(result["doc_root"]) == 1
        assert result["signatures"] == []
        assert result["creator"] == []
        assert result["creationDate"] == []

    def test_multiple_doc_roots(self):
        """多个 DocRoot（多文档场景）"""
        xml_obj = {
            "ofd:OFD": {
                "ofd:DocRoot": [
                    "Doc_0/Document.xml",
                    "Doc_1/Document.xml",
                ]
            }
        }
        parser = OFDFileParser(xml_obj)
        result = parser()
        assert len(result["doc_root"]) == 2
