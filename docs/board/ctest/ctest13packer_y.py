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
    # ## options: main 
    # ap.add_argument('-l', '--maxlen', type=int,
    #                 help='specify maximum length of messages')
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
                   imagesize='QVGA',
                   portrait=False,
                   boundingbox=opt.boundingbox,
                   max_perturb=bd.DEFAULT_LINE_WIDTH*4.0,                   
                   verbose=opt.verbose)

    cr = CV.context()
    #cim = CV.get_image_board() ##ImageBoardオブジェクト
    #cr = cim.context()

    #====== テスト ==============================
    dskip = 50
    hspan, vspan = 50, 50
    hnum, vnum = 5, 4
    line_width = 2 
    hair_line_width = 0.5 
    mygrey = crt.MYCOL['grey50']
    ow, oh = hspan*0.5, vspan*0.5
    COLS = list(crt.DARKCOL.values())

    cr.set_line_width(line_width)

    #====== テスト ==============================
    # cboard.Board の構成実験
    LEAF_LIST = [] #オブジェクト木の葉の集合
    
    ## 描画領域オブジェクトA．余白(x=dskip, y=dskip)
    DrawingPanel = CV.put(trans=crt.Translate(x=dskip, y=dskip),
                          child=bd.Board(tags='DrawingPanel'))
    
    # #====== Markerのテスト ==============================
    # # 格子点にマーカーを置く
    # ## 描画領域オブジェクトA．余白(x=dskip, y=dskip)
    # MarkerBoard = DrawingPanel
    # for i in range(vnum+1): #row
    #     for j in range(hnum+1): #column
    #         #描画オブジェクト: circle
    #         MarkerBoard.put(trans=crt.Translate(x=hspan*j, y=vspan*i),
    #                         child=bd.DrawCircle(x=0, y=0, r=3,
    #                                             line_width=0.75,
    #                                             anchor_x='center',
    #                                             anchor_y='mid', 
    #                                             rgb=crt.cr_add_alpha(crt.MYCOL['blue'], 0.375),
    #                                             fill='fill', 
    #                                             tags=f'Marker_{i}_{j}',
    #                                             boundingbox=False)
    #                         )
    
    #===== 図形のテスト ==============================
    # 格子点に図形をおく
    ## row
    if not opt.anchor_x: opt.anchor_x = 'left'
    if not opt.anchor_y: opt.anchor_y = 'top'

    VStack = DrawingPanel.put(trans=crt.Translate(dest=(0,0)),
                              child=bd.PackerBoard(orient='y',
                                                   margin=hspan/2, 
                                                   ))
    
    oid = 0
    for i in range(vnum): #行
        Row = VStack.add(child=bd.PackerBoard(orient='x',
                                              margin=hspan/4, 
                                              pack_anchor_x=opt.anchor_x,
                                              pack_anchor_y=opt.anchor_y, 
                                              ))
        for j in range(hnum): #列
            rgb = COLS[oid % vnum ]
            if i % 2 == 0: 
                D = Row.add(child=bd.DrawRectangle(width=oh, height=oh,
                                                   # anchor_x=opt.anchor_x,
                                                   # anchor_y=opt.anchor_y, 
                                                   source_rgb=rgb,
                                                   tags=f'Box_{i}_{j}',
                                                   show_origin=True, 
                                                   )
                            )
            else:
                D = Row.add(child=bd.DrawCircle(r = 0.5*oh, 
                                                # anchor_x=opt.anchor_x,
                                                # anchor_y=opt.anchor_y, 
                                                source_rgb=rgb,
                                                tags=f'Circle_{i}_{j}',
                                                show_origin=True, 
                                                )
                            )
            LEAF_LIST.append(D)
            oid += 1
    #===== 図形のテスト ==============================

    # #====== Polylineのテスト ==============================
    # PL = DrawingPanel.put(trans=crt.Translate(dest=(0,0)),
    #                       child=bd.DrawPolyLines(line_width=0.5,
    #                                              rgb=crt.MYCOL['blue'], 
    #                                              )
    #                       )
    # if opt.verbose:
    #     print(f'@debug: line: hnum, vnum { hnum, vnum  }: ')
    # ncol = 0
    # for j in range(vnum):
    #     x = hspan*i
    #     for i in range(hnum):
    #         y = vspan*j
    #         if opt.verbose:
    #             print(f'@debug: line at { i,j }: ')
    #         if i > 0 and j > 0:
    #             PL.move_to(hspan*(i-1), vspan*(j-1))  #polyline
    #             col_ = COLS[(ncol % len(COLS))]
    #             PL.line_to(hspan*i, vspan*j, has_arrow=True) #polyline
    #             ncol += 1
    
    # # #====== Polylineのテスト ==============================

    #============
    #印刷
    #============
    CV.show(noshow=opt.noshow)

    #debug
    if opt.verbose: 
        print(f'\n===== { "printing the object tree..." } ======')
        CV.dump()

        
    if False and opt.verbose: 
        print(f'===========')
        print(f'@Applying the local transformation associated to each leaf node to a point p=(0,0)...')
        ancestor=CV
        if LEAF_LIST and len(LEAF_LIST) > 0:
            for idx, leaf in enumerate(LEAF_LIST):
                p0=(0.0, 0.0)
                # p0=(0.0, 0.0, 1.0, 1.0)
                p1 = ancestor.relative_transform(p=p0, target=leaf,
                                           verbose=False)
                # p0 = ancestor.relative_transform_by_apath(p=(0.0, 0.0), apath=apath)
                print(f'LEAF{idx}\tp0={ p0 } at { ancestor.myinfo(depth=True) } => p1={ p1 } at {leaf.myinfo(depth=True)}')
                apath = leaf.relative_apath_get(top=ancestor)
                tpath = ancestor.relative_apath_to_tpath(apath=apath, verbose=False)
                apath1 = [ (obj.myinfo(), ord) for obj, ord in apath ]
                print(f'\tapath={ apath1 }')
                print(f'\t=> tpath={ [ trans.__str__() for trans in tpath ] }')
            print(f'Note that the obtained transformation result is tentative, and wrong, and just for development purpose. This must be reversed. ')
    
    pass 

##EOF


