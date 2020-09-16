# coding: cp932
#  �C������
#   2018/10/23 IPv4���K�\���̃o�O�C���i���� ��S�I�N�e�b�g���R���̏ꍇ�ɖ�����������o�O���C���j
#   2018/10/24 IPv6���K�\���̃o�O�C���i���� �r����"::"��"0000"���܂܂��ꍇ�����������o����悤�C���j
#   2018/10/25 �P�s�ɕ�����IP�A�h���X���܂܂��ꍇ�ɑS�Ē��o����悤�Ή� �i�����j
#   2020/09/08 Whois�T�C�g��URL�y�уf�U�C���ύX�ɑΉ� �i�����j

import wx,os,sys
import urllib,urllib.request
from urllib.parse import urlparse
import http.client
import base64
import re
from time import sleep 
import threading
import datetime

def choose_file_in(self): # ���̓t�@�C���Q�ƃ{�^���N���b�N���̃C�x���g�i�t�H���_�I���_�C�A���O�j
  in_filename = frame.box_infile.GetValue
  file = wx.FileDialog(None, "���̓t�@�C���̎w��", style=wx.DD_CHANGE_DIR,)
  if file.ShowModal() == wx.ID_OK:
      in_filename = file.GetPath()
      frame.box_infile.SetValue(in_filename)
  file.Destroy()

def choose_file_ot(self): # �o�̓t�@�C���Q�ƃ{�^���N���b�N���̃C�x���g�i�t�H���_�I���_�C�A���O�j
  ot_filename = frame.box_otfile.GetValue
  file = wx.FileDialog(None, "�o�̓t�@�C���̎w��", style=wx.DD_CHANGE_DIR,)
  if file.ShowModal() == wx.ID_OK:
      ot_filename = file.GetPath()
      frame.box_otfile.SetValue(ot_filename)
  file.Destroy()
  
def state_change_stealth(self): # �X�e���X�[���̃`�F�b�N�{�b�N�X����
  state_stealth = frame.check_stealth.GetValue()
  if state_stealth:
    frame.code_stealth.Enable() # �`�F�b�N�{�b�N�X���I���Ȃ�E�ԃp�X�̓��͂�L���ɂ���
    frame.pass_stealth.Enable()
    frame.label_code.SetForegroundColour('#000000') # �E�Ԃ̃��x�����u���b�N��
    frame.label_pass.SetForegroundColour('#000000') # �p�X�̃��x�����u���b�N��
    frame.Refresh()
  else:
    frame.code_stealth.Disable() # �`�F�b�N�{�b�N�X���I�t�Ȃ�E�ԃp�X�̓��͂𖳌��ɂ���
    frame.pass_stealth.Disable()
    frame.label_code.SetForegroundColour('#808080') # �E�Ԃ̃��x�����O���[�A�E�g
    frame.label_pass.SetForegroundColour('#808080') # �p�X�̃��x�����O���[�A�E�g
    frame.Refresh()
    
def whois_edit(w_html_data,op_delimiter): #Whois���̕ҏW����
  # �l�b�g���[�N��
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

  # ����
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

  # �t��������host����؂���
  # o_hostname = re.search(r'<div class="panel-heading"><strong>.*?</strong></div>',str(w_html_data))  2020/09/08 �T�C�g�̃f�U�C���ύX�ɑΉ�
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

def hostname_edit(n_html_data): # host���̕ҏW����
  # �t��������host����؂���
  o_hostname = re.search(r"PTR</td><td>.*?</tr>",str(n_html_data))
  if o_hostname:
    nslookup_hostname = o_hostname.group()
  else:
    nslookup_hostname = "??"
  nslookup_hostname = re.sub(r'PTR|<td>|</td>|<tr>|</tr>',"",str(nslookup_hostname))
  nslookup_hostname = re.sub(',',"---",str(nslookup_hostname))
  nslookup_hostname = 'host=' + nslookup_hostname
  return nslookup_hostname  
  
