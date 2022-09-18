# coding: utf_8
# 画盤モジュール
# cboard.py
"""画盤モジュール

* 画盤システムの実装モジュール．
* 220815: Created by Hiroki Arimura, arim@ist.hokudai.ac.jp 
* based on board.py 

Attributes: 

DEFAULT_PPT = 720 (int): デフォールトの解像度
DEFAULT_LINE_WIDTH = 1 (float): デフォールトの辺幅
DEFAULT_COLOR_BORDER_INNER = 'red' (str): デフォールトの境界色（内側）
DEFAULT_COLOR_BORDER_OUTER = 'blue' (str): デフォールトの境界色（外側）
"""
import sys
import os 
import math 
import numpy as np
import random 
import copy 
# import inspect
# import cairo 
from typing import NamedTuple

# sys.path.insert(0, os.path.abspath('../board/'))

import common as com
import kwargs as kw
import crtool as crt
import loggable as log 
import backupcaller as bc

# DEFAULT_PPI = 720 
# DEFAULT_LINE_WIDTH = 1 
# DEFAULT_COLOR_BORDER_INNER = 'red'
# DEFAULT_COLOR_BORDER_OUTER = 'blue'
# EMPTY_RECT = ((0,0), (0,0))

## PARAMS 2022 version
EMPTY_RECT = (0.0, 0.0, 0.0, 0.0)
MYCOLS = list(crt.DARKCOL.values())
#MYCOLS = list(crt.MYCOL.values())
DEFAULT_LINE_WIDTH=1

# 辞書（語彙）

## 画像サイズ
DISPLAY_SHAPE = {
    'QVGA': (320, 240),
    'VGA' : (640, 480), 
    'SVGA': (800, 600), 
    'XGA' : (1024, 768), #default size
    'WXGA': (1280, 800), 
    'UXGA': (1600, 1200), 
    'QXGA': (2048, 1536),
}
DEFAULT_IMAGE_SIZE='XGA'

# #constants
# CMD_MOVE = 0
# CMD_LINE = 1

def perturb_point(x=0.0, y=0.0, max_perturb=0.0):
    """与えられた点 (x, y) に対して，幅
    [(-1)*max_perturb, (+1)*max_perturb] 
    の摂動を与えた点(x1, y1)を返す．
    Args: 
      x, y (float) : 入力点のx- and y-coordinates．デフォールト値 x = y = 0.0

    Returns: 
         x1, y1 (float) : 摂動を加えた点のx- and y-coordinates

    Notes: 
         xとyが省略されたときは，値0.0, 0.0を中心とした摂動を返す．
    """
    if max_perturb==0.0:
        print(f'warning: cboard.perturb_point: max_perturb==0.0!')
    x1 = x + max_perturb*random.random()
    y1 = y + max_perturb*random.random()
    return x1, y1


