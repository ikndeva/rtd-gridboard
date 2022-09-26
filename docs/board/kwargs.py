#!/usr/bin/env python3 
# coding: utf_8
# bintree.py
import sys
import common as com
import numpy as np

#parameters
# verbose=True
debug=False

# # A template for docstring 
# Args: 
# ----------
# name: type
#   Desciptions ...
# 
# Returns 
# ----------
# 
# Atributes
# ----------
# 

#======
# ヘルパー関数：キーワード引数辞書
#======

# キーワードの所属性テスト
def contains(kwargs=None, key=None):
    """キーワード辞書がkeyの非None値を含むか？"""
    if key==None:
        panic(f'key is None!')
    return ((key in kwargs) and kwargs[key])

# 値を取り出す．必須キーワードの検査も兼ねる．
def get(kwargs=None, key=None, altkeys=None, required=False, default=None):
    """キーワード辞書kwargsにおいて，key値の検査をして，その値を返す. 
    もしそのkeyが見つからない場合には，続いて，次の動作を順に行う: 
    - キーdefaultが指定されていればそれを返す．してされていなければ，次へ進む．
    - ブール値required=Trueが指定されていれば，直ちにエラーを起こして停止する．
    - もし見つからなければNoneを返す．

    Args: 
    	kwargs (dict): キーワード辞書 (None)
    	key (int or str): 指定したキーワード. 
    	default (object): 任意の値．指定キーワードの値がNoneの場合に返すデフォールト値．
    	required (bool): 必須キーワードかのフラグ．この値がTrueの場合，キーワードの値が未定義（None）ならば，エラーを投げる．default=False. 

    Returns: 
    	object: 辞書におけるキーワードkeyの値．値がNoneの場合は上記の説明に従う． 
    """
    keys_ = []
    ## keyを処理
    if key != None: 
        if isinstance(key, str):
            keys_.append(key)
        else: com.panic(f'key="{key}" must be str!')
    ## altkeysを処理
    if altkeys != None: 
        if com.is_typeof_seq(altkeys, etype=str, verbose=True): 
            keys_.extend(altkeys)
        else: com.panic(f'altkeys="{altkeys}" must be of sequence type (str, tuple, list, dict...)!')

    #キーリストkeys_のメンバーを順にテストする
    for key in keys_: 
        if key in kwargs: 
            return kwargs[key]
    
    #まだ見つからなければ，次を試す
    if default != None:
        return default
    elif required:
        com.panic(f'key={key} is not defined!')
    else:
        return None

# 値を取り出す．必須キーワードの検査も兼ねる．
def get_required(kwargs=None, key=None):
    """キーワード辞書kwargsのkeyの値を返す. 未定義ならエラーを投げる

    * get(kwargs=kwargs, key=key, default=None)へのラッパー．
    """
    return get(kwargs=kwargs, key=key, default=None)

# 必須キーワードの検査
def require(kwargs=None, keys=None, verbose=False):
    """キーワード辞書kwargsがキーまたはキーのリストkeysのキーを含むかどうか検査する．検査に成功するとTrueを返し，失敗するとエラーを投げる．
    """
    def panic0(key):
        com.panic(f'key={key} is required!')
    if type(keys) is str:
        if verbose: print(f'@require: a single key')
        if not contains(kwargs=kwargs, key=keys):
            panic0(keys)
    elif type(keys) is list:
        if verbose: print(f'@require: multiple keys')
        for key0 in keys:
            com.ensure(type(key0) is str,
                       f'key={key0} must be str!: type={type(key0)}')
            if not contains(kwargs=kwargs, key=key0):
                panic0(key0)
    return True 
            
