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
    """標準関数print(msg)のラッパー．出力ストリームoutsを与えるとそこへ，指定がなければstd.errへ，print(msg)の出力を書き込む．
    
    Args: 
         msg (str) : 出力する文字列
    
         outs (出力ストリーム) : 出力先．default=sys.stderr.
    """
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
			panic('ensure_defined: value={value} is required and default={default}!:')
	else:
		return value 
          
##=====
## 便利関数：型チェック
##=====

def elemtype_normalize(etype=None):
    """与えられた入力オブジェクトetypeが，正しい型オブジェクトかを検査し，
    型リストetypes_を返す．もしそうでなければ，エラーを投げて異常終了する．
    ただし，etype==Noneのときは，そのまま返す（任意の型を表す）．

    Args: 
         etype (Object) : 基礎型，または，基礎型のリスト（和）

    Returns: 
         (list(型)) : 正規化された型リスト
    """
    if etype == None:
        return etype
    
    ety_list = None ## 作業用：a list for a union type
    if isinstance(etype, type): ## primitive type
        ety_list = [etype]
    elif isinstance(etype, tuple): ##union type
        ety_list = []
        for idx, ty in enumerate(etype):
            if isinstance(ty, type):
                ety_list.append(ty)
            else: 
                panic(f'common.is_sequence: the {idx}-th element "{ ty }"'+
                      f' of etype must be a type object!')
        pass 
    else: 
        panic(f'common.is_sequence: etype="{etype}"'+
              f' must be a type object!')
    return ety_list 

def _normalize_elemtype(etype=None): 
    """関数is_typeof_value()の補助関数．受け取った型または型リストelemtypeを，型リストに変換して返す．
    """
    etypes_ = None ## 作業用：a list for a union type
    # if etype == None:
    #      panic(f'normalize_etype: etype must be non-None!')
    ensure_defined(etype, required=True)
    if isinstance(etype, type): ## primitive type
        etypes_ = [etype]
    elif isinstance(etype, tuple): ##union type
        etypes_ = []
        for idx, ty in enumerate(etype):
            if isinstance(ty, type):
                etypes_.append(ty)
            else: 
                panic(f'normalize_etype: the {idx}-th element "{ ty }" of etype must be a type object!')
    else: 
        panic(f'normalize_elemtype: etype="{elemetype}" must be a type object!')
    return etypes_

def is_typeof_seq(L, etype=None, dim=None, verbose=False):
    """オブジェクトLが，指定された型と長さをもつ系列オブジェクトかを真偽で返す．
    さらに系列型であり，etypeがNoneでないときに，系列の全ての要素が型etypeをもつならば`True`，そうでなければ`False`を返す．

    Args: 
         L (object) : オブジェクト

         etype (Type) : int, float, strなどのprimitive型，または，型の選言（union etype）を表すリスト `(ty1, ..., tyN)`. 

         length (int) : 系列が満たすべき長さ

         verbose (bool) : ログ出力のスイッチ

    Returns: 
         (bool) : オブジェクトLが，etypeの型指定を満たす系列型ならば`True`を, そうでなければ`False`を返す．

    Example:: 

       >>> com.is_typeof_seq([1,2,3], etype=int)
       True
       >>> com.is_typeof_seq([1,2.0,3], etype=int)
       False
       >>> com.is_typeof_seq([1,2.0,3], etype=(int, float))
       True
       >>> com.is_typeof_seq([1,'b',3], etype=int)
       False
       >>> com.is_typeof_seq([1,'b',3], etype=(int, str))     
       True 
    """
    ## 型引数のテスト
    etypes_ = elemtype_normalize(etype)
     
    ## 系列型かどうかをテスト
    if isinstance(L, tuple) or isinstance(L, list):
        isSeq = True
    elif hasattr(L, '__iter__'):
        ## iterableかどうかを判定する標準の書き方
        isSeq = True
    else:
        isSeq = False

    ##長さテスト
    if isSeq and dim!=None and len(L) != dim:
        if verbose: print(f'warning: common.is_sequence: it must have dim={dim} but len={len(L)}!')
        return False
     
    if not isSeq: 
        if verbose: print(f'warning: common.is_sequence: the object L is not of sequence type!: L={L}')
        return False
    else: ## isSeq==True
        ## もしtypeが与えられていたら，さらに要素型をテストする
        if etypes_ == None:
            return True
        else:
            for idx, elem in enumerate(L):
                res_ = False
                for ty in etypes_: 
                    if isinstance(elem, ty):
                        res_ = True
                        break
                if not res_: 
                    if verbose: print(f'warning: common.is_sequence: the {idx}-th element "{elem}" does not satisfies etype "{etype}" in the sequence {L}!')
                    return False
        ## 全ての要素が要素型を満たした
        return True