#=====
# 画盤（board）のクラス: 座標系オブジェクト
#=====
# class Board(com.Loggable):
class BoardBase(log.Loggable):
    """画盤（board）のクラス: 座標系オブジェクト

    Args: 
         **kwargs : 他のキーワード引数．上位クラスに渡される．

    Attributes: 
         verbose (bool): ログ出力のフラグ

    """

    count = 0 #board id

    def __init__(self, **kwargs):
        """画盤オブジェクトを初期化する
        """
        #引数
        #親Loggableの初期化
        super().__init__(**kwargs)
        
        #内部変数
        
        
        ##自身の配置情報
        self.trans_self = None #自身の変換
        self.box_self   = None #自身の包含矩形.
        # self.boxes_   = None #デバグ用_元の包含矩形.
        
        if self.verbose:
            self.repo(msg=f'{self.myinfo()}.__init__(): { self.vars() }')
        return

    # # exp 基本：子を追加する
    # def put(self, child=None, trans=None): 
    #     """子を追加する．

    #     Args: 
    #         trans (cairo.Matrix) : 自座標における子の配置を指示する変換行列．原点にある子を所望の場所に配置するためのアフィン変換を表す．

    #         child (Board): 子として追加するBoardオブジェクト

    #     Returns:
    #         (Board) : 追加した子
        
    #     Example:: 
        
    #     		root = Canvas()
    #     		child = root.put(Board())
    #     		child = parent.put(trans=Translate(x=1, y=2), 
    #     			Rectangle())
    #     """
    #     def _vars_put_(board=None):
    #         return kw.extract(kwargs=vars(board),
    #                           keys=['cmd','depth','verbose'])
    #     #子の型チェック
    #     com.ensure(child != None and isinstance(child, BoardBase),
    #                f'{self.myinfo()}.put(): child must be a BoardBase!: {child}') 
    #     # 親子関係の管理
    #     self.register_child(child)

    #     # 子を追加する
    #     if self.max_children_ >= 0 and len(self.children_) >= self.max_children_:
    #         com.panic(f'cannot add more than max_children_={self.max_children_}!')
    #     else:
    #         child.ord_ = len(self.children_)      #子ID
    #         self.children_.append((trans, child)) #子リスト

    #     #
    #     if self.verbose: self.repo(msg=f'=> added: {self.myinfo()}.put(): trans={trans} child={ child } with vars={ child.vars() }...')
        
    #     return child #Do not change!

    
    #=====
    # 雑関数
    #=====

    def get_box(self):
        box = self.box_self
        com.ensure(box==None or crt.isProperBox(box),
                   f'get_box: box must be isProperBox')
        return box


    # exp 基本：配置の計算
    def _arrange(self):
        """配置を計算する．配置は，ボトムアップに再帰的に計算される．

        Returns: 
        	rect: 計算済みの自身の包含矩形オブジェクト
        """
        if self.verbose:
            self.repo(msg=f'{self.myinfo()}._arrange(): { self.vars() }')

        #子供全ての包含長方形を計算する
        boxes = EMPTY_RECT
        
        #自身の描画配置情報を得る
        box0 = self.arrange_me()
        boxes = crt.box_union(boxes, box0) #包含矩形の更新
        
        # for idx, pair in enumerate(self.children()):
        for idx, pair in self.children_enumerated():
            trans, child = pair #分解
            #子の型チェック
            com.ensure(isinstance(child, BoardBase),
                       'child must be a subclass of BoardBase!: {child}')
            if trans:
                com.ensure(isinstance(trans, crt.GeoTransform),
                           f'trans must be of crt.GeoTransform: {type(trans)}')
            if self.verbose:
                self.repo(msg=f'=> calling on {idx}-th child={child.myinfo()}',
                          isChild=True, header=False)
                
            #子の再帰処理
            child_box = child._arrange()
                
            #自身の包含矩形の更新
            if child_box:
                child_box = crt.box_apply_trans(child_box, trans=trans)
                boxes = crt.box_union(boxes, child_box) #包含矩形の更新
            
        #子のパック処理をする
        boxes = self._arrange_pack(boxes)
        
        #注意：関数arrange_self_transformはサブクラスでオーバーライドする
        #デフォールト: self.trans_self = None, self.box_self := boxes
        self.trans_self, self.box_self = self.arrange_anchor(boxes)

        #自身の描画配置情報を得る．包含矩形の処理は自身の責任で行う．
        #次の情報を更新できるので注意: self.box_self, self.box_trans
        self.arrange_me_post()
        
        if True:
            print(f'@debug:trans:{self.myinfo()}: trans={self.trans_self}')
        if self.verbose:
            self.repo(msg=f'{self.myinfo()}._arrange()=> box={ boxes }', isChild=True)
        return self.box_self 

    # #To be Override
    # def arrange_me(self):
    #     """自分の座標系で配置を計算する．子孫クラスでオーバーライドすること"""
    #     box = None
    #     return box

    #Override 
    def arrange_me(self):
        width = kw.get(self.kwargs, 'width')
        height = kw.get(self.kwargs, 'height')
        box = None 
        if width!=None and height!=None: 
            x = kw.get(self.kwargs, 'x', default=0)
            y = kw.get(self.kwargs, 'y', default=0)
            box = (x, y, x+width, y+height)
        return box 

    #To be Override
    def _arrange_pack(self, boxes_last=None, **kwargs):
        """自分の座標系で配置を計算する．子孫クラスでオーバーライドすること"""
        return boxes_last
        
    #To be Override
    def arrange_me_post(self):
        """自分の座標系で配置を計算する．子孫クラスでオーバーライドすること"""
        box = None
        return box 
        
    #To be Override
    def arrange_anchor(self, box):
        """アンカー情報から，変換と包含矩形を計算する．子孫クラスでオーバーライドすること"""
        trans = None #identity
        return trans, box
        
    # #Override
    # def arrange_modify_child(self, trans, child, child_box):
    #     """変換と，子ボード，子の包含矩形から，更新した変換と子ボードを返す．上書きすること．
    #     """
    #     ##必要ならここで何かする．とりあえず，そのまま返す．
    #     return trans, child

    #=====
    # 描画
    #=====
    def _draw(self, cr):
        """トップダウンに画像を描画する．

        Args: 
             trans (crt.GeoTransform) : 空間変換

             pm0 (pim.ImageBoard) : 基本描画のプリミティブボード
        """
        if self.verbose:
            self.repo(isChild=True, msg=f'{self.myinfo()}._draw(): { self.vars() }')
            
        ## 自分の空間を開く
        cr.save()  ##self
        ## 自身の変換を適用する
        crt.cr_apply_trans(trans=self.trans_self, context=cr)
        if True: print(f'@debug:draw:self:{self.myinfo()}: apply trans_self={self.trans_self}')
            
        #必要なら自分の描画を行う
        self.draw_me(cr)
        
        #子の描画を行う
        for idx, pair in self.children_enumerated():
            trans, child = pair #分解
            #子の型チェック
            com.ensure(isinstance(child, BoardBase),
                       f'{self.myinfo()}.draw: child must be a subclass of BoardBase!: {child}'+
                       f': children_={self.children_}')
            
            cr.save()    ## 子の空間を開く
            crt.cr_apply_trans(trans=trans, context=cr) ## 変換を適用する
            if True: print(f'- @debug:draw:child:{child.myinfo()}: apply trans={trans}')
            child._draw(cr)
            cr.restore() ## 子の空間を閉じる

        #必要なら自分の描画を行う
        self.draw_me_post(cr)

        ## 自分の空間を閉じる
        cr.restore()  ##self

        ## debug: 包含矩形を描画する
        if self.fetch(key='boundingbox', default=False) and crt.isBoxOrPoint(self.get_box()):
            if self.verbose: self.repo(msg=f'@option boundingbox: draw my box={ self.get_box() }', isChild=True)
            self.draw_perturbed_box(self.get_box(), context=cr)

        # debug: 自分の原点位置をマーカーで描画する．
        if kw.get(self.kwargs, key='show_origin', default=False):
            rgb = kw.get(self.kwargs, key='rgb_origin',
                         default=crt.MYCOL['red'])
            angle = kw.get(self.kwargs, key='angle_origin',
                         default=math.pi/4)
            crt.cr_draw_marker_cross(context=cr, x=0,y=0,
                                     linewidth=0.5, angle=angle, 
                                     rgb=crt.cr_add_alpha(rgb, alpha=0.5))
        # debug: 自分の原点位置をマーカーで描画する．
        if kw.get(self.kwargs, key='show_box', default=False):
            rgb = kw.get(self.kwargs, key='rgb_box',
                         default=crt.MYCOL['green'])
            (x0, y0, x1, y1) = self.get_box()
            crt.cr_rectangle(x0, y0, x1 - x0, y1 - y0,
                             context=cr,
                             rgb=crt.cr_add_alpha(rgb, alpha=0.5), 
                             line_width=1)
        return

    # 派生：Override
    def draw_me(self, cr):
        """自分の描画を行う．子孫クラスでオーバーライドすること．

        Args: 
             cr (Cairo.Context) : Cairoの文脈オブジェクト
        """
        if self.verbose: self.repo(isChild=True, msg=f'{self.myinfo()}.draw_me()...')
        ## ここでcontext crに何か描く．
        return 

    # 派生：Override
    def draw_me_post(self, cr):
        """自分の描画を行う．子孫クラスでオーバーライドすること．

        Args: 
             cr (Cairo.Context) : Cairoの文脈オブジェクト
        """
        if self.verbose: self.repo(isChild=True, msg=f'{self.myinfo()}.draw_me()...')
        ## ここでcontext crに何か描く．
        return

    #=====
    # おまけ関数．drawの副関数
    #=====
    def draw_perturbed_box(self, box, context=None, max_perturb=None):
        """位置を
        """
        cr = context 
        box = crt.box_normalize(self.get_box())
        x, y = box[0], box[1]
        width, height=(box[2]-box[0]), (box[3]-box[1])
        ## 色を選ぶ
        rgb = MYCOLS[0]  ## 色
        rgb_alpha = 0.25 ## 色の透明度
        # rgb_alpha = 0.5
        if self.depth: 
            rgb = MYCOLS[self.depth % len(MYCOLS)]  ## 色
            rgb = (rgb[0], rgb[1], rgb[2], rgb_alpha)
        else:
            if self.verbose: print(f'debug: self.depth=None at { self.myinfo() }')
        ## 位置を微小変動させる
        max_perturb = self.fetch(key='max_perturb', default=8.0 * DEFAULT_LINE_WIDTH)
        com.ensure(max_perturb != None, f'max_perturb={max_perturb} must be defined!')
        dx = dy = max_perturb*random.random() - 0.5*max_perturb 
        crt.cr_rectangle(x + dx, y + dy, width, height,
                         source_rgb=rgb,
                         line_width=1,
                         context=cr)
        
        ## キャプション
        tx, ty = x + dx, y + dy
        fsize = 4
        fmargin = 0.25*fsize
        msg = self.myinfo()
        x, y, width, height, dx, dy = crt.cr_text_extent(tx, ty, msg=msg, context=cr)
        crt.cr_text(tx + fmargin, ty + 1.0*dy + fmargin, msg=msg, fsize=fsize, 
                    context=cr)

        return 

    #==========
    # 座標系
    #==========
    def get_anchor_point(self, anchor_x=None, anchor_y=None, anchor=None):
        """アンカー指定から，自身の包含矩形上の対応する点を返す．

        Args: 

             anchor_x (str) : 横方向の位置指示 in (left, middle, right)

             anchor_y (str) : 縦方向の位置指示 in (top, middle, bottom, above, below)

             anchor (str) : 代替の位置指示．内容に応じて横または縦の位置表示として用いる．ただし，anchor_xまたはanchor_yを優先し，両方設定しようとするとエラーを呼ぶ．

        Returns: 

             (tuple(float, float)) : アンカー点(x,y)
        """
        ## exp: アンカー情報を用いて，変換transを求める
        
        # アンカーキーワードから，アンカー比率を返す．
        ratio_x, ratio_y = crt.get_anchor_ratio(anchor_x=anchor_x, anchor_y=anchor_y, anchor=anchor)
        com.ensure(self.get_box() != None, f'self.box_self is None!')
        x, y = crt.get_point_by_anchor_ratio(self.box_self, ratio_x=ratio_x, ratio_y=ratio_y)
        com.ensure(isinstance(x, (float, int)) and
                   isinstance(y, (float, int)),
                   f'x={x} and y={y} must be numbers')
        return x, y

    pass ## end class BoardBase 


    #==========
    # 外部アクセス: exp
    #==========
    def relative_apath_get(self, top=None, cid=None, apath=None, hgt=0):
        """基準オブジェクトから自身へのアクセスパス（子添字列）を返す．
        Args: 
          top (BoardBase) : 基準オブジェクト．このBoardBaseか根へ到達すると停止する．
        Returns: 
          (list(int)) : 成功すれば，基準オブジェクトから自身へのアクセスパス（子添字列）．失敗すればNone
        Note: 
          仮定：self.depth==Noneの場合は，全ての子孫のdepth==None
        """
        com.ensure(top!=None, f'top must not be None!')
        if apath==None:
            apath=[]
        apath.append((self, cid))
        pa = self.parent
        if self==top: 
            apath.reverse() #return None
            return apath
        elif pa==None or (not isinstance(pa, BoardBase)):
            return None 
        else:
            return pa.relative_apath_get(top=top, cid=self.ord_, apath=apath, 
                                      hgt=hgt+1)
    
    def relative_apath_to_tpath(self, apath=None, tpath=None,
                                verbose=False):
        """点p=(x,y)を，アクセスパスapath=((), ..., ())

        Args: 
             p (tuple) : 点p=(x,y) or 矩形p=(x0, y0, x1, y1)

             apath (list) : (ord, board)のリスト．最初の要素はord=None
        """
        if verbose: print(f'debug: call apath={apath} \t tpath={tpath}')
        if tpath==None:
            tpath=[]
            
        if apath==None or len(apath)==0: 
            return tpath
        
        node, ord = apath[0]
        com.ensure(isinstance(node, BoardBase), f'node must be of BoardBase type!')
        if ord==None:
            if verbose: print(f'\tdebug: last element!')
            return tpath
        elif not (ord < len(node.children_)):
            com.panic(f'ord={ord} is out of range!:'+
                      f' num children={ len(node.children_) }')
        else: 
            trans, child = node.children_[ord]
            tpath.append(trans)
            if verbose:
                print(f'\tdebug: visit { (node.myinfo(), ord) } => { trans } tpath={tpath}')
            apath1 = apath[1:]
            return child.relative_apath_to_tpath(apath=apath1, tpath=tpath, verbose=verbose)
    
    def relative_apply_transform_by_apath(self, p=None, apath=None,
                                          verbose=False):
        """点p=(x,y)を，アクセスパスapath=((), ..., ())

        Args: 
             p (tuple) : 点p=(x,y) or 矩形p=(x0, y0, x1, y1)

             apath (list) : (ord, board)のリスト．最初の要素はord=None
        """
        if len(apath)==0:
            com.panic(f'- empty list; It must not reach!')
        else:
            x, ord = apath[0]
            com.ensure(isinstance(x, BoardBase), f'x must be of BoardBase type!')
            com.ensure(self==x, f'condition self==apath[0][0] must hold!')
            if verbose:
                print(f'\tdebug: relative_transform_point_by_apath: p={ p }\tapath[0]={ (x, ord) }')
            if ord==None:
                if verbose: print(f'- last element; return p={ p }!')
                return p
            elif not (ord < len(x.children_)):
                com.panic(f'ord={ord} is out of range!:'+
                          f' num children={ len(x.children_) }')
            else: 
                trans, child = x.children_[ord]
                if crt.isBoxOrPoint(p):
                    if (len(p) == 2):
                        p1 = trans.apply_point(p[0], p[1])
                        # p1 = crt.apply_trans_point(p, trans=trans)
                    elif (len(p) == 4):
                        p1 = crt.box_apply_trans(p, trans=trans)
                        # p1 = crt.box_apply_trans(p, trans=trans)
                    else:
                        panic(f'p={p} must be either a point or a box!')
                apath1 = apath[1:]
                return child.relative_apply_transform_by_apath(p1, apath1, verbose=verbose)
   
    def relative_transform(self, p=None, target=None, verbose=False):
        """自身の子孫であるBoardBaseオブジェクトtargetの座標系における，
        点p=(x,y)の局所座標を返す，

        Args: 
             target (BoardBase) : 自身の子孫であるBoardBaseオブジェクト

             p (tuple) : 点p=(x,y)

        Notes: 
          apath (list) は，selfからtargetへのアクセスパスであり，
          (board, ord)のリスト．
          - 末尾以外の要素boardについて，その子はboard.chidren_[ord]であり，
          - 末尾要素boardに対してはord=Noneである．
        """
        apath = target.relative_apath_get(top=self)
        if verbose: 
            self.repo(msg=f'relative_transform_point: apath={ [ (obj, ord) for obj, ord in apath ] }')
        return self.relative_apply_transform_by_apath(p=p, apath=apath,
                                                      verbose=verbose)
    
