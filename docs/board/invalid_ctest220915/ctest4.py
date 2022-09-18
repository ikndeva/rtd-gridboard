# coding: utf_8
# btest1.py
# 画盤モジュールのテスト
import sys
from argparse import ArgumentParser
import cairo 
import math 

import common as com 
##
import crtool 
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
                   imagesize='SVGA',
                   portrait=True, #縦長
                   boundingbox=opt.boundingbox, 
                   verbose=True)

    pim = CV.get_image_board() ##ImageBoardオブジェクト
    cr = pim.context()

    #============
    #描画: Board
    #============

    #マーカーを格子に配置
    hspan, vspan = 100, 100
    for i in range(6): 
        for j in range(4): 
            crtool.cr_draw_marker(hspan*i, vspan*j, context=cr,
                           ffamily="Sans", source_rgb=(1,0,0))

    #長方形
    COL = [(0,0,1), (0,0.5,0), (1,0,0)]
    def add_alpha(rgb, alpha=None):
        if len(rgb)==3 and alpha!=None:
            return (rgb[0], rgb[1], rgb[2], alpha)
        else:
            return rgb

    """
    mtx = Matrix(xx=1.0, yx=0.0, xy=0.0, yy=1.0, x0=0.0, y0=0.0)

    transformaton mtx: x, y => x_new, y_new
    x_new = xx * x + xy * y + x0
    y_new = yx * x + yy * y + y0
    """
        
    #1スパン下へ移動
    cr.translate(0, vspan) #layer1
    mtx1 = cairo.Matrix() #identity
    for i in range(4):
        cr.save()  #push layer1.i
        #1スパン右への並行移動を，i回合成する
        for j in range(i): 
            cr.translate(hspan, 0) #these transfomations are composed
            # #並行移動を行列で書く: 
            # h1, v1 = hspan, 0
            # mtx0 = cairo.Matrix(1.0, 0.0,
            #                     0.0, 1.0,
            #                     h1, v1)
            # mtx1 = mtx1 * mtx0 #途中で行列を乗算して
        # cr.transform(mtx1)     #最後に1回だけ変換を適用しても良い．

        #変形なし長方形
        pim.rectangle(0, 0, 50, 50, source_rgb=(0.25,0.25,0.25, 0.5))
        crtool.cr_circle(0, 0, r=5, fill='stroke', source_rgb=(0,0,1,0.5), context=cr)

        
        #変形した長方形
        for j in range(i): #x<=x, y<=0.5*xのゆがみ変換をi回合成する
            mtx = cairo.Matrix()
            mtx.rotate(math.pi/12.0)
            cr.transform(mtx)
        
        pim.rectangle(0, 0, 50, 50,
                      source_rgb=add_alpha(COL[i % len(COL)], alpha=0.5),
                      fill='fill')
        crtool.cr_text(5, +5, msg=f'{180*(i/12.0):.0f} deg',
                       source_rgb=COL[i % len(COL)], 
                       context=cr)
        cr.restore()  #pop layer1.i
    pass 
    
    # #1スパン下へ移動
    # cr.translate(0, vspan) #layer1
    # for i in range(4):
    #     cr.save()  #push layer1.i
    #     #1スパン右への並行移動を，i回合成する
    #     for j in range(i): 
    #         #cr.translate(hspan, 0) #these transfomations are composed
    #         #並行移動を行列で書く: 
    #         h1, v1 = hspan, 0
    #         mtx0 = cairo.Matrix(1.0, 0.0,
    #                             0.0, 1.0,
    #                             h1, v1)
    #         cr.transform(mtx0)

    #     #変形なし長方形
    #     pim.rectangle(0, 0, 50, 50, source_rgb=(0.25,0.25,0.25, 0.2), verbose=True)
        
    #     #変形した長方形
    #     for j in range(i): #x<=x, y<=0.5*xのゆがみ変換をi回合成する
    #         mtx = cairo.Matrix(1.0, 0.5,
    #                            0.0, 1.0,
    #                            0.0, 0.0)
    #         #these transfomations are composed
    #         cr.transform(mtx)
    #     pim.rectangle(0, 0, 50, 50,
    #                   source_rgb=add_alpha(COL[i % len(COL)], alpha=0.5),
    #                   verbose=True)
    #     cr.restore()  #pop layer1.i
    # pass 
    
    # #長方形
    # COL = [(0,0,1), (0,1,0), (1,0,0)]
    # for i in range(4): 
    #     pim.rectangle(0, 0, 50, 50, source_rgb=COL[i % len(COL)], verbose=True)
    #     #after
    #     if i % 2 == 0: 
    #         cr.translate(hspan, vspan)
    #     else:
    #         cr.translate(hspan, -1.0*vspan)
    #     pass 
    
    
    # #============
    # #長方形
    # #============
    # ox, oy = ox, oy+vskip ##描画の基準点
    # ox, oy = ox, oy - 0.5*vskip ##描画の基準点
    # cr.set_source_rgb(0.0, 0.0, 0.75) #blue =(0.0, 0.0, 1.0)
    # ## 線幅
    # cr.set_line_width(5)
    # ## 線の点線
    # # cr.set_dash([10.0])
    # # cr.set_dash([10.0, 2.0])
    # ## 継ぎ目の形
    # #cr.set_line_join(cairo.LINE_JOIN_MITER)
    # cr.set_line_join(cairo.LINE_JOIN_BEVEL)
    # #cr.set_line_join(cairo.LINE_JOIN_ROUND)

    # use_rect = False
    # px, py = ox, oy
    # if use_rect:
    #     cr.rectangle(ox, oy, width, height)
    # else:
    #     cr.move_to(px, py)
    #     cr.line_to(px,  py+height)
    #     cr.line_to(px+width, py+height)
    #     cr.line_to(px+width, py)
    #     cr.close_path()
    # cr.stroke()

    #============
    #円形
    #============
    # ox, oy = ox, oy+vskip ##描画の基準点
    # qx, qy = ox + 0.5*width, oy
    # r=height

    # ## 円盤

    # ## 円盤
    # blend=0.5
    # # blend=1.0
    # cr_circle(qx, qy, r, fill='fill_preserve',
    #           source_rgb=(0.0 + blend, 0.5, 0.0 + blend), context=cr)

    # ## 輪郭
    # blend=0.125
    # cr.set_source_rgb(1.0 - blend, 0.0 + blend, 0.0) #orange 
    # cr.set_line_width(5) ## 線幅
    # cr.stroke() #輪郭

    # ## 中心点
    # # cr.arc(qx, qy, rsmall, 0.0*math.pi, 2.0*math.pi); cr.fill()
    # cr_circle(qx, qy, rsmall, fill='fill', context=cr)

    # #============
    # #曲線
    # #============
    # ox, oy = ox, oy+vskip ##描画の基準点    
    # rx, ry = ox, oy
    # #cr.set_source_rgb(0.5, 0.0, 0.125) #
    # cr.set_source_rgb(0.75, 0.25, 0.0) #
    # cr.move_to(rx, ry)
    # cx1, cy1 = rx + 0.5*width, ry + 1.0*height
    # cx2, cy2 = rx + 0.5*width, ry - 1.0*height
    # # cx1, cy1 = rx + 0.5*width, ry - 1.0*height
    # # cx2, cy2 = rx + 0.5*width, ry - 1.0*height
    # sx,  sy  = rx + 1.0*width, ry
    # cr.curve_to(cx1, cy1, cx2, cy2, sx, sy)
    # cr.set_line_width(5) ## 線幅
    # cr.stroke()

    # ## draw control points
    # cr.set_source_rgb(1.0, 0.0, 0.0) #red
    # cr.set_line_width(2) ## 線幅
    # cr.move_to(rx, ry); cr.line_to(cx1, cy1); cr.stroke()
    # cr.move_to(sx, sy); cr.line_to(cx2, cy2); cr.stroke()
    # cr.arc(cx1, cy1, rsmall, 0.0*math.pi, 2.0*math.pi); cr.fill()
    # cr.arc(cx2, cy2, rsmall, 0.0*math.pi, 2.0*math.pi); cr.fill()
    # ## draw end points in 
    # cr.set_source_rgb(0.0, 0.0, 1.0) #blue
    # cr.set_line_width(2) ## 線幅
    # cr.arc(rx, ry, rsmall, 0.0*math.pi, 2.0*math.pi); cr.fill()
    # cr.arc(sx, sy, rsmall, 0.0*math.pi, 2.0*math.pi); cr.fill()

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


