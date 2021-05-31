# PRO_2021_1
<実行方法>
順方向バイトコード生成; java Parser XXX.txt
順方向実行: python vm_CUI.py code.txt f
逆方向バイトコード生成: python vm_CUI.py code.txt c
逆方向実行: python vm_CUI.py inv_code.txt b


<実行環境>
Parser.jj: 対象プログラムのソースコードから順方向バイトコードを生成するプログラム
vm_CUI.py: 順方向実行，逆方向バイトコードへの変換，逆方向実行をするプログラム


<サンプルプログラム>
airline.txt: 手続きの例，何度か実行すると多くの場合seatsの値は0であるが-1になることがある。
bug_fact.txt: 再帰関数の例，実行毎に生成されるプロセス数が異なる．
