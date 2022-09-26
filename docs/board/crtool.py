# coding: utf_8
# btest1.py
"""Cairoライブラリの描画機能を提供するモジュール．

Attributes: 

  FONT_SLANT (dict(str, cairo.FontSlant)) : 
    フォントの斜体スタイルを表す定数の辞書．次の値をもつ

    * 'italic': cairo.FontSlant.ITALIC
    * 'normal': cairo.FontSlant.NORMAL
    * 'oblique': cairo.FontSlant.OBLIQUE

  FONT_WEIGHT  (dict(str, cairo.FontWeight)) : 
    フォントの太字スタイルを表す定数の辞書．次の値をもつ．

    * 'bold': cairo.FontWeight.BOLD
    * 'normal': cairo.FontWeight.NORMAL

  LINE_CAP (dict(str, Object)) : 
    線の終端のスタイルを表す定数の辞書．次の値をもつ．

    * 'square': cairo.LINE_CAP_SQUARE
    * 'round': cairo.LINE_CAP_ROUND
    * 'butt': cairo.LINE_CAP_BUTT

  LINE_JOIN (dict(str, Object)) : 
    線の結合部のスタイルを表す定数の辞書．次の値をもつ．

    * 'miter': cairo.LINE_JOIN_MITER
    * 'round': cairo.LINE_JOIN_ROUND
    * 'bevel': cairo.LINE_JOIN_BEVEL

  ANCHOR_X (dict(str, float)) : 
    位置合わせ用のx方向のアンカー値を表す定数の辞書．範囲`[0,1]`の値をとり，辺上の正規化された位置を表す．複数の別名を提供している．

    * 'left'   : 0.0, 'center'  : 0.5, 'right'  : 1.0, #標準名
    * 'beg' : 0.0, 'mid' : 0.5, 'end' : 1.0, #xとy方向の共通名

  ANCHOR_Y  (dict(str, float)) : 
    位置合わせ用のy方向のアンカー値を表す定数の辞書．範囲`[0,1]`の値をとり，辺上の正規化された位置を表す．複数の別名を提供している．

    * 'top'    : 0.0, 'middle' : 0.5, 'bottom' : 1.0, #標準名
    * 'bot' : 1.0, 'above'  : 0.0, 'below'  : 1.0, #別名
    * 'beg' : 0.0, 'mid' : 0.5, 'end' : 1.0, #xとy方向の共通名

  MYCOL (dict(str, (float,float,float))) : 
    色を表す定数の辞書．色名の文字列に，RGB表現の三つ組$(r,g,b) \in [0,1]^3$を対応させる．

    * pure color: 'red':(1,0,0),'blue':(0,0,1),'lightgreen':(0,1,0),
    * basic color: 'yellow':(1,1,0),'magenta':(1,0,1),'cyan':(0,1,1),
    * dark color: 'darkgreen':(0,0.5,0),'darkred':(0.5,0,0),'darkblue':(0,0,0.5),
    * alias color: 'green':(0,0.5,0),'brown':(0.5,0,0),'navy':(0,0,0.5),'orange':(1.0 - 0.125, 0.0 + 0.125, 0.0),
    * black-and-white: 'black':(0,0,0), 'grey0':(0,0,0), 'grey10':(0.10,0.10,0.10), 'grey25':(0.25,0.25,0.25), 'grey50':(0.50,0.50,0.50), 'grey75':(0.75,0.75,0.75), 'grey100':(1,1,1), 'white':(1,1,1). 

  DARKCOL (dict(str, (float,float,float))) : 
    色を表す定数の辞書．色名の文字列に，RGB表現の三つ組$(r,g,b) \in [0,1]^3$を対応させる．

        * pure color: 'red':(1,0,0),    'blue':(0,0,1),
        * dark color: 'darkgreen':(0,0.5,0), 'darkred':(0.5,0,0),    'darkblue':(0,0,0.5),    'orange':(1.0 - 0.125, 0.0 + 0.125, 0.0),
        * black-and-white:     'black':(0,0,0),     'grey0':(0,0,0),     'grey10':(0.10,0.10,0.10),     'grey25':(0.25,0.25,0.25),     'grey50':(0.50,0.50,0.50),     'grey75':(0.75,0.75,0.75),     'grey100':(1,1,1), 
  
"""
import sys
import math 
from typing import Any, NoReturn
import cairo 

import common as com 
import kwargs as kw

verbose = True

## 定数：画像サイズ
DISPLAY_SHAPE = {
    'QVGA': (320, 240),
    'VGA' : (640, 480), 
    'SVGA': (800, 600), 
    'XGA' : (1024, 768), #default size
    'WXGA': (1280, 800), 
    'UXGA': (1600, 1200), 
    'QXGA': (2048, 1536),
}
DEFAULT_DISPLAY_SHAPE=(640, 480)
DEFAULT_IMAGE_SIZE='XGA' #obsolute 

#Cairo定数
DEFAULT_IMGTYPE=cairo.FORMAT_ARGB32, #cairoのSurface format

FONT_SLANT = {
    'italic': cairo.FontSlant.ITALIC, #pycairo
    'normal': cairo.FontSlant.NORMAL, #pycairo
    'oblique': cairo.FontSlant.OBLIQUE, #pycairo
}

FONT_WEIGHT = {
    'bold': cairo.FontWeight.BOLD, #pycairo
    'normal': cairo.FontWeight.NORMAL, #pycairo
}

LINE_CAP = {
    'square': cairo.LINE_CAP_SQUARE, #pycairo
    'round': cairo.LINE_CAP_ROUND,   #pycairo
    'butt': cairo.LINE_CAP_BUTT,     #pycairo
}

LINE_JOIN = {
    'miter': cairo.LINE_JOIN_MITER, #pycairo
    'round': cairo.LINE_JOIN_ROUND,   #pycairo
    'bevel': cairo.LINE_JOIN_BEVEL,     #pycairo
}

#色
fancy = ['lightskyblue', 'lightgreen', 'lightgrey']
solid = ['red', 'lightcoral', 'orange', 'darkorchid', 'royalblue', ]

MYCOL={
    ## pure 
    'red':(1,0,0),
    'blue':(0,0,1),
    'lightgreen':(0,1,0),
    ## basic
    'yellow':(1,1,0),
    'magenta':(1,0,1),
    'cyan':(0,1,1),
    ## dark 
    'darkgreen':(0,0.5,0),
    'darkred':(0.5,0,0),
    'darkblue':(0,0,0.5),
    ## alias
    'green':(0,0.5,0),
    'brown':(0.5,0,0),
    'navy':(0,0,0.5),
    'orange':(1.0 - 0.125, 0.0 + 0.125, 0.0),
    ## bw
    'black':(0,0,0), 
    'grey0':(0,0,0), 
    'grey10':(0.10,0.10,0.10), 
    'grey25':(0.25,0.25,0.25), 
    'grey50':(0.50,0.50,0.50), 
    'grey75':(0.75,0.75,0.75), 
    'grey100':(1,1,1), 
    'white':(1,1,1),
}