#=====
# ボードの実装クラス
#=====
class AnchorBoard(BoardBase):
    """画盤オブジェクトのクラス．BoardBaseのラッパー．

    Args: 
         anchor_x (str) : 横方向の位置指示 in (left, middle, right)

         anchor_y (str) : 縦方向の位置指示 in (top, middle, bottom, above, below)

         anchor (str) : 代替の位置指示．内容に応じて横または縦の位置表示として用いる．ただし，anchor_xまたはanchor_yを優先し，両方設定しようとするとエラーを呼ぶ．

         **kwargs : 他のキーワード引数．上位クラスに渡される．
    """
    
    def __init__(self, anchor_x=None, anchor_y=None, anchor=None, **kwargs):
        #引数
        super().__init__(**kwargs)
        
        #アンカーのデフォールト設定
        self.anchor_x = com.ensure_defined(anchor_x, default='left')
        self.anchor_y = com.ensure_defined(anchor_y, default='top')
        self.anchor = anchor
        #内部変数
        self.anchor_ratio_x = None
        self.anchor_ratio_y = None
        self.anchor_trans = None
        
        if self.verbose:
            self.repo(msg=f'{self.myinfo()}.__init__(): { self.vars() }')
        return

    #To be Override
    def arrange_anchor(self, box_native):
        """アンカー情報から，変換と包含矩形を計算する．子孫クラスでオーバーライドすること"""
        ## exp: アンカー情報を用いて，変換transを求める
        
        # アンカーキーワードから，アンカー比率を返す．
        if (self.anchor_x == None and
            self.anchor_y == None and
            self.anchor == None):
            trans, box = None, box_native
        else:
            self.anchor_ratio_x, self.anchor_ratio_y = \
                crt.get_anchor_ratio(anchor_x=self.anchor_x,
                                     anchor_y=self.anchor_y,
                                     anchor=self.anchor)
        
            x, y = crt.get_point_by_anchor_ratio(box_native,
                                                 ratio_x=self.anchor_ratio_x,
                                                 ratio_y=self.anchor_ratio_y)
            com.ensure(isinstance(x, (float, int)) and
                       isinstance(y, (float, int)),
                       f'{self.myinfo()}.arrange_me_post:'+
                       f' x={x} and y={y} must be numbers')
            trans = crt.Translate(0.0 - x, 0.0 - y) ##新しい変換
            
            ##新しい変換で包含矩形を変換する
            box = crt.box_apply_trans(box_native, trans=trans)
            if True: print(f'@debug:arrange_self_transform:{self.myinfo()}: ratio={ self.anchor_ratio_x, self.anchor_ratio_y } => x,y={x,y} trans={self.trans_self}: box0={box_native} => box={box}')
        
        return trans, box

    pass ##class AnchorBoard
        
