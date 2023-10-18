
from loguru import logger
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.pdfbase.ttfonts import TTFont

# from ofd_parser import *
from .ofd_parser import OFDParser

font_map = {"simsun.ttc":["宋体","SWPMEH+SimSun","SimSun","SWDKON+SimSun"],
            'simkai.ttf':["KaiTi","楷体","SWLCQE+KaiTi","SWHGME+KaiTi","BWSimKai"],
            'STKAITI.TTF':["STKAITI"],
            "COURI.TTF":["Courier New","CourierNewPSMT","CourierNew","SWCRMF+CourierNewPSMT","SWANVV+CourierNewPSMT"],
            "simhei.ttf":["SimHei","hei","黑体"]
            }
pdfmetrics.registerFont(UnicodeCIDFont('STSong-Light'))

# 初始化字体
for font,names in font_map.items():
    for name in names:
        try:
            pdfmetrics.registerFont(TTFont(name, font))
        except:
            logger.warning(f"FONT  registerFont failed {font}: {name}")
            
__all__=["OFDParser"]
                                    



