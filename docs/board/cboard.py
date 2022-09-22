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
import math 
import numpy as np
import random 
import copy 
from typing import NamedTuple
# import inspect
# import cairo 

import os #for rtd
sys.path.insert(0, os.path.abspath('../board/')) #for rtd

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


# #constants
# CMD_MOVE = 0
# CMD_LINE = 1

def numpair_normalize(margin=None, default=None):
    """マージン指定を正規化する．margin が数の対(float,float)ならばそのまま返し，
    margin が数ならば，(margin,margin)を返す．
    margin==Noneのときは，(0.0,0.0)を返す．
    """
    if margin==None:
        margin1 = com.ensure_defined(value=default,
                                    default=(0.0, 0.0))
    elif isinstance(margin, (float,int)): 
        margin1 = (margin, margin)
    elif com.is_sequence_type(margin, elemtype=(float,int), length=2):
        margin1 = margin
    else:
        com.panic(f'margin={margin} must be either float or (float,float)!')
    com.ensure(crt.isProperPoint(margin1),
               f'margin={margin1} must be a pair of numbers')
    return margin1 
    
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

def pair_normalize(pair=None):
    """変換と子ボードの対を分解し，検査して返す．

    Args: 
         pair (tuple()) : 
    
    Returns: 
         (tuple()) : 変換と子ボードの対 (trans, child)
    """
    trans, child = pair #分解
    #子の型チェック
    if child != None: 
        com.ensure(isinstance(child, BoardBase),
                   'child must be a subclass of BoardBase!: {child}')
    if trans!=None:
        com.ensure(isinstance(trans, crt.GeoTransform),
                   f'trans must be of crt.GeoTransform: {type(trans)}')
    return trans, child