#=====
# ボードのインタフェースのクラス
#=====
#class Board(PackerBoard):
class Board(AnchorBoard):
    """画盤（board）のクラス．`AnchorBase`のラッパー．

    Args: 
          **kwargs : 他のキーワード引数．上位クラスに渡される．
    """
    def __init__(self, **kwargs):
        """画盤オブジェクトを初期化する
        """
        #引数
        super().__init__(**kwargs)
        if self.verbose:
            self.repo(msg=f'{self.myinfo()}.__init__(): { self.vars() }')
        return

#======
#基盤画像系: exp 
#======
class Canvas(Board):
    """トップレベルのボードのクラス．描画のためのCairoのSurfaceを保持する．
    描画対象のすべての要素（ボード）は，本オブジェクトの子孫として保持する．


    Args: 
          imgtype (cairo.Format) : Surfaceフォーマット (default: cairo.FORMAT_ARGB32)

          format (str) : 出力ファイルフォーマット（拡張子 pdf, png）default: "pdf"

          outfile (str) : 出力ファイル名（拡張子を除く）default: "out"

          imagesize (str) : 初期の画像サイズ. default: 'XGA'        

          verbose (bool): ログ出力のフラグ．default=False    

          portrait (bool) : 画像サイズが縦長か？

          boundingbox (bool)  : デバッグ用: 包含矩形のデバッグ出力をする

          max_perturb (float) : デバッグ用: 包含矩形の摂動幅
    """
    # background (string): 背景色．デバッグ用．default='skyblue', #debug
    def __init__(self,
                 imgtype=cairo.FORMAT_ARGB32, #cairoのSurface format
                 format="pdf",   #出力ファイルフォーマット（拡張子 pdf, png）
                 outfile="out",  #出力ファイル名（拡張子を除く）
                 imagesize='XGA',#初期の画像サイズ
                 portrait=None, #画像サイズが縦長か？
                 ## for debugging
                 boundingbox=False, #デバッグ用: 包含矩形のデバッグ出力をする
                 max_perturb=None,  #デバッグ用: 
                 # show_origin=None,  #デバッグ用: 
                 **kwargs):
        """トップレベルのボードを生成する．描画のためのCairoのSurfaceを保持する．
        """
        #基礎クラスの生成子
        super().__init__(dep_init=0, **kwargs) 
        #パラメータ
        self.imgtype   = imgtype
        self.format    = format
        self.outfile   = outfile
        self.imagesize = imagesize
        self.portrait  = portrait
        self.boundingbox = boundingbox #fetchで子孫からアクセス
        self.max_perturb = max_perturb #fetchで子孫からアクセス
        # self.show_origin = show_origin #fetchで子孫からアクセス
        verbose = kw.get(kwargs, key='verbose', default=False)

        ##属性
        self.im    = None   #基礎画像オブジェクト．遅延生成
        self.display_size = None
        # self.verbose = verbose 
        
        if verbose: 
            self.repo(msg=f'{self.myinfo()}.__init__(): vars={ self.vars() }')

        #基底描画オブジェクトの生成
        if self.format: #cairoのformatが与えられていたら，直ちに基底画像pimを生成
            #画像フォーマット
            com.ensure(format, f'format must be defined!')
            if self.verbose: 
                self.repo(msg=f'.create_pim: format={ format }')

            #display_sizeの設定
            ##画像サイズ
            if (self.imagesize == None) or (not (self.imagesize in DISPLAY_SHAPE)):
                self.imagesize = DEFAULT_IMAGE_SIZE
            xsize_, ysize_ = DISPLAY_SHAPE[self.imagesize]
            if self.portrait: #縦長
                self.display_size = (ysize_, xsize_)
            else: #横長
                self.display_size = (xsize_, ysize_)
                
            self.im = crt.ImageBoard(
                # dep_init=self.depth+1, 
                format=format, 
                outfile=outfile,
                display_size=self.display_size, 
                verbose=self.verbose, 
            )  ##ImageBoardの生成
            self.im.depth=self.depth+1
        return 
        
    #=====
    # 基底描画系の生成
    #=====

    def canvas_size(self):
        return self.display_size

    # 基本：画像を表示する
    def show(self, noshow=False, depth=0):
        """配置と描画を行ない，画像をディスプレイに表示する．
        次の手順で描画する．

        - ステップ1: 再帰的に子オブジェクトへ _arrange() 命令を送り，ボトムアップに配置の包含矩形 box を計算する
        - ステップ2: 包含矩形情報 box を元に，self.create_pim() 命令を発行して，pillowの画像盤 self.im を生成する．
        - ステップ3: 再帰的に draw() 命令を発行して，トップダウンに描画を行う
        - ステップ4: 自身のもつpillowオブジェクト self.imに show() 命令を送り，画像を表示する
        """
        if self.verbose:
            self.repo(msg=f'{self.myinfo()}.show(): { self.vars() }')
        
        #ステップ1: ボトムアップに配置を計算する
        box = self._arrange()
        com.ensure(box, 'self.shape_pt must be defined!')

        #ステップ2: トップダウンに描画を行う
        cr = self.im.context()
        self._draw(cr)
        
        #ステップ3: 画像を表示する
        self.im.show(noshow=noshow)  ##pilimage.ImageBoard
        # self.im.show(noshow=noshow, depth=depth)  ##pilimage.ImageBoard
        return

    #Cairo.contextオブジェクトの返却
    def context(self): 
        """Cairo.contextオブジェクトを返す．"""
        return self.im.context()  ##Cairo.contextオブジェクト
            
    # 画像をファイルに保存する
    def save(self, imgfile, **kwargs):
        """imgfile: 保存する画像ファイルの名前．"""
        self.im.save(imgfile=imgfile, **kwargs)
        return

