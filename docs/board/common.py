#!/usr/bin/env python3 
# coding: utf_8
# bintree.py
import sys
import random
import math 
# import kwargs as kw

## constants

DEFAULT_PEN_WIDTH=0.25

#parameters
verbose=True
debug=False

# # A template for docstring 
# Parameters
# ----------
# name: type
      
    # Returns 
    # ----------

#=====
#ヘルパー関数
#=====

def log(msg, outs=sys.stderr):
     print(f'{ msg }', file=outs)

def panic(msg, outs=sys.stdout):
     """メッセージ文字列を標準出力に印刷して，例外を投げて実行を中止する．
     
     Args: 
    	msg (str): メッセージ文字列
     
    	outs (outstream): 出力ストリーム．デフォールトはsys.stdout. 
     """
     print(f'@panic!: {msg}', file=outs)
     raise Exception("panic!")

def ensure(test, msg=None, outs=None):
     """ブール式test を評価し，真ならばTrueを返し，偽ならば，panic関数を呼んで，メッセージ文字列を出力して実行を中止する．

     Args: 
    	test (ブール式): テストのためのブール式

    	msg (str): メッセージ文字列

    	outs (outstream): 出力ストリーム．デフォールトはsys.stdout. 
     """
     if test:
          return test
     else:
          panic(f'@ensure: {msg}', outs=outs)

def report_module_path(name): 
     log(f'@printing paths in module:{ name }...')
     for d in sys.path:
          log(f' - { d }')
          log(f'@paths end')

def is_sequence_type(L, elemtype=None, verbose=False):
     """オブジェクトLが系列として扱える型ならば`True`を返し，それ以外のとき`False`を返す．
     さらに系列型であり，elemtypeがNoneでないときに，系列の全ての要素が型elemtypeをもつならば`True`，そうでなければ`False`を返す．

     Args : 
       L (object) : オブジェクト
       elemtype (Type) : int, float, strなどのprimitive型，または，union type `(ty1, ..., tyN)`. 
       verbose (bool) : ログ出力のスイッチ

     Returns : 
       (bool) : オブジェクトLが，elemtypeの型指定を満たす系列型ならば`True`を, そうでなければ`False`を返す．

     Example: 
       >>> com.is_sequence_type([1,2,3], elemtype=int)
       True
       >>> com.is_sequence_type([1,2.0,3], elemtype=int)
       False
       >>> com.is_sequence_type([1,2.0,3], elemtype=(int, float))
       True
       >>> com.is_sequence_type([1,'b',3], elemtype=int)
       False
       >>> com.is_sequence_type([1,'b',3], elemtype=(int, str))     
       True 
     """
     ## 引数テスト
     elemtypes_ = None ## 作業用：a list for a union type
     if elemtype != None: 
          if isinstance(elemtype, type): ## primitive type
               elemtypes_ = [elemtype]
               pass
          elif isinstance(elemtype, tuple): ##union type
               elemtypes_ = []
               for idx, ty in enumerate(elemtype):
                    if isinstance(ty, type):
                         elemtypes_.append(ty)
                    else: 
                         panic(f'common.is_sequence: the {idx}-th element "{ ty }" of elemtype must be a type object!')
          else: 
               panic(f'common.is_sequence: elemtype="{elemetype}" must be a type object!')
     
     ## 系列型かどうかをテスト
     isSeq = False
     if isinstance(L, tuple) or isinstance(L, list):
          isSeq = True
     elif hasattr(L, '__iter__'):
          ## iterableかどうかを判定する標準の書き方
          isSeq = True
     
     if not isSeq: 
          if verbose: print(f'warning: common.is_sequence: the object L is not of sequence type!: L={L}')
          return False
     else: ## isSeq==True
          ## もしelemtypeが与えられていたら，さらに要素型をテストする
          if elemtypes_ != None: 
               for idx, elem in enumerate(L):
                    res_ = False
                    for ty in elemtypes_: 
                         if isinstance(elem, ty):
                              res_ = True
                              break
                    if not res_: 
                         if verbose: print(f'warning: common.is_sequence: the {idx}-th element "{elem}" does not satisfies type "{elemtype}" in the sequence {L}!')
                         return False
          ## 全ての要素が要素型を満たした
          return True

def normalize_elemtype(elemtype=None): 
     ## 引数テスト
     elemtypes_ = None ## 作業用：a list for a union type
     if elemtype == None:
          panic(f'normalize_elemtype: elemtype must be non-None!')
     else:
          if isinstance(elemtype, type): ## primitive type
               elemtypes_ = [elemtype]
          elif isinstance(elemtype, tuple): ##union type
               elemtypes_ = []
               for idx, ty in enumerate(elemtype):
                    if isinstance(ty, type):
                         elemtypes_.append(ty)
                    else: 
                         panic(f'normalize_elemtype: the {idx}-th element "{ ty }" of elemtype must be a type object!')
          else: 
               panic(f'normalize_elemtype: elemtype="{elemetype}" must be a type object!')
     return elemtypes_
          
def is_typeof(obj, elemtype=None):
     """オブジェクトobjが空でなく，型elemtypeをもつとき，`True`を返し，それ以外のとき`False`を返す．
     Args : 
       obj (object) : オブジェクト
       elemtype (Type) : 型のリスト`(ty1, ..., tyN)`．
     Returns : 
       (bool) : オブジェクトobjが，elemtypeの型指定を満たすならば`True`を, そうでなければ`False`を返す．
     """
     ## 引数テスト: 型リストに正規化する．単一型tは，単一元リスト(t)とする．
     elemtypes_ = normalize_elemtype(elemtype=elemtype)
     
     ## 要素型をテストする
     for ty in elemtypes_: 
          if isinstance(obj, ty):  
               return True  ##型tyを満たした
     return False ##どの型も満たさない


def ensure_defined(value=None, default=None, required=False):
	"""空でなければ，値valueをそのまま返す．代入時に，変数の値が空でないことを保証するために用いる．

	* 空のときに，フラグ`required==True`ならば即時にエラーを投げて停止する．
	* そうでないときに，非空のデフォールト値`default`が与えられていれば，それを返す．

	Args: 
	     value (Any) : 値

	     default (Any) : デフォールト値

	     required (bool) : 値が非Noneであることを要請するフラグ．
	"""
	if value==None:
		if required==False and default != None:
			return default
		else: 
			panic('wrap_default: value={value} is required and default={default}!:')
	else:
		return value 
          
##=====
## 便利関数：コマンドライン入力
##=====
#未使用
def parse_opt_shape(str_shape=None, default_shape=None):
     """shape文字列str_shape=='m:n'をパーズしてshape = (m,n)を返す
     """
     if str_shape:
          shape0 = str_shape.split(':')
          ensure(len(shape0)==2, 'shape={mn} must have two numbers!')
          shape = [0,0]
          for i in range(2):
               shape[i] = int(shape0[i])
          return shape
     else:
          return default_shape

#未使用
def parse_opt_width(width=None): 
     if width:
          return width
     else:
          return DEFAULT_PEN_WIDTH #基底描画システムのデフォールト値

#未使用
def get_cyclic(elements=None, idx=0):
     """非負整数idxを受け取り，長さnの配列の`(idx % n)`番目の要素を返す．
     Args: 
    	elements=None (list(object))
    	idx=0 (int)
     Returns: 
    	object: 選択された要素
     Notes: 
    	どのように大きなidxに対しても，添字エラーにならず何かの要素を返す．
     """
     return elements[idx % len(elements)]

##=====
## ヘルパー関数：
##=====

##=====
## EOF 
##=====