##キーワード引数辞書からの部分コピー
def extract(kwargs=None, keys=[],
            required=[],
            deleted=[], 
            trans=[], func=None,
            reduced=False, 
            verbose=False):
    """
    キーワード引数辞書から指定した属性を抽出して得られた新しい辞書を返す．
    このとき，パラメータtransに指定したキーワード属性は，ptからpxへ単位変換を行う．

    Args: 

    	kwargs (dict):  元のキーワード引数の辞書．

    	keys (list(str)): 抽出するキーワードのリスト．Noneならば，transと全てのキーをコピーする．空リスト`[]`のときは，trans以外のキーはコピーしない

    	required (list(str)): 必須のキーワードのリスト．検査して含まれてなければ，エラーで停止する．keysと重複して良い．

    	deleted (list(str)): 除去するキーワードのリスト．keysと重複してはいけない（重複すると返り値の辞書から除去されるので注意）．

    	trans (list(str)): 値を変換して抽出するキーワードのリスト（keysに含まれていなくても良い）

    	func (lambda): 座標変換関数. transのための座標変換関数またはラムダ式．ここに，関数func(xy)は，引数として，点xy=(x0,y0)または点のリストxy=[(x0,x1), (y0,y1), ...]の型の入力を受けつけること．
    
        reduced=False (bool): 関数kwargs.reduceを用いて，値がNoneのキーワードを除去したコピーを作成して返す．非破壊的であり，元の辞書は変更しない．

    Returns: 

    	dict: 新しいキーワード引数の辞書 kwargs1. 

    - 全ての属性をコピーしたい時は，引数keys=Noneとおく．このとき，transで指定した変換を行い，他の全ての属性をコピーする．
    - もしtrans以外の属性をコピーしたくない時は，明示的に`keys=[]`とおく．（空リスト[]と空値Noneのあつかいは異なるので注意）

    Examples: 

    	例:描画情報`xy`を座標変換し，他のすべての属性を取り出す::

        	kwargs1 = kw.extract(kwargs, trans=['xy'], keys=None)

    	例:属性'fill', 'width', 'outline'を取り出す::

        	kwargs1 = 
		  kw.extract(kwargs=kwargs, 
		    keys=['fill', 'width', 'outline'])

    	例:属性'fill', 'width', 'outline'を取り出す::

        	kwargs1 = 
		  kw.extract(kwargs=kwargs, 
		     keys=['xy', 'text', 'font', 'size', 
    			'anchor', 'orient', 'direction',])

    	例: 指定属性 'margin', 'padding' 以外の全ての属性を取り出す::

		kwargs1 = 
    		  kw.extract(kwargs, keys=None, 
    			deleted=['margin', 'padding'])

    """
    if verbose:
        print(f'@kwargs.extract: kwargs={kwargs}')
    #前処理：
    #もしkeysが空値Noneならば，すべてのキーをコピーする
    #引数keysが空リスト`[]`のときは，trans以外の属性はコピーしない
    if keys==None: 
        keys = list(kwargs.keys()) #dict_keysからlistへ変換

    #キーの検査
    for key in required:
        if not key in kwargs: 
            com.panic(f'required key={key} was not found!')
    
    #リストkeysとtransで重複するキーを，keysから除去する
    if trans==None:
        trans = []
    for key in trans:
        if key in keys: #exp: 非効率的:線形探索
            keys.remove(key)  #exp: 非効率的:線形探索
    #実行処理
    kwargs1={}
    #keysを抽出して，新しいdictへ加える
    for key in keys: 
        # if key in kwargs and kwargs[key]: 
        if key in kwargs: 
            kwargs1[key] = kwargs[key]
        # if key in kwargs: 
        #     kwargs1[key] = kwargs[key]
                
    #与えられた関数funcで値を変換して，新しいdictへ加える
    for key in trans: 
        if key in kwargs: 
            kwargs1[key] = func(kwargs[key])

    #キーの除去
    for key in deleted:
        if key in kwargs1: 
            del kwargs1[key]

    #関数reduceを使って既約化したコピーを返す．
    if reduced:
        kwargs1 = reduce(kwargs1)	#コピーを返す．
        
    return kwargs1


#その場の変換適用
def replace_apply(kwargs=None, keys=None, func=None, verbose=False):
    """キーワード引数辞書において，指定したキーに関数funcを適用して置き換える．

    Args: 

    	kwargs (dict):  元のキーワード引数の辞書．

    	keys (list(str)): 抽出するキーワードのリスト．Noneならば，transと全てのキーをコピーする．空リスト`[]`のときは，trans以外のキーはコピーしない

    	func (lambda): 座標変換関数. transのための座標変換関数またはラムダ式．ここに，関数func(xy)は，引数として，点xy=(x0,y0)または点のリストxy=[(x0,x1), (y0,y1), ...]の型の入力を受けつけること．
    
    Returns: 

    	dict: 新しいキーワード引数の辞書 kwargs1. 

    * 引数のkwargsに破壊的変更を加えるので，注意すること．

    * 主に，数値引数の離散化に用いる（px）. 
    """
    if verbose:
        print(f'@kwargs.replace_apply: kwargs={kwargs}')
    if keys==None:
        return kwargs
    for key in keys:
        if key in kwargs:
            value = kwargs[key]
            if value: 
                kwargs[key] = func(value) #整数化
    return kwargs

# 必須キーワードの検査
def reduce(kwargs=None):
    """キーワード辞書kwargsからNone値のキーと値を取り除き，残りを複製して得られた辞書を返す．元の辞書は破壊されず，コピーを返す．

    Args: 

    	kwargs (dict):  元のキーワード引数の辞書．

    Returns: 

    	dict: 新しいキーワード引数の辞書 kwargs1. 

    """
    kwargs1 = {} 
    for key in kwargs.keys():
        if False: print(f'@debug: reduce: key={key} kwargs{kwargs}')
        value = kwargs[key]
        if isinstance(value, np.ndarray): 
            if False:
                print(f'@debug: isinstance(value, np.ndarray)!: type(value)={type(value)}')
            kwargs1[key] = value
        elif value == None: 
            pass
        else:
            kwargs1[key] = value
    return kwargs1 
            
# # 必須キーワードの検査
# def reduce(kwargs=None):
#     """キーワード辞書kwargsからNone値のキーと値を取り除き，残りを複製して得られた辞書を返す．元の辞書は破壊されず，コピーを返す．

#     Args: 

#     	kwargs (dict):  元のキーワード引数の辞書．

#     Returns: 

#     	dict: 新しいキーワード引数の辞書 kwargs1. 

#     """
#     kwargs1 = {} 
#     for key in kwargs.keys():
#         if True: print(f'@debug: reduce: key={key} kwargs{kwargs}')
#         value = 
#         if kwargs[key] == None: 
#             pass
#         else:
#             kwargs1[key] = kwargs[key]
#     return kwargs1 
            
#EOF
