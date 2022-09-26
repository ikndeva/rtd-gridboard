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
                   verbose=opt.verbose)

    cr = CV.context()
    #cim = CV.get_image_board() ##ImageBoardオブジェクト
    #cr = cim.context()

    #====== テスト ==============================
    dskip = 20
    hnum, vnum = 5, 4
    #hnum, vnum = 6, 5
    hspan, vspan = 50, 50
    line_width = 2 
    mygrey = crt.MYCOL['grey50']
    ow, oh = hspan*0.5, vspan*0.5
    COLS = list(crt.DARKCOL.values())

    cr.set_line_width(line_width)

    #====== テスト ==============================
    # cboard.Board の構成実験
    LEAF_LIST = [] #オブジェクト木の葉の集合
    
    ## 描画領域オブジェクトA．余白(x=dskip, y=dskip)
    A = bd.Board(tags='A')
    CV.put(trans=crt.Translate(dest=(dskip, dskip)), child=A)
    
    ## row
    oid = 0
    for i in range(vnum):
        ## 行オブジェクトB
        B = bd.Board(tags='B::Line')
        A.put(trans=crt.Translate(dest=(0, vspan*i)), child=B)
        for j in range(hnum):
            C = bd.Board(tags='C::ParentDrawCmd')
            rgb = COLS[oid % vnum ]
            if i % 2 == 0:
                #描画オブジェクトD
                D = bd.DrawRectangle(x=0, y=0, width=oh, height=oh,
                                     source_rgb=rgb, tags='tag::DrawRectangle')
                C.put(trans=crt.Translate(dest=(hspan*0.25, hspan*0.25)), child=D)
            else:
                #描画オブジェクトD
                D = bd.DrawCircle(x=0, y=0, r=hspan*0.25-line_width*0.5, 
                                  source_rgb=rgb, tags='tag::DrawCircle')
                C.put(trans=crt.Translate(dest=(hspan*0.25, hspan*0.25)),
                      child=D)
            LEAF_LIST.append(D)
            B.put(trans=crt.Translate(dest=(hspan*j, 0)),
                  child=C)
            ## セルオブジェクトC 
            oid += 1    

    #====== Polylineのテスト ==============================
    cr.save() ##
    ## 描画領域オブジェクトA．余白(x=dskip, y=dskip)
    if opt.verbose:
        print(f'@debug: line: hnum, vnum { hnum, vnum  }: ')
    ncol = 0
    for j in range(vnum+1):
        x = hspan*i
        for i in range(hnum+1):
            y = vspan*j
            if opt.verbose:
                print(f'@debug: line at { i,j }: ')
            if i > 0 and j > 0:
                col_ = COLS[(ncol % len(COLS))]
                crt.cr_set_context_parameters(context=cr, rgb=col_, line_width=0.5)
                cr.move_to(hspan*(i-1), vspan*(j-1))
                cr.line_to(hspan*i, vspan*j)
                cr.stroke()
                ncol += 1
    cr.restore()  #描画領域
    #====== Polylineのテスト ==============================

    #============
    #描画: Marker 
    #============
    #====== 描画領域 ==============================
    cr.save()  #描画領域
    

    #テキスト
    x, y, width, height, dx, dy = crt.cr_text_extent(0, 0, msg="rectangles and cirles", context=cr)
    crt.cr_text(0, dy, msg="Rectangles and cirles...", context=cr,
                fontfamily='Times',
                # fontfamily='Palatino',
                )

    #描画領域
    cr.translate(dskip, dskip)

    
    #===== 格子 =======
    cr.save() ## 
    for i in range(vnum): 
        #============
        cr.save() ## 
        for j in range(hnum):
            crt.cr_draw_marker(0, 0, r=2, context=cr,
                                  ffamily="Sans", source_rgb=crt.MYCOL['grey25'])
            cr.stroke()
            cr.translate(hspan, 0) ##
        cr.restore() ## 
        #============
        cr.translate(0, vspan) ##
    cr.restore() ## 
    #===== 格子 =======

    cr.restore()  #描画領域

    # #===== 折れ線 =======
    # cr.save() ##
    # if True:
    #     print(f'@debug: line: hnum, vnum { hnum, vnum  }: ')
    # ncol = 0
    # for j in range(vnum+1):
    #     x = hspan*i
    #     for i in range(hnum+1):
    #         y = vspan*j
    #         if True:
    #             print(f'@debug: line at { i,j }: ')
    #         if i > 0 and j > 0:
    #             col_ = COLS[(ncol % len(COLS))]
    #             crt.cr_set_context_parameters(context=cr, rgb=col_, line_width=0.5)
    #             cr.move_to(hspan*(i-1), vspan*(j-1))
    #             cr.line_to(hspan*i, vspan*j)
    #             cr.stroke()
    #             ncol += 1
    # cr.restore()  #描画領域
    
    # #====== 描画領域 ==============================

    #============
    #印刷
    #============
    CV.show(noshow=opt.noshow)

    #debug
    if opt.verbose: 
        print(f'===== { "printing the object tree..." } ======')
        CV.dump()
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