DARKCOL={
        ## pure 
        'red':(1,0,0),
        'blue':(0,0,1),
        ## basic
        # 'magenta':(1,0,1),
        ## dark 
        'darkgreen':(0,0.5,0),
        'darkred':(0.5,0,0),
        'darkblue':(0,0,0.5),
        'orange':(1.0 - 0.125, 0.0 + 0.125, 0.0),
        ## bw
        'black':(0,0,0), 
        'grey0':(0,0,0), 
        'grey10':(0.10,0.10,0.10), 
        'grey25':(0.25,0.25,0.25), 
        'grey50':(0.50,0.50,0.50), 
        'grey75':(0.75,0.75,0.75), 
        'grey100':(1,1,1), 
}

DEFAULT_HEAD_SHAPE = 'sharp'

## 軸
ORIENT_X = {
    'x' : True, 
}
ORIENT_Y = {
    'y' : True, 
}

## 位置合わせ
ANCHOR_STR_ORIGIN = ('left','top') #左上のアンカー指定
ANCHOR_STR_CENTER = ('mid','mid') #中央のアンカー指定
DEFAULT_ANCHOR_STR = ANCHOR_STR_ORIGIN
DEFAULT_ANCHOR_VALUE = 0.5 #not used 

ANCHOR_X = {
    'left'   : 0.0, 
    'center' : 0.5, 
    'right'  : 1.0,
    ## uni
    'beg' : 0.0, 
    'mid' : 0.5, 
    'end' : 1.0, 
}
ANCHOR_Y = {
    'top'    : 0.0, 
    'middle' : 0.5, 
    'bottom' : 1.0, 
    ## uni
    'beg' : 0.0, 
    'mid' : 0.5, 
    'end' : 1.0, 
    ## alt
    'bot' : 1.0, 
    ## alt
    'above'  : 0.0, 
    'below'  : 1.0, 
}

#==========
# 便利関数
#==========

#===========
# vector 
#===========
def vt_add(vec0, vec1):
    """二つのベクトルvec0, vec1の成分和のベクトル`vec0 + vec1`を返す．
    
    Args: 
         vec0 (tuple(float,float)) : vec0 = (x0, y0)

         vec1 (tuple(float,float)) : vec1 = (x1, y1)

    Returns: 
         (tuple(float,float)) : vec = (x0+x1, y0+y1)
    """
    com.ensure_point(vec0, name='vec0')
    com.ensure_point(vec1, name='vec1')
    return vec0[0]+vec1[0], vec0[1]+vec1[1]

def vt_sub(vec0, vec1):
    """二つのベクトルvec0, vec1の成分差のベクトル`vec0 - vec1`を返す．
    
    Args: 
         vec0 (tuple(float,float)) : vec0 = (x0, y0)

         vec1 (tuple(float,float)) : vec1 = (x1, y1)

    Returns: 
         (tuple(float,float)) : vec = (x0-x1, y0-y1)
    """
    return vt_add(vec0, vt_scale(vec1, scale=(-1.0)))

def vt_mult(vec0, vec1):
    """二つのベクトルvec0, vec1の成分ごと積のベクトル`vec0 * vec1`を返す．
    
    Args: 
         vec0 (tuple(float,float)) : vec0 = (x0, y0)

         vec1 (tuple(float,float)) : vec1 = (x1, y1)

    Returns: 
         (tuple(float,float)) : vec = (x0*x1, y0*y1)
    """
    com.ensure_point(vec0, name='vec0')
    com.ensure_point(vec1, name='vec1')
    return vec0[0]*vec1[0], vec0[1]*vec1[1]

def vt_scale(vec0, scale=None):
    """ベクトルvec0とスカラーscaleの積のベクトル`scale * vec0`を返す．
    
    Args: 
         vec0 (tuple(float,float)) : ベクトル vec0 = (x0, y0)

         scale (num) : スカラー

    Returns: 
         (tuple(float,float)) : vec = (scale*x0, scale*y0)
    """
    com.ensure_point(vec0, name='vec0')
    if scale==None:
        return vec0
    else:
        com.ensure(isinstance(scale, (float,int)),
                   f'scale={scale} must be a number!')
        return vec0[0]*scale, vec0[1]*scale 

##=====
## ヘルパー関数： 座標と座標変換
##=====

# # # * val = ensureAnchorPoint(val:Any, default:Any, nullable:bool) -> tuple

##=====
## old: ヘルパー関数： 座表と座表変換
##=====

# def isBoxOrPoint(box):
#     """与えられたオブジェクトboxが，点または矩形かどうかを返す．

#     Args: 

#          box (tuple) : オブジェクト

#     Returns: 

#          (bool) : boxが，点または矩形ならばTrue, それ以外ならばFalse. 
#     """
#     if box==None:
#         return False
#     elif com.is_typeof_seq(box, etype=(float,int)): 
#         if (len(box) == 2) or (len(box) == 4):
#             return True
#         else:
#             return False
#     else:
#         return False

# def isProperPoint(box):
#     """与えられたオブジェクトboxが，点かどうかを返す．後方互換性のため実装．"""
#     value = com.ensure_vector(value=box, to_check_only=True, 
#                           etype=(float,int), dim=2)
#     if value==None: return False
#     else: return True


# def isProperBox(box):
#     """与えられたオブジェクトboxが，点かどうかを返す．後方互換性のため実装．"""
#     value = com.ensure_vector(value=box, to_check_only=True, 
#                           etype=(float,int), dim=4)
#     if value==None: return False
#     else: return True


def box_normalize(box):
    """4座標（矩形）からなる正しい矩形であることを検査し，2座標（点）なら4座標に正規化する．
    """
    com.ensure_box(box, name='box', nullable=False) 
    # if len(box)==2:
    #     box = (box[0], box[1], box[0], box[1])
    x0, y0, x1, y1 = box
    com.ensure((x1 - x0 >= 0) and (y1 - y0 >= 0),
               f'box must a properbox: box={box}')
    return box

def box_from_shape(shape=None, origin=None):
    """形状shape=(sx, sy)を受け取り，矩形 box = (x0, y0, x1, y1)を返す．
    """
    com.ensure_point(shape, name='shape', nullable=False) 
    if origin==None:
        origin = 0.0, 0.0
    else:
        com.ensure_point(origin, name='origin') 
    x0, y0 = origin
    x1, y1 = vt_add(origin, shape)
    return x0, y0, x1, y1 