def is_typeof_value(obj, etype=None):
     """オブジェクトobjが空でなく，型etypeをもつとき，`True`を返し，それ以外のとき`False`を返す．

     Args: 
          obj (object) : オブジェクト

          etype (Type) : 型のリスト`(ty1, ..., tyN)`．

     Returns: 
          (bool) : オブジェクトobjが，etypeの型指定を満たすならば`True`を, そうでなければ`False`を返す．
     """
     ## 引数テスト: 型リストに正規化する．単一型tは，単一元リスト(t)とする．
     etypes_ = _normalize_elemtype(etype=etype)
     
     ## 要素型をテストする
     for ty in etypes_: 
          if isinstance(obj, ty):  
               return True  ##型tyを満たした
     return False ##どの型も満たさない


##=====
## 便利関数：型チェック
##=====

def _simple_type_name(etype=None):
    # ensure(etype!=None, f'etype={None} must be defined!')
    ensure_defined(etype, required=True)
    if not isinstance(etype, tuple):
        return f'{etype.__name__}'
    else:
        s = f'tuple('
        for idx, ty in enumerate(etype):
            if idx > 0: s += ', '
            s += f'{_simple_type_name(etype=ty)}'
        return s + ')'

def ensure_value(value=None, default=None, etype=None, nullable=True, name='it', typename=None, to_check_only=False):
    """入力として受け取った値`value`が指定された要素型`etype`の値であるかを検査し，条件を満たせば値をそのまま返す．もし指定の条件を満たさなければ，エラーを投げて終了する．

    * 空でなければ，値valueをそのまま返す．

    * 空のときに，フラグ`required==True`ならば即時にエラーを投げて停止する．
    * そうでないときに，非空のデフォールト値`default`が与えられていれば，それを返す．

    Args: 
         value (Any) : 値

         etype (tuple(type)) : 型のタプル．型の選言を表す．デフォールト値`etype=None`. 

         default (Any) : 任意のデフォールト値を与える．値がNoneのとき返される．

         nullable (bool) : 値がNoneでも良いことを表すフラグ．nullable=Trueかつ値がNullならばエラーを投げる．

         to_check_only (bool) : もし真ならば，型を満たさない時は，エラーを投げずに実行されて，Noneを返す．default is False．ここに，to_check_onlyが真ならば，`nullable==False`および`default = None`に上書きされるので注意．

    Notes: 
        データの検査を行う関数の実装用に用いる．典型的な使用例は，次の通り：

        * 変数の値を保証して代入するためのフィルタの実装
        * 値の型を保証した代入

    Note: 
        引数`etype`の組の要素として，`None`の型を与えたい時は，要素型として`type(None)`を与えること．
    """
    ensure(etype!=None, f'etype={etype} must be defined!')
    #判定関数に用いる場合の前処理
    if to_check_only:
        nullable = False
        default = None
    if typename==None:
        typename=_simple_type_name(etype)
    
    #値が空な場合の処理
    if value==None:
        if nullable==True:
            if default != None:
                return default
            else:
                return None
        else:
            if to_check_only: return None
            else: com.panic(f'{name}={value} must be {typename}! case 1: value(={value})==None while nullable={nullable}')
        
    #指定された型の値の対か？
    if is_typeof_value(value, etype=etype):
        return value
    else:
        if to_check_only: return None
        else: com.panic(f'{name}={value} must be {typename}! case 2: value={value} is not a sequence of specified type={etype}')
          
