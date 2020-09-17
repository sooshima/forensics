 Create PathList from fte_result.txt (※Export data from 'fte'.  'fte' is $MFT Parsing tool.)
  fte_result.txt' is delimited by "|" and its code is UTF-8(JP).
  fte --> http:#www.kazamiya.net/fte

$MFTのファイルID－親ファイルID分析

【例】
フォルダ構成

 (root) 3
     \
     |      1         2
     |---- aaa\ ---- xx.file
     |
     |      4         5
     |---- bbb\ ---- yy.file
     |        |
     |        |       6
     |        | ---- ccc\
     |                  |       7         8
     |                  | ---- ddd\ ---- zz.file
     

ファイル名	ファイルID	親ファイルID
---------	---------	------------
 aaa     	   1     	    3
 xx.file 	   2     	    1
(root)   	   3     	    3
 bbb     	   4     	    3
 yy.file 	   5     	    4
 ccc     	   6     	    4
 ddd     	   7     	    6
 zz.file 	   8     	    7
 
あるファイルのフルパス検索アルゴリズム
 ① rootフォルダのファイルIDを特定（ファイルID = 親ファイルID）
 ② 対象ファイルの親ファイルIDでファイルIDを検索し、親フォルダ名を特定
 ③ 特定した親フォルダの親ファイルIDでファイルIDを検索し、親の親フォルダを特定
 ④ ③をループ（終了条件：親ファイルID = rootフォルダのファイルID）
 