#=====
# ラッパーのクラス
#=====
class WrapperBoard(BoardBase):
    """ラッパーのクラス．唯一の子をもち，指定された以外のメソッド呼び出しを子に転送する．

    Args: 
          **kwargs : 他のキーワード引数．上位クラスに渡される．

    Attributes: 
        verbose (bool): ログ出力のフラグ
    """
    def __init__(self, child=None, **kwargs):
        """画盤オブジェクトを初期化する
        """
        #引数
        #親Loggableの初期化
        super().__init__(max_children=1, #Can have at most one child
                         **kwargs)
        com.ensure(child != None, f'child must be to None!')
        self.put(trans=None, child=child)   #子に追加
        self.the_child = child  #転送先オブジェクト
        #内部変数
        if self.verbose:
            self.repo(msg=f'{self.myinfo()}.__init__(): { self.vars() }')
        return

    # Override exp 基本：配置の計算
    def _arrange(self):
        """配置を計算する．配置は，ボトムアップに再帰的に計算される．

        Args: 

        Returns: 
        	rect: 計算済みの自身の包含矩形オブジェクト
        """
        if self.verbose:
            self.repo(msg=f'{self.myinfo()}._arrange(): { self.vars() }')

        for idx, pair in self.children_enumerated():
            trans, child = pair #分解
            #子の型チェック
            com.ensure(isinstance(child, BoardBase),
                       'child must be a subclass of BoardBase!: {child}')
            #子の再帰処理
            child_box = child._arrange()
            x0, y0, x1, y1 = child_box
			
			#自身の包含矩形とアンカーを，左上を原点にそろえて，正規化する．
            self.trans_self = crt.Translate((-1)*x0, (-1)*y0)
            self.box_self = crt.box_apply_trans(child_box, trans=self.trans_self)
                
        if self.verbose:
            self.repo(msg=f'{self.myinfo()}._arrange()=> box={ boxes }', isChild=True)
        return self.box_self 

    #=====
    ## メソッド転送
    #=====
    def __getattr__(self, name):
        """メソッドが未定義のとき，呼び出される特殊関数．
		未定義の属性呼び出しのときも呼ばれるので注意．
        """
        if self.verbose:
            print(f'\t@WrapperBoard: method="__getattr__" is called')
        return bc.BackupCaller(self.the_child, name, verbose=True)

    #=====
    # 子のリスト
    #=====
    
