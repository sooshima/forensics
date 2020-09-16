# coding: cp932
#  修正履歴
#   2018/10/23 IPv4正規表現のバグ修正（完了 第４オクテットが３桁の場合に末尾が落ちるバグを修正）
#   2018/10/24 IPv6正規表現のバグ修正（完了 途中に"::"や"0000"が含まれる場合も正しく抽出するよう修正）
#   2018/10/25 １行に複数のIPアドレスが含まれる場合に全て抽出するよう対応 （完了）
#   2020/09/08 WhoisサイトのURL及びデザイン変更に対応 （完了）

import wx,os,sys
import urllib,urllib.request
from urllib.parse import urlparse
import http.client
import base64
import re
from time import sleep 
import threading
import datetime

def choose_file_in(self): # 入力ファイル参照ボタンクリック時のイベント（フォルダ選択ダイアログ）
  in_filename = frame.box_infile.GetValue
  file = wx.FileDialog(None, "入力ファイルの指定", style=wx.DD_CHANGE_DIR,)
  if file.ShowModal() == wx.ID_OK:
      in_filename = file.GetPath()
      frame.box_infile.SetValue(in_filename)
  file.Destroy()

def choose_file_ot(self): # 出力ファイル参照ボタンクリック時のイベント（フォルダ選択ダイアログ）
  ot_filename = frame.box_otfile.GetValue
  file = wx.FileDialog(None, "出力ファイルの指定", style=wx.DD_CHANGE_DIR,)
  if file.ShowModal() == wx.ID_OK:
      ot_filename = file.GetPath()
      frame.box_otfile.SetValue(ot_filename)
  file.Destroy()
  
def state_change_stealth(self): # ステルス端末のチェックボックス処理
  state_stealth = frame.check_stealth.GetValue()
  if state_stealth:
    frame.code_stealth.Enable() # チェックボックスがオンなら職番パスの入力を有効にする
    frame.pass_stealth.Enable()
    frame.label_code.SetForegroundColour('#000000') # 職番のラベルをブラックに
    frame.label_pass.SetForegroundColour('#000000') # パスのラベルをブラックに
    frame.Refresh()
  else:
    frame.code_stealth.Disable() # チェックボックスがオフなら職番パスの入力を無効にする
    frame.pass_stealth.Disable()
    frame.label_code.SetForegroundColour('#808080') # 職番のラベルをグレーアウト
    frame.label_pass.SetForegroundColour('#808080') # パスのラベルをグレーアウト
    frame.Refresh()
    
def whois_edit(w_html_data,op_delimiter): #Whois情報の編集処理
  # ネットワーク名
  o_netname = re.search(r"<th>description</th><td>(?!Japan Network Info).*?</td>",str(w_html_data))
  if o_netname:
    whois_netname = o_netname.group()
  else:
    o_netname = re.search(r"<th>name</th><td>(?!JPNIC).*?</td>",str(w_html_data))
    if o_netname:
      whois_netname = o_netname.group()
    else:
      whois_netname = "??unknown"
  whois_netname = re.sub(r'<br/>.*?</td>|<td>|</td>|<th>|</th>|description|name',"",str(whois_netname))
  whois_netname = re.sub(',',"-",str(whois_netname))
  whois_netname = 'netname=' + whois_netname

  # 国名
  o_country = re.search(r"<th>country</th><td>.*?</td>",str(w_html_data))
  if o_country:
    whois_country = o_country.group()
  else:
    o_country = re.search(r"<th>Country</th><td>.*?</td>",str(w_html_data))
    if o_country:
      whois_country = o_country.group()
    else:
      whois_country = "??"
  whois_country = re.sub(r'<td>|</td>|<th>|</th>|country|Country',"",str(whois_country))
  whois_country = re.sub(',',"-",str(whois_country))
  whois_country = 'country=' + whois_country

  # 逆引きしたhost名を切り取り
  # o_hostname = re.search(r'<div class="panel-heading"><strong>.*?</strong></div>',str(w_html_data))  2020/09/08 サイトのデザイン変更に対応
  o_hostname = re.search(r'<div class="card mb-3"><div class="card-header"><strong>.*?</strong></div>',str(w_html_data))
  if o_hostname:
    nslookup_hostname = o_hostname.group()
  else:
    nslookup_hostname = "??"
  nslookup_hostname = re.sub(r'<div class="card mb-3"><div class="card-header"><strong>|</strong></div>',"",str(nslookup_hostname))
  nslookup_hostname = re.sub(',',"-",str(nslookup_hostname))
  nslookup_hostname = 'host=' + nslookup_hostname

  whois_result = whois_netname + op_delimiter + whois_country + op_delimiter + nslookup_hostname
  return whois_result