#=====
# 画盤（board）のクラス: 座標系オブジェクト
#=====
# class Board(com.Loggable):
class BoardBase(log.Loggable):
    """図形（Board）の描画に関する基本機能を提供するクラス．子孫クラスから呼び出される二つの私的関数`_arrange()`と`_draw(self, cr)`を提供する．

    Args: 
         **kwargs : 他のキーワード引数．上位クラスに渡される．

    Attributes: 
         trans (GeoTransform) : 自身の変換

         box   (tuple(float,float,float,float)) : 自身の包含矩形.

         boxes (float,float,float,float) : 子全体の包含矩形.

         verbose (bool): ログ出力のフラグ

    Note: 
          本クラスでは，主ループとして，配置関数`_arrange()`と描画関数`_draw(self, cr)`を提供し，子孫クラスにおいて，これらの以下のサブメソッドを実装することで，独自の振る舞いを定義する．

         * 関数`_arrange()`のサブメソッド

             * `arrange_box_children(self)`: 子を相互に配置し，子全体の包含矩形`self.boxes`を求める．

             * `arrange_box_self(self)`: 子全体の包含矩形`self.boxes`と修飾情報(modifiers)から自身の包含矩形を求める．ボードは，修飾情報として，余白やアンカー点の情報をもつ．

         * 関数`_draw()`のサブメソッド: 

             * `draw_me_before(self, cr)`: Cairoの文脈オブジェクト`cr`を受け取り，子の描画の前に，自身を描画する手続きを定義する．

             * `draw_me_after(self, cr)`: Cairoの文脈オブジェクト`cr`を受け取り，子の描画の後に，自身を描画する手続きを定義する．
    """
    def __init__(self,
                 anchor=None,
                 **kwargs):
        """画盤オブジェクトを初期化する
        """
        #引数
        #親Loggableの初期化
        super().__init__(**kwargs)
        
        #内部変数
        self.anchor = self._init_anchor(anchor_str=anchor)
        
        ##自身の配置情報
        self.trans : crt.GeoTransform = None #自身の変換
        self.box   = None #自身の包含矩形.
        self.boxes = None #子全体の包含矩形.
        
        if self.verbose:
            self.repo(msg=f'{self.myinfo()}.__init__(): { self.vars() }')
        return

    #=====
    # 雑関数
    #=====

    def _init_anchor(self, anchor_str=None):
        """アンカー文字列指定`anchor_str`を受け取り，格納する．"""
        #アンカーのデフォールト設定
        _anchor = crt.anchor_vector(anchor_str=anchor_str)
        # if anchor_str==None:
        #     print(f'@debug: BoardBase: {self.myinfo()}.__init__(): anchor_str=={anchor_str}! => _anchor={_anchor}')
        com.ensure((_anchor != None and
                    crt.isProperPoint(_anchor)),
                   f'_anchor={None} must be a point!')
        return _anchor 

    def get_box(self) -> 'tuple(float,float,float,float)':
        """保持する自身の包含矩形を返す．

        Returns: 
             (tuple(float,float,float,float)) : 自身の包含矩形．親による自身の配置を規定する．
        """
        _box = self.box 
        com.ensure(_box!=None and crt.isProperBox(_box),
                   f'get_box: box={_box} must be isProperBox')
        return _box

    def get_trans(self) -> crt.GeoTransform:
        """保持する変換を返す．

        Returns: 
             (GeoTransform) : 自身に適用する変換．自身の子の配置を規定する．
        """
        _trans = self.trans 
        #self.transはNone（降等変換）でも良い．
        com.ensure(_trans==None or isinstance(_trans, crt.GeoTransform),
                   f'get_trans: trans={_trans} must be a GeoTrans')
        return _trans 

    
    def get_anchor(self) -> 'tuple(float,float)':
        """自身の包含矩形上のアンカー点（配置の原点）を返す．ここに，各種の配置関数`_arrange()`は，アンカー点を原点として図形を配置する．

        Attributes: 
self.anchor (tuple(float,float)) : 正規化アンカーベクトル `a = (ax,ay) in [0,1]^2`

        Returns: 
             (tuple(float, float)) : 2次元平面上のアンカー点 `b = (bx,by) in R^2`
        """
        com.ensure((self.anchor != None and
                    crt.isProperPoint(self.anchor)),
                   f'self.anchor={None} must be a point!')
        apos = crt.anchor_point_by_vector(box=self.box,
                                           vect=self.anchor)
        com.ensure(apos != None and isProperPoint(apos),
                   f'apos={apos} must be a pair of numbers')
        return apos

    
    # exp 基本：配置の計算
    def _arrange(self):
        """配置を計算する．配置は，ボトムアップに再帰的に計算される．

        Returns: 
        	rect: 計算済みの自身の包含矩形オブジェクト
        """
        if self.verbose:
            self.repo(msg=f'{self.myinfo()}._arrange(): { self.vars() }')

        #子の配置情報を再帰的に得る
        self._arrange_apply_children()
                
        #子供全てを再配置する．
        self.arrange_box_children()
            
        #注意：関数arrange_self_transformはサブクラスでオーバーライドする
        self.arrange_box_self()

        if True:
            print(f'@debug:trans:{self.myinfo()}: trans={self.trans}')
        com.ensure(self.box != None, f'self.box={self.box} != None!')
        return self.box 

    def _arrange_apply_children(self):
        """自身の子すべてに対して，再帰的に配置を行う．
        次の属性を操作する: 

        * self.children_: 読み出し
        """
        for idx, pair in self.children_enumerated():
            trans, child = pair_normalize(pair)
            if self.verbose: self.repo(msg=f'=> call _arrange() on {idx}-th child={child.myinfo()}', is_child=True, header=False)
            
            child._arrange() #再帰的に子の配置を実行
            
            com.ensure(child.get_box() != None,
                       f'child.get_box()={child.get_box()} != None')
        return 

    def arrange_box_children(self):
        """自身の子たちの配置情報を計算する．子孫クラスでオーバーライドすること．

        Note: 

         配置情報として，子リストにおいて子それぞれの変換と子自身を計算する．終了前に属性`self.boxes`を設定すること．
         次の属性を操作する: 

            * 読み出し: `self.children_`
            * 書き込み: `self.boxes` (非None) 
        """
        _boxes = EMPTY_RECT
        for idx, pair in self.children_enumerated(): 
            trans, child = pair_normalize(pair)
            
            #自身の包含矩形の更新
            box = child.get_box()
            com.ensure(box != None, f'child.get_box()={box} != None')
            
            box = crt.box_apply_trans(box, trans=trans)
            _boxes = crt.box_union(_boxes, box) #包含矩形の更新
        self.boxes = _boxes
        com.ensure(crt.isProperBox(self.boxes),
                   f'self.boxes={self.boxes} must be a box!')
        if self.verbose:
            self.repo(msg=f'{self.myinfo()}._arrange()=> box={ self.boxes }', is_child=True)
        return 
        
    #To be Override
    def arrange_box_self(self):
        """修飾情報から自身の配置情報を計算する．子孫クラスでオーバーライドすること

        Note: 

            自身の配置情報として変換と包含矩形を求める．終了前に属性`self.box`と`self.trans`を設定すること．次の属性を操作する: 

            * 読み出し: `self.boxes` (非None)
            * 書き込み: `self.box`   (非None)
            * 書き込み: `self.trans` (Noneも許す)
        """
        self.box = self.boxes
        return 
        
    # #Override 
    # def arrange_box_self(self):
    #     width = kw.get(self.kwargs, 'width')
    #     height = kw.get(self.kwargs, 'height')
    #     box = None 
    #     if width!=None and height!=None: 
    #         x = kw.get(self.kwargs, 'x', default=0)
    #         y = kw.get(self.kwargs, 'y', default=0)
    #         box = (x, y, x+width, y+height)
    #     return box 

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
            self.repo(is_child=True, msg=f'{self.myinfo()}._draw(): { self.vars() }')
            
        ## 自分の空間を開く
        cr.save()  ##self
        ## 自身の変換を適用する
        crt.cr_apply_trans(trans=self.get_trans(), context=cr)
        if True: print(f'@debug:draw:self:{self.myinfo()}: apply trans={self.get_trans()}')
            
        #必要なら自分の描画を行う
        self.draw_me_before(cr)
        
        #子の描画を行う
        for idx, pair in self.children_enumerated():
            trans, child = pair #分解
            
            #子の型チェック
            com.ensure(isinstance(child, BoardBase),
                       f'{self.myinfo()}.draw: child must be a subclass of'+
                       f' BoardBase!: {child}: children_={self.children_}')
            
            cr.save()    ## 子の空間を開く
            crt.cr_apply_trans(trans=trans, context=cr) ## 変換を適用する
            if True: print(f'- @debug:draw:child:{child.myinfo()}: apply trans={trans}')
            child._draw(cr)
            cr.restore() ## 子の空間を閉じる

        #必要なら自分の描画を行う
        self.draw_me_after(cr)

        ## 自分の空間を閉じる
        cr.restore()  ##self

        ## debug: 包含矩形を描画する
        self.draw_origin_and_box(cr) #自分の原点位置と包含矩形を描画する．
        return

    # 派生：Override
    def draw_me_before(self, cr):
        """自分の描画を行う．子の描画の前に実行される．子孫クラスでオーバーライドすること．

        Args: 
             cr (Cairo.Context) : Cairoの文脈オブジェクト
        
        Note: 
            文脈オブジェクトに，配置情報を元に直接書き込みを行う．
        """
        if self.verbose: self.repo(is_child=True,
                                   msg=f'{self.myinfo()}.draw_me_before()...')
        ## ここでcontext crに何か描く．
        return 

    # 派生：Override
    def draw_me_after(self, cr):
        """自分の描画を行う．子の描画の前に実行される．子孫クラスでオーバーライドすること．

        Args: 
             cr (Cairo.Context) : Cairoの文脈オブジェクト

        Note: 
            文脈オブジェクトに，配置情報を元に直接書き込みを行う．
        """
        if self.verbose: self.repo(is_child=True,
                                   msg=f'{self.myinfo()}.draw_me_before()...')
        ## ここでcontext crに何か描く．
        return

    #=====
    # おまけ関数．drawの副関数
    #=====
    def draw_origin_and_box(self, cr):
        """自分の原点位置と包含矩形をマーカーで描画する．
        """
        #自分の包含矩形を描画する．
        if self.fetch(key='boundingbox', default=False) and crt.isBoxOrPoint(self.get_box()):
            self.draw_perturbed_box(self.get_box(), context=cr)
            
        #自分の原点位置をマーカーで描画する．
        if kw.get(self.kwargs, key='show_origin', default=False):
            rgb = kw.get(self.kwargs, key='rgb_origin',
                         default=crt.MYCOL['red'])
            angle = kw.get(self.kwargs, key='angle_origin',
                         default=math.pi/4)
            crt.cr_draw_marker_cross(context=cr, x=0,y=0,
                                     linewidth=0.5, angle=angle, 
                                     rgb=crt.cr_add_alpha(rgb, alpha=0.5))
        #自分の包含矩形を描画する．
        if kw.get(self.kwargs, key='show_box', default=False):
            rgb = kw.get(self.kwargs, key='rgb_box',
                         default=crt.MYCOL['green'])
            (x0, y0, x1, y1) = self.get_box()
            crt.cr_rectangle(x0, y0, x1 - x0, y1 - y0,
                             context=cr,
                             rgb=crt.cr_add_alpha(rgb, alpha=0.5), 
                             line_width=1)
        return
    
    def draw_perturbed_box(self, box, context=None, max_perturb=None):
        """自分の包含矩形を描画する．視認性のため，
        max_perturbで決まる摂動を加えて描画する．
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
        crt.cr_text(tx + fmargin, ty + 1.0*dy + fmargin,
                    msg=msg, fsize=fsize, context=cr)
        return 

    pass ## end class BoardBase 

        
#=====
# ボードのインタフェースのクラス
#=====
#old: class Board(AnchorBoard):
class CoreBoard(BoardBase):
    """描画を行う画盤（board）のクラス．具体的な子の配置方法は持たず，サブクラスで実装される．`WrapperBoard`とは比較不能（兄弟）な継承関係をもつ．

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

