# coding: utf_8
# btest1.py
# 画盤モジュールのテスト
import sys
from argparse import ArgumentParser
import cairo 
import math 

import common as com 
# ##
import cboard as bd
#import cimage as pim

verbose = True

#色
fancy = ['lightskyblue', 'lightgreen', 'lightgrey']
solid = ['red', 'lightcoral', 'orange', 'darkorchid', 'royalblue', ]

#画像の解像度をppi (pixel per inch)で設定する
#myppi = 1024
#myppi = 572

##=====
## コマンドライン引数
##=====
CMD_NAME = (__file__.split('/'))[-1]

def reading_args_and_options():
    USAGE_STR = f'Usage: python3 { CMD_NAME } OPTIONS '
    ap = ArgumentParser(usage=USAGE_STR)
    ## 
    # ap.add_argument('args', type=str,
    #                 ##note: デフォールトはpositional argなのでdestは不要
    #                 help='sequence of numbers')
    ## options: 
    ## noshow
    ap.add_argument('-n', '--noshow', action='store_true', default=False, 
                    help='supreess to displaying graphics')
    ## boundingbox
    ap.add_argument('-b', '--boundingbox', action='store_true', default=False, 
                    help='show verbose messages')
    ## verbose 
    ap.add_argument('-v', '--verbose', action='store_true', default=False, 
                    help='show verbose messages')
    ## 
    args = ap.parse_args()
    return args, ap

#=====
#便利関数
#=====
def pos(xy): 
    return vec.geom_trans_gen(xy, 
                func=lambda p: vec.point_apply(p, 
                        lambda orig:(orig * edgelen)))

##======
## メイン文
##======