def hostname_edit(n_html_data): # host名の編集処理
  # 逆引きしたhost名を切り取り
  o_hostname = re.search(r"PTR</td><td>.*?</tr>",str(n_html_data))
  if o_hostname:
    nslookup_hostname = o_hostname.group()
  else:
    nslookup_hostname = "??"
  nslookup_hostname = re.sub(r'PTR|<td>|</td>|<tr>|</tr>',"",str(nslookup_hostname))
  nslookup_hostname = re.sub(',',"---",str(nslookup_hostname))
  nslookup_hostname = 'host=' + nslookup_hostname
  return nslookup_hostname  
  
#### Whois情報取得 ##### ここから
def whois_ip():  # 実行ボタンクリック時のイベント
  infile = frame.box_infile.GetValue()  # 入力ファイル名のセット
  otfile = frame.box_otfile.GetValue()  # 出力ファイル名のセット
  option_ot = element_array[combobox_option.GetSelection()]  # 区切り文字等、出力オプションのセット
  text = ""  # メッセージのクリア
  
  # 区切り文字（オプション）のセット  ※デフォルトはCSV
  op_delimiter = ","
  if (option_ot == "t"):
    op_delimiter = "\t"
  if (option_ot == "s"):
    op_delimiter = " "
  flg_IPonly = 0
  if (option_ot == "i"):
    flg_IPonly = 1   # IPアドレスと取得情報のみ出力

  # プロキシ設定（ステルス端末使用の場合）
  state_stealth = frame.check_stealth.GetValue()
  if state_stealth:
    code_txt = frame.code_stealth.GetValue()
    pass_txt = frame.pass_stealth.GetValue()
    hostname = "10.1.0.241"
    port = "8080"
    test = http.client.HTTPSConnection(hostname, port) 
    conn = http.client.HTTPSConnection(hostname, port) 
    auth = code_txt + ":" + "pass_txt"
    auth_b = base64.b64encode(auth.encode('utf-8'))
    auth_header = 'Basic ' + auth_b.decode('utf-8')
    # プロキシ経由でSSLトンネルのコネクションを確立する
    try:
      # プロキシ認証チェック（接続テスト）
      test.set_tunnel("https://whois.toolforge.org/", 443, headers={
       'User-Agent': 'Python3',
       'Host': 'https://whois.toolforge.org/:443',
       'Proxy-Authorization':auth_header
      })
      # Whoisサイトへ接続してみる
      test.request("GET", "/", headers={
       'User-Agent': 'Python3',
      })
      # 認証エラーがなければ再度コネクションを張り直す
      conn.set_tunnel("https://whois.toolforge.org/", 443, headers={
       'User-Agent': 'Python3',
       'Host': 'https://whois.toolforge.org/:443',
       'Proxy-Authorization':auth_header
      })
    except:
      text = text + "\r\n\r\n!プロキシ認証エラー!\r\n"
      text = text + "\r\n\r\n ※ 職番・パスワードの誤り、もしくはプロキシサーバーの障害\r\n"
      frame.label_message.SetLabel(text)
      execute_btn.Enable() # 実行ボタンを元に戻す
      execute_btn.SetLabel("実行") 
      return


  # 開始メッセージ表示処理
  text = ""
  text = infile + "\r\nに含まれるIPアドレスのWhois情報を取得します\r\n"
  text = text + "出力オプション："
  text = text + option_ot
  if state_stealth:
    stealth_msg = "\r\nステルス端末を使用する（プロキシ経由）"
  else:
    stealth_msg = "\r\nステルス端末を使用しない（インターネットに直接接続）"
  text = text + stealth_msg
  frame.label_message.SetLabel(text)
  dialog = wx.MessageDialog(None, u'Whois情報取得を開始します\r\n' + stealth_msg, u'処理開始', wx.YES_NO)
  result = dialog.ShowModal()
  if result == wx.ID_NO:
    text = text + "\r\n\r\n処理を中止しました。\r\n"
    frame.label_message.SetLabel(text)
    return
  execute_btn.Disable() # 実行ボタンを無効化
  execute_btn.SetLabel("処理中...") 
  start_msg = text + "\r\n\r\nStart!   " + datetime.datetime.today().strftime("%Y/%m/%d %H:%M:%S") + "\r\n"
  start_msg = start_msg + "\r\n処理中・・・ \r\n"
  text = start_msg
  frame.label_message.SetLabel(text)
  frame.Refresh()

  # 入出力ファイルのオープン
  try:
    ifile = open(infile, 'r')
  except:
    text = text + "\r\n\r\n!入力ファイルを開くことができません!\r\n"
    frame.label_message.SetLabel(text)
    execute_btn.Enable() # 実行ボタンを元に戻す
    execute_btn.SetLabel("実行") 
    return
    
  try:
    ofile = open(otfile, 'w')
  except:
    text = text + "\r\n\r\n!出力ファイルを開くことができません!\r\n"
    frame.label_message.SetLabel(text)
    ifile.close
    execute_btn.Enable() # 実行ボタンを元に戻す
    execute_btn.SetLabel("実行") 
    return
       
  # 1行読み込み
  buf_line = ifile.readline()
  icnt = 0
  Save_IPadd = ""
  Save_buf_out = ""