#=====
# ラッパーのクラス
#=====

class WrapperBoard(BoardBase):
    """ラッパーのクラス．描画は行わず，唯一の子の位置パラメータ決めのみを行う．自身が持たないメソッド呼び出しを，唯一の子に転送する．
    `CoreBoard`とは比較不能（兄弟）な継承関係をもつ．

    Args: 
          child (BoardBase) : 子として保持するBoardBaseオブジェクト．

          **kwargs : 他のキーワード引数．上位クラスに渡される．

    Attributes: 
        verbose (bool): ログ出力のフラグ
    """
    # def __init__(self, child=None, **kwargs):
    def __init__(self, child=None,
                 **kwargs):
        """画盤オブジェクトを初期化する
        """
        #引数
        #親Loggableの初期化
        super().__init__(max_children=1, #Can have at most one child
                         **kwargs)

        ## 包み込む唯一の子を設定する
        com.ensure(child != None, f'child must be to None!')
        child.parent = None ##使用済みの子から親への参照を切る．破壊的代入．        
        # self.put(trans=None, child=child)   #子に追加
        self.append(pair=(None, child))   #子に追加

        ## メソッド転送設定
        self.the_child : BoardBase = child  #転送先オブジェクト
        #内部変数
        if self.verbose:
            self.repo(msg=f'{self.myinfo()}.__init__(): { self.vars() }')
        return

    def get_the_child(self) -> BoardBase:
        _child = self.the_child
        com.ensure(isinstance(_child, BoardBase),
                   'child must be a subclass of BoardBase!: {_child}')
        return _child 
    
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
    pass #class WrapperBoard

