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
    DrawingPanel = bd.Board(tags='DrawingPanel')
    # DrawingPanel = bd.Board().add_tag('DrawingPanel')
    CV.put(trans=crt.Translate(x=dskip, y=dskip), child=DrawingPanel)
    
    ## row
    oid = 0
    for i in range(vnum):
        ## 行オブジェクトB
        RowBoard = bd.Board(tags='RowBoard::Line')
        DrawingPanel.put(trans=crt.Translate(x=0, y=vspan*i), child=RowBoard)
        for j in range(hnum):
            C = bd.AnchorBoard(anchor_x='center', anchor_y='mid')
            RowBoard.put(trans=crt.Translate(x=hspan*j, y=0), child=C)
            rgb = COLS[oid % vnum ]
            if i % 2 == 0:
                #描画オブジェクトD
                D = bd.DrawRectangle(x=0.25*hspan, y=-0.25*vspan,
                                     # x=0, y=0,
                                     width=oh, height=oh,
                                     source_rgb=rgb,
                                     tags=f'Box_{i}_{j}')
                C.put(trans=crt.Translate(), child=D)
            else:
                #描画オブジェクトD
                D = bd.DrawCircle(x=0, y=0, r=hspan*0.25-line_width*0.5, 
                                  source_rgb=rgb, tags=f'Circle_{i}_{j}')
                C.put(trans=crt.Translate(x=hspan*0, y=hspan*0),
                      child=D)
            LEAF_LIST.append(D)
            ## セルオブジェクトC 
            oid += 1    

    #====== Markerのテスト ==============================
    # 格子点にマーカーを置く
    ## 描画領域オブジェクトA．余白(x=dskip, y=dskip)
    MarkerBoard = bd.Board(tags='MarkerBoard')
    DrawingPanel.put(child=MarkerBoard)
    for i in range(vnum+1): #row
        for j in range(hnum+1): #column
            #描画オブジェクト: circle
            M = bd.DrawCircle(x=0, y=0, r=2.0,
                              line_width=0.5, 
                              rgb=crt.MYCOL['red'],
                              tags=f'Marker_{i}_{j}')
            MarkerBoard.put(trans=crt.Translate(x=hspan*i, y=vspan*j), child=M)
            # DrawingPanel.put(trans=crt.Translate(x=hspan*i, y=vspan*j), child=M)
    
    #====== Polylineのテスト ==============================
    PL = bd.DrawPolyLines(line_width=0.5,
                          rgb=crt.MYCOL['blue'], 
                          linecap='round', 
                          linejoin='round', 
                          )
    DrawingPanel.put(trans=crt.Translate(x=0, y=0), child=PL)
    if opt.verbose:
        print(f'@debug: line: hnum, vnum { hnum, vnum  }: ')
    ncol = 0
    for j in range(vnum):
        x = hspan*i
        for i in range(hnum):
            y = vspan*j
            if opt.verbose:
                print(f'@debug: line at { i,j }: ')
            if i > 0 and j > 0:
                PL.move_to(hspan*(i-1), vspan*(j-1))
                col_ = COLS[(ncol % len(COLS))]
                PL.line_to(hspan*i, vspan*j, has_arrow=True)
                ncol += 1
    
    #====== Polylineのテスト ==============================

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


