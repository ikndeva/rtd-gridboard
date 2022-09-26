# coding: utf_8
# ctest15side.py
# - サイズ指定図形機構を実装する．
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
    ## margin 
    ap.add_argument('-m', '--margin', type=float, 
                    help='set margin to float in [0,1]')
    ## orient 
    ap.add_argument('-o', '--orient', type=str, 
                    help='set orient to str')
    ## pack 
    ap.add_argument('-p', '--pack', action='store_true', default=False, 
                    help='show verbose messages')
    ## max perturb ratio
    ap.add_argument('-u', '--max_perturb_ratio', type=float, 
                    help='set max_perturb_ratio to positive float. default=8.0')
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
    if opt.max_perturb_ratio==None:
        opt.max_perturb_ratio = 8.0

    # 位置指定による2D配置のテスト
    #画像枠の生成
    CV = bd.Canvas(outfile="out",
                   #imagesize='QVGA',
                   # imagesize='VGA',
                   portrait=False,
                   boundingbox=opt.boundingbox,
                   # max_perturb=bd.DEFAULT_LINE_WIDTH*4.0,
                   max_perturb=bd.DEFAULT_LINE_WIDTH*opt.max_perturb_ratio, 
                   verbose=opt.verbose)
    # cr = CV.context() #Cairo.Context

    #====== テスト ==============================
    uspan = 50 #単位スパン
    line_width = 2 
    
    # uspan = 50 #単位スパン
    dskip = 0.5*uspan
    hspan, vspan = uspan, uspan 
    # hnum, vnum = 5, 4 
    hnum, vnum = 3, 1
    hair_line_width = line_width/2
    mygrey = crt.MYCOL['grey50']
    #ow = uspan 
    # ow, oh = hspan*0.5, vspan*0.5
    COLS = list(crt.DARKCOL.values())

    # cr.set_line_width(line_width)

    if opt.margin: 
        com.ensure(opt.margin >= 0.0 and opt.margin <= 0.5,
                   f'opt.margin={opt.margin} must range between 0.0 to 0.5!')
        m_ratio = opt.margin
    else:
        m_ratio = 0.125
    
    #====== テスト ==============================
    # cboard.Board の構成実験
    LEAF_LIST = [] #オブジェクト木の葉の集合
    
    ## 描画領域オブジェクトA．余白(x=dskip, y=dskip)
    DrawingPanel = CV.put(trans=crt.Translate(dest=(dskip,dskip)),
                          child=bd.Board(shape=(4*uspan,4*uspan), 
                                         tags='DrawingPanel')
                          )

    #exp: ラッパーで包んでから，子リストに加える
    _debug_wrapper = {
        #デバッグ用の包含矩形描画
        'show_box': True,
        # rgb_box=crt.MYCOL['magenta'],
        'rgb_box':  crt.cr_add_alpha(crt.MYCOL['magenta'], alpha=0.5),
        #デバッグ用の原点描画
        'show_origin':  True,
        'angle_origin':  (math.pi/4)*0,
    }
    
    
    #セルの図形
    oid = 1
    C = random.random() #[0,1]の乱数    
    uspan_in = uspan*(1.0 - 2*m_ratio)
    rgb = COLS[oid % 3 ]
    if oid % 2 == 0:
        child = bd.DrawRectangle(width=uspan_in*C, height=uspan_in*C,
                                 source_rgb=rgb,
                                 show_origin=True, 
                )
    else:
        child = bd.DrawCircle(r = 0.5*uspan_in*C, 
                              source_rgb=rgb,
                              show_origin=True, 
                )
    child1 = bd.SideWrapper(child=child,
                            side=(opt.anchor_x, opt.anchor_y),
                            rgb_origin=crt.MYCOL['green'],
                            verbose=True, 
                            **_debug_wrapper, #デバッグ表示用
                            ) 
    child2 = bd.MarginWrapper(child=child1,
                              shape=(2*uspan, 2*uspan), 
                              margin=hspan*m_ratio,
                              rgb_origin=crt.MYCOL['blue'],
                              **_debug_wrapper, #デバッグ表示用
                              ) 
    DrawingPanel.put(child2)
            
#LEAF_LIST.append(D)
#oid += 1
    #===== 図形のテスト ==============================

    #============
    #印刷
    #============
    CV.show(noshow=opt.noshow)

    #debug
    if False and opt.verbose: 
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