### --- Start of loop ---
  while buf_line:
    # 改行コード除去
    buf_line = buf_line.replace('\r','')
    buf_line = buf_line.replace('\n','')

    # 正規表現でIPアドレスを抽出
    # V4
    Array_IPadd  = re.findall("((1[0-9]{2}|2[0-4][0-9]|25[0-5]|[1-9]?[0-9])\.(1[0-9]{2}|2[0-4][0-9]|25[0-5]|[1-9]?[0-9])\.(1[0-9]{2}|2[0-4][0-9]|25[0-5]|[1-9]?[0-9])\.(1[0-9]{2}|2[0-4][0-9]|25[0-5]|[1-9]?[0-9]))",buf_line)
    if not Array_IPadd:
      # V6
      Array_IPadd  = re.findall("(([0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|(([0-9a-fA-F]{1,4}:){1,6}:)[0-9a-fA-F]{1,4}(:[0-9a-fA-F]{1,4}){0,5}|([0-9a-fA-F]{1,4}:){1,7}:|([0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,5}(:[0-9a-fA-F]{1,4}){1,2}|([0-9a-fA-F]{1,4}:){1,4}(:[0-9a-fA-F]{1,4}){1,3}|([0-9a-fA-F]{1,4}:){1,3}(:[0-9a-fA-F]{1,4}){1,4}|([0-9a-fA-F]{1,4}:){1,2}(:[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:((:[0-9a-fA-F]{1,4}){1,6})|:((:[0-9a-fA-F]{1,4}){1,7}|:)|fe80:(:[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|::(ffff(:0{1,4}){0,1}:){0,1}((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])|([0-9a-fA-F]{1,4}:){1,4}:((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9]))",buf_line)

    if Array_IPadd:  # 読み込んだ行にIPアドレスが含まれる場合
      buf_out = str(buf_line)
      