#=====
# ボードの実装クラス
#=====
# class PackerBoard(AnchorBoard):
class PackerBoard(Board):
    """画盤（board）のクラス．Boardのサブクラス

    Args: 
         align (str) : 並べる主軸方向の指定．`x`または`y`の値をとる．default='x'

         margin_x (float) : 子セルそれぞれの周囲のx方向の余白．default=None．

         margin_y (float) : 子セルそれぞれの周囲のy方向の余白．default=None

         margin (float) : 子セルそれぞれの周囲のx方向とy方向の余白．default=None, 

         pack_anchor (str) : 主軸方向の子のアンカー指定．引数`align`が，`x`の場合は`y`方向の子のアンカー指定については，alignの値`(True, False)`に従って，次のように強制される．

             + パックする場合(pack==True)は，先頭から詰めて配置するため，先頭寄せにする．
             + パックしない場合(pack==False)は，両側が均等に空くように中央寄せにする 

         expand (bool) : 子を拡張するかどうかのフラグ．default=False. もし`expand=True`の場合は，主軸方向のサイズが定義されている必要がある．具体的には，次の制約を満たすこと．
    
             + `align=='x'`ならば`width != None`を満たすこと．
             + `align=='y'`ならば`height != None`を満たすこと．

         width (float) : 自身の幅．default=None. 

         height (float) : 自身の高さ．default=None. 

    	 kwargs : 他のキーワード引数．上位クラスに渡される．
    """
    def __init__(self,
                 align='x',
                 # pack=False,
                 margin_x=None, 
                 margin_y=None, 
                 margin=None, 
                 pack_anchor=None,
                 ##
                 expand=False,
                 width=None,
                 height=None, 
                 **kwargs):
        #引数
        super().__init__(**kwargs)
        #内部変数
        self.align = align
        ## マージン設定
        self._set_margin_x_and_y(margin, margin_x, margin_y) 
        self.pack_anchor = pack_anchor
        # self.pack_anchor_x = None 
        # self.pack_anchor_y = None
        #size
        self.width =width
        self.height=height
        #expand
        self.expand=expand
        if self.expand:
            if align in ('x'):
                com.ensure(self.width!=None, f'align=x: width==None!')
            else:
                com.ensure(self.height!=None, f'align=y: height==None!')
        
        #debug
        self.pack_done = False
                        
        if self.verbose:
            self.repo(msg=f'{self.myinfo()}.__init__(): { self.vars() }')
        return

    def _set_margin_x_and_y(self, margin=None, margin_x=None, margin_y=None):
        """マージン設定"""
        _margin = com.ensure_defined(value=margin, default=0.0)
        if self.align in ('x'): 
            self.margin_y = margin_y
            self.margin_x = com.ensure_defined(value=margin_x, default=_margin)
        else: ## self.align in ('y'): 
            self.margin_x = margin_x
            self.margin_y = com.ensure_defined(value=margin_y, default=_margin)
        return 
    
    # exp 基本：子を追加する
    def add(self, child=None): 
        """子を追加する．関数`BoardBase.put(child, trans=None)`へのラッパー関数．

        Args: 
            child (Board): 子として追加するBoardオブジェクト

        Returns:
            (Board) : 追加した子
        
        Example::
        
        		root = Canvas()
        		parent= root.put(Board())
        		child = parent.add(Rectangle())
        		child = parent.add(Circle())
        """
        com.ensure(child != None, f'child must be to None!')
        print(f'@debug: self={self.myinfo(depth=True)} child={child.myinfo(depth=True)}')
        wrapper = WrapperBoard(child=child)
        return self.put(trans=None, child=wrapper)

    # 基本：子画盤の並びを返す
    ##Override
    def children_box_enumerated(self):
        """添字とエントリの対`idx, triple`の並び children を返す．
        現在は，`triple`は，三つ組`trans, child, child_box`である．必要なら部分クラスで上書きする．

        Returns: 
             (list): 三つ組`trans (GeoTransform)`, `child (BoardBase)`, child_box (tuple(float,float,float,float))`のリスト．
          
        Notes: 
          
              ただし，childはNoneでないことを保証し，そうでないときはErrorを投げる．
              transとchild_boxはNoneでも良い．
          """
        idx = 0
        for trans, child in self.children_:
            #子の型チェック
            com.ensure(isinstance(child, BoardBase),
                       'child must be a subclass of BoardBase!: {child}')
            child_box = child.get_box()
            triple = trans, child, child_box
            yield idx, triple
            idx += 1

    def _accumulate_boxes(boxes): 
        """包含矩形のリストを受け取り，要素である包含矩形を走査して，
        サイズの最大と総和を求める副関数
        
        Args: 
             boxes (list(Box)) : 包含矩形の並び（リスト or iterator）

        Returns: 
             MAXSZ (tuple(float, float)) : 矩形のx-とy-サイズの最大値の対
             SUMSZ (tuple(float, float)) : 矩形x-とy-のサイズの総和の対
             NUM (int) : 矩形の数
        """
        MAXSZ = [0, 0] #サイズの最大値
        SUMSZ = [0, 0] #サイズの総和
        NUM = 0
        # for idx, triple in self.children_box_enumerated():
        for idx, triple in boxes:
            trans, child, child_box = triple #分解
            com.ensure(child_box != None,
                       f'child_box={child_box} must be non-None')
            #子の包含矩形の最大サイズを更新
            cwidth0, cwidth1  = crt.box_shape(child_box)
            MAXSZ[0], MAXSZ[1] = max(MAXSZ[0],cwidth0), max(MAXSZ[1],cwidth1)
            SUMSZ[0], SUMSZ[1] = SUMSZ[0] + cwidth0, SUMSZ[1] + cwidth1
            NUM += 1
        return MAXSZ, SUMSZ, NUM

    # def _accumulate_boxes(self): 
    #     """子の包含矩形のサイズの最大と総和を求める副関数"""
    #     MAXSZ = [0, 0] #サイズの最大値
    #     SUMSZ = [0, 0] #サイズの総和
    #     num_children = 0
    #     for idx, triple in self.children_box_enumerated():
    #         trans, child, child_box = triple #分解
    #         com.ensure(child_box != None,
    #                    f'child_box={child_box} must be non-None')
    #         #子の包含矩形の最大サイズを更新
    #         cwidth0, cwidth1  = crt.box_shape(child_box)
    #         MAXSZ[0], MAXSZ[1] = max(MAXSZ[0],cwidth0), max(MAXSZ[1],cwidth1)
    #         SUMSZ[0], SUMSZ[1] = SUMSZ[0] + cwidth0, SUMSZ[1] + cwidth1
    #         num_children += 1
    #     return MAXSZ[0], MAXSZ[1], SUMSZ[0], SUMSZ[1], num_children

    def _sub_child_dup(self, child_new, child, width=None, height=None): 
        child_new.ord_ = child.ord_
        child_new.box_self = (0, 0, width, height)
        child_new.anchor_x = child.anchor_x
        child_new.anchor_y = child.anchor_y
        child_new.anchor = child.anchor
        return

    #To be Override
    def _arrange_pack(self, boxes_last=None,
                      # expand=False, 
                      # max_length=None,
                      **kwargs):
        """実装関数．自身と子の描画配置情報を計算する．Boardクラスの同名関数のオーバーライド．

        Args: 

        Note: 

        * 現状では，boxes_lastは用いていない．

        TODO: 
        次の拡張モードは，後日実装予定．

          expand (bool) : 真ならば拡張モードで，self.packの値によらず，max_lengthを子の数で当分割して配置する．
          max_length (float) : 主軸方向の固定長さ
        """
        # com.ensure(self.pack_done == False,
        #            f'{self.myinfo()}.arrange_me_pack: Executed twice!')
        if self.pack_done: 
            print(f'{self.myinfo()}.arrange_me_pack: Executed twice and skip!')
            return self.box_self
        
        ## 軸の設定: Primary, secondary
        if self.align in ('x'):   AX_PRI, AX_SEC = 0, 1
        elif self.align in ('y'): AX_PRI, AX_SEC = 1, 0
        else: com.panic(f'no such align={self.align}!')

        #作業変数の初期化
        MYSZ= [self.width, self.height]
        POS = [0, 0] #配置位置
        INC = [0, 0] #増分
        MAR = [self.margin_x, self.margin_y] #余白

        ## PackAnchor 子の配置のアンカー調整
        self.pack_anchor = com.ensure_defined(self.pack_anchor, default='mid')
        PANC = [0, 0] #リスト
        if self.expand: 
            PANC[AX_PRI], PANC[AX_SEC] = 'beg', self.pack_anchor
        else:
            PANC[AX_PRI], PANC[AX_SEC] = 'mid', self.pack_anchor
        
        # 第1回目のパス: 子の包含矩形のサイズの最大と総和を求める
        MAXSZ, SUMSZ, NUM = PackerBoard._accumulate_boxes(self.children_box_enumerated())
        #配置の増分を求める
        is_expand_mode = False
        _size = 0
        if self.expand and (MYSZ[AX_PRI] != None) and MYSZ[AX_PRI] / NUM >= MAXSZ[AX_PRI]: 
            _size = MYSZ[AX_PRI] / NUM
            is_expand_mode = True
            INC[AX_PRI] = _size #十分な長さがある
        # elif self.pack: ## 子を詰め込む
        #     pass ##あとで動的に設定する
        else: ## 最大サイズで子を等間隔に置く
            INC[AX_PRI] = MAXSZ[AX_PRI]
        
        ##設定
        RATIO = [0, 0] #アンカー比率ratio
        RATIO[0] = kw.get(crt.ALIGN_X, key=PANC[0], required=True)
        RATIO[1] = kw.get(crt.ALIGN_Y, key=PANC[1], required=True)
        POS[AX_SEC] = MAXSZ[AX_SEC] * RATIO[AX_SEC] #アンカー比率での内分点

        # 第2回目のパス
        boxes = EMPTY_RECT #包含矩形の初期値
        children_new_ = []
        for idx, triple in self.children_box_enumerated():
            trans, child, child_box = triple #分解

            #expand mode
            if is_expand_mode: 
                if True: print(f'@debug:expandmode:{self.myinfo()} {self.align} => child={child.myinfo()}: INC[AX_PRI]={INC[AX_PRI]}')
                MAR[AX_PRI] = 0.0
                ## 拡張された箱サイズBOXSZを求める
                BOXSZ = [0, 0]
                BOXSZ[AX_PRI] = INC[AX_PRI]  #主軸方向の増分
                if MYSZ[AX_SEC] != None: 
                    BOXSZ[AX_SEC] = MYSZ[AX_SEC] #副軸方向の親の幅
                else:
                    BOXSZ[AX_SEC] = MAXSZ[AX_SEC]
                
                #=================
                ## exp 暫定的: childを複製する．
                child_new = Board(show_origin=True,
                                  rgb_origin=crt.MYCOL['blue'],
                                  angle_origin=(math.pi/4)*0,
                                  show_box=True,
                                  rgb_box=crt.MYCOL['blue'])
                self._sub_child_dup(child_new, child,
                                    width=BOXSZ[0], height=BOXSZ[1])
                x1, y1 = child_new.get_anchor_point(anchor_x=child.anchor_x, anchor_y=child.anchor_y, anchor=child.anchor)                
                child.parent = None ##exp 破壊的代入につき，要注意!
                child_new.put(trans=crt.Translate(0, 0),
                          child=child)
                child = child_new
                child_new.arrange_me()
                #=================

            #子のアンカー位置を上書き
            child.anchor_x, child.anchor_y = PANC[0], PANC[1]
            child._arrange() #exp
            child_box = child.get_box()
            if True: print(f'@debug:pack:align={self.align} => child={child.myinfo()}.anchor={child.anchor_x, child.anchor_y}')

            #現在のカーソル位置x,yに対応する変換を求める
            trans1 = crt.Translate(x=POS[0], y=POS[1]) #への配置変換
            if True: 
                print(f'@debug:pack:align={self.align} => trans1={trans1}')
            
            #子の包含矩形の計算と更新
            child_box = crt.box_apply_trans(child_box, trans=trans1)
            
            #親の包含矩形の更新
            boxes = crt.box_union(boxes, child_box)
            if True: print(f'@debug:pack:update:{self.myinfo()} child={child_box} => self={boxes}')

            #新しい子リストに子を追加する
            com.ensure(child.ord_ == len(children_new_)) #ord_の検査
            children_new_.append((trans1, child)) #子リスト

            #次の配置位置を求める
            # if (not is_expand_mode) and self.pack: ## 子を詰め込む
            #     INC[0], INC[1] = crt.box_shape(child_box)
            if (not is_expand_mode): ## 子を詰め込む
                INC[0], INC[1] = crt.box_shape(child_box)
            else:
                pass 
            POS[AX_PRI] += INC[AX_PRI] + MAR[AX_PRI] #次の配置位置
            if True: print(f'@debug:pack:align={self.align} pos={POS[AX_PRI]} + inc={INC[AX_PRI]} + mg={MAR[AX_PRI]} => pos_new={POS[AX_PRI]}')
        
        #exp 自身の情報を更新
        self.children_  = children_new_ #子リストの更新
        self.trans_self = None
        self.box_self   = boxes

        self.pack_done = True
        return self.box_self
        
    pass ##class PackerBoard
        

