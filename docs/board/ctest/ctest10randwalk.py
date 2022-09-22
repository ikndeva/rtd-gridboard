# coding: utf_8
# ctest8cbd.py
# - アンカー点の機構を実装する．
# - 
import sys
from argparse import ArgumentParser
import cairo 
import math
import random 

import common as com 
##
import crtool as crt
import cboard as bd
#import cimage as cim

verbose = True

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
    ## width 
    ap.add_argument('-m', '--numpoints', type=int, default=1, 
                    help='set the number of points')
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
                   boundingbox=opt.boundingbox, 
                   verbose=opt.verbose)

    cr = CV.context()
    #cim = CV.get_image_board() ##ImageBoardオブジェクト
    #cr = cim.context()

    def put_a_marker(x, y, rgb=None): 
        cr.save()
        crt.cr_draw_marker(x, y, r=2, context=cr, rgb=rgb)
        cr.stroke()
        cr.restore()
        return
    
    #====== テスト ==============================
    dskip = 20
    hnum, vnum = 5, 4
    hspan, vspan = 50, 50
    #hsize, vsize = hspan*hnum, vspan*vnum
    hsize, vsize = CV.canvas_size()
    line_width = 2 
    mygrey = crt.MYCOL['grey50']
    ow, oh = hspan*0.5, vspan*0.5
    COLS = list(crt.DARKCOL.values())

    cr.set_line_width(line_width)

    #====== テスト ==============================
    # cboard.Board の構成実験
    LEAF_LIST = [] #オブジェクト木の葉の集合
    
    ## 描画領域オブジェクトA．余白(x=dskip, y=dskip)
    A = bd.Board().add_tag('A').add_tag('panel')
    CV.put(trans=crt.Translate(x=dskip, y=dskip), child=A)

    #A = 
    CV.put(child=bd.DrawRectangle(x=0, y=0, width=hsize, height=vsize,
                                  rgb=crt.MYCOL['red']).add_tag('A1').add_tag('rect'))

    ## 折れ線オブジェクト
    PL = bd.DrawPolyLines(line_width=0.5,
                          rgb=crt.MYCOL['blue'],
                          arrow_head={
                              'head_length': 5, 
                              'head_shape': 'sharp',
                              #'head_shape': 'triangle',
                              #'head_shape': 'stroke',
                              # 'rgb': crt.MYCOL['magenta'], 
                              # 'line_width': 3,
                          }, 
                          # head_shape='sharp',
                          linecap='round', 
                          linejoin='round', 
                          # linecap='square', 
                          # linejoin='miter', 
                          # linecap='butt', 
                          # linejoin='bevel',                          
                          )
    A.put(trans=crt.Translate(x=0, y=0), child=PL)
    MFL = 1.0 #平均自由行程
    #MFL = 0.3 #平均自由行程
    dx, dy = MFL*hspan, MFL*vspan
    if opt.verbose:
        print(f'@debug: line: hnum, vnum { hnum, vnum  }: ')
    x, y = hsize*random.random(), vsize*random.random()
    A.put(trans=crt.Translate(x, y), child=bd.DrawCircle(x=0, y=0, r=5, rgb=crt.MYCOL['magenta']))
    PL.move_to(x, y)
    ncol = 0
    for i in range(opt.numpoints):
        ## 次の点
        x, y = x + dx*(random.random()-0.5), y + dy*(random.random() - 0.5)
        if x > hsize or y > vsize:
            x, y = (x % hsize), (y % vsize)
        col_ = COLS[(ncol % len(COLS))]
        if opt.verbose: 
            print(f'@debug: walk: {i}: { x,y }')
        A.put(trans=crt.Translate(x, y), child=bd.DrawCircle(x=0, y=0, r=1, fill='fill', rgb=crt.MYCOL['red']))
        #put_a_marker(x, y, rgb=crt.MYCOL['lightgreen'])
        PL.line_to(x, y, has_arrow=True,
                   )
        ncol += 1
        
    # if opt.verbose: 
    #     print(f'@debug: line: hnum, vnum { hnum, vnum  }: ')
    # x, y = hspan*random.random(), vspan*random.random()
    # PL.move_to(x, y)
    # ncol = 0
    # for i in range(opt.numpoints):
    #     ## ランダム
    #     x, y = hspan*random.random(), vspan*random.random()
    #     col_ = COLS[(ncol % len(COLS))]
    #     print(f'@debug: walk: {i}: { x,y }')
    #     PL.line_to(x, y)
    #     ncol += 1
        
    #====== Polylineのテスト ==============================

    #============
    #描画: Marker 
    #============
    # #====== 描画領域 ==============================
    # cr.save()  #描画領域
    

    # #テキスト
    # x, y, width, height, dx, dy = crt.cr_text_extent(0, 0, msg="rectangles and cirles", context=cr)
    # crt.cr_text(0, dy, msg="Rectangles and cirles...", context=cr,
    #             fontfamily='Times',
    #             # fontfamily='Palatino',
    #             )

    # #描画領域
    # cr.translate(dskip, dskip)

    
    # #===== 格子 =======
    # cr.save() ## 
    # for i in range(vnum): 
    #     #============
    #     cr.save() ## 
    #     for j in range(hnum):
    #         crt.cr_draw_marker(0, 0, r=2, context=cr,
    #                               ffamily="Sans", source_rgb=crt.MYCOL['grey25'])
    #         cr.stroke()
    #         cr.translate(hspan, 0) ##
    #     cr.restore() ## 
    #     #============
    #     cr.translate(0, vspan) ##
    # cr.restore() ## 
    # #===== 格子 =======

    # cr.restore()  #描画領域

    #============
    #印刷
    #============
    CV.show(noshow=opt.noshow)

    # #debug
    # if opt.verbose: 
    #     print(f'===== { "printing the object tree..." } ======')
    #     CV.dump()
    #     print(f'===========')

    #     print(f'@Applying the local transformation associated to each leaf node to a point p=(0,0)...')
    #     ancestor=CV
    #     if LEAF_LIST and len(LEAF_LIST) > 0:
    #         for idx, leaf in enumerate(LEAF_LIST):
    #             p0=(0.0, 0.0)
    #             # p0=(0.0, 0.0, 1.0, 1.0)
    #             p1 = ancestor.relative_transform(p=p0, target=leaf,
    #                                        verbose=False)
    #             # p0 = ancestor.relative_transform_by_apath(p=(0.0, 0.0), apath=apath)
    #             print(f'LEAF{idx}\tp0={ p0 } at { ancestor.myinfo(depth=True) } => p1={ p1 } at {leaf.myinfo(depth=True)}')
    #             apath = leaf.relative_apath_get(top=ancestor)
    #             tpath = ancestor.relative_apath_to_tpath(apath=apath, verbose=False)
    #             apath1 = [ (obj.myinfo(), ord) for obj, ord in apath ]
    #             print(f'\tapath={ apath1 }')
    #             print(f'\t=> tpath={ [ trans.__str__() for trans in tpath ] }')
    #         print(f'Note that the obtained transformation result is tentative, and wrong, and just for development purpose. This must be reversed. ')
    
    pass 

##EOF


