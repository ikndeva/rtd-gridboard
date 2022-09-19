#!/usr/bin/env python3 
# coding: utf_8
# loggable.py 
"""ボードの基本機能を提供するモジュール．

* loggableモジュールは，ボードオブジェクトが，複合画像の木のノードとしてもつ最低限の機能を提供する．
* 複合画像を表すボードオブジェクトは木構造をなす．
* Loggableオブジェクトは，次の機能を提供する: 

	* 親子情報の管理
	* ログ出力の管理
"""
import sys
import common as com
import kwargs as kw

#==========
# 補助クラス
#==========

class LoggableHolder:
    """Loggableにおける子のホルダー．子に加えて，補助情報を保持する子クラスを生成して利用する．
     
    Args: 
         child (Loggable) : 保持する子の初期値．default=None. 
    """
    def __init__(self, child=None):
        self.set_child(child)
        return 

    def get_child(self):
        """ホルダーの子要素を設定する．子要素は`None`を許す. 

        Returns: 
               (Loggable) : ホルダーがもつ子要素
        """
        return self.child
      
    def set_child(self, child=None):
        """ホルダーの子要素を設定し，自分自身を返す．
        子要素`child`が`None`のときは，エラーを投げて終了する．

        Args: 
             child (Loggable) : ホルダーに設定する子要素

        Returns: 
             (Loggable) : 自分自身．(cascading style API)
        """
        if child == None or not isinstance(child, Loggable):
            com.panic(f'if child is not None, it must be Loggable: it={child}')
            self.child = child 
        return self 
    pass ##class ChildHolder

