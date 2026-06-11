"""
测试 Document 解析器
"""
import pytest


class TestDocumentFileParser:
    """测试 Document.xml 解析"""

    def test_parse_basic_document(self, sample_xml_obj):
        """基础 Document.xml 解析"""
        from easyofd.parser_ofd.file_doc_parser import DocumentFileParser

        parser = DocumentFileParser(sample_xml_obj)
        result = parser()

        assert "size" in result
        assert "public_res" in result
        assert "document_res" in result
        assert "page" in result
        assert "page_id_map" in result

    def test_page_count(self, sample_xml_obj):
        """验证正确解析出 2 页"""
        from easyofd.parser_ofd.file_doc_parser import DocumentFileParser

        parser = DocumentFileParser(sample_xml_obj)
        result = parser()

        assert len(result["page"]) == 2

    def test_page_id_map(self, sample_xml_obj):
        """验证 page_id_map 映射是否正确"""
        from easyofd.parser_ofd.file_doc_parser import DocumentFileParser

        parser = DocumentFileParser(sample_xml_obj)
        result = parser()

        assert result["page_id_map"] == {"1": 1, "2": 2}

    def test_document_with_tpl(self):
        """带模板页的 Document 解析"""
        xml_with_tpl = {
            "ofd:Document": {
                "ofd:Page": [
                    {"@ID": "1", "@BaseLoc": "Pages/Page_1/Content.xml"},
                ],
                "ofd:TemplatePage": [
                    {"@ID": "tpl1", "@BaseLoc": "Tpls/Tpl_0/Content.xml"},
                ],
                "ofd:PublicRes": "PublicRes.xml",
                "ofd:DocumentRes": "DocumentRes.xml",
            }
        }
        from easyofd.parser_ofd.file_doc_parser import DocumentFileParser

        parser = DocumentFileParser(xml_with_tpl)
        result = parser()

        assert "tpls" in result
        assert len(result["tpls"]) == 1
        assert result["tpls"][0] == "Tpls/Tpl_0/Content.xml"

    def test_document_with_annotations(self):
        """带注释的 Document 解析"""
        xml_with_anno = {
            "ofd:Document": {
                "ofd:Page": [
                    {"@ID": "1", "@BaseLoc": "Pages/Page_1/Content.xml"},
                ],
                "ofd:Annotations": "Annotations.xml",
                "ofd:PublicRes": "PublicRes.xml",
            }
        }
        from easyofd.parser_ofd.file_doc_parser import DocumentFileParser

        parser = DocumentFileParser(xml_with_anno)
        result = parser()

        assert "Annotations" in result
        assert result["Annotations"] == ["Annotations.xml"]

    def test_document_with_custom_tags(self):
        """带自定义标签的 Document 解析"""
        xml_with_tag = {
            "ofd:Document": {
                "ofd:Page": [
                    {"@ID": "1", "@BaseLoc": "Pages/Page_1/Content.xml"},
                ],
                "ofd:CustomTags": "CustomTags.xml",
                "ofd:PublicRes": "PublicRes.xml",
            }
        }
        from easyofd.parser_ofd.file_doc_parser import DocumentFileParser

        parser = DocumentFileParser(xml_with_tag)
        result = parser()

        assert "custom_tag" in result
        assert result["custom_tag"] == ["CustomTags.xml"]

    def test_empty_document_fails(self):
        """空 Document 应返回空字段"""
        from easyofd.parser_ofd.file_doc_parser import DocumentFileParser

        parser = DocumentFileParser({})
        result = parser()

        # 不报错，返回空列表
        assert result["page"] == []
        assert result["public_res"] == []
        assert result["document_res"] == []
