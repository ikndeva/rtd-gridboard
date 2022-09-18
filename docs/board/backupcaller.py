# coding: utf_8
"""forward_medhods.py

* 未定義メソッドの代理呼び出しをするクラス．
* Pythonのリフレクション機能を用いる．
* 220830: Created by Hiroki Arimura, arim@ist.hokudai.ac.jp
"""
import sys


    # Example::

    #       import sys
    #       import backupcaller as bc 
    # 
    #       class OtherObject:
    #           """転送先オブジェクトのクラス．
    #           ふつうのオブジェクトであり，特別な準備は不要．
    #           """
    #           def swim(self, name):
    #               print(f'\t@OtherObject: method="swim" is called')
    #               print(f'An animal {name} swims!')
          
    #       class MyObject:
    #           """転送元オブジェクトのクラス．
    #           """
    #           def __init__(self):
    #               """ここで，転送先オブジェクトを準備する．"""
    #               self.child = OtherObject() #転送先オブジェクト
          
    #           ## メソッド転送
    #           def __getattr__(self, name):
    #               """メソッドが未定義のとき，呼び出される特殊関数．
    #       		未定義の属性呼び出しのときも呼ばれるので注意．
    #               """
    #               print(f'\t@MyObject: method="__getattr__" is called')
    #               return bc.BackupCaller(self.child, name, verbose=True)
          
    #           def walk(self, name):
    #               print(f'\t@OtherObject: method=swim is called')
    #               print(f'A cat {name} walk!')
          
    #       a_cat = MyObject()
          
    #       print('\n### EXP: Call a method "walk" defined on MyObject')
    #       a_cat.walk('a_cat')
          
    #       print('\n### EXP: Call a method "swim" not defined on MyObject, but defined on OtherObject')
    #       a_cat.swim('a_cat')
          
    #       print('\n### EXP: Call a method "donothing" not defined both on MyObject and OtherObject')
    #       a_cat.donothing('a_cat')


## メソッド転送
class BackupCaller():
    """メソッド呼び出しの転送をするクラス．

    Args: 
          host (Object) : 呼び出しの転送先オブジェクト．

          fname (str) : 呼び出しの関数名/メソッド名．

          verbose (bool) : デバグ用出力のフラグ. default=False. 

    Notes: 

          具体的な利用法は，下記のExampleを参照されたい．次の手順で，メソッド転送が実行される．

          * `MyObject`の初期化時に，自分が実装していないメソッドの転送先オブジェクトに，`OtherObject`を設定する．
    	  * `MyObject`は，特殊関数 `__getattr__()`を次のように実装する: 

               + もし関数名（属性名）`name`が自身に対して呼ばれたら，
               + 代理オブジェクト`agent`と関数名`name`を引数として，オブジェクト BackupCaller(self.agent, name)を生成して，それを返り値として返す．この時点では，元の呼び出しの引数`(a1,...,aN)`は渡されないことに注意．
          * 呼び出し側では，返り値のBackupCallerオブジェクトを受け取り，python処理系が，それに元の呼び出しの引数`(a1,...,aN)`を与えて実行する．

    Example:: 

          import sys
          import backupcaller as bc 
          
          class OtherObject:
              #転送先オブジェクトのクラス．
              #ふつうのオブジェクトであり，特別な準備は不要．
              def swim(self, name):
                  print(f'\t@OtherObject: method="swim" is called')
                  print(f'An animal {name} swims!')
          
          class MyObject:
              #転送元オブジェクトのクラス．
              def __init__(self, agent=None):
                  #ここで，転送先オブジェクトを準備する．#
    		  if agent != None: 
                      self.agent = agent #転送先オブジェクト
          
              ## メソッド転送
              def __getattr__(self, name):
                  #メソッドが未定義のとき，呼び出される特殊関数．
          	  #未定義の属性呼び出しのときも呼ばれるので注意．
                  print(f'\t@MyObject: method="__getattr__" is called')
                  return bc.BackupCaller(self.agent, name, verbose=True)
          
              def walk(self, name):
                  print(f'\t@OtherObject: method=swim is called')
                  print(f'A cat {name} walk!')

          #a duck can swim
          a_duck = OtherObject() 

          #a cat can walk, but cannot swim
          a_cat = MyObject(agent=a_duck) 

          a_cat.walk('a_cat') #a cat can walk
	  => walk
          a_cat.swim('a_cat') #Since a cat cannot swim, a duck swims instead
	  => swim
          a_cat.donothing('a_cat')
	  => fail
    """
    def __init__(self, host, fname, verbose=False, verbose_prefix=None):
        """元の呼び出し先のオブジェクト`host`と呼びされるメソッド名`fname`を受け取り，格納する．
        """
        self.host = host
        self.fname = fname
        self.verbose = verbose
        self.verbose_prefix = verbose_prefix

    def __call__(self, *args, **kwargs):
        """このオブジェクトのメソッド呼び出しにおいて，常に呼び出される特殊関数．
        * 引数`(arg1, ..., kwargs1, ...)` は，元のメソッド呼び出しの引数．
        * タスクとして，自身に格納した元の呼び出しのオブジェクト`host`とメソッド名`fname`に対して，呼び出し`host.fname(arg1, ..., kwargs1, ...)`を実行する．
        """
        if self.verbose_prefix: 
            prefix = self.verbose_prefix
        else:
            prefix = ''
        if self.verbose: print(f'@BackupCaller: method="__call__" is called')
        if hasattr(self.host, self.fname): 
            func = getattr(self.host, self.fname, None)
            if self.verbose: print(f'@BackupCaller: found method={type(func)} in self.host={self.host}')
            if self.verbose: print(f'@BackupCaller: exec method={type(func)} as "{self.fname}"')
            func(*args, **kwargs)
            # return self.host.func(self.fname, *args, **kwargs)
        else:
            print(f'error: {self.host} has no method {self.fname}!')
            sys.exit(1)

## EOF