class MarginWrapper(WrapperBoard):
    """唯一の子を指定した余白（margin）で包むラッパーのクラス，
    自身が持たないメソッド呼び出しを子に転送する．

    Args: 
          child (BoardBase) : 子として保持するBoardBaseオブジェクト．

          margin (float, tuple(float, float)) : 子の外周に付与する余白の情報

          **kwargs : 他のキーワード引数．上位クラスに渡される．

    Attributes: 
        margin (tuple(float,float)) : 余白情報 margin = (margin_x, margin_y). 

        box (tuple(float,float,float,float)) : 修正された包含矩形．子の包含矩形の外側にmarginで指定したx方向とｙ方向の幅の余白を拡大した形状になる．関数`get_box()`で返される．

        trans (GeoTransform) : 修正された変換．拡大された包含矩形の左上隅を原点とする．

        verbose (bool): ログ出力のフラグ
    """
    # def __init__(self, child=None, **kwargs):
    def __init__(self, child=None,
                 margin=None,
                 **kwargs):
        """画盤オブジェクトを初期化する
        """
        #引数
        #親Loggableの初期化
        super().__init__(child=child, 
                         **kwargs)

        ##マージン
        self.margin : tuple = margin
        
        #内部変数
        if self.verbose:
            self.repo(msg=f'{self.myinfo()}.__init__(): { self.vars() }')
        return

    # Override exp 基本：配置の計算
    def arrange_box_self(self):
        """アンカー情報から，変換と包含矩形を計算する．子孫クラスでオーバーライドする．
        次の属性を操作する: 

        * self.boxes  : 読み出し
        * self.box    : 書き込み
        * self.trans  : 書き込み

        crt.ANCHOR_ORIGINは，左上原点のアンカー指定(left,top)
        """
        child_box = self.get_the_child().get_box()
        x0, y0, x1, y1 = child_box

        #変換を求める
        mx, my = numpair_normalize(margin=self.margin)
        _self_box = x0 - mx, y0 - my, x1 + mx, y1 + my
        xx0, yy0, xx1, yy1 = _self_box
        ## 
        dst = 0.0, 0.0
        src = xx0, yy0
        moves = crt.vt_sub(dst, src)  #moves = dst - src
			
		#自身の包含矩形とアンカーを，左上を原点にそろえて，正規化する．
        self.trans : crt.GeoTransform  = crt.Translate(dest=moves)
        self.box : tuple  = crt.box_apply_trans(_self_box, trans=self.trans)
        return self.box 
    
    pass #class MarginWrapper 
    
#=====
# ボードの実装クラス
#=====

## TODO:PlaceBoard
class PlaceBoard(CoreBoard):
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
        if self.verbose:
            self.repo(msg=f'{self.myinfo()}.__init__(): { self.vars() }')
        return

    # exp 基本：子を追加する
    def put(self, child=None, trans=None) -> BoardBase: 
        """子を追加する．

        Args: 
            trans (cairo.Matrix) : 自座標における子の配置を指示する変換行列．原点にある子を所望の場所に配置するためのアフィン変換を表す．

            child (Board): 子として追加するBoardオブジェクト

        Returns:
            (Board) : 追加した子
        
        Example:: 
        
        		root = Canvas()
        		child = root.put(Board())
        		child = parent.put(trans=Translate(dest=(1,2)), 
        			Rectangle())
        """
        #型チェック: 変換transは，Noneを許す．
        com.ensure(trans == None or isinstance(trans, crt.GeoTransform),
                   f'{self.myinfo()}.put(): trans must be a GeoTransform!: {trans}') 
        #型チェック: 子childはNoneを許さない．
        com.ensure(child != None and isinstance(child, BoardBase),
                   f'{self.myinfo()}.put(): child must be a BoardBase!: {child}') 
        self.append((trans, child)) #子リスト

        if self.verbose: self.repo(msg=f'=> added: {self.myinfo()}.put(): trans={trans} child={ child } with vars={ child.vars() }...')
        
        return child #Do not change!
    