#### Whois���擾 ##### ��������
def whois_ip():  # ���s�{�^���N���b�N���̃C�x���g
  infile = frame.box_infile.GetValue()  # ���̓t�@�C�����̃Z�b�g
  otfile = frame.box_otfile.GetValue()  # �o�̓t�@�C�����̃Z�b�g
  option_ot = element_array[combobox_option.GetSelection()]  # ��؂蕶�����A�o�̓I�v�V�����̃Z�b�g
  text = ""  # ���b�Z�[�W�̃N���A
  
  # ��؂蕶���i�I�v�V�����j�̃Z�b�g  ���f�t�H���g��CSV
  op_delimiter = ","
  if (option_ot == "t"):
    op_delimiter = "\t"
  if (option_ot == "s"):
    op_delimiter = " "
  flg_IPonly = 0
  if (option_ot == "i"):
    flg_IPonly = 1   # IP�A�h���X�Ǝ擾���̂ݏo��

  # �v���L�V�ݒ�i�X�e���X�[���g�p�̏ꍇ�j
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
    # �v���L�V�o�R��SSL�g���l���̃R�l�N�V�������m������
    try:
      # �v���L�V�F�؃`�F�b�N�i�ڑ��e�X�g�j
      test.set_tunnel("https://whois.toolforge.org/", 443, headers={
       'User-Agent': 'Python3',
       'Host': 'https://whois.toolforge.org/:443',
       'Proxy-Authorization':auth_header
      })
      # Whois�T�C�g�֐ڑ����Ă݂�
      test.request("GET", "/", headers={
       'User-Agent': 'Python3',
      })
      # �F�؃G���[���Ȃ���΍ēx�R�l�N�V�����𒣂蒼��
      conn.set_tunnel("https://whois.toolforge.org/", 443, headers={
       'User-Agent': 'Python3',
       'Host': 'https://whois.toolforge.org/:443',
       'Proxy-Authorization':auth_header
      })
    except:
      text = text + "\r\n\r\n!�v���L�V�F�؃G���[!\r\n"
      text = text + "\r\n\r\n �� �E�ԁE�p�X���[�h�̌��A�������̓v���L�V�T�[�o�[�̏�Q\r\n"
      frame.label_message.SetLabel(text)
      execute_btn.Enable() # ���s�{�^�������ɖ߂�
      execute_btn.SetLabel("���s") 
      return


  # �J�n���b�Z�[�W�\������
  text = ""
  text = infile + "\r\n�Ɋ܂܂��IP�A�h���X��Whois�����擾���܂�\r\n"
  text = text + "�o�̓I�v�V�����F"
  text = text + option_ot
  if state_stealth:
    stealth_msg = "\r\n�X�e���X�[�����g�p����i�v���L�V�o�R�j"
  else:
    stealth_msg = "\r\n�X�e���X�[�����g�p���Ȃ��i�C���^�[�l�b�g�ɒ��ڐڑ��j"
  text = text + stealth_msg
  frame.label_message.SetLabel(text)
  dialog = wx.MessageDialog(None, u'Whois���擾���J�n���܂�\r\n' + stealth_msg, u'�����J�n', wx.YES_NO)
  result = dialog.ShowModal()
  if result == wx.ID_NO:
    text = text + "\r\n\r\n�����𒆎~���܂����B\r\n"
    frame.label_message.SetLabel(text)
    return
  execute_btn.Disable() # ���s�{�^���𖳌���
  execute_btn.SetLabel("������...") 
  start_msg = text + "\r\n\r\nStart!   " + datetime.datetime.today().strftime("%Y/%m/%d %H:%M:%S") + "\r\n"
  start_msg = start_msg + "\r\n�������E�E�E \r\n"
  text = start_msg
  frame.label_message.SetLabel(text)
  frame.Refresh()

  # ���o�̓t�@�C���̃I�[�v��
  try:
    ifile = open(infile, 'r')
  except:
    text = text + "\r\n\r\n!���̓t�@�C�����J�����Ƃ��ł��܂���!\r\n"
    frame.label_message.SetLabel(text)
    execute_btn.Enable() # ���s�{�^�������ɖ߂�
    execute_btn.SetLabel("���s") 
    return
    
  try:
    ofile = open(otfile, 'w')
  except:
    text = text + "\r\n\r\n!�o�̓t�@�C�����J�����Ƃ��ł��܂���!\r\n"
    frame.label_message.SetLabel(text)
    ifile.close
    execute_btn.Enable() # ���s�{�^�������ɖ߂�
    execute_btn.SetLabel("���s") 
    return
       
  # 1�s�ǂݍ���
  buf_line = ifile.readline()
  icnt = 0
  Save_IPadd = ""
  Save_buf_out = ""