####### 第２Loop （１行に含まれるIPアドレスを全てWhois）
      for Ar2_IPadd in Array_IPadd:
      
        # 検索結果は２次元配列になっており、先頭セルにIPアドレスのフル桁がセットされているため取り出す
        IPadd = str(Ar2_IPadd[0])

        # iオプションの場合はIPアドレスとWhois情報のみ出力
        if flg_IPonly == 1:  
          buf_out = str(IPadd)
        else:
          buf_out = buf_out + op_delimiter + str(IPadd)
          #print("--debug-- IPonly buf_line : " + IPadd)
        
        # IPアドレスが前のデータと同じなら、取得済みのWhois情報をセットして、Webアクセスはスキップ
        if IPadd == Save_IPadd:
          buf_out = str(buf_out) + op_delimiter + whois_result
          Save_IPadd = IPadd  # IPアドレスのセーブ（比較用）
          IPadd = ""
        else:
          Save_IPadd = IPadd  # IPアドレスのセーブ（比較用）

        # Whois & nslookup 実行
        if (IPadd != ""):

          if state_stealth:  #ステルス端末使用時（プロキシ経由）
            req_url = "/gateway.py?lookup=true&ip=" + IPadd
            try:
              conn.request("GET", req_url, headers={
               'User-Agent': 'Python3',
              })
              response = conn.getresponse()
            except:
              whois_result = "!! Whois Access Error in request"
              buf_out = str(buf_out) + op_delimiter + whois_result
            else:
              try:
                # Whois結果を取得
                w_html_data_b =response.read()
                w_html_data = w_html_data_b.decode('utf-8')
              except:
                whois_result = "!! Whois Access Error in open.read"
                buf_out = str(buf_out) + op_delimiter + whois_result
              else:  
                # whois情報からネットワーク名・国名・ホスト名を切り取り
                whois_result = whois_edit(w_html_data,op_delimiter)
                # 結果を出力バッファーにセット
                buf_out = str(buf_out) + op_delimiter + whois_result

          else:  #インターネットに直接接続した端末使用時
            # whois_url = "https://tools.wmflabs.org/whois/gateway.py"  2020/9/8 URL変更対応
            whois_url = "https://whois.toolforge.org/gateway.py"
            params = {
                      'lookup':'true', 'ip':IPadd
            }
            try:
              obj_url = urllib.request.Request('{}?{}'.format(whois_url, urllib.parse.urlencode(params)))
            except:
              whois_result = "!! Whois Access Error in request"
              buf_out = str(buf_out) + op_delimiter + whois_result
            else:
              try:
                # Whois結果を取得
                res = urllib.request.urlopen(obj_url)
                w_html_data = res.read()
              except:
                whois_result = "!! Whois Access Error in open.read"
                buf_out = str(buf_out) + op_delimiter + whois_result
              else:  
                # whois情報からネットワーク名・国名・ホスト名を切り取り
                whois_result = whois_edit(w_html_data,op_delimiter)
                # 結果を出力バッファーにセット
                buf_out = str(buf_out) + op_delimiter + whois_result
                #print("--debug-- str(buf_line) : " + str(buf_line))
                #print("--debug-- buf_out : " + buf_out)
                res.close
        # オプション"i"のときはIPアドレス毎に出力
        if flg_IPonly == 1:
          if buf_out != Save_buf_out:
            ofile.write(str(buf_out) + "\n")

          Save_buf_out = buf_out

####### ------第２Loopここまで

      # １行分の結果出力（オプション"i"以外）
      if flg_IPonly == 0:
        ofile.write(str(buf_out) + "\n")
     
    # IPアドレスが含まれない行はそのまま出力(オプションｉの場合を除く)
    else:
      buf_out = str(buf_line)
      if flg_IPonly == 0:
        ofile.write(str(buf_out) + "\n")

    # 処理件数カウント＆メッセージ表示
    icnt = icnt + 1
    if ((icnt % 50) == 0):
      text = text + "\r\n--- processed " + str(icnt) + " lines "
      frame.label_message.SetLabel(text)
      frame.Refresh()

    # 1行読み込み
    buf_out = ""
    buf_line = ""
    buf_line = ifile.readline()
### --- End of loop ---

  # 入出力ファイルのクローズ
  ifile.close
  ofile.close

  # 終了メッセージ
  text = start_msg + "\r\n\r\nDone!!   " + datetime.datetime.today().strftime("%Y/%m/%d %H:%M:%S") + "\r\n"
  frame.label_message.SetLabel(text)

  execute_btn.Enable() # 実行ボタンを元に戻す
  execute_btn.SetLabel("実行") 

  return

#### Whois情報取得 ##### ここまで

# 実行ボタン押下処理（マルチスレッド）
def Clicked(self):  # 実行ボタンクリック時のイベント

  th1 = threading.Thread(name="a", target=whois_ip, args=())
  th1.start()
  

############################################

