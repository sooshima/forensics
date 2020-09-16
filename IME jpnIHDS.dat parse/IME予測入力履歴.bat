@echo off
echo @@@ IME予測入力履歴表示 @@@  2020/6/4版
echo +++

rem 作業ディレクト変更
%~d0
cd /d %~dp0

rem 取得データ保存先作成
set time_tmp=%time: =0%
set now=%date:/=%%time_tmp:~0,2%%time_tmp:~3,2%%time_tmp:~6,2%
rem echo %now%
set BUFolder=%now%
mkdir %BUFolder%


rem IME予測入力データ取得
mkdir %BUFolder%\JpnIHDS
set JpnIHDS_dat=%APPDATA%\Microsoft\InputMethod\Shared\JpnIHDS.dat
IF exist %JpnIHDS_dat% goto NEXT_Process
echo "Error : JpnIHDS.dat not found"
pause
exit /b

:NEXT_Process
copy %JpnIHDS_dat% %BUFolder%\JpnIHDS\
echo JpnIHDS.datを %BUFolder%\JpnIHDS\フォルダに保存しました

rem JpnIHDS.datからIME予測入力履歴を抽出
echo 分析開始．．．
IME_jp_parse.exe .\%BUFolder%\JpnIHDS\JpnIHDS.dat .\%BUFolder%\IME_JpnIHDS_history.csv.tmp
sort %BUFolder%\IME_JpnIHDS_history.csv.tmp > %BUFolder%\IME_JpnIHDS_history.csv
del %BUFolder%\IME_JpnIHDS_history.csv.tmp

echo +++
echo +++ 完了!!
echo +++ 結果は %BUFolder%\IME_JpnIHDS_history.csv に保存されました
echo +++ 【注意】履歴の時刻は、PCに設定された地域のローカルタイム（JST等）です！！
echo +++
echo +++ 続いて上記ファイルをメモ帳で表示します
echo +++ 【注意】データ内に半角の「"」（コーテーション）が含まれているとき、
echo +++ csvファイルをExcelで開くと表示がおかしくなる場合があります！
echo +++
echo +++   Please push any key...
pause > nul

rem 結果表示
notepad %BUFolder%\IME_JpnIHDS_history.csv