#=====
# ボードのインタフェースのクラス
#=====
#old: class Board(AnchorBoard):
class Board(PlaceBoard):
    """描画を行う画盤（board）のクラス．`PackerBoard`のラッパー．

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
# class Canvas(Board):
class Canvas(PlaceBoard):
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
                 imgtype=crt.DEFAULT_IMGTYPE, #cairoのSurface format
                 # imgtype=cairo.FORMAT_ARGB32, #cairoのSurface format
                 format="pdf",   #出力ファイルフォーマット（拡張子 pdf, png）
                 outfile="out",  #出力ファイル名（拡張子を除く）
                 imagesize='XGA',#初期の画像サイズ
                 portrait=False, #画像サイズが縦長か？
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
        self.max_perturb : float = max_perturb #fetchで子孫からアクセス
        # self.show_origin = show_origin #fetchで子孫からアクセス
        verbose = kw.get(kwargs, key='verbose', default=False)

        ##属性
        self.im  = None   #基礎画像オブジェクト．遅延生成
        self.display_shape = None
        # self.verbose = verbose 
        
        if verbose: 
            self.repo(msg=f'{self.myinfo()}.__init__(): vars={ self.vars() }')

        #基底描画オブジェクトの生成
        if self.format: #cairoのformatが与えられていたら，直ちに基底画像pimを生成
            #画像フォーマット
            com.ensure(format, f'format must be defined!')
            if self.verbose: 
                self.repo(msg=f'.create_pim: format={ format }')

            ##画像サイズの設定
            self.display_shape = crt.get_display_shape(shape=self.imagesize, portrait=self.portrait)
                
            self.im = crt.ImageBoard(
                format=format, 
                outfile=outfile,
                display_shape=self.display_shape, 
                verbose=self.verbose, 
            )  ##ImageBoardの生成
            self.im.depth=self.depth+1
        return 
        
    #=====
    # 基底描画系の生成
    #=====

    def canvas_size(self) -> 'tuple(int, int)':
        return self.display_shape

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
        com.ensure(box, 'box={box} must be defined!')

        #ステップ2: トップダウンに描画を行う
        cr = self.im.context()
        self._draw(cr)
        
        #ステップ3: 画像を表示する
        self.im.show(noshow=noshow)  ##pilimage.ImageBoard
        # self.im.show(noshow=noshow, depth=depth)  ##pilimage.ImageBoard
        return

    #Cairo.contextオブジェクトの返却
    def context(self) -> 'cairo.Context': 
        """Cairo.contextオブジェクトを返す．"""
        return self.im.context()  ##Cairo.contextオブジェクト
            
    # 画像をファイルに保存する
    def save(self, imgfile, **kwargs):
        """imgfile: 保存する画像ファイルの名前．"""
        self.im.save(imgfile=imgfile, **kwargs)
        return

#=====
# ボードの実装クラス
#=====

# class PackerBoard(BoardBase):
class PackerBoard(CoreBoard):
    """画盤（board）のクラス．Boardのサブクラス

    Args: 
         orient (str) : 並べる主軸方向の指定．`x`または`y`の値をとる．default='x'

         packing (str) : 内部のボードの詰め方の指定情報. packing in ('even','pack')

         width (float) : 自身の幅．default=None. 

         height (float) : 自身の高さ．default=None. 

    	 kwargs : 他のキーワード引数．上位クラスに渡される．
    """
    def __init__(self,
                 orient='x',
                 packing=None,
                 cell_margin=None, #exp
                 ##
                 width=None,
                 height=None, 
                 **kwargs):
        #引数
        super().__init__(**kwargs)
        
        #内部変数
        ## マージン設定
        self.packing : str = packing 
        self.cell_margin : tuple  = cell_margin
        
        #内部変数
        self.orient : str = orient
        self.width : float = width
        self.height: float = height
        
        
        #debug
        if self.verbose:
            self.repo(msg=f'{self.myinfo()}.__init__(): { self.vars() }')
        return

    
    # exp 基本：子を追加する
    def add(self, child:BoardBase=None) -> BoardBase: 
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
        
        #exp: ラッパーで包んでから，子リストに加える
        _debug_wrapper = {}
        if self.fetch(key='verbose', default=False): 
            _debug_wrapper = {
                #デバッグ用の包含矩形描画
                'show_box': True,
                # rgb_box=crt.MYCOL['magenta'],
                'rgb_box':  crt.cr_add_alpha(crt.MYCOL['magenta'], alpha=0.5),
                #デバッグ用の原点描画
                'show_origin':  True,
                'rgb_origin':  crt.MYCOL['blue'],
                'angle_origin':  (math.pi/4)*0,
            }
        # child1 = WrapperBoard(child=child,
        #                       margin=self.cell_margin, 
        #                       **PackerBoard._debug_wrapper, #デバッグ表示用
        #                       ) 
        # child1 = WrapperBoard(child=child,
        #                       **PackerBoard._debug_wrapper, #デバッグ表示用
        #                       ) 
        # return self.put(trans=None, child=child1) #exp
        child1 = MarginWrapper(child=child,
                              margin=self.cell_margin, 
                              **_debug_wrapper, #デバッグ表示用
                              ) 
        return self.append(pair=(None, child1)) #exp
        

    # 基本：子画盤の並びを返す
    ##Override
    def children_box_enumerated(self) -> 'iterator':
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
             max_shape (tuple(float, float)) : 矩形のx-とy-サイズの最大値の対
             SUMSZ (tuple(float, float)) : 矩形x-とy-のサイズの総和の対
             NUM (int) : 矩形の数
        """
        max_shape = [0, 0] #サイズの最大値
        sum_shape = [0, 0] #サイズの総和
        num_shape = 0
        # for idx, triple in self.children_box_enumerated():
        for idx, triple in boxes:
            trans, child, child_box = triple #分解
            com.ensure(child_box != None,
                       f'child_box={child_box} must be non-None')
            #子の包含矩形の最大サイズを更新
            cwidth0, cwidth1  = crt.box_shape(child_box)
            max_shape[0], max_shape[1] = max(max_shape[0],cwidth0), max(max_shape[1],cwidth1)
            sum_shape[0], sum_shape[1] = sum_shape[0] + cwidth0, sum_shape[1] + cwidth1
            num_shape += 1
        return max_shape, sum_shape, num_shape


    def _get_axes(orient=None):
        """与えられた文字列orient (str)に応じて，主軸と副軸の添字の対 AX_PRI, AX_SEC を返す．
        """
        if orient in ('x'):   ax_pri, ax_sec = 0, 1
        elif orient in ('y'): ax_pri, ax_sec = 1, 0
        else: com.panic(f'no such orient={ orient }!')
        return ax_pri, ax_sec 
    
    #To be Override
    def arrange_box_children(self, **kwargs):
        """自身の子すべてを再配置する．必ず終わりにself.boxesを設定すること．
        次の属性を操作する: 

        * self.children_
        * self.boxes
        """
        ## 軸の設定: Primary, secondary
        ax_pri, ax_sec = PackerBoard._get_axes(self.orient)

        # 第1回目のパス: 子の包含矩形のサイズの最大と総和を求める
        _max_shape, _, _ = PackerBoard._accumulate_boxes(self.children_box_enumerated())

        # 内部の子ボードの形状サイズ指定
        _ishape = [None, None] #内部のさや(pod)の形状サイズ．可変データ
        com.ensure(com.is_sequence_type(_max_shape, elemtype=(float,int),
                                        length=2, verbose=True),
                   f'max_shape={_max_shape} must be a pair of numbers!')
        _ishape = _max_shape
        if self.packing==None:
            pass
        elif self.packing in ('even'):
            pass
        elif self.packing in ('pack'):
            _ishape[ax_pri] = None #primary-axis has unbounded size
            pass
        else:
            pass

        # 第2回目のパス
        _child_pos = [0, 0] #初期値: 子ボードの配置位置
        _boxes = EMPTY_RECT #包含矩形の初期値
        for idx, pair in self.children_enumerated():
            trans, child = pair #分解

            #子配置の変換
            trans1 = crt.Translate(dest=_child_pos)

            #変換と子を追加
            self.set_child_by_idx(idx=idx, pair=(trans1, child)) 

            ##=========================
            #子を新たに生成したラッパーで包み，子リストに再登録する
            # child1 = WrapperBoard(child=child, **PackerBoard._debug_wrapper) #デバッグ用
            # self.set_child_by_idx(idx=idx, pair=(trans1, child1)) #子を追加
            ##=========================
            
            #子の配置情報の計算
            child._arrange() #再帰的に処理

            #自身の包含矩形の計算
            box0 = child.get_box()
            com.ensure(box0 != None, f'box0={box0} is None!')
            box1 = crt.box_apply_trans(box0, trans=trans1)
            com.ensure(box1 != None, f'box1={box1} is None!')
            _boxes = crt.box_union(_boxes, box1) #親の包含矩形の更新
            if True: print(f'@debug:pack:update:{self.myinfo()} child={box1} => self={_boxes}')

            #次の配置位置を求める
            _old_child_pos = copy.copy(_child_pos)
            ## 主軸: 子の主軸長だけ，配置位置を進める
            if _ishape[ax_pri]!=None: 
                _child_pos[ax_pri] += _ishape[ax_pri]
            else:                
                _child_pos[ax_pri] += crt.box_shape(box1)[ax_pri]
            ## 副軸: 配置位置は変えない．
                
            if True: print(f'@debug:pack:orient={self.orient} pos={ _old_child_pos } => pos_new={ _child_pos }')
        
        #exp 自身の情報を更新
        self.boxes   = _boxes
        com.ensure(crt.isProperBox(self.boxes),
                   f'self.boxes={self.boxes} must be a box!')
        return self.box
    
    pass ##class PackerBoard
        

