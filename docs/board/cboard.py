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
        self.trans = None #自身の変換
        self.box   = None #自身の包含矩形.
        self.boxes = None #子全体の包含矩形.
        
        if self.verbose:
            self.repo(msg=f'{self.myinfo()}.__init__(): { self.vars() }')
        return

    # exp 基本：子を追加する
    def put(self, child=None, trans=None): 
        """子を追加する．

        Args: 
            trans (cairo.Matrix) : 自座標における子の配置を指示する変換行列．原点にある子を所望の場所に配置するためのアフィン変換を表す．

            child (Board): 子として追加するBoardオブジェクト

        Returns:
            (Board) : 追加した子
        
        Example:: 
        
        		root = Canvas()
        		child = root.put(Board())
        		child = parent.put(trans=Translate(x=1, y=2), 
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
    # 雑関数
    #=====

    def get_box(self):
        _box = self.box 
        com.ensure(_box!=None and crt.isProperBox(_box),
                   f'get_box: box={_box} must be isProperBox')
        return _box

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
        self._arrange_children_boxes()
            
        #注意：関数arrange_self_transformはサブクラスでオーバーライドする
        self._arrange_self_box()

        if True:
            print(f'@debug:trans:{self.myinfo()}: trans={self.trans}')
        if self.verbose:
            self.repo(msg=f'{self.myinfo()}._arrange()=> box={ boxes }', isChild=True)
        com.ensure(self.box != None, f'self.box={self.box} != None!')
        return self.box 

    def _arrange_apply_children(self):
        """自身の子すべてに対して，再帰的に配置を行う．
        次の属性を操作する: 

        * self.children_: 読み出し
        """
        for idx, pair in self.children_enumerated():
            trans, child = pair_normalize(pair)
            if self.verbose: self.repo(msg=f'=> call _arrange() on {idx}-th child={child.myinfo()}', isChild=True, header=False)
            
            child._arrange() #再帰的に子の配置を実行
            
            com.ensure(child.get_box() != None,
                       f'child.get_box()={child.get_box()} != None')
        return 

    def _arrange_children_boxes(self):
        """自身の子すべてを再配置する．必ず終わりにself.boxesを設定すること．
        次の属性を操作する: 

        * self.children_: 読み出し
        * self.boxes    : 書き込み
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
        return 
        
    #To be Override
    def _arrange_self_box(self):
        """アンカー情報から，変換と包含矩形を計算する．子孫クラスでオーバーライドすること
        次の属性を操作する: 

        * self.boxes  : 読み出し．非None．
        * self.box    : 書き込み．非None．
        * self.trans  : 書き込み．Noneも許す．
        """
        self.box = self.boxes
        return 
        
    # #Override 
    # def _arrange_self_box(self):
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
            self.repo(isChild=True, msg=f'{self.myinfo()}._draw(): { self.vars() }')
            
        ## 自分の空間を開く
        cr.save()  ##self
        ## 自身の変換を適用する
        crt.cr_apply_trans(trans=self.trans, context=cr)
        if True: print(f'@debug:draw:self:{self.myinfo()}: apply trans={self.trans}')
            
        #必要なら自分の描画を行う
        self.draw_me(cr)
        
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
        self.draw_me_post(cr)

        ## 自分の空間を閉じる
        cr.restore()  ##self

        ## debug: 包含矩形を描画する
        self.draw_origin_and_box(cr) #自分の原点位置と包含矩形を描画する．
        return

    # 派生：Override
    def draw_me(self, cr):
        """自分の描画を行う．子孫クラスでオーバーライドすること．

        Args: 
             cr (Cairo.Context) : Cairoの文脈オブジェクト
        """
        if self.verbose: self.repo(isChild=True,
                                   msg=f'{self.myinfo()}.draw_me()...')
        ## ここでcontext crに何か描く．
        return 

    # 派生：Override
    def draw_me_post(self, cr):
        """自分の描画を行う．子孫クラスでオーバーライドすること．

        Args: 
             cr (Cairo.Context) : Cairoの文脈オブジェクト
        """
        if self.verbose: self.repo(isChild=True,
                                   msg=f'{self.myinfo()}.draw_me()...')
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
        crt.cr_text(tx + fmargin, ty + 1.0*dy + fmargin, msg=msg, fsize=fsize, 
                    context=cr)
        return 

    #==========
    # 座標系
    #==========
    def get_anchor_point(self, anchor=None):
        """アンカー指定から，自身の包含矩形上の対応する点を返す．

        Args: 
             anchor (tuple(str,str)) : x方向とy方向の位置指示

        Returns: 
             (tuple(float, float)) : アンカー点 point = (x,y)
        """
        ## exp: アンカー情報を用いて，変換transを求める
        
        # アンカーキーワードから，アンカー比率を返す．
        ratio = crt.get_anchor_ratio(anchor=anchor)
        com.ensure(self.get_box() != None, f'self.box is None!')
        point = crt.get_point_by_anchor_ratio(self.box, ratio=ratio)
        com.ensure(isProperPoint(point),
                   f'point={point} must be a pair of numbers')
        return point 

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
         anchor (tuple(str, str)) : x方向とy方向の原点位置指示. 

         **kwargs : 他のキーワード引数．上位クラスに渡される．

    Notes: anchor = (anchor_x, anchor_y)は次の値をとる
    
         anchor_x (str) : 横方向の位置指示 in (left, middle, right)

         anchor_y (str) : 縦方向の位置指示 in (top, middle, bottom, above, below)

    """
    
    # def __init__(self, anchor_x=None, anchor_y=None, anchor=None, **kwargs):
    def __init__(self, anchor=None, **kwargs):
        #引数
        super().__init__(**kwargs)
        
        #アンカーのデフォールト設定
        self.anchor = anchor_normalize(anchor=anchor, default=('left','top'))

        #内部変数
        # self.anchor_ratio = None
        
        if self.verbose:
            self.repo(msg=f'{self.myinfo()}.__init__(): { self.vars() }')
        return

    #To be Override
    def _arrange_self_box(self):
        """アンカー情報から，変換と包含矩形を計算する．子孫クラスでオーバーライドする．
        次の属性を操作する: 

        * self.boxes  : 読み出し
        * self.box    : 書き込み
        * self.trans  : 書き込み
        """
        _trans, _box = None, None #変数
        com.ensure(self.boxes != None, f'self.boxes={self.boxes} is None!')
        _boxes = self.boxes
        # _trans, _box = None, _boxes
        
        # アンカーキーワードから，アンカー点src in R^2を求める．
        com.ensure(self.anchor!=None, f'self.anchor={self.anchor} is None!')
        _ratio = crt.get_anchor_ratio(anchor=self.anchor)
        src = crt.get_point_by_anchor_ratio(_boxes, ratio=_ratio)

        # アンカー点を原点に写す変換_transを求める．
        _trans = crt.Translate(source=src) ##新しい変換
        self.trans = _trans
        # x, y = crt.get_point_by_anchor_ratio(_boxes, ratio=_ratio)
        # _trans = crt.Translate(0.0 - x, 0.0 - y) ##新しい変換

        ##新しい変換で包含矩形を変換する
        _box = crt.box_apply_trans(_boxes, trans=_trans)
        self.box = _box
        
        if True: print(f'@debug:arrange_self_transform:{self.myinfo()}: ratio={ _ratio } => src={src} trans={self.trans}: box0={_boxes} => box={_box}')
        return 

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
                 imgtype=crt.DEFAULT_IMGTYPE, #cairoのSurface format
                 # imgtype=cairo.FORMAT_ARGB32, #cairoのSurface format
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

    def canvas_size(self):
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
          child (BoardBase) : 子として保持するBoardBaseオブジェクト．

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
        ## 包み込む唯一の子を設定する
        com.ensure(child != None, f'child must be to None!')
        child.parent = None ##使用済みの子から親への参照を切る．破壊的代入．        
        self.put(trans=None, child=child)   #子に追加

        ## メソッド転送設定
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
            self.trans = crt.Translate((-1)*x0, (-1)*y0)
            self.box = crt.box_apply_trans(child_box, trans=self.trans)
                
        if self.verbose:
            self.repo(msg=f'{self.myinfo()}._arrange()=> box={ boxes }', isChild=True)
        return self.box 

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

def numpair_normalize(margin=None, default=None):
    """マージン指定を正規化する．margin が数の対(float,float)ならばそのまま返し，
    margin が数ならば，(margin,margin)を返す．
    margin==Noneのときは，(0.0,0.0)を返す．
    """
    if margin==None:
        margin = com.ensure_defined(value=default,
                                    default=(0.0, 0.0))
    elif isinstance(margin, (float,int)): 
        margin = (margin, margin)
    elif com.is_sequence_type(margin, elemtype=(float,int), length=2):
        pass
    else:
        com.panic(f'margin={margin} must be either num or (num,num)!')
    return margin
    
def anchor_normalize(anchor=None, default=None):
    """アンカー指定を正規化する．anchor がstrの対(str,str)ならばそのまま返し，
    anchor がstrならば，(anchor,anchor)を返す．
    anchor==Noneのときは，デフォールト値(left,top)を返す．
    """
    if anchor==None:
        anchor = com.ensure_defined(value=default,
                                    default=('left', 'top'))
    elif isinstance(anchor, str):
        anchor = (anchor, anchor)
    elif com.is_sequence_type(anchor, elemtype=(str), length=2):
        pass 
    else:
        com.panic(f'anchor={anchor} must be either str or (str,str)!')
    return anchor 

# class PackerBoard(AnchorBoard):
class PackerBoard(Board):
    """画盤（board）のクラス．Boardのサブクラス

    Args: 
         align (str) : 並べる主軸方向の指定．`x`または`y`の値をとる．default='x'

         packing (str) : 内部のボードの詰め方の指定情報. packing in ('even','pack')

         width (float) : 自身の幅．default=None. 

         height (float) : 自身の高さ．default=None. 

    	 kwargs : 他のキーワード引数．上位クラスに渡される．
    """
    def __init__(self,
                 align='x',
                 # pack=False,
                 margin=None,
                 packing=None, 
                 ##
                 # pack_anchor=None,
                 # expand=False,
                 width=None,
                 height=None, 
                 **kwargs):
        #引数
        super().__init__(**kwargs)
        
        #内部変数
        ## マージン設定
        self.mshape = numpair_normalize(margin) #margin-shape
        self.packing = packing 
        
        #内部変数
        self.align = align
        self.width = width
        self.height= height
        
        
        #debug
        if self.verbose:
            self.repo(msg=f'{self.myinfo()}.__init__(): { self.vars() }')
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
        return self.put(trans=None, child=child) #exp
        # wrapper = WrapperBoard(child=child)
        # return self.put(trans=None, child=wrapper)

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

    def _get_axes(align=None):
        """与えられた文字列align (str)に応じて，主軸と副軸の添字の対 AX_PRI, AX_SEC を返す．
        """
        if align in ('x'):   ax_pri, ax_sec = 0, 1
        elif align in ('y'): ax_pri, ax_sec = 1, 0
        else: com.panic(f'no such align={ align }!')
        return ax_pri, ax_sec 
    
    #To be Override
    def _arrange_children_boxes(self, **kwargs):
        """自身の子すべてを再配置する．必ず終わりにself.boxesを設定すること．
        次の属性を操作する: 

        * self.children_
        * self.boxes
        """
        ## 軸の設定: Primary, secondary
        ax_pri, ax_sec = PackerBoard._get_axes(self.align)

        # 第1回目のパス: 子の包含矩形のサイズの最大と総和を求める
        _max_shape, _, _ = PackerBoard._accumulate_boxes(self.children_box_enumerated())

        # 内部の子ボードの形状サイズ指定
        _ishape = [None, None] #内部のさや(pod)の形状サイズ．可変データ
        com.ensure(com.is_sequence_type(_max_shape, elemtype=(float,int),
                                        length=2, verbose=True),
                   f'max_shape={_max_shape} must have type (num, num)!')
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
            trans1 = crt.Translate(x=_child_pos[0], y=_child_pos[1])

            #子を新たに生成したラッパーで包み，子リストに再登録する
            child1 = WrapperBoard(child=child, **PackerBoard._debug_wrapper) #デバッグ用
            self.set_child_by_idx(idx=idx, pair=(trans1, child1)) #子を追加

            #子の配置情報の計算
            child1._arrange() #再帰的に処理

            #自身の包含矩形の計算
            box0 = child1.get_box()
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
                
            if True: print(f'@debug:pack:align={self.align} pos={ _old_child_pos } => pos_new={ _child_pos }')
        
        #exp 自身の情報を更新
        self.boxes   = _boxes
        com.ensure(crt.isProperBox(self.boxes),
                   f'self.boxes={self.boxes} must be a box!')
        return self.box
    
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
    def _arrange_self_box(self):
        x = kw.get(self.kwargs, 'x', required=True)
        y = kw.get(self.kwargs, 'y', required=True)
        width = kw.get(self.kwargs, 'width', required=True)
        height = kw.get(self.kwargs, 'height', required=True)
        self.box = (x, y, x+width, y+height)
        return 
        # return box 
        
    #Override 
    def draw_me_impl(self, cr):
        crt.cr_rectangle(context=cr, **self.kwargs)
        if kw.get(self.kwargs, 'debug', default=False): 
            crt.cr_text(context=cr, ox=0, oy=0,
                        msg=f'{self.trans}', fsize=CFSIZE) #debug
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
    def __init__(self, **kwargs):
        kwargs['x'] = kw.get(kwargs, 'x', default=0.0)
        kwargs['y'] = kw.get(kwargs, 'y', default=0.0)
        super().__init__(cmd='circle', **kwargs)
        return 

    #Override 
    def _arrange_self_box(self):
        x = kw.get(self.kwargs, 'x', required=True)
        y = kw.get(self.kwargs, 'y', required=True)
        r = kw.get(self.kwargs, 'r', required=True)
        self.box = (x-r, y-r, x+r, y+r)
        return 
        
    #Override 
    def draw_me_impl(self, cr):
        # Note: self.kwargs contains keys 'x', 'y', 'r'. 
        crt.cr_circle(context=cr, **self.kwargs) 
        if kw.get(self.kwargs, 'debug', default=False): 
            crt.cr_text(context=cr, ox=0, oy=0,
                        msg=f'{self.trans}', fsize=CFSIZE)#debug
            crt.cr_text(context=cr, ox=0, oy=2*CFSIZE, fsize=CFSIZE,
                        msg=f'box_={ self.box }') #debug
        if kw.get(self.kwargs, 'show_native_origin', default=False): 
            crt.cr_draw_marker_cross(context=cr, x=0, y=0, 
                                     linewidth=0.5, angle=math.pi*0.0, 
                                     rgb=crt.cr_add_alpha(crt.MYCOL['blue'], alpha=0.5))
        return 


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
    def _arrange_self_box(self):
        #命令全ての包含長方形を計算する
        _boxes = EMPTY_RECT
        for idx, pair in enumerate(self.CMDS):
            cmd, x, y, _ = pair #分解
            _boxes = crt.box_union(_boxes, (x, y))
        self.boxes = self.box = _boxes
        if True: print(f'@debug:polyline: self.box={self.box}')
        return 

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