##======
## 描画演算オブジェクト
##======

class DrawCommandBase(Board):
    """描画演算オブジェクトの基底クラス．Boardクラスのサブクラス．

    Args: 
         cmd (str) : 命令の名前の文字列．default=None. 

         **kwargs (dict) : 上位コマンドに渡すオプション引数．

    Attributes: 
         cmd (str) : 命令の名前の文字列．default=None. 
    """
    def __init__(self,
                 cmd=None, #命令の名前
                 **kwargs  #命令の引数
                 ):
        verbose = kw.get(kwargs, key='verbose')
        com.ensure(cmd!=None, f'DrawCommandBase(): cmd must not be None!')
        super().__init__(**kwargs)
        if verbose: 
            self.repo(msg=f'{self.myinfo()}(): cmd={ cmd } kwargs={ kwargs }')
        com.ensure(type(cmd) is str, f'cmd={cmd} must be str!')

        #命令を格納する
        self.cmd     = cmd 
        # self.kwargs  = kwargs  #exp
        return


    #Override 
    def draw_me(self, cr):
        if self.verbose:
            self.repo(isChild=True, msg=f'{self.myinfo()}.draw_me(): { self.vars() }')
        kwargs1 = kw.extract(kwargs=self.kwargs, keys=['x', 'y', 'width', 'height', 'fill', 'source_rgb', 'edge_rgb', 'line_width'])
        self.draw_me_impl(cr)
        return 

    #Override: To be implemented 
    def draw_me_impl(self, cr):
        """To be implemented 
        """
        return 
        
    #Override 
    def get_kwargs(self):
        return self.kwargs
    pass

class DrawCommandTemplate(DrawCommandBase):
    """描画演算オブジェクトのクラス．DrawCommandBaseクラスのサブクラス．
    """
    def __init__(self, cmd=None, **kwargs):
        super().__init__(cmd=cmd, **kwargs)
        return 

#======
# 単一図形描画
#======
CFSIZE=4
class DrawRectangle(DrawCommandBase):
    """描画演算オブジェクトのクラス．DrawCommandBaseクラスのサブクラス．

    Args: 
          x (float) : default=0.0. 

          y (float) : default=0.0. 

          **kwargs (dict) : 上位コマンドに渡すオプション引数．
    """
    def __init__(self, **kwargs):
        kwargs['x'] = kw.get(kwargs, 'x', default=0.0)
        kwargs['y'] = kw.get(kwargs, 'y', default=0.0)        
        super().__init__(cmd='rectangle', **kwargs)
        return 

    #Override 
    def arrange_me(self):
        x = kw.get(self.kwargs, 'x', required=True)
        y = kw.get(self.kwargs, 'y', required=True)
        width = kw.get(self.kwargs, 'width', required=True)
        height = kw.get(self.kwargs, 'height', required=True)
        box = (x, y, x+width, y+height)
        return box 
        
    #Override 
    def draw_me_impl(self, cr):
        crt.cr_rectangle(context=cr, **self.kwargs)
        if kw.get(self.kwargs, 'debug', default=False): 
            crt.cr_text(context=cr, ox=0, oy=0,
                        msg=f'{self.trans_self}', fsize=CFSIZE) #debug
            crt.cr_text(context=cr, ox=0, oy=CFSIZE, fsize=CFSIZE,
                        msg=f'ratio={ self.anchor_ratio_x, self.anchor_ratio_y }') #debug
            crt.cr_text(context=cr, ox=0, oy=2*CFSIZE, fsize=CFSIZE,
                        msg=f'box_={ self.box_self }') #debug
        if kw.get(self.kwargs, 'show_native_origin', default=False): 
            crt.cr_draw_marker_cross(context=cr, x=0, y=0, 
                                     linewidth=0.5, angle=math.pi*0.0, 
                                     rgb=crt.cr_add_alpha(crt.MYCOL['blue'], alpha=0.5))
        return 