#=====
# サブクラス
#=====
class GridPackerBoard(PackerBoard):
    """描画を行う画盤（board）のクラス．`PackerBoard`のラッパー．

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

##======
## 描画演算オブジェクト
##======

class DrawCommandBase(CoreBoard):
    """描画演算オブジェクトの基底クラス．Boardクラスのサブクラス．

    Args: 
         cmd (str) : 命令の名前の文字列．default=None. 

         **kwargs (dict) : 上位コマンドに渡すオプション引数．

    Attributes: 
        cmd (str) : 命令の名前の文字列．default=None. 

        kwargs (dict) : コマンドの引数からなる辞書．各コマンドは，この辞書の項目を参照して実装する．
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
        self.cmd :str = cmd 
        # self.kwargs  = kwargs  #exp
        return


    #Override 
    def draw_me_before(self, cr):
        if self.verbose:
            self.repo(is_child=True, msg=f'{self.myinfo()}.draw_me_before(): { self.vars() }')
        kwargs1 = kw.extract(kwargs=self.kwargs, keys=['x', 'y', 'width', 'height', 'fill', 'source_rgb', 'edge_rgb', 'line_width'])
        self.draw_me_impl(cr)
        return 

    #Override: To be implemented 
    def draw_me_impl(self, cr):
        """To be implemented 
        """
        return 
        
    # #Override 
    # def get_kwargs(self):
    #     return self.kwargs
    # pass

