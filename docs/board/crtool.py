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

  ALIGN_X (dict(str, float)) : 
    位置合わせ用のx方向のアンカー値を表す定数の辞書．範囲`[0,1]`の値をとり，辺上の正規化された位置を表す．複数の別名を提供している．

    * 'left'   : 0.0, 'center'  : 0.5, 'right'  : 1.0, #標準名
    * 'beg' : 0.0, 'mid' : 0.5, 'end' : 1.0, #xとy方向の共通名

  ALIGN_Y  (dict(str, float)) : 
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
import cairo 
import math 

import common as com 
import kwargs as kw

verbose = True

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

## 位置合わせ
ALIGN_X = {
    'left'   : 0.0, 
    'center'  : 0.5, 
    'right'  : 1.0,
    ## uni
    'beg' : 0.0, 
    'mid' : 0.5, 
    'end' : 1.0, 
}
ALIGN_Y = {
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
DEFAULT_ALIGN_RATIO_X = 0.0
DEFAULT_ALIGN_RATIO_Y = 0.0

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

         display_size (tuple(int, int)) : 画像のサイズ `(xsize, ysize)`

         outfile (str) : 出力画像ファイル名の本体を表す文字列．例：`out`

         verbose (bool) : デバッグ/実行情報の表示のフラグ

    Attributes: 

         ims (cairo.ImageSurface, cairo.PDFSurface) : Cairoの画像オブジェクト（Surface）を保持する．

         cr (cairo.Context) : Cairoの文脈オブジェクト．関数`context()`で取得し，各種のCairoの描画操作，または，crtoolの描画操作を適用できる．

    """
    count = 0  #count instance id 
    
    def __init__(self,
                 # dep_init=None, 
                 imgtype=cairo.FORMAT_ARGB32, #cairoのSurface format
                 format="pdf",   #出力ファイルフォーマット（拡張子 pdf, png）
                 outfile="out",  #出力ファイル名（拡張子を除く）
                 display_size=None, 
                 # imagesize='XGA',#初期の画像サイズ
                 # portrait=False, #画像サイズが縦長か？
                 verbose=False):
        """実装レイヤーの画盤を生成するコンストラクタ．
        Args: 
             imgtype (str) : 画像フォーマット (cairo)

             format (str) : 出力ファイルの描画フォーマット (cairo) in "pdf", "png"

             display_size (tuple(int, int)) : 画像のサイズ `(xsize, ysize)`

             verbose (bool) : 実行情報を表示する
        """
        #親Loggableの初期化
        # super().__init__(dep_init=dep_init, verbose=verbose)
        # super().__init__(dep_init=dep_init, verbose=verbose)
        #パラメータ
        self.imgtype = imgtype
        self.format  = format
        self.outfile = outfile
        self.display_size = display_size
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
        com.ensure(com.is_sequence_type(self.display_size, elemtype=(int, float)),
                   f'display_size must be a pair of numbers: {display_size}')
        
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
            self.ims = cairo.ImageSurface(cairo.FORMAT_ARGB32,
                                          self.display_size[0],
                                          self.display_size[1]) #image surface
        elif self.format == "pdf": 
            self.ims = cairo.PDFSurface(self.myoutfile,
                                        self.display_size[0],
                                        self.display_size[1]) #image surface
        else:
            panic(f'no such a file format={ self.format } is supported!')

        ## CairoのContext (image handle)の生成
        """ class cairo.Context(target)
        Parameters:	target – target Surface for the context
        Returns:	a newly allocated Context
        Raises :	MemoryError in case of no memory
        """
        self.cr = cairo.Context(self.ims) 
        return 
                
    def context(self):
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
            self.ims.write_to_png(self.myoutfile)
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

         default (ANy) : デフォールト値．

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
    
    Note: 

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
    com.ensure(com.is_sequence_type((x, y, x_last, y_last), elemtype=(float, int)),
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
    com.ensure(com.is_sequence_type((x,y,width, height), elemtype=(float, int)),
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

def cr_circle(x, y, r, context=None, **kwargs):
    """円盤を描く

    Args: 

         x (float) : x-coordinate of the center

         y (float) : y-coordinate of the center

         r (float) : radius 

         fill (bool) : fill (True) or stroke (False, default)

    Returns: 

         (Rect) : 包含矩形
    """
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

    Note: 
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

# def cr_draw_marker_cross(x=0.0, y=0.0, angle=None, 
#                          ticklen=DEFAULT_MARKER_TICKLEN,
#                          context=None, **kwargs):
#     linewidth = kw.get(kwargs, key='linewidth', altkeys=['line_width', 'pen_width'], default=2)
#     kwargs['linewidth'] = linewidth
#     cr_set_context_parameters(context=context, **kwargs)
#     if True: print(f'@debug:cr_draw_marker_cross:{x,y,angle}')
#     # context.save()
#     # if angle != None:
#     #     context.rotate(angle) #回転
#     # if x != 0 or y != 0: 
#     #     context.translate(x, y)
#         # cr_apply_trans(trans=Translate(x=x, y=y), context=context)
#     ##十時型を書く
#     ticklen=10
#     context.move_to(0, 0)
#     context.line_to(ticklen*1.0, ticklen*0.0)
#     context.move_to(0, 0)
#     context.line_to(ticklen*(-1.0), ticklen*0.0)
#     context.move_to(0, 0)
#     context.line_to(ticklen*0.0, ticklen*1.0)
#     context.move_to(0, 0)
#     context.line_to(ticklen*0.0, ticklen*(-1.0))
#     ##描き終わり
#     #context.restore()
#     # ##十時型を書く
#     # context.move_to(0, 0)
#     # context.line_to(ticklen*1.0, ticklen*0.0)
#     # context.move_to(0, 0)
#     # context.line_to(ticklen*(-1.0), ticklen*0.0)
#     # context.move_to(0, 0)
#     # context.line_to(ticklen*0.0, ticklen*1.0)
#     # context.move_to(0, 0)
#     # context.line_to(ticklen*0.0, ticklen*(-1.0))
#     # ##描き終わり
#     # cr_process_stroke_or_fill(context=context, fill='fill')
#     context.fill()
#     return 

def cr_draw_marker(ax, ay, r=None, context=None, **kwargs):
    """関数cr_draw_marker_circleのラッパー関数．下位互換性のため．"""
    return cr_draw_marker_circle(ax, ay, r=r, context=context, **kwargs)

##=====
## ヘルパー関数： 座表と座表変換
##=====

def isBoxOrPoint(box):
    """与えられたオブジェクトboxが，点または矩形かどうかを返す．

    Args: 

         box (tuple) : オブジェクト

    Returns: 

         (bool) : boxが，点または矩形ならばTrue, それ以外ならばFalse. 
    """
    if box==None:
        return False
    elif com.is_sequence_type(box, elemtype=(float,int)): 
        if (len(box) == 2) or (len(box) == 4):
            return True
        else:
            return False
    else:
        return False

def isProperPoint(box):
    """与えられたオブジェクトboxが，点かどうかを返す．

    Args: 

         box (tuple) : オブジェクト
    Returns: 

         (bool) : boxが，点ならばTrue, それ以外ならばFalse. 
    """
    if not isBoxOrPoint(box):
        return False
    elif len(box)!=2:
        return False
    else:
        return True

def isProperBox(box):
    """与えられたオブジェクトboxが，正しい矩形かをTrue, Falseで返す．

    Args: 
         box (tuple) : オブジェクト

    Returns: 
         (bool) : boxが，4座標（矩形）からなる正しい矩形ならばTrue, それ以外ならばFalse. 
    """
    if not isBoxOrPoint(box):
        return False
    elif len(box)!=4:
        return False
    else:
        x0, y0, x1, y1 = box
        if x1 >= x0 and y1 >= y0:
            return True
        else:
            return False

def box_normalize(box):
    """4座標（矩形）からなる正しい矩形であることを検査し，2座標（点）なら4座標に正規化する．
    """
    com.ensure(isBoxOrPoint(box), f'box must be of TypeBoundingBox: type(box)={ type(box) }')
    if len(box)==2:
        box = (box[0], box[1], box[0], box[1])
    com.ensure(isProperBox(box), f'box must a properbox: box={box}')
    return box

def box_shape(box):
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

##======
## 配置：ボード位置の微調整
##======

class GeoTransform():
    """空間変換の抽象クラス．これを継承した具体クラスを作成して用いる．
    """
    def __init__(self):
        return

    def apply_context(context=None, verbose=False):
        """変換をCairoの文脈contextに適用する．オーバーライドすること．

        Args: 
              context (cairo.Context) : 文脈. 

              verbose (bool) : デバッグ出力のフラグ．default=False. 
        """
        return 

    ##Override
    def apply_point(self, x, y):
        """変換を点(x, y)に適用した結果(x1, y1)を返す．オーバーライドすること．

        Args: 
              x (float) : 適用対象の点のx座標

              y (float) : 適用対象の点のy座標

        Returns: 
              (tuple(flaot, float)) : 変換後の点(x1, y1)
        """
        return x, y
    
    def __str__(self):
        return f'GeoTrans[{ self }]'

    def __repr__(self):
        return self.__str__()

    pass 

class Translate(GeoTransform):
    """並行移動の変換のクラス．

    Args: 
    	  x (float) : x方向の移動量. 
    
    	  y (float) : y方向の移動量. 
    
    """
    def __init__(self, x=0, y=0):
        com.ensure(x!=None and y!=None,
                   f'x={x} and y={y} must be non-None!')
        com.ensure(isProperPoint((x, y)), f'p={ x, y } must be pair of float')
        self.x = x
        self.y = y
        return

    def __str__(self):
        return f'Translate{(self.x, self.y)}'

    def apply_context(context=None, verbose=False):
        """
        Args: 
              context (cairo.Context) : 文脈. 

              verbose (bool) : デバッグ出力のフラグ．default=False. 
        """
        com.ensure(context != None, f'context must be non-None!')
        context.translate(self.x, self.y)
        return 

    ##Override
    def apply_point(self, x, y):
        """変換を点(x, y)に適用した結果(x1, y1)を返す．

        Args: 
              x (float) : 適用対象の点のx座標

              y (float) : 適用対象の点のy座標

        Returns: 
              (tuple(flaot, float)) : 変換後の点(x1, y1)
        """
        com.ensure(isProperPoint((x, y)), f'p={ x, y } must be a point!')
        x1, y1 = x + self.x, y + self.y
        return x1, y1 
    pass 

class Rotate(GeoTransform):
    """並行移動の変換のクラス

    Args: 
    	  angle (float) : 回転の量．単位はラジアンであり，`math.pi*0.5`, `math.pi/6`などのように指定する．
    
    """
    def __init__(self, angle=None):
        com.ensure(angle!=None and isinstance(angle, (float,int)), 
                   f'angle={angle} must be non-None!')
        com.ensure(isProperPoint((x, y)), f'p={ x, y } must be pair of float')
        self.angle = angle
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
    def apply_point(self, x, y):
        """変換を点(x, y)に適用した結果(x1, y1)を返す．

        Args: 
              x (float) : 適用対象の点のx座標

              y (float) : 適用対象の点のy座標

        Returns: 
              (tuple(flaot, float)) : 変換後の点(x1, y1)
        """
        com.ensure(isProperPoint((x, y)), f'p={ x, y } must be a point!')
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
                context.translate(trans.x, trans.y)
            else:
                panic(f'no such GeoTransform is implemented!')
        else: 
            panic(f'trans must be of GeoTransform!: trans={ trans }')
        return

#=====
#変換関数
#=====

def get_anchor_ratio(anchor_x=None, anchor_y=None,
                     anchor=None, verbose=False):
    """アンカーキーワード(anchor_x, anchor_y)またはanchorを受け取り

    Args: 
         anchor_x (str) : 横方向の位置指示 in (left, center, right)

         anchor_y (str) : 縦方向の位置指示 in (top, middle, bottom, above, below)

         anchor (str) : 代替の位置指示．単一キーワードまたはキーワードの対(anchor_x, anchor_y)．単一キーワードのときは，値に応じて横または縦の位置表示として用いる．

    Returns: 
         (tuple(float, float)) : 矩形[0,1]x[0,1]における正規化されたアンカー位置(anchor_x, anchor_y) in [0,1]x[0,1]
    """
    ## アンカーキーの正規化
    ratio_x, ratio_y = None, None
    if anchor_x==None and anchor_y==None and anchor != None:
        if isinstance(anchor, str):
            if anchor in ALIGN_X: anchor_x = anchor
            if anchor in ALIGN_Y: anchor_y = anchor
        elif com.is_sequence_type(anchor, str): 
            if len(anchor) == 1:
                if anchor in ALIGN_X: anchor_x = anchor
                if anchor in ALIGN_Y: anchor_y = anchor
            elif len(anchor) == 2:
                if anchor[0] in ALIGN_X: anchor_x = anchor[0]
                if anchor[1] in ALIGN_Y: anchor_y = anchor[1]
            else:
                panic(f'get_align: a wrong anchor={anchor}!')
    
    ## アンカーキーからアンカー比率へ変換
    if anchor_x != None and anchor_x in ALIGN_X:
        ratio_x = ALIGN_X[anchor_x]
    else:
        ratio_x = DEFAULT_ALIGN_RATIO_X
    if anchor_y != None and anchor_y in ALIGN_Y:
        ratio_y = ALIGN_Y[anchor_y]
    else:
        ratio_y = DEFAULT_ALIGN_RATIO_Y
    return ratio_x, ratio_y

def get_point_by_anchor_ratio(box, ratio_x, ratio_y, verbose=False):
    """矩形とアンカー表示を受け取り，矩形上のアンカー点の座標を返す．

    Args: 
         ratio_x (float) : 正規化されたx方向の位置 in [0,1]

         ratio_y (float) : 正規化されたy方向の位置 in [0,1]

    Returns: 
         (tuple(float, float)) : 包含矩形box上のアンカー位置の点 (x, y)
    """
    #boxの準備
    com.ensure(box != None and isBoxOrPoint(box),
               f'get_anchor_by_ratio: box must be a box or a point!')
    x0, y0, x1, y1 = box_normalize(box) 
    # compute x-anchor 
    if x1 - x0 == 0: x = x0
    else: x = x0 * (1.0 - ratio_x) + x1 * (ratio_x)            
    # compute y-anchor 
    if y1 - y0 == 0: y = y0
    else: y = y0 * (1.0 - ratio_y) + y1 * (ratio_y)
    if verbose:
        print(f'@debug: get_anchor_by_ratio: anchor_ratio={ratio_x, ratio_y} '+
              f'=> anchor_coordinates={x,y}')
    return x, y


##EOF