def box_to_shape(box):
    """矩形 box = (x0, y0, x1, y1)を受け取り，その幅widthと高さheightを返す．
    """
    x0, y0, x1, y1 = box_normalize(box)
    width, height = x1 - x0, y1 - y0
    return width, height

#長方形の和（最小包含矩形）
def box_union(boxes, box1, verbose=False):
    """矩形の対を受け取り，それらの最小包含長方形を表す対を返す．

    Args: 
    	 boxes, box1 : 点 (x0, y0) または矩形 (x0, y0, x1, y1)

    Returns: 
	 rect: 矩形 box = [p, q]
"""
    com.ensure(boxes != None, f'box_union: boxes must be non-None!')
    if box1 == None:
        return boxes 
    else: 
        boxes = box_normalize(boxes)
        box1 = box_normalize(box1)
        x0 = min(boxes[0], box1[0])
        y0 = min(boxes[1], box1[1])
        x1 = max(boxes[2], box1[2])
        y1 = max(boxes[3], box1[3])
        return (x0, y0, x1, y1)

#=====
# アンカー処理
#=====

def _anchor_str_normalize(anchor_str=None, default=None):
    """アンカー記述（アンカー文字列，または，その対）を受け取り，アンカー文字列対を返す．値が`None`ならば，デフォールト値を返す．
    """
    if anchor_str==None:
        anchor_str = com.ensure_defined(value=default,
                                        default=ANCHOR_STR_ORIGIN)
    elif isinstance(anchor_str, str):
        anchor_str = (anchor_str, anchor_str)
    elif com.is_typeof_seq(anchor_str, etype=(str), dim=2):
        pass 
    else:
        com.panic(f'anchor_str={anchor_str} must be either str or (str,str)!')
    return anchor_str

def _anchor_str_to_normal_value(adict=None, key=None, strict=False):
    """アンカー値の辞書`adict`とアンカー文字列`key`を受け取り，対応する正規化アンカー値`aval in [0,1]`を返す．
    """
    if key!=None and key in adict:
        return adict[key]
    elif strict:
        com.panic(f'no such anchor_value for key={key}')
    else:
        return DEFAULT_ANCHOR_VALUE

def anchor_vector(anchor_str=None, default=None, strict=False):
    """文字列対によるアンカー表記を受け取り，対応する正規化アンカーベクトル`a = (ax,ay) in [0,1]^2`を返す．

    Args:
         anchor_str (str, tuple(str,str)) : 文字列対によるアンカー表記．それ自体が`None`でも良いし，対の片方または両方の要素が`None`を取っても良い．

         default (tuple(str,str)) : アンカー表記のデフォールト値．`anchor_str==None`のとき，代わりに用いられる．

    Note: 

        アンカー表記の対の要素に`None`を許す．

        * アンカー表記自身が`None`のときは，値としてDEFAULT_ANCHOR_STRをとる．現在は，`ANCHOR_STR_ORIGIN = ('left','top')`である．

        * 対の要素が`None`のときは，値`None`を，`mid`に相当する値`DEFAULT_ANCHOR_VALUE = 0.5`に置き換える．

    Example::

            anchor=('left' , 'top') => (0.0, 0.0)
            anchor=('mid'  , 'mid') => (0.5, 0.5)
            anchor=('right', 'bot') => (1.0, 1.0)
            anchor=('left' ,  None) => (0.0, 0.5)
            anchor=(None   , 'top') => (0.5, 0.0)
    """
    str_pair = _anchor_str_normalize(anchor_str=anchor_str,
                                     default=default)
    ax = _anchor_str_to_normal_value(adict=ANCHOR_X, key=str_pair[0], strict=strict)
    ay = _anchor_str_to_normal_value(adict=ANCHOR_Y, key=str_pair[1], strict=strict)
    return (ax, ay)

def anchor_point_by_vector(box=None, vect=None):
    """矩形`box`において，正規化アンカーベクトル`vect`が表すアンカー点を返す．

    Args: 
         vect (tuple(float, float)) : 正規化アンカー位置`vect=(ax,ay) in [0,1]^2`

    Returns: 
         (tuple(float, float)) : 包含矩形box上の点 a = (ax, ay)
    """
    #boxの準備
    com.ensure_box(box, name='box', nullable=False)
    com.ensure_point(vect, name='vect', nullable=False)
    x0, y0, x1, y1 = box_normalize(box) 
    # compute x-anchor 
    if x1 - x0 == 0:
        ax = x0
    else:
        ax = x0 * (1.0 - vect[0]) + x1 * (vect[0])            
    # compute y-anchor 
    if y1 - y0 == 0:
        ay = y0
    else:
        ay = y0 * (1.0 - vect[1]) + y1 * (vect[1])
    return ax, ay

#==========
# 便利関数
#==========

def get_display_shape(shape=None, portrait=None):
    """入力の画像サイズ指定shapeから， 画像サイズを表す正数の組 shape = (xsize,ysize)を返す．

    Args: 
        shape (str, (float,float)) : 出力画像サイズを表す文字列sizenameまたは正数の組(xsize, ysize)

        portrait (bool) : 画面向きの指定．Trueならば縦長画面か，Falseならば横長画面．default=False. 

    Returns: 
         ((float,float)) : 画像サイズを表す正数の組
    """
    if shape==None: 
        _shape = DEFAULT_DISPLAY_SHAPE
    elif (isinstance(shape, str) and
        shape in DISPLAY_SHAPE): 
        _shape = DISPLAY_SHAPE[shape]
    elif com.is_typeof_seq(shape, etype=(float,int), dim=2):
        _shape = shape
    else:
        com.panic(f'shape={shape} must be either (str) or (number,number)!')

    #長辺の向きの調整: 縦長ならば要素を入れ替える．
    if portrait: 
        _shape = (_shape[1], _shape[0]) 
    return _shape 
        
#==========
#Cairo.context
#==========