### --- Start of loop ---
  while buf_line:
    # ���s�R�[�h����
    buf_line = buf_line.replace('\r','')
    buf_line = buf_line.replace('\n','')

    # ���K�\����IP�A�h���X�𒊏o
    # V4
    Array_IPadd  = re.findall("((1[0-9]{2}|2[0-4][0-9]|25[0-5]|[1-9]?[0-9])\.(1[0-9]{2}|2[0-4][0-9]|25[0-5]|[1-9]?[0-9])\.(1[0-9]{2}|2[0-4][0-9]|25[0-5]|[1-9]?[0-9])\.(1[0-9]{2}|2[0-4][0-9]|25[0-5]|[1-9]?[0-9]))",buf_line)
    if not Array_IPadd:
      # V6
      Array_IPadd  = re.findall("(([0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|(([0-9a-fA-F]{1,4}:){1,6}:)[0-9a-fA-F]{1,4}(:[0-9a-fA-F]{1,4}){0,5}|([0-9a-fA-F]{1,4}:){1,7}:|([0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,5}(:[0-9a-fA-F]{1,4}){1,2}|([0-9a-fA-F]{1,4}:){1,4}(:[0-9a-fA-F]{1,4}){1,3}|([0-9a-fA-F]{1,4}:){1,3}(:[0-9a-fA-F]{1,4}){1,4}|([0-9a-fA-F]{1,4}:){1,2}(:[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:((:[0-9a-fA-F]{1,4}){1,6})|:((:[0-9a-fA-F]{1,4}){1,7}|:)|fe80:(:[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|::(ffff(:0{1,4}){0,1}:){0,1}((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])|([0-9a-fA-F]{1,4}:){1,4}:((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9]))",buf_line)

    if Array_IPadd:  # �ǂݍ��񂾍s��IP�A�h���X���܂܂��ꍇ
      buf_out = str(buf_line)
      
####### ��QLoop �i�P�s�Ɋ܂܂��IP�A�h���X��S��Whois�j
      for Ar2_IPadd in Array_IPadd:
      
        # �������ʂ͂Q�����z��ɂȂ��Ă���A�擪�Z����IP�A�h���X�̃t�������Z�b�g����Ă��邽�ߎ��o��
        IPadd = str(Ar2_IPadd[0])

        # i�I�v�V�����̏ꍇ��IP�A�h���X��Whois���̂ݏo��
        if flg_IPonly == 1:  
          buf_out = str(IPadd)
        else:
          buf_out = buf_out + op_delimiter + str(IPadd)
          #print("--debug-- IPonly buf_line : " + IPadd)
        
        # IP�A�h���X���O�̃f�[�^�Ɠ����Ȃ�A�擾�ς݂�Whois�����Z�b�g���āAWeb�A�N�Z�X�̓X�L�b�v
        if IPadd == Save_IPadd:
          buf_out = str(buf_out) + op_delimiter + whois_result
          Save_IPadd = IPadd  # IP�A�h���X�̃Z�[�u�i��r�p�j
          IPadd = ""
        else:
          Save_IPadd = IPadd  # IP�A�h���X�̃Z�[�u�i��r�p�j

        # Whois & nslookup ���s
        if (IPadd != ""):

          if state_stealth:  #�X�e���X�[���g�p���i�v���L�V�o�R�j
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
                # Whois���ʂ��擾
                w_html_data_b =response.read()
                w_html_data = w_html_data_b.decode('utf-8')
              except:
                whois_result = "!! Whois Access Error in open.read"
                buf_out = str(buf_out) + op_delimiter + whois_result
              else:  
                # whois��񂩂�l�b�g���[�N���E�����E�z�X�g����؂���
                whois_result = whois_edit(w_html_data,op_delimiter)
                # ���ʂ��o�̓o�b�t�@�[�ɃZ�b�g
                buf_out = str(buf_out) + op_delimiter + whois_result

          else:  #�C���^�[�l�b�g�ɒ��ڐڑ������[���g�p��
            # whois_url = "https://tools.wmflabs.org/whois/gateway.py"  2020/9/8 URL�ύX�Ή�
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
                # Whois���ʂ��擾
                res = urllib.request.urlopen(obj_url)
                w_html_data = res.read()
              except:
                whois_result = "!! Whois Access Error in open.read"
                buf_out = str(buf_out) + op_delimiter + whois_result
              else:  
                # whois��񂩂�l�b�g���[�N���E�����E�z�X�g����؂���
                whois_result = whois_edit(w_html_data,op_delimiter)
                # ���ʂ��o�̓o�b�t�@�[�ɃZ�b�g
                buf_out = str(buf_out) + op_delimiter + whois_result
                #print("--debug-- str(buf_line) : " + str(buf_line))
                #print("--debug-- buf_out : " + buf_out)
                res.close
        # �I�v�V����"i"�̂Ƃ���IP�A�h���X���ɏo��
        if flg_IPonly == 1:
          if buf_out != Save_buf_out:
            ofile.write(str(buf_out) + "\n")

          Save_buf_out = buf_out