if __name__ == '__main__':
    #コマンドラインの引数とオプションの読み込み
    opt, ap = reading_args_and_options()

    #parameters
    # -p 576 -s 3:2 -w 1
    verbose=False
    fontsize = 12
    ppi = 576
    shape = (3,2)
    width = 40
    uspan = 50

    # 位置指定による2D配置のテスト
    #画像枠の生成
    CV = bd.Canvas(outfile="out",
                   imagesize='VGA', 
                   portrait=True, #縦長
                   boundingbox=opt.boundingbox, 
                   verbose=True)

    cr = CV.context()
    # pim = CV.get_image_board() ##ImageBoardオブジェクト
    # cr = pim.context()

    #============
    #描画: Cairo のprimitive 
    #============

    #============
    ## draw
    #============
    rsmall = 5 #the radius of a small disk

    #============
    #テキスト
    #============
    ox, oy = 10, 10  ##描画の基準点
    # ffamily = "Sans"
    # ffamily = "Times New Roman"
    ffamily = "Palatino"
    cr.select_font_face(ffamily,
                        cairo.FONT_SLANT_NORMAL,
                        cairo.FONT_WEIGHT_NORMAL)

    ## テキストの描画情報を取得
    msg = "Hello World!"
    fsize = 80
    cr.set_font_size(fsize) #default: font_size = 10
    fx, fy, width, height, dx, dy = cr.text_extents(msg)

    ## テキストを描画
    cr.set_source_rgb(0.75, 0.0, 0.00) #blue =(0.0, 0.0, 1.0)
    cr.move_to(ox, oy + height)
    cr.show_text(msg)

    #============
    #部分図の間隔設定
    #============
    vskip  = 2.5*height ##部分図の間隔
    
    #============
    #長方形
    #============
    ox, oy = ox, oy+vskip ##描画の基準点
    ox, oy = ox, oy - 0.5*vskip ##描画の基準点
    cr.set_source_rgb(0.0, 0.0, 0.75) #blue =(0.0, 0.0, 1.0)
    ## 線幅
    cr.set_line_width(5)
    ## 線の点線
    # cr.set_dash([10.0])
    # cr.set_dash([10.0, 2.0])
    ## 継ぎ目の形
    #cr.set_line_join(cairo.LINE_JOIN_MITER)
    cr.set_line_join(cairo.LINE_JOIN_BEVEL)
    #cr.set_line_join(cairo.LINE_JOIN_ROUND)

    use_rect = False
    px, py = ox, oy
    if use_rect:
        cr.rectangle(ox, oy, width, height)
    else:
        cr.move_to(px, py)
        cr.line_to(px,  py+height)
        cr.line_to(px+width, py+height)
        cr.line_to(px+width, py)
        cr.close_path()
    cr.stroke()

    #============
    #円形
    #============
    ox, oy = ox, oy+vskip ##描画の基準点
    qx, qy = ox + 0.5*width, oy
    r=height

    ## 円盤
    blend=1.0
    cr.set_source_rgb(0.0, 0.0, 0.0 + blend) #orange
    cr.arc(qx, qy, r, 0.0*math.pi, 2.0*math.pi)
    # cr.fill()
    cr.fill_preserve() #塗りつぶし

    ## 輪郭
    blend=0.125
    cr.set_source_rgb(1.0 - blend, 0.0 + blend, 0.0) #orange 
    cr.set_line_width(5) ## 線幅
    cr.stroke() #輪郭

    ## 中心点
    cr.arc(qx, qy, rsmall, 0.0*math.pi, 2.0*math.pi); cr.fill()

    #============
    #曲線
    #============
    ox, oy = ox, oy+vskip ##描画の基準点    
    rx, ry = ox, oy
    #cr.set_source_rgb(0.5, 0.0, 0.125) #
    cr.set_source_rgb(0.75, 0.25, 0.0) #
    cr.move_to(rx, ry)
    cx1, cy1 = rx + 0.5*width, ry + 1.0*height
    cx2, cy2 = rx + 0.5*width, ry - 1.0*height
    # cx1, cy1 = rx + 0.5*width, ry - 1.0*height
    # cx2, cy2 = rx + 0.5*width, ry - 1.0*height
    sx,  sy  = rx + 1.0*width, ry
    cr.curve_to(cx1, cy1, cx2, cy2, sx, sy)
    cr.set_line_width(5) ## 線幅
    cr.stroke()

    ## draw control points
    cr.set_source_rgb(1.0, 0.0, 0.0) #red
    cr.set_line_width(2) ## 線幅
    cr.move_to(rx, ry); cr.line_to(cx1, cy1); cr.stroke()
    cr.move_to(sx, sy); cr.line_to(cx2, cy2); cr.stroke()
    cr.arc(cx1, cy1, rsmall, 0.0*math.pi, 2.0*math.pi); cr.fill()
    cr.arc(cx2, cy2, rsmall, 0.0*math.pi, 2.0*math.pi); cr.fill()
    ## draw end points in 
    cr.set_source_rgb(0.0, 0.0, 1.0) #blue
    cr.set_line_width(2) ## 線幅
    cr.arc(rx, ry, rsmall, 0.0*math.pi, 2.0*math.pi); cr.fill()
    cr.arc(sx, sy, rsmall, 0.0*math.pi, 2.0*math.pi); cr.fill()
    
    #============
    #描画: Board
    #============
    # #図形を書く
    # px, py = 10, 10
    # qx, qy = px + width, py + width
    # CV.rectangle(xy=[(px, py), (qx, qy)], fill='red', verbose=True)
    # px, py = px + uspan, py
    # qx, qy = px + width, py + width
    # CV.rectangle(xy=[(px, py), (qx, qy)], fill='green', verbose=True)
    # px, py = px + uspan, py
    # qx, qy = px + width, py + width
    # CV.rectangle(xy=[(px, py), (qx, qy)], fill='blue', verbose=True)
    # px, py = px + uspan, py
    # qx, qy = px + width, py + width

    #============
    #印刷
    #============
    CV.show(noshow=opt.noshow)
    pass 

##EOF