# class ImageBoard(log.Loggable):
class ImageBoard:
    """Cairoの文脈(context)の生成と出力を実装するクラス．

    * 本オブジェクトの生成時に，オプション引数を与えると，Cairo.contextを生成し，保持する．
    
    Args: 
         imgtype (str) : 画像フォーマット (cairo)

         format (str) : 出力ファイルの描画フォーマット (cairo) in "pdf", "png"

         display_shape (tuple(int, int)) : 画像のサイズ `(xsize, ysize)`

         outfile (str) : 出力画像ファイル名の本体を表す文字列．例：`out`

         verbose (bool) : デバッグ/実行情報の表示のフラグ

    Attributes: 

         ims (cairo.ImageSurface, cairo.PDFSurface) : Cairoの画像オブジェクト（Surface）を保持する．

         cr (cairo.Context) : Cairoの文脈オブジェクト．関数`context()`で取得し，各種のCairoの描画操作，または，crtoolの描画操作を適用できる．

    """
    def __init__(self,
                 # dep_init=None, 
                 imgtype=cairo.FORMAT_ARGB32, #cairoのSurface format
                 format="pdf",   #出力ファイルフォーマット（拡張子 pdf, png）
                 outfile="out",  #出力ファイル名（拡張子を除く）
                 display_shape=None, 
                 verbose=False):
        """実装レイヤーの画盤を生成するコンストラクタ．
        Args: 
             imgtype (str) : 画像フォーマット (cairo)

             format (str) : 出力ファイルの描画フォーマット (cairo) in "pdf", "png"

             display_shape (tuple(int, int)) : 画像のサイズ `(xsize, ysize)`

             verbose (bool) : 実行情報を表示する
        """
        #親Loggableの初期化
        # super().__init__(dep_init=dep_init, verbose=verbose)
        # super().__init__(dep_init=dep_init, verbose=verbose)
        #パラメータ
        self.imgtype = imgtype
        self.format  = format
        self.outfile = outfile
        self.display_shape = display_shape
        if verbose:
            print(f'ImageBoard.__init__(): { kw.reduce(vars(self)) }')

        #==========
        #準備
        #==========
        if verbose:
            print(f'option: format={ self.format }')
            
        ## 出力ファイルフォーマット
        if self.format=="png": 
            OFILE_EXT = "png"
        elif self.format=="pdf": 
            OFILE_EXT = "pdf"
        else: 
            print(f'the file format={self.format} is not supported; instead use the default format={ "pdf"  }: ')
            self.format = OFILE_EXT = "pdf" #default
            
        ## 出力ファイル名
        if outfile:
            mybody = self.outfile #本体名
        else:
            mybody = "out"
        self.myoutfile = mybody + "." + OFILE_EXT #ファイル名

        ##画像サイズ
        com.ensure(com.is_typeof_seq(self.display_shape, etype=(int, float)),
                   f'display_shape must be a pair of numbers: {display_shape}')
        
        ## Cairoのサーフェースの生成
        """ class cairo.ImageSurface(format, width, height)
        Parameters:	
          format – FORMAT of pixels in the surface to create
          width – width of the surface, in pixels
          height – height of the surface, in pixels
        Returns:	
          a new ImageSurface
        Raises :	
          MemoryError in case of no memory
        """
        if self.format == "png": 
            self.img_surface = cairo.ImageSurface(cairo.FORMAT_ARGB32,
                                          self.display_shape[0],
                                          self.display_shape[1]) #image surface
        elif self.format == "pdf": 
            self.img_surface = cairo.PDFSurface(self.myoutfile,
                                        self.display_shape[0],
                                        self.display_shape[1]) #image surface
        else:
            panic(f'no such a file format={ self.format } is supported!')

        ## CairoのContext (image handle)の生成
        """ class cairo.Context(target)
        Parameters:	target – target Surface for the context
        Returns:	a newly allocated Context
        Raises :	MemoryError in case of no memory
        """
        self.cr = cairo.Context(self.img_surface) 
        return 
                
    def context(self) -> 'cairo.Context':
        """描画ハンドル`self.cr`を返す．

        Returns: 
          (cairo.Context) : Cairoの描画contextオブジェクト 
        """
        if self.cr == None:
            com.panic('画像オブジェクトself.cr==None!')
        return self.cr 

    #============
    #表示
    #============
    # def show(self, noshow=False, verbose=False, depth=0):
    def show(self, noshow=False, verbose=False):
        """画像を，出力ファイルに書き出す．出力ファイル書式は`format`で，出力ファイル名（本体）文字列は`outfile`で，ImageBoardオブジェクトの生成時に指定する．
        """
        if noshow:
            if verbose: print(f'ImageBoard.show()@@: @Warning: skipping show() for pil.Image object due to flag noshow={ noshow }')
            return 

        if verbose:
            print(f'ImageBoard.show()...')
            print(f'@printing an image to "{ self.myoutfile }"...')
        
        if self.format=="png":
            self.img_surface.write_to_png(self.myoutfile)
        elif self.format=="pdf":
            self.cr.show_page()
        else:
            panic(f'the file format={ self.format } is not supported!')
        
        return 
    pass ##end: class Image

#=====
#便利関数
#=====

def cr_add_alpha(rgb=None, alpha=0.0):
    """色指定の三つ組rgbにalpha in [0.0,1.0]を追加する

    Args: 
         rgb (tuple(float, float, float)) : 色を表す3つ組 $(r,g,b) \in [0,1]^3$. 

         alpha (float) : アルファ値を表す実数 in $\alpha \in [0,1]$. 

    Returns: 
         rgb (tuple(float, float, float)) : アルファ値つきの色を表す4つ組 $(r,g,b, a) \in [0,1]^4$. 
    """
    com.ensure(rgb!=None, f'rgb={rgb} must of length 3')
    if len(rgb)==3: 
        return (rgb[0], rgb[1], rgb[2], alpha)
    elif len(rgb)==4: 
        return (rgb[0], rgb[1], rgb[2], rgb[3])
    else:
        panic(f'rgb={rgb} must of length 3 or 4')

def cr_set_source_rgb(source_rgb=None, context=None):
    """contextに色source_rgbを設定する．
    source_rgbはアルファなし(r,g,b)とアルファあり(r,g,b,a)の両方を受け付ける．
    """
    if source_rgb: 
        rgb = source_rgb
    else:
        rgb = (0.5,0.5,0.5) #grey50
    if rgb:
        if len(rgb)==3: 
            context.set_source_rgb(rgb[0], rgb[1], rgb[2])
        elif len(rgb)==4: 
            context.set_source_rgba(rgb[0], rgb[1], rgb[2], rgb[3])
        else:
            panic(f'source_rgb must be (r,g,b) or (r,g,b,a)!: {rgb}')
    return

def lookup_dict(dict=None, key=None, default=None):
    """与えられた辞書を，文字列キーで検索して，値を返す．
    ただし，辞書のキーは小文字化されていることを仮定する．
    このとき，次の点でpython組み込みの辞書と異なる．

    * キー文字列は大文字小文字を区別しないこと. 
    * キーが登録されていなければ引数defaultの値を返すこと．

    Args: 
         dict (dict) : python組み込みの辞書．キーが小文字のみであること．

         key (str) : キー文字列．大文字小文字の別は無視される．

         default (Any) : デフォールト値．

    Returns: 
         (Any) : キーに対応する値．ただし，値が見つからない時は，default値が返される．

    """
    if key != None and key.lower() in dict:
        return dict[key.lower()]
    else:
        return default