####### ------��QLoop�����܂�

      # �P�s���̌��ʏo�́i�I�v�V����"i"�ȊO�j
      if flg_IPonly == 0:
        ofile.write(str(buf_out) + "\n")
     
    # IP�A�h���X���܂܂�Ȃ��s�͂��̂܂܏o��(�I�v�V�������̏ꍇ������)
    else:
      buf_out = str(buf_line)
      if flg_IPonly == 0:
        ofile.write(str(buf_out) + "\n")

    # ���������J�E���g�����b�Z�[�W�\��
    icnt = icnt + 1
    if ((icnt % 50) == 0):
      text = text + "\r\n--- processed " + str(icnt) + " lines "
      frame.label_message.SetLabel(text)
      frame.Refresh()

    # 1�s�ǂݍ���
    buf_out = ""
    buf_line = ""
    buf_line = ifile.readline()
### --- End of loop ---

  # ���o�̓t�@�C���̃N���[�Y
  ifile.close
  ofile.close

  # �I�����b�Z�[�W
  text = start_msg + "\r\n\r\nDone!!   " + datetime.datetime.today().strftime("%Y/%m/%d %H:%M:%S") + "\r\n"
  frame.label_message.SetLabel(text)

  execute_btn.Enable() # ���s�{�^�������ɖ߂�
  execute_btn.SetLabel("���s") 

  return

#### Whois���擾 ##### �����܂�

# ���s�{�^�����������i�}���`�X���b�h�j
def Clicked(self):  # ���s�{�^���N���b�N���̃C�x���g

  th1 = threading.Thread(name="a", target=whois_ip, args=())
  th1.start()
  

############################################