# class DrawCommandTemplate(DrawCommandBase):
#     """描画演算オブジェクトのクラス．DrawCommandBaseクラスのサブクラス．
#     """
#     def __init__(self, cmd=None, **kwargs):
#         super().__init__(cmd=cmd, **kwargs)
#         return 

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
    def __init__(self, x=0.0, y=0.0, width=None, height=None, **kwargs):
        self.x = com.ensure_defined(value=x, required=True)
        self.y = com.ensure_defined(value=y, required=True)
        self.width : float = com.ensure_defined(value=width, required=True)
        self.height: float = com.ensure_defined(value=height, required=True)
        super().__init__(cmd='rectangle', **kwargs)
        return 

    #Override 
    def arrange_box_self(self):
        x, y = self.x, self.y
        width, height = self.width, self.height
        self.box = (x, y, x+width, y+height)
        return 
        
    #Override 
    def draw_me_impl(self, cr):
        crt.cr_rectangle(x=self.x, y=self.y,
                         width=self.width, height=self.height, 
                         context=cr,
                         **self.kwargs)
        if kw.get(self.kwargs, 'debug', default=False): 
            crt.cr_text(context=cr, ox=0, oy=0,
                        msg=f'{self.get_trans()}', fsize=CFSIZE) #debug
            crt.cr_text(context=cr, ox=0, oy=2*CFSIZE, fsize=CFSIZE,
                        msg=f'box_={ self.box }') #debug
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
    def __init__(self,
                 x=0.0, 
                 y=0.0,
                 r=None, 
                 **kwargs):
        self.x : float = x
        self.y : float = y
        self.r : float = r
        com.ensure(self.r != None, f'r={r} is None!')
        super().__init__(cmd='circle', **kwargs)
        return 

    #Override 
    def arrange_box_self(self):
        x = self.x
        y = self.y
        r = self.r
        self.box = (x-r, y-r, x+r, y+r)
        return 
        
    #Override 
    def draw_me_impl(self, cr):
        crt.cr_circle(x=self.x, y=self.y, r=self.r, context=cr,
                      **self.kwargs) 
        if kw.get(self.kwargs, 'debug', default=False): 
            crt.cr_text(context=cr, ox=0, oy=0,
                        msg=f'{self.get_trans()}', fsize=CFSIZE)#debug
            crt.cr_text(context=cr, ox=0, oy=2*CFSIZE, fsize=CFSIZE,
                        msg=f'box_={ self.box }') #debug
        if kw.get(self.kwargs, 'show_native_origin', default=False): 
            crt.cr_draw_marker_cross(context=cr, x=0, y=0, 
                                     linewidth=0.5, angle=math.pi*0.0, 
                                     rgb=crt.cr_add_alpha(crt.MYCOL['blue'], alpha=0.5))
        return 