#==========
# 基底オブジェクトのクラス
#==========
class Loggable:
    """ボードの最基底クラス．
    複合画像を表すボードオブジェクトの木のノードがもつ最低限の機能を提供する．

    Args: 

           dep_init (int) : 深さの初期値．default=None. 

           tags (str, list(str)) : タグ文字列またはタグ文字列のリスト．タグ文字列のリストは，オブジェクトの属性`tags`に保持され，実装者と利用者により，各種の用途に用いることができる．default=None. 

           verbose (bool) : デバッグ用出力のフラグ．default=False. 

           **kwargs : 任意のオプション引数．オブジェクトの属性`kwargs`に保持されて，実装者と利用者により，各種の用途に用いることができる．

    Attributes: 

           tags (str, list(str)) : タグ文字列またはタグ文字列のリスト．実装者と利用者により，各種の用途に用いることができる．

           kwargs (dict) : オプション引数の辞書．オブジェクトの属性`kwargs`に保持されて，実装者と利用者により，各種の用途に用いることができる．
    """
    _freeLID = 0 #loggable id (lid)
    
    def __init__(self,
                 dep_init=0,
                 # dep_init=None,
                 max_children=-1, 
                 tags=None, 
                 verbose=False,
                 **kwargs):
        """
        生成するコンストラクタ．
        Args: 
             depth (int): デバッグ用の入れ子の深さを表す非負整数．デフォールトdepth=0

		     verbose (bool): 実行情報を表示する

             **kwargs (dict) : 他のキーワード引数．上位クラスに渡される．

        Atributes : 
            depth (int): デバッグ用のボード構成の入れ子の深さを表す非負整数．

            verbose (bool): 実行情報を表示する．

            id (int): ボードオブジェクトの連番．0で始まる．

            kwargs (dict) : キーワードを格納する辞書．キーワードは任意のものを使って良い．ボードの内部変数の階層化のためであり，関数`kw.get(kwargs, key)`を用いてアクセスする．
        """
        ## 引数
        self.depth = dep_init #dep_init can be None, which means `undefined`.
        self.verbose = verbose
        self.tags = None
        self.kwargs  = kwargs 
		
        ## 内部変数
        self.parent = None # 親オブジェクト
        self.id = Loggable._freeLID;          
        Loggable._freeLID += 1
		
        ## 子供
        self.children_ = [] # 子のリスト
        self.ord_   = None  # 子ID (親の子リスト中の自身の添字)．外部アクセスに必要．
        self.max_children_ = max_children # 子数の上限（>=0）．-1 means unbounded
		
        #タグ
        if tags != None:
            self.addTag(tags)
        return 

    #=====
    # キーワード辞書
    #=====
    def vars(self):
        """自身のオブジェクトの属性からなる辞書を返す．
        その際，未定義（値がNone）の属性はスキップする．
        """
        return kw.reduce(vars(self))
	
    def myinfo(self, depth=False, ord=False, tag=False):
        """便利関数．ログ用に，Boardオブジェクトの情報の文字列を返す．
          """
        bstr = self.__class__.__name__
        if depth: 
            bstr += f"[depth={ self.depth }]"
        if ord: 
            bstr += f"[ord={ self.ord_ }]"
        if tag and self.tag: 
            bstr += f"['{ self.tag }']"
        return bstr

    #=====
    # 親子関係
    #=====

    def fetch(self, key=None, default=None, verbose=False):
        """自分の先祖にフィールド`key`が定義されているボードがあれば，そのような直近の先祖での値を返す．もしそのような先祖がなければ，`default`が指定されていれば，その値を返し，それ以外ならば`None`を返す．
        
        Args: 
             key (str) : 検索するキー文字列

             default (Any) : キーをもつ先祖が見つからない時に返すデフォールト値
        
        Returns:
             (Any) : キーをもつ最近先祖におけるキーの値
        """
        com.ensure(key != None, f'fetch: key={key} must not be None!')
        com.ensure(default != None, f'fetch: default={default} must not be None!')
        if verbose:
            self.repo(msg=f'@debug:fetch: {self.myinfo()}.fetch:'+
                      f' key={key} => {key in vars(self)}: against'+
                      f' vars={kw.extract(self.vars(), deleted=["children_"])}')
        if key in vars(self) and (vars(self)[key] != None):
            return vars(self)[key]
        elif self.parent == None or not (isinstance(self.parent, Loggable)):
            return default
        else: ## assuming isinstance(self.parent, Loggable)
            val_ = self.parent.fetch(key=key, default=default)
            if verbose: self.repo(msg=f'@debug:fetch: {self.myinfo()}.fetch => val={val_}')
            com.ensure(val_ != None, f'fetch: val={val_} must not be None!')
            return val_

    #exp 親子関係の管理
    def register_child(self, child=None): 
        """親子関係の管理．
        
        Args: 
             child (Board) : 自身に追加する子．制約として，childは親をもってはいけない．すなわち，`child.parent != None`の場合は，エラーとなる．

        Note: 
             自身が既に子をもっていた場合は，エラーにならず，単に新しい子で上書きする．子が既に他の親を持っていた場合は，エラーを投げて強制終了する．
        """
        com.ensure(isinstance(child, Loggable),
                   f'child={child} must be a subclass of Loggable!')
        com.ensure(child.parent == None,
                   f'parent is already defined! parent={child.parent}')
         
        ##親の属性verboseを子に引き継ぐ．
        child.verbose = child.verbose or self.verbose
          
        ##親ボードを設定
        child.parent = self
        Loggable.adjust_depth(self, child) # 深さ調整
        return 

    def adjust_depth(parent=None, child=None, verbose=None):
        """再帰的に，属性`depth`を調整し，自分と全ての子孫に正しく深さを設定する．
        
        Args: 
               parent (Loggable) : 継ぎ木される親

               child (Loggable) : 継ぎ木する子

        Note: 
               次のように処理を行う: 

               * 木 t が整合的な深さ番号づけをもつとは，(i) `$depth(t.root) \ge 0$`，かつ，(ii) 根以外のノード$v$に対して $PropDepth(v.parent, v) <=> depth(v) = depth(v.parent) + 1$が成立する．
               * 既存の親木と子木のすべては，整合的な深さ番号づけをもつと仮定する．
               * ノード$u$にノード$v$を継ぎ木する場合に，性質$PropDepth(u, v)$が成立すれば何もしない．成立しなければ，$depth(v) := depth(v.parent) + 1$を実行し，$v$の全ての子$w in v.children()$に対して，$PropDepth(v, w)$の成立を検査する．
          """
        #print(f'{ "| "*dep }{ X.myinfo()} \tdepth={ X.depth }')
        com.ensure((parent != None and isinstance(parent, Loggable)),
                   f'parent must be a Loggable!')
        com.ensure((child != None and isinstance(child, Loggable)),
                   f'child must be a Loggable!')
        com.ensure((parent.depth != None and
                    type(parent.depth) in (int, float)),
                   f'parent.depth must be valid!: it={ parent.depth }')
        
        if child.depth == parent.depth + 1:
            pass 
        else: 
            #親から子へ深さを引き継ぐ
            child.depth = parent.depth + 1
            
            #すべての子に対して，再帰的に処理を行う
            for value in child.children():
                _, child1 = value
                Loggable.adjust_depth(parent=child, child=child1, verbose=verbose) 
        return

    #=====
    # 子のリスト
    #=====

    # exp 基本：子を追加する
    def append(self, pair=None): 
        """子ボードの対 pair (trans, child)を受け取り，子配列に追加する．

        * trans (cairo.Matrix) : 自座標における子の配置を指示する変換オブジェクト
        
        * child (Board): 子として追加するBoardオブジェクト
        
        Args: 
             pair (tuple) : 変換と子ボードの対 (trans, child)

        Returns:
             (Board) : 追加した子
         
        Example:: 
         
               root = Canvas()
               child = root.put(Board())
               child = parent.put(trans=Translate(x=1, y=2), Rectangle())
        """
        #子の型チェック
        com.ensure((pair != None and
                    com.is_sequence_type(pair, elemtype=None, length=2)),
                   ##elemtype=Noneは任意の型を許し，長さ=2のみテストする
                   f'{self.myinfo()}.put(): pair={pair} must be a pair of trans and child board!')
        trans, child = pair 
        #子の型チェック
        com.ensure(child != None and isinstance(child, Loggable),
                   f'{self.myinfo()}.put(): child must be a Loggable!: {child}') 
        # 親子関係の管理
        self.register_child(child)
        
        # 子を追加する
        if self.max_children_ >= 0 and len(self.children_) >= self.max_children_:
            com.panic(f'cannot add more than max_children_={self.max_children_}!')
        else:
            child.ord_ = len(self.children_)      #子ID
            self.children_.append(pair) #子リスト
            
        #ログ
        if self.verbose: self.repo(msg=f'=> added: {self.myinfo()}.put(): trans={trans} child={ child } with vars={ child.vars() }...')
        return #Do not change!

    # exp 基本：子を追加する
    def set_child_by_idx(self, idx=None, pair=None): 
        """添字 idx と変換と子ボードの対 pair (trans, child)を受け取り，
        子配列のidxセルにpairを代入する．
        添字は，下記の例のように元の配列から取り出したものに限る．

        * trans (cairo.Matrix) : 自座標における子の配置を指示する変換オブジェクト
        
        * child (Board): 子として追加するBoardオブジェクト
        
        Args: 
             idx (int) : 子配列の添字

             pair (tuple) : 変換と子ボードの対 (trans, child)

        Example:: 
         
             for idx, value in parent: 
                 trans, child = value
                 trans1, child1 = modifing(trans, child)
                 parent.set(idx, trans=trans1, child1) 
        """
        #子の型チェック
        com.ensure((pair != None and
                    com.is_sequence_type(pair, elemtype=None, length=2)),
                   ##elemtype=Noneは任意の型を許し，長さ=2のみテストする
                   f'{self.myinfo()}.put(): pair={pair} must be a pair of trans and child board!')
        trans, child = pair 
        # com.ensure(trans != None and isinstance(trans, GeoTransform),
        #            f'{self.myinfo()}.put(): trans must be a GeoTransform!: {trans}') 
        com.ensure(child != None and isinstance(child, Loggable),
                   f'{self.myinfo()}.put(): child must be a Loggable!: {child}') 
        # 親子関係の管理
        child.parent = None  #親への参照を来る
        self.register_child(child)
        
        # 子を追加する
        com.ensure(idx < len(self.children_), 
                   f'{self.myinfo()}.set(): index={idx} >= num of children={len(self.children_)}!')
        
        child.ord_ = idx    #子ID
        self.children_[idx] = (trans, child) #子リスト. 上書きなので注意!
            
        #ログ
        if self.verbose: self.repo(msg=f'overwrite =>{self.myinfo()}.set(): idx={idx} trans={trans} child={ child } with vars={ child.vars() }...')
        return child 

     # # exp 基本：子を追加する
     # def put_holder(self, holder=None): 
     #      """子を追加する．
          
     #      Args: 
     #           holder (LoggableHolder): 子として追加するクラスLoggableHolder（の部分クラス）のオブジェクト

     #      Returns:
     #           (LoggableHolder) : 追加した子ホルダー
     #      """
     #      #ホルダーの型チェック
     #      com.ensure(holder != None and isinstance(holder, LoggableHolder))
          
     #      #子の管理
     #      ## 型チェック
     #      child = holder.get_child()
     #      com.ensure(child != None and isinstance(child, Loggable),
     #                 f'{self.myinfo()}.put(): child must be a Loggable!: {child}') 
     #      ## 親子関係の管理
     #      self.register_child(child)
          
     #      # 子ホルダを追加する
     #      com.ensure(self.max_children_ >= 0 and len(self.children_) >= self.max_children_, 
     #                 f'cannot add more than max_children_={self.max_children_}!')
     #      child.ord_ = len(self.children_)      #子に自分の順位を設定する
     #      self.children_.append(holder) #子リスト
          
     #      #
     #      if self.verbose: self.repo(msg=f'=> added: {self.myinfo()}.put(): holder={holder} with vars={ child.vars() }...')
          
     #      return holder #Do not change!

    
    ##Override
    def children(self):
        """子エントリの並び children を返す．ここに，子エントリvalue = (trans, child) は，変換 trans と子オブジェクトchildの対である．
          
        Returns: 
             list: 子エントリvalue = (trans, child) のリスト
        """
        return self.children_  ##ダミー：子クラスでOverrideすること

        # idx = 0
        # for trans, child in self.children_:
        #     #子の型チェック
        #     com.ensure(isinstance(child, BoardBase),
        #                'child must be a subclass of BoardBase!: {child}')
        #     child_box = child.get_box()
        #     triple = trans, child, child_box
        #     yield idx, triple
        #     idx += 1
        
    ##Override
    def children_enumerated(self):
        """添字と子エントリの対`idx, value`の並び children を返す．
        現在は，`trans, child = value`である．部分クラスで上書きする．

        Returns: 
             list: 子オブジェクトのリスト
          
        Notes : 
             読み出し`idx, value = children_enumerated()`と書き込み`children_replace(idx, value)`を対にして用いる．
        """
        return enumerate(self.children_)  ##ダミー：子クラスでOverrideすること

        
    #=====
    # タグ
    #=====
    def getTags(self):
        """タグ文字列のリストを返す．

        Returns:
            (list(str)) : タグ文字列のリスト
        """
        return self.tags
      
    def addTag(self, tags):
        """タグ文字列を追加する．
        Args: 
             tags (str) : タグ文字列．任意のグルーピングに用いる．
          
        Returns:
             (Loggable) : 自分自身．いわゆる'cascade object call interface' のため．
        """
        if self.tags == None:
            self.tags = []
        if isinstance(tags, str):
            self.tags.append(tags)
        elif com.is_sequence_type(tags, elemtype=str):
            for a_tag in tags:
                if not (a_tag in self.tags): 
                    self.tags.append(a_tag)
        else:
            panic(f'tags={tags} must have as type str or list(str))!: {type(tags)}')
        return self #for cascade object interface
      
    #=====
    # ログ出力
    #=====
    def repo(self, msg=None, header=True, isChild=False, file=sys.stderr):
        """入れ子深さを考慮したレポート文字列を出力する．
        
        Args: 
             dep=0 (int): 入れ小深さ

             msg=None (str):  出力する文字列

             header=True (str):  出力するヘッダー文字列．ふつうは関数名 'methodname'

             file (outstream): 出力ストリーム．デフォールトsys.stderr

        Examples::

                self.repo(depth, msg=f'.send_draw: cmd={cmd} kwargs={kwargs1}')
         """
        if not isinstance(msg, str):
            print(f'warning: common.repo: msg="{msg} (type={type(msg)})" must be str!')
            
        if self.depth != None:
            dep_ = self.depth
        else:
            dep_ = 0
        if isChild:
            dep_ += 1
        if not (isinstance(dep_, int)):
            print(f'warning: common.py.repo: dep_={ dep_ } must be of int type!')     
        h=f'{ "| " * dep_ }'    #入れ小深さに対応する柱文字列を作成
        if header: 
            h += f'@{ self.myinfo() }'
        if len(msg) >= 1 and not (msg[0] in ('.', '_')):
            h += ': '
        print(f'{h}{msg}', file=file) 

    ##=====
    ## 表示
    ##=====
    def dump(self, dep=0, file=sys.stdout):
        """Loggableオブジェクトの構造を印刷する．

        Args: 
             B (Loggable) : ボードオブジェクトの根
        """
        print(f'{ "| "*dep }{ self.myinfo()}\t'+
              f' depth={ self.depth }'+f' ord_={ self.ord_ }'
              f' verbose={ self.verbose }', end='', file=file)
        if self.getTags() != None: 
            print(f' tags={self.getTags()}', end='', file=file)
            print('', file=file)
        for idx, pair in self.children_enumerated():
            trans, child = pair #分解
            if isinstance(child, Loggable):
                child.dump(dep=dep+1, file=file)
        return

    pass 

##=====
## 表示
##=====
def dump_board(B, dep=0):
    """Loggableオブジェクトの構造を印刷する．

     Args: 
          B (Loggable) : ボードオブジェクトの根
     """
    print(f'{ "| "*dep }{ B.myinfo()}\t'+
          f' depth={ B.depth }'+f' ord_={ B.ord_ }'
          f' verbose={ B.verbose }', end='')
    if B.getTags() != None: 
        print(f' tags={B.getTags()}', end='')
        print('')
    for idx, pair in B.children_enumerated():
        trans, child = pair #分解
        if isinstance(child, B):
            dump_board(child, dep=dep+1)
    return

## EOF