def ensure_vector(value=None, dim=2, default=None, etype=None, nullable=True, name='it', typename=None, to_check_only=False):
    """入力として受け取った値`value`が指定された要素型`etype`と要素数`dim`をもつ数値の組であるかを検査し，条件を満たせば値をそのまま返す．もし指定の条件を満たさなければ，エラーを投げて終了する．

    * 空でなければ，値valueをそのまま返す．

    * 空のときに，フラグ`required==True`ならば即時にエラーを投げて停止する．
    * そうでないときに，非空のデフォールト値`default`が与えられていれば，それを返す．

    Args: 
         value (Any) : 値

         dim (int) : ベクトルの長さ

         etype (tuple(type)) : 型のタプル．型の選言を表す．デフォールト値`etype=None`. 

         default (Any) : 任意のデフォールト値を与える．値がNoneのとき返される．

         nullable (bool) : 値がNoneでも良いことを表すフラグ．nullable=Trueかつ値がNullならばエラーを投げる．

         to_check_only (bool) : もし真ならば，型を満たさない時は，エラーを投げずに実行されて，Noneを返す．default is False．ここに，to_check_onlyが真ならば，`nullable==False`および`default = None`に上書きされるので注意．

    Notes: 
        データの検査を行う関数の実装用に用いる．典型的な使用例は，次の通り：

        * 変数の値を保証して代入するためのフィルタの実装
        * 値の型を保証した代入

    Note: 
        引数`etype`の組の要素として，`None`の型を与えたい時は，要素型として`type(None)`を与えること．
    """
    ensure(etype!=None, f'etype={etype} must be non-None!')
    #判定関数に用いる場合の前処理
    if to_check_only:
        nullable = False
        default = None
    if typename==None:
        typename=_simple_type_name(etype)
    
    #値が空な場合の処理
    if value==None:
        if nullable==True:
            if default != None:
                return default
            else:
                return None
        else:
            if to_check_only: return None
            else: com.panic(f'{name}={value} must be {typename}! case 1: value(={value})==None while nullable={nullable}')
        
    #指定された型の値の対か？
    if not is_typeof_seq(value, etype=etype):
        if to_check_only: return None
        else: com.panic(f'{name}={value} must be {typename}! case 2: value={value} is not a sequence of specified type={etype}')
    elif len(value) != dim:
        if to_check_only: return None
        else: com.panic(f'{name}={value} must be {typename}! case 3: value={value} has wrong length where len(value)(={len(value)})==dim(={dim})')
    else:
        return value
          
def ensure_point(value=None, name=None, nullable=True, default=None, etype=None, to_check_only=False):
    """値が指定された型の点（数の対）かどうかを検査し，値valueをそのまま返す．
    条件を満たさなければ，エラーを投げて終了する．
    関数`ensure_vector`のラッパー．

    * 空のときに，フラグ`required==True`ならば即時にエラーを投げて停止する．
    * そうでないときに，非空のデフォールト値`default`が与えられていれば，それを返す．

    Args: 
         value (Any) : 値

         nullable (bool) : 値がNoneでも良いことを表すフラグ．

         default (Any) : 任意のデフォールト値を与える．値がNoneのとき返される．

         etype (tuple(type)) : 型のタプル．型の選言を表す．数値ベクトルは，デフォールトの`etype=(int, float)`で良い．

         to_check_only (bool) : もし真ならば，型を満たさない時は，エラーを投げずに実行されて，Noneを返す．default is False．ここに，to_check_onlyが真ならば，`nullable==False`および`default = None`に上書きされるので注意．
    """
    if etype==None:
        etype = (float,int) #要素型のdefaultは，数値型
        typename='a point'
    else:  
        typename=_simple_type_name(etype)
        
    return ensure_vector(value=value, default=default,
                         etype=etype, nullable=nullable, 
                         dim=2, name=name, typename=typename,
                         to_check_only=to_check_only)
    
def ensure_box(value=None, name=None, nullable=True, default=None, etype=None, to_check_only=False):
    """値が指定された型の点（数の対）かどうかを検査し，値valueをそのまま返す．
    条件を満たさなければ，エラーを投げて終了する．
    関数`ensure_vector`のラッパー．

    * 空のときに，フラグ`nullable==False`ならば即時にエラーを投げて停止する．
    * そうでないときに，非空のデフォールト値`default`が与えられていれば，それを返す．

    Args: 
         value (Any) : 値

         etype (tuple(type)) : 選言型のタプル．defaultは(float,int). 

         nullable (bool) : 値がNoneでも良いことを表すフラグ．

         etype (tuple(type)) : 型のタプル．型の選言を表す．数値ベクトルは，デフォールトの`etype=(int, float)`で良い．

         default (Any) : 任意のデフォールト値を与える．値がNoneのとき返される．

         to_check_only (bool) : もし真ならば，型を満たさない時は，エラーを投げずに実行されて，Noneを返す．default is False．ここに，to_check_onlyが真ならば，`nullable==False`および`default = None`に上書きされるので注意．
    """
    if etype==None:
        etype = (float,int) #要素型のdefaultは，数値型
        typename='a point'
    else:  
        typename=_simple_type_name(etype)
    return ensure_vector(value=value, default=default,
                         etype=etype, nullable=nullable, 
                         dim=4, name=name, typename=typename,
                         to_check_only=to_check_only)
    
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
