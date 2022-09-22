# 210723 Boardクラスの座標変換

210723 by Hiroki Arimura, Hokkaido University, arim@ist.hokudai.ac.jp

<center>
<img border="1" width="150" src="fig/arrange5.png"/>
</center>

<!-- ![](fig/arrange5.png) -->

## あらまし

* Boardクラスの座標変換に必要な属性（インスタンス変数）の設計を行う．

## Boardクラスがもつ情報

クラスboardの各オブジェクトは，子オブジェクトの描画のための座表変換に必要な情報として，次の情報をもつ．

* **offset** `= p = (p0, p1): point`: 位置
* **ratio** `= r = (r0, r1): point`: 拡大率
* **anchor_point** `= a = (a0, a1): point`: 参照点．

一般に，anchor_pointは，子オブジェクトの生成時に利用者によって設定される．一方で，offsetとratioは，配置の際に，親によって与えられた情報と，子がもつ子孫から得られる情報から自動的に計算される．具体的には，次の情報が必要である

* **bb** `= [p, q]`:  子座標での包含長方形．`p`と`q`は定義された値と仮定する．`p`は`(0,0)` とは限らないので注意のこと．関数`arrange()`によって，その子オブジェクト全てから，ボトムアップに計算される．

* **xy** `= [p', q']`:  親座標での目標長方形．第1点`p'`のみ与えられ，第2点`q'`が不定のときは，恒等拡大`ratio=(1,1)`を仮定して，`offset`のみを求めると約束する．一般に，bbが求められた後で，利用者から引数として，または，親の文脈から与えられる．

詳細は，以下で説明する．


### 参照点

次のように定める．

* 参照点は，任意の点である．
* デフォールトは，bb=[p, q]の左隅の点pであり，アンカー文字列`'la'`で表す．
* 参照点のアンカー文字列は，包含長方形上の点（頂点と辺の中点）を表す次の2文字からなる文字列`ac in ('l','m','r')x('a','m','b')`である．中心点`'mm'`と周上の8近傍の点を表す．
* 第一の文字`ac[0]`は水平方向の位置を表わし，第二の文字`ac[1]`は垂直方向の位置を表わす．
* 次でアンカー指定から計算可能``
	`b.anchor_point() = vec.anchor_point(b.anchor)`

図形内部の参照点は，次のいずれかによって表す．

* 内部座標系での点 $p \in R^{2}$
* アンカー文字列 $ac$
* 異なる参照点の対 $line=[ac0, ac1] \in (R^{2})^{2}$ と，内分点の比率 $balance \in [0,1]$ 
	
### 点と図形の変換

親は，子c を用いて，子の座標系の点から，その親座標系での点を次の関数を用いて計算する．

```python 
class Board: 
  def trans_pos(p): 
    """子座標系の点pに対応する親座標系の点を求める
	"""
```

これは，情報(offset, ratio, anchor_point=(0,0))から，board `b` の内部座標の点 `p`は外部座標の点`pos(p)`に次のように変換される



* b.pos(p) = b.**offset** - b.**anchor_point**() + vec.scale(p, b.**ratio**)

図形がもつ制御点それぞれを関数 $\phi: R^{2} \to R^{2}$ で変換することで，その図形全体が変換される．例えば，長方形 $b=[p, q]$ は，$\phi(b) := [\phi(p), \phi(q)]$のように準同型によって変換される．

$$\forall x, x\in \phi(b) \iff \phi(x) \in [\phi(p), \phi(q)]$$

テキストの包含長方形のサイズはpxで与えられ，固定サイズの図形のサイズはptで与えられる．したがって，そのbbを求めるのには，逆写像が必要である．
これは，offsetとratioに分けて考えれば良い．

* 並行移動offsetは，そのまま順方向の変換で，参照点を写像して求められる．

* 拡大率ratioは， pxまたはptで表示されたサイズを，pxまたはptを単位にもつ基底画像までのratioの積で割ることで求められる．

### 変換情報の計算

以下では，子のアンカーポイント anchor_point は，利用者によって指定されていると仮定する．このとき，親は，子cの変換情報を次の関数を用いて計算する．

```python 
class Board: 
  def calculate_trans(xy=None, anchor=None): 
    """与えられた目標長方形xyに対して，
	- はじめに，自身の参照点をanchorに設定する．省略されたときは，子の既存点を使う．
	- 次に，bbを対応づける変換(offset, ratio)を求める．
	"""
```

