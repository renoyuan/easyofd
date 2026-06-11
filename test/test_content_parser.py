"""
测试 Content 页面内容解析器
"""
import pytest


class TestContentFileParser:
    """测试页面内容解析"""

    def test_parse_empty_page(self):
        """空页面解析"""
        from easyofd.parser_ofd.file_content_parser import ContentFileParser

        xml = {"ofd:Page": {}}
        parser = ContentFileParser(xml)
        result = parser()

        assert "text_list" in result
        assert "img_list" in result
        assert "line_list" in result
        assert result["text_list"] == []
        assert result["img_list"] == []
        assert result["line_list"] == []

    def test_parse_page_with_text(self):
        """带文本的页面解析"""
        from easyofd.parser_ofd.file_content_parser import ContentFileParser

        xml = {
            "ofd:Page": {
                "ofd:Content": {
                    "ofd:Layer": {
                        "ofd:TextObject": {
                            "@ID": "1",
                            "@Font": "1",
                            "@Size": "12.0",
                            "@Boundary": "10 20 100 15",
                            "ofd:TextCode": {
                                "#text": "测试文本",
                                "@X": "0",
                                "@Y": "12.0",
                            },
                            "ofd:FillColor": {"Value": "0 0 0"},
                        }
                    }
                }
            }
        }
        parser = ContentFileParser(xml)
        result = parser()

        assert len(result["text_list"]) == 1
        text_obj = result["text_list"][0]
        assert text_obj["text"] == "测试文本"
        assert text_obj["size"] == 12.0

    def test_parse_page_with_image(self):
        """带图片的页面解析"""
        from easyofd.parser_ofd.file_content_parser import ContentFileParser

        xml = {
            "ofd:Page": {
                "ofd:Content": {
                    "ofd:Layer": {
                        "ofd:ImageObject": {
                            "@ID": "1",
                            "@ResourceID": "img_001",
                            "@Boundary": "0 0 200 100",
                            "@CTM": "200 0 0 100 0 0",
                        }
                    }
                }
            }
        }
        parser = ContentFileParser(xml)
        result = parser()

        assert len(result["img_list"]) == 1
        img_obj = result["img_list"][0]
        assert img_obj["ResourceID"] == "img_001"

    def test_parse_page_with_path(self):
        """带 Path 对象的页面解析"""
        from easyofd.parser_ofd.file_content_parser import ContentFileParser

        xml = {
            "ofd:Page": {
                "ofd:Content": {
                    "ofd:Layer": {
                        "ofd:PathObject": {
                            "@ID": "1",
                            "@Boundary": "0 0 100 50",
                            "@LineWidth": "1.0",
                            "ofd:StrokeColor": {"Value": "0 0 0"},
                        }
                    }
                }
            }
        }
        parser = ContentFileParser(xml)
        result = parser()

        assert len(result["line_list"]) == 1

    def test_parse_multiple_layers(self):
        """多 Layer 的页面解析"""
        from easyofd.parser_ofd.file_content_parser import ContentFileParser

        xml = {
            "ofd:Page": {
                "ofd:Content": {
                    "ofd:Layer": [
                        {
                            "@ID": "1",
                            "ofd:TextObject": {
                                "@ID": "1",
                                "@Font": "1",
                                "@Size": "10",
                                "@Boundary": "0 0 50 10",
                                "ofd:TextCode": {"#text": "图层1"},
                            },
                        },
                        {
                            "@ID": "2",
                            "ofd:TextObject": {
                                "@ID": "2",
                                "@Font": "1",
                                "@Size": "10",
                                "@Boundary": "0 10 50 10",
                                "ofd:TextCode": {"#text": "图层2"},
                            },
                        },
                    ]
                }
            }
        }
        parser = ContentFileParser(xml)
        result = parser()

        assert len(result["text_list"]) == 2

    def test_parse_multi_page_content(self):
        """多文本对象的页面"""
        from easyofd.parser_ofd.file_content_parser import ContentFileParser

        xml = {
            "ofd:Page": {
                "ofd:Content": {
                    "ofd:Layer": {
                        "ofd:TextObject": [
                            {
                                "@ID": "1",
                                "@Font": "1",
                                "@Size": "10",
                                "@Boundary": "0 0 50 10",
                                "ofd:TextCode": {"#text": "文本1"},
                            },
                            {
                                "@ID": "2",
                                "@Font": "1",
                                "@Size": "12",
                                "@Boundary": "0 10 50 10",
                                "ofd:TextCode": {"#text": "文本2"},
                            },
                        ]
                    }
                }
            }
        }
        parser = ContentFileParser(xml)
        result = parser()

        assert len(result["text_list"]) == 2
        assert result["text_list"][0]["text"] == "文本1"
        assert result["text_list"][1]["text"] == "文本2"

    def test_draw_param_color_parse(self):
        """测试带 DrawParam 引用颜色的解析"""
        from easyofd.parser_ofd.file_content_parser import ContentFileParser

        xml = {
            "ofd:Page": {
                "ofd:Content": {
                    "ofd:Layer": {
                        "ofd:TextObject": {
                            "@ID": "1",
                            "@Font": "1",
                            "@Size": "12",
                            "@Boundary": "0 0 100 15",
                            "ofd:TextCode": {"#text": "带颜色"},
                            "ofd:FillColor": {"@RefID": "dp_1"},
                        }
                    }
                }
            }
        }
        parser = ContentFileParser(xml)
        result = parser()

        assert len(result["text_list"]) == 1
        # 当颜色是通过 RefID 引用时，应标记出来
        assert "颜色取色" not in str(result)  # 不应直接崩溃
