# coding: utf_8
# ctest8cbd.py
# - アンカー点の機構を実装する．
# - 
import sys
from argparse import ArgumentParser
import cairo 
import math 

import common as com 
##
import crtool as crt
import cboard as bd
#import cimage as cim

verbose = True


#色
fancy = ['lightskyblue', 'lightgreen', 'lightgrey']
solid = ['red', 'lightcoral', 'orange', 'darkorchid', 'royalblue', ]

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
    # ## options: main 
    # ap.add_argument('-l', '--maxlen', type=int,
    #                 help='specify maximum length of messages')
    ## align 
    ap.add_argument('-a', '--align', type=str, 
                    help='set align to str')
    ## pack 
    ap.add_argument('-p', '--pack', action='store_true', default=False, 
                    help='show verbose messages')
    ## anchor 
    ap.add_argument('-x', '--anchor_x', type=str, 
                    help='set anchor_x to str')
    ## anchor 
    ap.add_argument('-y', '--anchor_y', type=str, 
                    help='set anchor_y to str')
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
    verbose=False

    # 位置指定による2D配置のテスト
    #画像枠の生成
    CV = bd.Canvas(outfile="out",
                   #imagesize='QVGA',
                   imagesize='VGA',
                   portrait=False,
                   boundingbox=opt.boundingbox,
                   # max_perturb=bd.DEFAULT_LINE_WIDTH*4.0,
                   max_perturb=bd.DEFAULT_LINE_WIDTH*8.0, 
                   verbose=opt.verbose)
    cr = CV.context() #Cairo.Context

    #====== テスト ==============================
    uspan = 50 #単位スパン
    line_width = 0.75
    # line_width = 2 
    
    # uspan = 50 #単位スパン
    dskip = 0.5*uspan
    hspan, vspan = uspan, uspan 
    hnum, vnum = 5, 4 
    hair_line_width = line_width/2
    mygrey = crt.MYCOL['grey50']
    ow, oh = hspan*1, vspan*1
    # ow, oh = hspan*0.5, vspan*0.5
    COLS = list(crt.DARKCOL.values())

    cr.set_line_width(line_width)

    #====== テスト ==============================
    # cboard.Board の構成実験
    LEAF_LIST = [] #オブジェクト木の葉の集合
    
    ## 描画領域オブジェクトA．余白(x=dskip, y=dskip)
    DrawingPanel = CV.put(trans=crt.Translate(dest=(dskip,dskip)),
                          child=bd.Board(tags='DrawingPanel'))
    
    #====== Markerのテスト ==============================
    # 格子点にマーカーを置く
    ## 描画領域オブジェクトA．余白(x=dskip, y=dskip)
    if False: 
        MarkerBoard = DrawingPanel
        for i in range(vnum+1): #row
            for j in range(hnum+1): #column
                #描画オブジェクト: circle
                MarkerBoard.put(trans=crt.Translate(x=hspan*j, y=vspan*i),
                                child=bd.DrawCircle(x=0, y=0, r=3,
                                                    line_width=0.75,
                                                    anchor=('center','mid'),
                                                    rgb=crt.cr_add_alpha(crt.MYCOL['blue'], 0.375),
                                                    fill='fill', 
                                                    tags=f'Marker_{i}_{j}',
                                                    boundingbox=False)
                                )
    
    #===== 図形のテスト ==============================
    # 格子点に図形をおく
    ## row
    if not opt.align: opt.align = 'y'
    if opt.align in ('x'): align_outer, align_inner = 'y', 'x'
    else: align_outer, align_inner = 'x', 'y'

    VStack = DrawingPanel.put(trans=crt.Translate(x=0, y=0),
                              child=bd.PackerBoard(align=align_outer,
                                                   pack=False,
                                                   margin=0, 
                                                   #margin=hspan/2, 
                                                   ))
    
    oid = 0
    for i in range(vnum): #行
        rgb = COLS[oid % vnum ]
        ow_var, oh_var = ow, oh
        if oid % 2 == 0: 
            D = VStack.add(bd.DrawCircle(r=0.5*ow_var,
                                         # anchor=('left', 'top'),
                                         source_rgb=rgb,
                                         tags=f'Box_{i}',
                                         show_origin=True, 
                                         ))
        else:
            D = VStack.add(bd.DrawRectangle(width=ow_var, height=oh_var,
                                            source_rgb=rgb,
                                            tags=f'Box_{i}',
                                            show_origin=True, 
                                            ))
        LEAF_LIST.append(D)
        oid += 1
    #===== 図形のテスト ==============================

    #============
    #印刷
    #============
    CV.show(noshow=opt.noshow)

    
    pass 

##EOF