if __name__ == "__main__":# ���C��
   
  # ���C���E�B���h�E�ݒ�
  #app = wx.PySimpleApp()
  app = wx.App()
  frame = wx.Frame(None, -1, "WhoisTool" , size=(550,600))
  frame.SetTitle('Whois��񎩓��擾�c�[�� V2  by ooshima')
  panel_ui = wx.Panel(frame, -1, pos=(50, 50), size=(300, 300))
   
  # ���̓t�@�C���w��e�L�X�g�{�b�N�X
  desktop_folder = os.path.expanduser('~') + "\\Desktop\\"
  frame.label_infile = wx.StaticText(panel_ui, -1, '���̓t�@�C���i���O���Ɋ܂܂��IP�A�h���X���������o����Whois�����o�͂��܂��j', pos=(10, 10))
  frame.box_infile = wx.TextCtrl(panel_ui, -1, pos=(10, 30), size=(450,40), style=wx.TE_MULTILINE)
  frame.box_infile.SetValue(desktop_folder)
  choose_btn_infile = wx.Button(panel_ui, -1, '�Q��', pos=(470, 30), size=(40,20))
  choose_btn_infile.Bind(wx.EVT_BUTTON, choose_file_in)  # �Q�ƃ{�^���ƃN���b�N���̃C�x���g���o�C���h

  # �o�̓t�@�C���w��e�L�X�g�{�b�N�X
  frame.label_otfile = wx.StaticText(panel_ui, -1, '�o�̓t�@�C��', pos=(10, 80))
  frame.box_otfile = wx.TextCtrl(panel_ui, -1, pos=(10, 100), size=(450,40), style=wx.TE_MULTILINE)
  frame.box_otfile.SetValue(desktop_folder)
  choose_btn_otfile = wx.Button(panel_ui, -1, '�Q��', pos=(470, 100), size=(40,20))
  choose_btn_otfile.Bind(wx.EVT_BUTTON, choose_file_ot)  # �Q�ƃ{�^���ƃN���b�N���̃C�x���g���o�C���h
   
  # �o�̓I�v�V�����I���R���{�{�b�N�X
  frame.label_option = wx.StaticText(panel_ui, -1, '�o�̓I�v�V����', pos=(10, 180))
  element_array = ('i', 't', 's','c')
  combobox_option = wx.ComboBox(panel_ui, wx.ID_ANY, '' , choices=element_array, style=wx.CB_DROPDOWN, pos=(10, 200))
  help_text = "i ��� IP��Whois���̂ݏo��"
  help_text = help_text + "\nt ��� �^�u��؂�Ō��f�[�^��Whois����ǉ�"
  help_text = help_text + "\ns ��� �X�y�[�X��؂�Ō��f�[�^��Whois����ǉ�"
  help_text = help_text + "\nc ��� �J���}��؂�Ō��f�[�^��Whois����ǉ��i�f�t�H���g�j"
  frame.label_help = wx.StaticText(panel_ui, -1, help_text, pos=(70, 200))
   
  # �X�e���X�[���̃v���L�V�ݒ�i�`�F�b�N�{�b�N�X�AID�p�X���[�h���̓{�b�N�X�j ���X�e���X�̃v���L�V�o�R��SSL���ʐM�s�̂��߁AV2�ł͎g�p�ł��Ȃ�
  frame.check_stealth = wx.CheckBox(panel_ui, -1, '�X�e���X�[�����g�p', pos=(380, 200))
  frame.check_stealth.SetValue(False)
  frame.check_stealth.Bind(wx.EVT_CHECKBOX, state_change_stealth)
  frame.label_code = wx.StaticText(panel_ui, -1, 'k�E��+M', pos=(400, 220))
  frame.code_stealth = wx.TextCtrl(panel_ui, -1, pos=(450, 220), size=(70,20))
  frame.label_pass = wx.StaticText(panel_ui, -1, '�p�X���[�h', pos=(400, 240))
  frame.pass_stealth = wx.TextCtrl(panel_ui, -1, pos=(450, 240), size=(70,20), style=wx.TE_PASSWORD)
  frame.label_code.SetForegroundColour('#808080') # �E�Ԃ̃��x�����O���[�A�E�g
  frame.label_pass.SetForegroundColour('#808080') # �p�X�̃��x�����O���[�A�E�g
  ### frame.check_stealth.Disable()
  frame.code_stealth.Disable()
  frame.pass_stealth.Disable()
  
  # ���s�{�^��
  execute_btn = wx.Button(panel_ui, -1, '���s', pos=(220, 270))
  execute_btn.Bind(wx.EVT_BUTTON, Clicked)  # ���s�{�^���ƃN���b�N���̃C�x���g���o�C���h�iWhois���擾�����j
   
  # ���b�Z�[�W�\�����x��
  #frame.label_message = wx.StaticText(panel_ui, -1, '', pos=(10, 310), size=(480,240), style=wx.TE_MULTILINE|wx.SUNKEN_BORDER
  frame.label_message = wx.TextCtrl(panel_ui, -1, '', pos=(10, 300), size=(480,250), style=wx.TE_READONLY|wx.TE_MULTILINE|wx.SUNKEN_BORDER)
  frame.label_message.SetForegroundColour('#FF0000')
   
  # ���C���E�B���h�E�\��
  frame.Show(True)
  app.SetTopWindow(frame)
  app.MainLoop()