class DrawCircle(DrawCommandBase):
    """描画演算オブジェクトのクラス．DrawCommandBaseクラスのサブクラス．

    Args: 
          x (float) : 円の中心位置のx座標．default=0.0. 

          y (float) : 円の中心位置のy座標．default=0.0. 

          r (float) : 円の半径．必須．

          **kwargs (dict) : 上位コマンドに渡すオプション引数．
    """
    def __init__(self, **kwargs):
        kwargs['x'] = kw.get(kwargs, 'x', default=0.0)
        kwargs['y'] = kw.get(kwargs, 'y', default=0.0)
        super().__init__(cmd='circle', **kwargs)
        return 

    #Override 
    def arrange_me(self):
        x = kw.get(self.kwargs, 'x', required=True)
        y = kw.get(self.kwargs, 'y', required=True)
        r = kw.get(self.kwargs, 'r', required=True)
        box = (x-r, y-r, x+r, y+r)
        return box 
        
    #Override 
    def draw_me_impl(self, cr):
        # Note: self.kwargs contains keys 'x', 'y', 'r'. 
        crt.cr_circle(context=cr, **self.kwargs) 
        if kw.get(self.kwargs, 'debug', default=False): 
            crt.cr_text(context=cr, ox=0, oy=0,
                        msg=f'{self.trans_self}', fsize=CFSIZE)#debug
            crt.cr_text(context=cr, ox=0, oy=CFSIZE, fsize=CFSIZE,
                        msg=f'ratio={ self.anchor_ratio_x, self.anchor_ratio_y }') #debug
            crt.cr_text(context=cr, ox=0, oy=2*CFSIZE, fsize=CFSIZE,
                        msg=f'box_={ self.box_self }') #debug
        if kw.get(self.kwargs, 'show_native_origin', default=False): 
            crt.cr_draw_marker_cross(context=cr, x=0, y=0, 
                                     linewidth=0.5, angle=math.pi*0.0, 
                                     rgb=crt.cr_add_alpha(crt.MYCOL['blue'], alpha=0.5))
        return 

# #未使用
# class DrawArc(DrawCommandBase):
#     """描画演算オブジェクトのクラス．DrawCommandBaseクラスのサブクラス．
#     """
#     def __init__(self, **kwargs):
#         super().__init__(cmd='arc', **kwargs)
#         return 

#     #Override 
#     def arrange_me(self):
#         box = (0, 0)
#         return box 
        
#     #Override 
#     def draw_me_impl(self, cr):
#         crt.cr_arc(context=cr, **self.kwargs) 
#         return 

#======
# 線分列の描画
#======

#constants
CMD_MOVE = 0
CMD_LINE = 1

class DrawPolyLines(DrawCommandBase):
    """描画演算オブジェクトのクラス．DrawCommandBaseクラスのサブクラス．

    Args: 
          **kwargs (dict) : 上位コマンドに渡すオプション引数．

    Examples:: 
    
                #サイズが4x4の十字型(X)を書く．
              	P = DrawPolyLine()
        	P.move_to(0.0, 0.0)
        	P.line_to(4.0, 4.0)
        	P.move_to(0.0, 4.0)
        	P.line_to(4.0, 0.0)
    """
    
    def __init__(self, **kwargs):
        super().__init__(cmd='polylines', **kwargs)
        self.CMDS = []
        return 

    #Override 
    def arrange_me(self):
        #命令全ての包含長方形を計算する
        boxes = EMPTY_RECT
        for idx, pair in enumerate(self.CMDS):
            cmd, x, y, _ = pair #分解
            boxes = crt.box_union(boxes, (x, y))
        if True: print(f'@debug:polyline: boxes={boxes}')
        return boxes 

    #Override 
    def draw_me_impl(self, cr):
        crt.cr_set_context_parameters(context=cr, **self.kwargs)
        x_last, y_last = None, None 
        for idx, pair in enumerate(self.CMDS):
            cmd, x, y, has_arrow = pair #分解
            if cmd==CMD_MOVE:
                if self.verbose:
                    kwargs={ 'x':x, 'y': y, }
                    self.repo(isChild=True, msg=f'@debug: cr_move_to: { kwargs }')
                crt.cr_move_to(x, y, context=cr)
            elif cmd==CMD_LINE:
                if self.verbose:
                    kwargs={ 'x':x, 'y': y, 'has_arrow': has_arrow,
                             'x_last': x_last, 'y_last': y_last, }
                    self.repo(isChild=True, msg=f'@debug: cr_line_to: { kwargs }')
                if x_last != None and y_last != None: 
                    crt.cr_line_to(x, y, context=cr, 
                                   x_last=x_last, y_last=y_last,
                                   has_arrow=has_arrow,
                                   **self.kwargs)
            else:
                com.panic(f'PolyLines.draw_me_impl: no such cmd={cmd}!')
            x_last, y_last = x, y 
            pass
        crt.cr_process_stroke_or_fill(context=cr, **self.kwargs)
        return

    def move_to(self, x, y):
        """ペンを位置`(x,y)`に移動する．直線は引かない．
        Args: 

              x (float) : x- and y-coodinates

              y (float) : x- and y-coodinates

        Returns:
              (Board) : 自分自身．いわゆる'cascade object call interface' のため．
        """
        has_arrow = False
        self.CMDS.append((CMD_MOVE, x, y, has_arrow))
        return self #for cascade object interface 
    
    def line_to(self, x, y, has_arrow=False):
        """ペンを現在位置から目標位置`(x,y)`まで移動して，直線を引く．

        Args: 

              x (float) : x- and y-coodinates

              y (float) : x- and y-coodinates

        Returns:
              (Board) : 自分自身．いわゆる'cascade object call interface' のため．

        """
        self.CMDS.append((CMD_LINE, x, y, has_arrow)) 
        return self #for cascade object interface 
    
    pass 

class DrawMarkerCross(DrawPolyLines):
    """原点 (0,0) を中心とした×印（Cross）を書く．

    Args: 
         ticklen (float) : ×印の交差辺の長さ. default=4.0. 

         line_width (float) : ×印の交差辺の線幅．default=0.75．
    """
    def __init__(self, **kwargs):
        # kwargs['x'] = kw.get(kwargs, 'x', default=0.0)
        # kwargs['y'] = kw.get(kwargs, 'y', default=0.0)        
        ticklen = kw.get(kwargs, 'ticklen', default=4.0)
        linewidth = kw.get(kwargs, key='linewidth',
                           altkeys=['line_width', 'pen_width'], default=0.75)
        kwargs['linewidth'] = linewidth
        super().__init__(**kwargs)
        # clen = 5
        self.move_to(0, 0)
        self.line_to(ticklen*1.0, ticklen*0.0)
        self.move_to(0, 0)
        self.line_to(ticklen*(-1.0), ticklen*0.0)
        self.move_to(0, 0)
        self.line_to(ticklen*0.0, ticklen*1.0)
        self.move_to(0, 0)
        self.line_to(ticklen*0.0, ticklen*(-1.0))
        return 




#======
# 関数終わり
#======

# ## メイン文
# if __name__ == '__main__':
#     shape = (9,6)
#     reg = ImageBoard(ratio=128, shape=shape, xy = (0.5, 0.5))
#     print('reg: \n', vars(reg))
    
##EOF

