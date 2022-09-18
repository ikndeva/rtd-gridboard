#=====
# 配置ボードのクラス obsolute 
#=====
class GridLocator(BoardBase):
    """アンカーオブジェクトのクラス
        Args: 
          num_x (int) : x方向のセルの個数

          num_y (int) : y方向のセルの個数

          margin (float) : セルとセルの間の余白．
    """
    def __init__(self,
                 num_x=None, 
                 num_y=None,
                 margin=0.0, 
                 **kwargs):
        """画盤オブジェクトを初期化する
        """
        super().__init__(**kwargs) #親の初期化
        if self.verbose:
            self.repo(msg=f'{self.myinfo()}.__init__(): { self.vars() }')
        #初期化
        self.shape = (num_x, num_y)
        self.margin = margin
        #作業変数
        ## Noneで埋められたサイズ(num_x x num_y)の2次元配列で初期化する
        self.grid = np.full(self.shape, None) 
        return

    def get_shape(self):
        """格子の形状 `(num_x, num_y)`を返す．
        """
        return self.shape

    # 基本：子画盤の並びを返す
    ##Override
    def children_enumerated(self):
        """添字とエントリの対`idx, value`の並び children を返す．実際にはiteratorを返す．
        現在は，`trans, child = value`である．
        Returns: 
        	list: 添字とエントリの対`idx, value`のリスト
        """
        ##ダミー：子クラスでOverrideすること
        shape = self.grid.shape
        com.ensure(isinstance(shape[0], int), f'shape[0]={shape[0]} must be int!: shape={shape}')
        com.ensure(isinstance(shape[1], int), f'shape[1]={shape[1]} must be int!: shape={shape}')
        for i in range(shape[0]):
            for j in range(shape[1]):
                value = self.grid[i, j]
                if value != None:
                    trans, child = value
                    yield ((i, j), (trans, child))

    # exp 基本：子を追加する
    def put(self, child=None, i=None, j=None): 
        """子を追加する．

        Args: 
             child (Board): 子として追加するBoardオブジェクト

             i (int) : x方向のセル添字

             j (int) : y方向のセル添字

        Returns:
            (Board) : 追加した子
        
        Example::
        
        		root = Canvas()
        		child = root.put(Board())
        		child = parent.put(trans=Translate(x=1, y=2), 
        			Rectangle())
        """
        com.ensure(child != None and isinstance(child, BoardBase),
                   'child must be a BoardBase!: {child}') #子の型チェック
        #配列に入れる
        shape = self.grid.shape
        shape0, shape1 = shape
        grid_new = self.grid
        if i >= shape0: 
            shape0 = i + 1 ##サイズは添字より一つ大きい
        if j >= shape1:
            shape1 = j + 1 ##サイズは添字より一つ大きい
        if shape0 > shape[0] or shape1 > shape[1]:
            #コピーする
            grid_new = np.full((shape0, shape1), None)
            for i_ in range(shape[0]):
                for j_ in range(shape[1]):
                    grid_new[i_, j_] = self.grid[i_, j_]
        
        #子の型チェックと親子関係の管理
        self.register_child(child)
        #新しい要素を入れる
        grid_new[i,j] = (None, child)
        child.ord_ = (i,j)
        
        self.grid = grid_new 
        if self.verbose: self.repo(msg=f'=> added {self.myinfo()}.put(): i={i} j={j} child={ child } with vars={ child.vars() }...')
        return child #do not change!

    #==========
    # ボードの配置
    #==========
    def _arrange(self):
        """配置を計算する．配置は，ボトムアップに再帰的に計算される．

        Args: 

        Returns: 
        	rect: 計算済みの自身の包含矩形オブジェクト
        """
        if self.verbose:
            self.repo(msg=f'{self.myinfo()}._arrange(): { self.vars() }')

        #1度目の子の巡回: 各子供の包含長方形を計算する
        maxlen_x, maxlen_y = 0, 0
        maxnum_x, maxnum_y = 0, 0
        boxes = EMPTY_RECT
        for idx, pair in self.children_enumerated():
            trans, child = pair #分解
            com.ensure(isinstance(child, BoardBase),
                       'child must be a subclass of BoardBase!: {child}') #子の型チェック
            com.ensure(trans == None or isinstance(trans, crt.GeoTransform),
                       f'trans must be of crt.GeoTransform: {type(trans)}')
            if self.verbose:
                self.repo(msg=f'=> [{idx}] calling on {idx}-th child={ child.myinfo() }', isChild=True, header=False)
                
            #子の再帰処理
            child_box = child._arrange()
            
            ## 縦横の最大値
            x0, y0, x1, y1 = crt.box_normalize(child_box) 
            maxlen_x = max(maxlen_x, x1 - x0)
            maxlen_y = max(maxlen_y, y1 - y0)
            if True:
                print(f'@debug:GridLocator: child_box={ child_box } => maxlen={maxlen_x, maxlen_y}')
            
            ## 添字の最大値
            i, j = idx
            maxnum_x = max(maxnum_x, i)
            maxnum_y = max(maxnum_y, j)
        self.shape = (maxnum_x + 1, maxnum_y + 1)
        
        if True:
            print(f'@debug:GridLocator: 1st-loop end => maxlen={maxlen_x, maxlen_y}')
        
        #2度目の子の巡回: 各子供の包含長方形を計算する
        boxes = EMPTY_RECT
        for idx, pair in self.children_enumerated():
            trans, child = pair #分解
            i, j = idx
            x0, y0 = (maxlen_x + self.margin)*i, (maxlen_y + self.margin)*j 
            x1, y1 = x0 + maxlen_x, y0 + maxlen_y
            trans_new = crt.Translate(x=x0, y=y0)
            if True:
                print(f'@debug:GridLocator: ij={i,j} x0,y0={x0,y0} x1,y1={x1,y1}, trans_new={trans_new}')
            self.children_replace(idx=idx, value=(trans_new, child))
            child_box = (x0, y0, x1, y1)
            #child_box = crt.box_apply_trans(child_box, trans=trans)
            boxes = crt.box_union(boxes, child_box) #包含矩形の更新
        self.box_self = boxes

        #自身の描画配置情報を得る
        #包含矩形の処理は自身の責任で行う．
        self.arrange_me_post()
        
        if self.verbose:
            self.repo(msg=f'{self.myinfo()}._arrange()=> box={ boxes }', isChild=True)
            for idx, pair in self.children_enumerated():
                trans, child = pair
                self.repo(msg=f'@debug:arrange {idx} trans={trans}, child={child.myinfo()}::{child.vars()}', isChild=True)
        return self.box_self

    pass