def cr_set_font_face(context=None, **kwargs):
    """cairo.ContextにFont Faceを設定する．

    Args: 
         context (cairo.Context) : Cairoの文脈オブジェクト．

         fontfamily (str) : Cairoのフォントファミリー指定．代替キーfont_family, ffamily

         fontslant  (str) : Cairoの斜体指定．値は`('italic', 'normal', 'oblique')`をとる．詳しくは，辞書`crtool.FONT_SLANT`を参照のこと．代替キーfont_slant, fslant．

         fontweight (str) : Cairoの太字指定．値は，`('normal', 'bold')`をとる．詳しくは，辞書`crtool.FONT_WEIGHT`を参照のこと．代替キーfont_weight, fweight．

    """
    ### fontfamily    
    ffamily = kw.get(kwargs, key='fontfamily',
                     altkeys=['font_family', 'ffamily'], default=None)
    ## ffamily must be at least specified
    if ffamily == None: 
        return
    
    ### fontslant
    fslant_ = kw.get(kwargs, key='fontslant',
                    altkeys=['font_slant', 'fslant'], default=None)
    fslant = lookup_dict(FONT_SLANT, key=fslant_, default=cairo.FontSlant.NORMAL)

    ### fontweight
    fweight_ = kw.get(kwargs, key='fontweight',
                     altkeys=['font_weight', 'fweight'], default=None)
    fweight = lookup_dict(FONT_WEIGHT, key=fweight_, default=cairo.FontWeight.NORMAL)

    ### select a fontface 
    context.select_font_face(ffamily, fslant, fweight)
    return 
            
def cr_set_context_parameters(context=None, **kwargs):
    """cairo.Contextに各種パラメータを設定するラッパー関数．各種の代替キーを提供する．

    Args: 
         context (cairo.Context) : Cairoの文脈オブジェクト．

         source_rgb (tuple(float, float, float)) : Cairoの色指定の数の三つ組．代替キー'rgb'

         linewidth (float) : 線幅．代替キー'line_width', 'pen_width'

         linecap (str) : 線端の形状．代替キー'line_cap', 'line_end'

         fontsize (float) : フォントサイズ．代替キー'font_size', 'fsize'. 

         fontfamily (str) : フォントファミリー指定．代替キーfont_family, ffamily．

         fontslant  (str) : フォントの斜体指定．代替キーfont_slant, fslant．値は`('italic', 'normal', 'oblique')`をとる．詳しくは，関数`cr_font_face`を参照のこと．

         fontweight (str) : フォントの太字指定．代替キーfont_weight, fweight．値は，`('normal', 'bold')`をとる．詳しくは，関数`cr_font_face`を参照のこと．
    """
    com.ensure(context!=None, 'context must be non-None!')
    #===== 共通
    ## 色設定
    source_rgb = kw.get(kwargs, key='source_rgb', altkeys=['rgb'], default=None)
    if source_rgb:
        cr_set_source_rgb(source_rgb=source_rgb, context=context)
    #===== 図形
    ## 線幅
    linewidth = kw.get(kwargs, key='linewidth',
                       altkeys=['line_width', 'pen_width'], default=None)
    if linewidth: 
        context.set_line_width(linewidth)

    ## 線端 linecap
    linecap_ = kw.get(kwargs, key='linecap', altkeys=['line_cap', 'line_end'], default=None)
    if linecap_: 
        linecap = lookup_dict(LINE_CAP, key=linecap_, default=cairo.LINE_CAP_SQUARE)
        context.set_line_cap(linecap)
    
    ## 線端 linecap
    linejoin_ = kw.get(kwargs, key='linejoin', altkeys=['line_join', 'line_end'], default=None)
    if linejoin_: 
        linejoin = lookup_dict(LINE_JOIN, key=linejoin_, default=cairo.LINE_JOIN_MITER)
        context.set_line_join(linejoin)
    
    #===== テキスト
    ## フォントファミリー
    cr_set_font_face(context=context, **kwargs)
    
    ## フォントサイズ
    fsize = kw.get(kwargs, key='fontsize', altkeys=['font_size', 'fsize'],
                   default=None)
    if fsize: 
        context.set_font_size(fsize) #default: font_size = 10
    #===== 終わり
    return 

def cr_process_stroke_or_fill(context=None,
                              #fill=None, preserve=None
                              **kwargs):
    """図形描画後の書き出しを行う．

    Args: 
         context (cairo.Context) : Cairoの文脈オブジェクト．

         cmd (str) :  次の命令の一つ: 'stroke', 'fill', 'stroke_preserve', 'fill_preserve'. 

         preserve (bool) : 演算後のパス保持のフラグ．パスを保存するなら`True`, しないなら`False`
    """
    fill     = kw.get(kwargs, 'fill')
    preserve = kw.get(kwargs, 'preserve')
    if fill:
        if fill=='stroke':
            if preserve: 
                context.stroke_preserve()
            else:
                context.stroke()
        elif fill=='fill': 
            if preserve:
                context.fill_preserve()
            else:
                context.fill()
        elif fill=='stroke_preserve': 
            context.stroke_preserve()
        elif fill=='fill_preserve': 
            context.fill_preserve()
        else: 
            panic(f'no such fill command={fill}!')
    else:
        context.stroke()
    return 

#=====
#描画関数
#=====

def cr_move_to(x, y, context=None):
    """ペンを移動する．

    Args: 
         x, y (float) : x- and y-coordinate of the center

    Returns: 
         (Rect) : 包含矩形
    """
    context.move_to(x, y)
    box = (x, y) 
    return box

ARROWHEAD_LENGTH=10
ARROWHEAD_ANGLE=math.pi/9
ARROWHEAD_OFFSET_RATIO=0.3
ARROWHEAD_SUPRESS_OVERHEAD_RATIO=0.95