これは，以下のように求める．

#### 変換情報の計算： 可変サイズ

変換情報 `(offset, ratio)` は，次のようにして情報 **xy** = dest_rect = [p, q], **bb** = [p', q'] から計算できる

**Find** (offset, ratio) **subject to**

*  xy = pos(b.**bb**)
$\iff$ **xy** = pos(**bb** | offset, ratio, anchor_point)
$\iff$ **xy** = offset - anchor_point + vec.scale(**bb**, ratio)
$\iff$ offset := **xy**[0] - (anchor_point - **bb**[0])
$\rule{1.75em}{0em}$ ratio := + (**xy**[1] - **xy**[0]) / (**bb**[1] - **bb**[0)]

#### 変換情報の計算： 固定サイズ

拡大率`ratio` は固定とする．このとき，変換情報 `offset` は，次のようにして情報 **xy** = dest_rect = [p, q], **bb** = src_rect = [p', q'] から計算できる．実際には，第一番目の点しかいらない．

* given **ratio**
*  **xy** = pos(b.**bb**)
$\iff$ **xy** = pos(**bb** | offset, ratio, anchor_point)
$\iff$ offset := **xy**[0] - (anchor_point - **bb**[0])

固定サイズの場合，拡大率は通常`ratio=(1,1)`である．
しかし，根付き木の描画の場合は，`ratio= shrink < (1,1)`とすることもある．

## 子の配置

親は，子を次のように配置する

* 再帰的に，子のbbを計算する．
* 子のbb列から，自身のbbを決定する．
* 順に，各子のbbと文脈から，その位置と大きさを決定する．

子の大きさと位置の設定は，次の方針で行う

### 親自身がサイズ指定をもたないとき

子のサイズはbbをそのまま使い，それらを含むのに十分なように親のサイズを決める．次に，子それぞれの位置を決める．

* `size == pack`: 
* `direction in (vertical, horizontal, grid)`: 
* `orient in (pack)`: 
* `margin`. オブジェクト`Spacer(margin=float, grue=float)`を間に挿入する．

### 親自身がサイズ指定をもつとき

親のサイズに合わせて，各子について文脈とそのbbから，そのサイズと位置を決める．

* `size == fixed`
* `direction in (vertical, horizontal)`: 
* `orient in (left, right, even)`: 
* `margin`. オブジェクト`Spacer(margin=float, grue=float)`を間に挿入する．

このとき，子自身に**拡大縮小型** `elastic in (fixed, iso, aniso, any)`をもたせるのが良いだろう．型が`fixed`ならば拡大縮小できない，`iso`ならば等方的にのみ拡大縮小でき，`(any, aniso, None)`ならば二方向に自由に拡大縮小できる．


## クラス図

```text 
class Board
 |   | * offset=p, ratio=p, anchor_point=p
 |   | * <-- parent.xy=[p,q]; self.bb()=[p,q], anchor_point=p
 | 
 |- class Canvas --> class PilImage
 |   | * offset=anchor_point==(0,0), ratio=(grid_len_px, grid_len_px) 
 |   |   grid_len_px := grid_len_pt * grid_len_pt
 |   | * PilImageへ渡す属性
 |   | * 自身の属性
 | 
 |- class DrawCommand
 |   | * PilImageの対応する描画演算へ渡す属性
 |   | * offset=anchor_point=(0,0), ratio=(1.0,1.0)
 |   | * <-- parent.xy=[p,q]; self.bb()=[(0,0), (xy[1] - xy[0])], anchor_point=p
 |   | 
 |   |- Line     : *xy=[p,q], 
 |   |- Rectangle: *xy=[p,q], (outline, width)
 |   |- Ellipse  : *xy=[p,q], (outline, width)
 |   |- Arc      : *xy=[p,q], start, end, (outline, width)
 | 
 |- class DrawCommandFixedSize
 |   |-- Dot : *xy=p, width, (fill)
 |   |-- Text: *xy=p, fontsize, (fill)
```

上記で，型は次の通り

* `num`は，数値 `(int, float)`. 
* `p`は，点または数値対`tuple(float,float)`
* `rect`は，点対`[p, p]`
* `*`は，変換対象の属性を表す．

## EOF

