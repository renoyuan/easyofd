from reportlab.pdfbase import pdfmetrics


from .draw_pdf import DrawPDF
from parser_ofd import *

FONTS = ['宋体',"SWPMEH+SimSun",'SimSun','KaiTi','楷体',"STKAITI","SWLCQE+KaiTi",
         'Courier New','STSong-Light',"CourierNew","SWANVV+CourierNewPSMT",
         "CourierNewPSMT","BWSimKai","hei","黑体","SimHei","SWDKON+SimSun",
         "SWCRMF+CourierNewPSMT","SWHGME+KaiTi"]

pdfmetrics.registerFont(TTFont('宋体', 'simsun.ttc'))
pdfmetrics.registerFont(TTFont('SWPMEH+SimSun', 'simsun.ttc'))
pdfmetrics.registerFont(TTFont('SimSun', 'simsun.ttc'))
pdfmetrics.registerFont(TTFont('SWDKON+SimSun', 'simsun.ttc'))
pdfmetrics.registerFont(TTFont('KaiTi', 'simkai.ttf'))
pdfmetrics.registerFont(TTFont('楷体', 'simkai.ttf'))
pdfmetrics.registerFont(TTFont('STKAITI', 'STKAITI.TTF'))
pdfmetrics.registerFont(TTFont('SWLCQE+KaiTi', 'simkai.ttf'))
pdfmetrics.registerFont(TTFont('SWHGME+KaiTi', 'simkai.ttf'))
pdfmetrics.registerFont(TTFont('BWSimKai', 'simkai.ttf'))
pdfmetrics.registerFont(TTFont('SWCRMF+CourierNewPSMT', 'COURI.TTF'))
pdfmetrics.registerFont(TTFont('SWANVV+CourierNewPSMT', 'COURI.TTF'))
pdfmetrics.registerFont(TTFont('CourierNew', 'COURI.TTF'))
pdfmetrics.registerFont(TTFont('CourierNewPSMT', 'COURI.TTF'))
pdfmetrics.registerFont(TTFont('Courier New', 'COURI.TTF'))
pdfmetrics.registerFont(UnicodeCIDFont('STSong-Light'))
pdfmetrics.registerFont(TTFont('SimHei', 'simhei.ttf'))
pdfmetrics.registerFont(TTFont('hei', 'simhei.ttf'))
pdfmetrics.registerFont(TTFont('黑体', 'simhei.ttf'))





    