def cr_arrow_head(x, y, x_last, y_last, context=None,
                  head_shape=None,
                  head_length=ARROWHEAD_LENGTH,
                  head_angle=ARROWHEAD_ANGLE,
                  head_offset_ratio=ARROWHEAD_OFFSET_RATIO,
                  to_surpress_short_head=True, 
                  **kwargs):
    """ペンを移動する．

    Args: 
         x (float) : x-coordinate of the center

         y (float) : y-coordinate of the center

         x_last (float) : 矢印をもつ場合に，前の点の座標を与える．矢印の向きを決める．

         y_last (float) : 矢印をもつ場合に，前の点の座標を与える．矢印の向きを決める．

         context (cairo.Context) : 文脈オブジェクト．必須．

         head_shape (str)    : 矢印頭の形状. 省略時は，`DEFAULT_HEAD_SHAPE='sharp'`. 

         head_length (float) : デフォールトARROWHEAD_LENGTH

         head_angle (float)  : デフォールトARROWHEAD_ANGLE

         head_offset_ratio (float) : デフォールトARROWHEAD_OFFSET_RATIO

         to_surpress_short_head (bool) : 矢印頭と同程度以下の長さの線分に対して矢印頭の描画を省略する．デフォールトTrue
    
    Notes: 

      矢印頭の形状 `head_shape (str)` は次のいずれかの値をとる. 

	- stroke   : 2辺の輪郭線によるV字型の矢印頭
	- triangle : 塗りつぶした二等辺三角形の矢印頭
	- sharp    : 塗りつぶした尖った鏃型の矢印頭．`triangle`の根本が凹んだ形．

      関数`line_to`による線分`(x_last, y_last), (x, y)`の描画時に呼びだされる．
    
    """    
    ## the definitions for innner functions 
    def compute_angle(x, y, x_last, y_last, verbose=False): 
        """The line from x_last, y_last to (x,y)の方向
           line_angle = (cos_angle, sin_angle)を計算する
        """
        x_len, y_len = x - x_last, y - y_last
        line_len = math.sqrt(x_len*x_len + y_len*y_len)
        com.ensure(line_len != 0.0, f'line_len={line_len} > 0 must hold!')
        cos_angle, sin_angle = x_len/line_len, y_len/line_len  ## cos(angle), sin(angle)
        if verbose:
            len_unit = (cos_angle*cos_angle + sin_angle*sin_angle) #for debug
            print(f'@debug: cr_line_to: { x, y, line_len } => { cos_angle, sin_angle, len_unit }')
        return cos_angle, sin_angle, line_len

    def sub_arrow_stroke(x_head, y_head):
        """折れ線で輪郭を書いた矢印頭"""
        #arrowhead
        context.move_to(0, 0); context.line_to(-x_head, y_head);  
        context.move_to(0, 0); context.line_to(-x_head, -y_head);
        context.stroke()
        return 

    def sub_arrow_filled_triangle(x_head, y_head): 
        """塗りつぶした2等辺三角形の矢印頭"""
        context.move_to(0, 0);
        context.line_to(-x_head, y_head);  #arrowhead
        context.line_to(-x_head, -y_head); #arrowhead
        context.line_to(0, 0);
        context.fill()
        return 

    def sub_arrow_filled_sharp(x_head, y_head): 
        """塗りつぶした尖った2等辺4辺形の矢印頭"""
        context.move_to(0, 0);
        context.line_to(-x_head, y_head);  #arrowhead
        context.line_to(-x_head + (head_length*head_offset_ratio), 0.0);  #arrowhead
        context.line_to(-x_head, -y_head); #arrowhead
        context.line_to(0, 0);
        context.fill()
        return 

    ## 矢印処理
    com.ensure(com.is_typeof_seq((x, y, x_last, y_last), etype=(float, int)),
               f'crtool.cr_arrow_head: x, y, x_last, y_last'+
               f'={ x, y, x_last, y_last } must be float or int!')
    #lineの方向line_angleを計算する
    if False: print(f'@debug: cr_arrow_head: kwargs={ kwargs }')
    cos_angle, sin_angle, line_len = compute_angle(x, y, x_last, y_last)
    
    context.save()
    cr_set_context_parameters(context=context, **kwargs)
    
    ## tranlate
    trans_trans = cairo.Matrix(); trans_trans.translate(x, y) 
    context.transform(trans_trans) #apply a transform
    
    ## rotate 
    trans_rotate = cairo.Matrix(xx=cos_angle, yx=sin_angle, xy=(-1.0)*sin_angle, yy=cos_angle, x0=0.0, y0=0.0)
    context.transform(trans_rotate) #apply a transform
    
    ## draw lines
    x_head = head_length * math.cos(ARROWHEAD_ANGLE)
    y_head = head_length * math.sin(ARROWHEAD_ANGLE)
        
    if to_surpress_short_head and line_len < head_length*ARROWHEAD_SUPRESS_OVERHEAD_RATIO:
        pass
    else:
        if head_shape == None: 
            head_shape = DEFAULT_HEAD_SHAPE ## default

        if head_shape in ('stroke'): 
            arrow_func = sub_arrow_stroke
        elif head_shape in ('triangle', 'filled_triangle'): 
            arrow_func = sub_arrow_filled_triangle
        elif head_shape in ('sharp', 'filled_sharp'): 
            arrow_func = sub_arrow_filled_sharp
        else:
            panic(f'crtool.cr_arrow_head: no such a head_shape="{ head_shape }"!: it must be one of: stroke, triangle (filled_triangle), ...')
        arrow_func(x_head, y_head)
        context.close_path()
        pass
    context.restore()
    return

EMPTY_DICT = {}

def cr_line_to(x, y, context=None,
               has_arrow=False, x_last=None, y_last=None, #optional for arrow
               **kwargs):
    """ペンを移動する．

    Args: 
         x (float) : x-coordinate of the center

         y (float) : y-coordinate of the center

         context (cairo.Context) : 文脈オブジェクト

         has_arrow (bool) : 線分端に矢印をもつか? 

         x_last (float) : 矢印をもつ場合に，前の点の座標を与える．矢印の向きを決める．省略可能．

         y_last (float) : 矢印をもつ場合に，前の点の座標を与える．矢印の向きを決める．省略可能．

         arrow_head (str) : 矢印の形状. 値は，関数`crtool.cr_arrow_head`を参照のこと．

    Returns: 
         (Rect) : 包含矩形
    """    
    context.move_to(x_last, y_last)
    context.line_to(x, y)
    context.stroke()
    kwargs = kw.get(kwargs, key='arrow_head', default=EMPTY_DICT)
    if has_arrow:
        if x_last != None and y_last != None:
            cr_arrow_head(x, y, x_last, y_last, context=context,
                          **kwargs)
            pass 
    box = (x, y) 
    return box

def cr_rectangle(x=None, y=None, width=None, height=None,  
                 context=None, 
                 fill=None,
                 edge_rgb=None,
                 **kwargs):
    """矩形を描く

    Args: 

         x (float) : x-coordinate of the center

         y (float) : y-coordinate of the center

         width (float) : width

         height (float): height 

         fill (bool) : fill if `True` or stroke if `False` (default)

    Returns: 
         (Rect) : 包含矩形
    """
    ## 文脈パラメータ設定
    cr_set_context_parameters(context=context, **kwargs)
    com.ensure(com.is_typeof_seq((x,y,width, height), etype=(float, int)),
               f'(x,y,width, height)={(x,y,width, height)} must be numbers!')
    if edge_rgb:
        #fill and edge
        context.rectangle(x, y, width, height)
        context.fill_preserve()
        context.save()
        cr_set_source_rgb(source_rgb=edge_rgb, context=context)
        context.stroke()
        context.restore()
    else:
        #fill only
        context.rectangle(x, y, width, height)
        cr_process_stroke_or_fill(fill=fill, context=context)
    box = (x, y, x + width, y + height) 
    return box