if __name__ == "__main__":# メイン
   
  # メインウィンドウ設定
  #app = wx.PySimpleApp()
  app = wx.App()
  frame = wx.Frame(None, -1, "WhoisTool" , size=(550,600))
  frame.SetTitle('Whois情報自動取得ツール V2  by ooshima')
  panel_ui = wx.Panel(frame, -1, pos=(50, 50), size=(300, 300))
   
  # 入力ファイル指定テキストボックス
  desktop_folder = os.path.expanduser('~') + "\\Desktop\\"
  frame.label_infile = wx.StaticText(panel_ui, -1, '入力ファイル（ログ等に含まれるIPアドレスを自動検出してWhois情報を出力します）', pos=(10, 10))
  frame.box_infile = wx.TextCtrl(panel_ui, -1, pos=(10, 30), size=(450,40), style=wx.TE_MULTILINE)
  frame.box_infile.SetValue(desktop_folder)
  choose_btn_infile = wx.Button(panel_ui, -1, '参照', pos=(470, 30), size=(40,20))
  choose_btn_infile.Bind(wx.EVT_BUTTON, choose_file_in)  # 参照ボタンとクリック時のイベントをバインド

  # 出力ファイル指定テキストボックス
  frame.label_otfile = wx.StaticText(panel_ui, -1, '出力ファイル', pos=(10, 80))
  frame.box_otfile = wx.TextCtrl(panel_ui, -1, pos=(10, 100), size=(450,40), style=wx.TE_MULTILINE)
  frame.box_otfile.SetValue(desktop_folder)
  choose_btn_otfile = wx.Button(panel_ui, -1, '参照', pos=(470, 100), size=(40,20))
  choose_btn_otfile.Bind(wx.EVT_BUTTON, choose_file_ot)  # 参照ボタンとクリック時のイベントをバインド
   
  # 出力オプション選択コンボボックス
  frame.label_option = wx.StaticText(panel_ui, -1, '出力オプション', pos=(10, 180))
  element_array = ('i', 't', 's','c')
  combobox_option = wx.ComboBox(panel_ui, wx.ID_ANY, '' , choices=element_array, style=wx.CB_DROPDOWN, pos=(10, 200))
  help_text = "i ･･･ IPとWhois情報のみ出力"
  help_text = help_text + "\nt ･･･ タブ区切りで元データにWhois情報を追加"
  help_text = help_text + "\ns ･･･ スペース区切りで元データにWhois情報を追加"
  help_text = help_text + "\nc ･･･ カンマ区切りで元データにWhois情報を追加（デフォルト）"
  frame.label_help = wx.StaticText(panel_ui, -1, help_text, pos=(70, 200))
   
  # ステルス端末のプロキシ設定（チェックボックス、IDパスワード入力ボックス） ※ステルスのプロキシ経由でSSLが通信不可のため、V2では使用できない
  frame.check_stealth = wx.CheckBox(panel_ui, -1, 'ステルス端末を使用', pos=(380, 200))
  frame.check_stealth.SetValue(False)
  frame.check_stealth.Bind(wx.EVT_CHECKBOX, state_change_stealth)
  frame.label_code = wx.StaticText(panel_ui, -1, 'k職番+M', pos=(400, 220))
  frame.code_stealth = wx.TextCtrl(panel_ui, -1, pos=(450, 220), size=(70,20))
  frame.label_pass = wx.StaticText(panel_ui, -1, 'パスワード', pos=(400, 240))
  frame.pass_stealth = wx.TextCtrl(panel_ui, -1, pos=(450, 240), size=(70,20), style=wx.TE_PASSWORD)
  frame.label_code.SetForegroundColour('#808080') # 職番のラベルをグレーアウト
  frame.label_pass.SetForegroundColour('#808080') # パスのラベルをグレーアウト
  ### frame.check_stealth.Disable()
  frame.code_stealth.Disable()
  frame.pass_stealth.Disable()
  
  # 実行ボタン
  execute_btn = wx.Button(panel_ui, -1, '実行', pos=(220, 270))
  execute_btn.Bind(wx.EVT_BUTTON, Clicked)  # 実行ボタンとクリック時のイベントをバインド（Whois情報取得処理）
   
  # メッセージ表示ラベル
  #frame.label_message = wx.StaticText(panel_ui, -1, '', pos=(10, 310), size=(480,240), style=wx.TE_MULTILINE|wx.SUNKEN_BORDER
  frame.label_message = wx.TextCtrl(panel_ui, -1, '', pos=(10, 300), size=(480,250), style=wx.TE_READONLY|wx.TE_MULTILINE|wx.SUNKEN_BORDER)
  frame.label_message.SetForegroundColour('#FF0000')
   
  # メインウィンドウ表示
  frame.Show(True)
  app.SetTopWindow(frame)
  app.MainLoop()