# class DrawCircle(DrawCommandBase):
#     """描画演算オブジェクトのクラス．DrawCommandBaseクラスのサブクラス．

#     Args: 
#           x (float) : 円の中心位置のx座標．default=0.0. 

#           y (float) : 円の中心位置のy座標．default=0.0. 

#           r (float) : 円の半径．必須．

#           **kwargs (dict) : 上位コマンドに渡すオプション引数．
#     """
#     def __init__(self, **kwargs):
#         kwargs['x'] = kw.get(kwargs, 'x', default=0.0)
#         kwargs['y'] = kw.get(kwargs, 'y', default=0.0)
#         super().__init__(cmd='circle', **kwargs)
#         return 

#     #Override 
#     def arrange_box_self(self):
#         x = kw.get(self.kwargs, 'x', required=True)
#         y = kw.get(self.kwargs, 'y', required=True)
#         r = kw.get(self.kwargs, 'r', required=True)
#         self.box = (x-r, y-r, x+r, y+r)
#         return 
        
#     #Override 
#     def draw_me_impl(self, cr):
#         # Note: self.kwargs contains keys 'x', 'y', 'r'. 
#         crt.cr_circle(context=cr, **self.kwargs) 
#         if kw.get(self.kwargs, 'debug', default=False): 
#             crt.cr_text(context=cr, ox=0, oy=0,
#                         msg=f'{self.get_trans()}', fsize=CFSIZE)#debug
#             crt.cr_text(context=cr, ox=0, oy=2*CFSIZE, fsize=CFSIZE,
#                         msg=f'box_={ self.box }') #debug
#         if kw.get(self.kwargs, 'show_native_origin', default=False): 
#             crt.cr_draw_marker_cross(context=cr, x=0, y=0, 
#                                      linewidth=0.5, angle=math.pi*0.0, 
#                                      rgb=crt.cr_add_alpha(crt.MYCOL['blue'], alpha=0.5))
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
        self.commands = []
        return 

    #Override 
    def arrange_box_self(self):
        #命令全ての包含長方形を計算する
        _boxes = EMPTY_RECT
        for idx, pair in enumerate(self.commands):
            cmd, x, y, _ = pair #分解
            _boxes = crt.box_union(_boxes, (x, y))
        self.boxes = self.box = _boxes
        if True: print(f'@debug:polyline: self.box={self.box}')
        return 

    #Override 
    def draw_me_impl(self, cr):
        crt.cr_set_context_parameters(context=cr, **self.kwargs)
        x_last, y_last = None, None 
        for idx, pair in enumerate(self.commands):
            cmd, x, y, has_arrow = pair #分解
            if cmd==CMD_MOVE:
                if self.verbose:
                    kwargs={ 'x':x, 'y': y, }
                    self.repo(is_child=True, msg=f'@debug: cr_move_to: { kwargs }')
                crt.cr_move_to(x, y, context=cr)
            elif cmd==CMD_LINE:
                if self.verbose:
                    kwargs={ 'x':x, 'y': y, 'has_arrow': has_arrow,
                             'x_last': x_last, 'y_last': y_last, }
                    self.repo(is_child=True, msg=f'@debug: cr_line_to: { kwargs }')
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

    def move_to(self, x, y) -> BoardBase:
        """ペンを位置`(x,y)`に移動する．直線は引かない．
        Args: 

              x (float) : x- and y-coodinates

              y (float) : x- and y-coodinates

        Returns:
              (Board) : 自分自身．いわゆる'cascade object call interface' のため．
        """
        has_arrow = False
        self.commands.append((CMD_MOVE, x, y, has_arrow))
        return self #for cascade object interface 
    
    def line_to(self, x, y, has_arrow=False) -> BoardBase:
        """ペンを現在位置から目標位置`(x,y)`まで移動して，直線を引く．

        Args: 

              x (float) : x- and y-coodinates

              y (float) : x- and y-coodinates

        Returns:
              (Board) : 自分自身．いわゆる'cascade object call interface' のため．

        """
        self.commands.append((CMD_LINE, x, y, has_arrow)) 
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
        self.ticklen = ticklen = kw.get(kwargs, 'ticklen', default=4.0)
        self.linewidth = linewidth = kw.get(kwargs, key='linewidth',
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