def cr_arc(x=None, y=None, r=None, start=None, end=None,
           context=None, **kwargs):
    """円盤を描く．

    Args: 

         x (float) : x-coordinate of the center

         y (float) : y-coordinate of the center

         r (float) : radius 

         start, end (float) : the starting and ending angle in radian

         fill (bool) : fill (True) or stroke (False, default)

    Returns: 

         (Rect) : 包含矩形
    """
    ## 文脈パラメータ設定
    cr_set_context_parameters(context=context,
                              **kwargs)
    context.arc(x, y, r, start, end)
    fill = kw.get(kwargs, 'fill')
    cr_process_stroke_or_fill(fill=fill, context=context)
    box = ((x - r, y - r), (x + r, y + r))
    return box

def cr_circle(x=None, y=None, r=None, context=None, **kwargs):
    """円盤を描く

    Args: 

         x (float) : x-coordinate of the center

         y (float) : y-coordinate of the center

         r (float) : radius 

         fill (bool) : fill (True) or stroke (False, default)

    Returns: 

         (Rect) : 包含矩形
    """
    com.ensure(x!=None and y!=None and r!=None,
               f'x={x}!=None and y={y}!=None and r={r}!=None!')
    context.new_sub_path() #for beginning with arc(). See pycairo manual
    box = cr_arc(x, y, r, math.pi*0, math.pi*2.0, context=context, **kwargs)
    return box

def cr_text_extent(ox, oy, msg = None, context=None,
                   **kwargs):
    """テキストの配置情報を事前に取得する．Cairo.context.text_extents(msg)のラッパー．

    Args: 

         context (cairo.Context) : Cairoの文脈オブジェクト．

         ox, oy (float) : テキストの配置位置 (ox, oy)

         msg (str) : テキスト

    Returns: 

         (tuple) : テキストの描画情報の6つ組 (x, y, width, height, dx, dy)

    Notes: 
      返り値の6つ組は次の通り

      - x, y : テキストの配置位置．原点は左上
      - width, height : テキストの包含矩形のサイズ
      - dx, dy : グリフ位置の増分

    """
    cr_set_context_parameters(context=context, **kwargs)
    
    ## テキストの描画情報
    if msg:
        x, y, width, height, dx, dy = context.text_extents(msg)
    else:
        panic(f'msg must be non-None!')
    return x, y, width, height, dx, dy

def cr_text(ox, oy, msg = None, context=None,
            #ffamily="Sans", fsize=10, source_rgb=None
            **kwargs):
    """文脈にテキストを描画する．Cairo.show_text(msg)のラッパー．

    Args: 

         context (cairo.Context) : Cairoの文脈オブジェクト．

         ox, oy (float) : テキストの配置位置 (ox, oy)

         msg (str) : テキスト
    """
    cr_set_context_parameters(context=context, **kwargs)
    ## テキストの描画情報
    if msg:
        fx, fy, width, height, dx, dy = context.text_extents(msg)
    else:
        panic(f'msg must be non-None!')
    ## テキストを描画
    context.move_to(ox, oy + height)
    context.show_text(msg)
    return fx, fy, width, height, dx, dy

DEFAULT_MARKER_RADIUS=5 

def cr_draw_marker_circle(ax, ay, r=None, context=None, **kwargs):
    """円形(circle)のマークを描画する．

    Args: 

         ax (float) : 配置位置のx座標

         ay (float) : 配置位置のy座標

         r (float) : 半径．

         context (cairo.Context) : Cairoの文脈オブジェクト．
    """
    cr_set_context_parameters(context=context, **kwargs)
    if not r: 
        r = DEFAULT_MARKER_RADIUS  #円の半径
    cr_circle(ax, ay, r, fill='fill', context=context) ## 点
    return

DEFAULT_MARKER_TICKLEN=4

def cr_draw_marker_cross(x=0.0, y=0.0, angle=math.pi*0.25, 
                         ticklen=DEFAULT_MARKER_TICKLEN,
                         context=None, **kwargs):
    """十文字型（crossing）のマークを描画する．

    Args: 

         x (float) : 配置位置のx座標

         y (float) : 配置位置のy座標

         angle (float) : マーカーの十文字の向きをラジアンで指定する実数．

         ticklen (float) : 十文字の各線分の長さ（default: DEFAULT_MARKER_TICKLEN)

         context (cairo.Context) : Cairoの文脈オブジェクト．
    """
    linewidth = kw.get(kwargs, key='linewidth', altkeys=['line_width', 'pen_width'], default=2)
    kwargs['linewidth'] = linewidth
    cr = context 
    cr.save()
    cr_set_context_parameters(context=cr, **kwargs)
    cr.translate(0,0)
    cr.rotate(angle)
    # cr.set_line_width(linewidth)
    cr.move_to(0, 0)
    cr.line_to(ticklen*1.0, ticklen*0.0)
    cr.move_to(0, 0)
    cr.line_to(ticklen*(-1.0), ticklen*0.0)
    cr.move_to(0, 0)
    cr.line_to(ticklen*0.0, ticklen*1.0)
    cr.move_to(0, 0)
    cr.line_to(ticklen*0.0, ticklen*(-1.0))
    cr.stroke()
    cr.restore()
    return 

def cr_draw_marker(ax, ay, r=None, context=None, **kwargs):
    """関数cr_draw_marker_circleのラッパー関数．下位互換性のため．"""
    return cr_draw_marker_circle(ax, ay, r=r, context=context, **kwargs)

##======
## 配置：ボード位置の微調整
##======

class GeoTransform():
    """空間変換の抽象クラス．これを継承した具体クラスを作成して用いる．
    """
    def __init__(self):
        return

    def apply_context(context=None, verbose=False) -> NoReturn:
        """変換をCairoの文脈contextに適用する．オーバーライドすること．

        Args: 
              context (cairo.Context) : 文脈. 

              verbose (bool) : デバッグ出力のフラグ．default=False. 
        """
        return 

    ##Override
    def apply_point(self, x:float, y:float) -> tuple:
        """変換を点(x, y)に適用した結果(x1, y1)を返す．オーバーライドすること．

        Args: 
              x (float) : 適用対象の点のx座標

              y (float) : 適用対象の点のy座標

        Returns: 
              (tuple(float, float)) : 変換後の点(x1, y1)
        """
        return x, y
    
    def __str__(self):
        return f'GeoTrans[{ self }]'

    def __repr__(self):
        return self.__str__()

    pass 

