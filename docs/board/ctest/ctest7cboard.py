# coding: utf_8
# ctest7cboard.py
# - cboardモジュールの再帰的な図像構成のテスト
# - 内部ノードはBoard.put関数を良いて，親版の指定の位置に子版を配置していく．
# - 最終的に葉ノードでは，図形描画オブジェクトを追加する．
# - 各オブジェクトの包含矩形の計算を実装した．
# - put関数： オブジェクトの親から子への属性（depth, verbose）の継承がうまくいっていないバグを解決した．
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
                   imagesize='VGA',
                   portrait=True, 
                   # imagesize='QVGA',
                   boundingbox=opt.boundingbox, 
                   verbose=opt.verbose)

    cr = CV.context()
    #cim = CV.get_image_board() ##ImageBoardオブジェクト
    # cr = cim.context()

    #====== テスト ==============================
    dskip = 20
    hnum, vnum = 6, 5
    hspan, vspan = 50, 50
    line_width = 2 
    mygrey = crt.MYCOL['grey50']
    ow, oh = hspan*0.5, vspan*0.5
    COLS = list(crt.DARKCOL.values())

    #====== テスト ==============================
    ## 描画領域オブジェクトA．余白(x=dskip, y=dskip)
    A = bd.Board(tags='A')
    CV.put(trans=crt.Translate(x=dskip, y=dskip),
           child=A)
    
    ## row
    oid = 0
    for i in range(vnum):
        ## 行オブジェクトB
        B = bd.Board(tags='B::Line')
        A.put(trans=crt.Translate(x=0, y=vspan*i),
              child=B)
        for j in range(hnum):
            C = bd.Board(tags='C::ParentDrawCmd')
            rgb = COLS[oid % vnum ]
            if i % 2 == 0:
                #描画オブジェクトD
                D = bd.DrawRectangle(x=0, y=0, width=oh, height=oh,
                                     source_rgb=rgb, tags='tag::DrawRectangle')
                C.put(trans=crt.Translate(), child=D)
            else:
                #描画オブジェクトD
                D = bd.DrawCircle(x=0, y=0, r=hspan*0.25-line_width*0.5, 
                                  source_rgb=rgb, tags='tag::DrawCircle')
                C.put(trans=crt.Translate(x=hspan*0.25, y=hspan*0.25),
                      child=D)
            B.put(trans=crt.Translate(x=hspan*j, y=0),
                  child=C)
            ## セルオブジェクトC 
            oid += 1
    
    # #====== テスト ==============================
    # ## 描画領域オブジェクトA．余白(x=dskip, y=dskip)
    # A = bd.Board()
    # CV.put(trans=crt.Translate(x=dskip, y=dskip),
    #        child=A)
    
    # ## row
    # oid = 0
    # for i in range(vnum):
    #     ## 行オブジェクトB
    #     B = bd.Board()
    #     A.put(trans=crt.Translate(x=0, y=vspan*i),
    #            child=B)
    #     for j in range(hnum):
    #         rgb = COLS[oid % vnum ]
    #         # rgb = COLS[oid % len(COLS)]
    #         if i % 2 == 0: 
    #             C = bd.DrawRectangle(x=0, y=0, width=oh, height=oh,
    #                                  source_rgb=rgb)
    #         else: 
    #             C = bd.DrawCircle(x=hspan*0.25, y=hspan*0.25,
    #                               r=hspan*0.25-line_width*0.5, 
    #                               source_rgb=rgb)
    #         ## セルオブジェクトC 
    #         B.put(trans=crt.Translate(x=hspan*j, y=0),
    #               child=C)
    #         oid += 1
    
    #====== 描画 ==============================
    
    #============
    #描画: Board
    #============
    cr.set_line_width(line_width)
    
    #====== 描画領域 ==============================
    cr.save()  #描画領域
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

    # #====== 描画領域 ==============================
    # cr.save()  #描画領域
    # dskip = 20
    # cr.translate(dskip, dskip)
    
    # hnum, vnum = 6, 5
    # #マーカーを格子に配置
    # hspan, vspan = 50, 50
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

    # #============
    # #色見本を格子に配置
    # cr.save() ## a region begin
    # bspan = 0.25*hspan
    # cr.save() ## the first line begins
    # i = 0
    # for col, rgb in crt.MYCOL.items():
    #     #============
    #     # セル
    #     cr.save() ## a block begins: cell 
    #     cr.set_source_rgb(rgb[0], rgb[1], rgb[2])
    #     #======
    #     #円
    #     cr.save() ## a block begins: circle
    #     cr.translate(hspan*0.5, vspan*0.5)
    #     cim.arc(0, 0, hspan*0.5 - line_width*0.5,
    #             math.pi*0.0, math.pi*2.0,
    #             source_rgb=rgb, fill='stroke')
    #     cr.restore() ## a block ends: circle 
    #     #======
    #     ## テキストcolname. 下にbspanだけ下げる．
    #     cr.save() ## a block begins: text
    #     crt.cr_set_context_parameters(ffamily="Sans", fsize=10, source_rgb=mygrey, context=cr)
    #     _, _, twidth, theight, _, _ = crt.cr_text_extent(0, 0, msg=f'{ col }', context=cr)
    #     cr.translate(hspan*0.5 - twidth*0.5,
    #                  vspan*0.5 - theight*0.5) #move origin 
    #     crt.cr_text(0, 0, msg=f'{ col }', context=cr)
    #     cr.fill()
    #     cr.restore() ## a block ends: text
    #     #======
    #     cr.restore() ## a block ends: cell
    #     #============
    #     ## 
    #     cr.translate(hspan, 0.0) ## move rightward
    #     i += 1

    #     ## line folding 
    #     if i % (hnum - 1) == 0:
    #         cr.restore() ## a line end 
    #         cr.translate(0.0, 1.0*vspan) ## move downward
    #         cr.save() ## a line begin
    # cr.restore() ## the final line ends 
    # #============

    # cr.restore() ## a region end
    # #============
    
    cr.restore()  #描画領域
    #====== 描画領域 ==============================

    #============
    #印刷
    #============
    CV.show(noshow=opt.noshow)

    #debug
    if opt.verbose: 
        print(f'===== { "printing the object tree..." } ======')
        CV.dump()
        print(f'===========')
    
    pass 

##EOF