class Translate(GeoTransform):
    """並行移動の変換のクラス．次の引数 destかsrcのどちらか一つを指定する．

    Args: 
         dest (tuple(float,float)) : 原点を移す先の点の座標

         src (tuple(float,float)) : 点原点に移す元の点（アンカー）

    Attributes: 
    move (tuple(float, float)) : 並行移動ベクトル `vect = (tx, ty)`
    """
    def __init__(self,
                 dest=None, src=None,
                 # x=None, y=None,
                 ):
        #正規化
        if dest == None:            
            dest = (0.0, 0.0)
        if src == None:
            src = (0.0, 0.0)

        ## 点src を点 destへ移す並行移動 trans: (0,0) maps to (x,y) を求める．
        com.ensure_point(src, name='src')
        com.ensure_point(dest, name='dest')
        self.move =  vt_sub(dest, src)
        return

    def __str__(self):
        return f'Translate{self.move}'

    def apply_context(context=None, verbose=False):
        """
        Args: 
              context (cairo.Context) : 文脈. 

              verbose (bool) : デバッグ出力のフラグ．default=False. 
        """
        com.ensure(context != None, f'context must be non-None!')
        tx, ty = self.move
        context.translate(tx, ty)
        return 

    ##Override
    def apply_point(self, x:float, y:float) -> tuple:
        """変換を点(x, y)に適用した結果(x1, y1)を返す．

        Args: 
              x (float) : 適用対象の点のx座標

              y (float) : 適用対象の点のy座標

        Returns: 
              (tuple(float, float)) : 変換後の点(x1, y1)
        """
        com.ensure_point((x, y), name='x and y')
        tx, ty = self.move
        x1, y1 = x + tx, y + ty
        return x1, y1 
    pass 

# class Translate(GeoTransform):
#     """並行移動の変換のクラス．次の引数 destかsrcのどちらか一つを指定する．

#     Args: 
#          dest (tuple(float,float)) : 原点を移す先の点の座標

#          src (tuple(float,float)) : 点原点に移す元の点（アンカー）

#     	 x (float) : x方向の移動量. obsolute 
    
#     	 y (float) : y方向の移動量. obsolute 
    
#     """
#     def __init__(self,
#                  x=None, y=None,
#                  dest=None, src=None,
#                  ):
#         #正規化
#         if x!=None and y!=None:
#             dest = (x, y)
#         elif dest == None:            
#             dest = (0.0, 0.0)
            
#         if src == None:
#             src = (0.0, 0.0)

#         ## 点src を点 destへ移す並行移動 trans: (0,0) maps to (x,y) を求める．
#         com.ensure_point(src, name='src')
#         com.ensure_point(dest, name='dest')
#         self.x : float = dest[0] - src[0] 
#         self.y : float = dest[1] - src[1]
#         return

#     def __str__(self):
#         return f'Translate{(self.x, self.y)}'

#     def apply_context(context=None, verbose=False):
#         """
#         Args: 
#               context (cairo.Context) : 文脈. 

#               verbose (bool) : デバッグ出力のフラグ．default=False. 
#         """
#         com.ensure(context != None, f'context must be non-None!')
#         context.translate(self.x, self.y)
#         return 

#     ##Override
#     def apply_point(self, x:float, y:float) -> tuple:
#         """変換を点(x, y)に適用した結果(x1, y1)を返す．

#         Args: 
#               x (float) : 適用対象の点のx座標

#               y (float) : 適用対象の点のy座標

#         Returns: 
#               (tuple(float, float)) : 変換後の点(x1, y1)
#         """
#         com.ensure_point((x, y), name='x and y')
#         x1, y1 = x + self.x, y + self.y
#         return x1, y1 
#     pass 

class Rotate(GeoTransform):
    """並行移動の変換のクラス

    Args: 
    	  angle (float) : 回転の量．単位はラジアンであり，`math.pi*0.5`, `math.pi/6`などのように指定する．
    
    """
    def __init__(self, angle=None):
        com.ensure(angle!=None and isinstance(angle, (float,int)), 
                   f'angle={angle} must be non-None!')
        com.ensure_point((x, y), name='x and y')
        self.angle : float = angle
        return

    def __str__(self):
        return f'Translate{(self.x, self.y)}'

    def apply_context(context=None, verbose=False):
        """変換を文脈に適用する．

        Args: 
              context (cairo.Context) : 文脈. 

              verbose (bool) : デバッグ出力のフラグ．default=False. 
        """
        com.ensure(context != None, f'context must be non-None!')
        context.rotate(self.angle)
        return 

    ##Override
    def apply_point(self, x:float, y:float) -> tuple:
        """変換を点(x, y)に適用した結果(x1, y1)を返す．

        Args: 
              x (float) : 適用対象の点のx座標

              y (float) : 適用対象の点のy座標

        Returns: 
              (tuple(float, float)) : 変換後の点(x1, y1)
        """
        com.ensure_point((x, y), name='x and y')
        #2次元の回転
        x1 = x*cos(self.angle) + y*(-1)*cos(self.angle)
        y1 = x*sin(self.angle) + y*cos(self.angle)
        return x1, y1 
    pass 

#=====
#変換関数
#=====

def box_apply_trans(box, trans=None, verbose=False): 
    """変換を適用する

    Args: 
          cr (Cairo.Context) : Cairo.Context

          trans (GeoTransform) : 空間変換
    """
    x0, y0, x1, y1 = box_normalize(box)
    if trans == None:
        if verbose: print(f'warning: empty trans: do nothing!')
    elif isinstance(trans, GeoTransform):
        x0, y0 = trans.apply_point(x0, y0)
        x1, y1 = trans.apply_point(x1, y1)
    else: panic(f'trans must be of GeoTransform!: trans={ trans }')
    return x0, y0, x1, y1

def cr_apply_trans(trans=None, context=None, verbose=False): 
    """変換を適用する

    Args: 
         context (Cairo.Context) : Cairo.Context

         trans (GeoTransform) : 空間変換
    """
    com.ensure(context != None, f'context must not None!')

    if trans == None:
        if verbose: print(f'warning: empty trans')
        return
    else: 
        if isinstance(trans, GeoTransform):
            if isinstance(trans, Translate):
                x, y = trans.move
                context.translate(x, y)
                # context.translate(trans.x, trans.y)
            else:
                panic(f'no such GeoTransform is implemented!')
        else: 
            panic(f'trans must be of GeoTransform!: trans={ trans }')
        return



##EOF
