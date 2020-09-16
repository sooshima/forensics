'''
 Parsing JpnIHDS.dat
 （IME 予測変換DB）
     Users\（ユーザーアカウント）\AppData\Roaming\Microsoft\InputMethod\Shared\JpnIHDS.dat
        文字コード：UNICODE   タイムスタンプ：Windows Epoch
'''

if __name__ == '__main__':

 import sys,io,struct
 from datetime import datetime

 param = sys.argv
 if (len(param) == 3):
  pass
 else:
  print("\n")
  print("(Usage) : IME_jp_parse.py c:\\Users\\...\\AppData\\Microsoft\\InputMethod\\Shared\\JpnIHDS.dat  OutputTextFile")
  print("\n")
  sys.exit()

 # Initialize
 pos = 32   # to skip File Header
 kana_buf = ""
 kanji_buf = ""

 # IN/OUT File Open
 ifile = param[1]
 ofile = param[2]
 dat = open(ifile, 'rb').read()
 txt = open(ofile, 'w')
 txt.write(" 日時（日本時間）,かな,漢字\n")

 ### Loop Start
 dat_len = len(dat)
 while pos < dat_len:
   #print("** debug ** pos : " + str(pos))
   # record header 16byte
   timest_st = struct.unpack_from("Q",dat,pos)  # timestamp 8byte
   timest = int(timest_st[0])   # convert to integer
   #print("** debug ** timest pos : " + str(pos))
   #print("** debug ** timest : " + str(timest))
   pos += 8
   rec_len_st = struct.unpack_from("H",dat,pos)  # record length 2byte
   pos += 2
   hd_len_st = struct.unpack_from("H",dat,pos)   # header length 2byte
   pos += 3
   rec_cnt_st = struct.unpack_from("B",dat,pos)  # record count 1byte
   pos += (int(hd_len_st[0]) - 13)   # first data position
   #print("** debug ** rec_cnt_st : " + str(rec_cnt_st))
   rec_cnt = int(rec_cnt_st[0])
   i_rec = 0
   kana_buf = ""
   kana_kanji = ""
   
   while i_rec < rec_cnt:
     # loop   record data x rec_cnt
     rdata_len_st = struct.unpack_from("H",dat,pos)  # data length 2byte
     pos += 2
     kana_len_st = struct.unpack_from("B",dat,pos)   # kana length 1byte
     pos += 1
     kanji_len_st = struct.unpack_from("B",dat,pos)  # kanji length 1byte
     kana_len = int(kana_len_st[0])
     if (kana_len < 0):
       print("** debug ** kana_len error  pos : " + str(pos))
       quit()
     kanji_len = int(kanji_len_st[0])
     if (kanji_len < 0):
       print("** debug ** kanji_len error  pos : " + str(pos))
       quit()
     #print("** debug ** kana_len : " + str(kana_len))
     #print("** debug ** kanji_len : " + str(kanji_len))
     pos += 5
     # Japanese kana kanji 
     kana_end = pos + (kana_len * 2 )    # kana end offset
     kana = bytes(dat[pos:kana_end])     # unicode 
     if (len(kana_buf) == 0):
       kana_buf = kana
     else:
       kana_buf = kana_buf + kana
     pos = kana_end

     kanji_end = pos + (kanji_len * 2)   # kanji end offset
     kanji = bytes(dat[pos:kanji_end])   # unicode
     if (len(kanji_buf) == 0):
       kanji_buf = kanji
     else:
       kanji_buf = kanji_buf + kanji
     pos = kanji_end
     i_rec += 1
     
   #txt.write(str(timest)) 		  					# timestamp write (win epoch)
   #txt.write(",")
   u_timest = (timest - 116444736000000000) / 10000000 # win epoch --> unix epoch
   dt = datetime.fromtimestamp(int(u_timest)) 		  	# timestamp to date
   date = str(dt.year) + "/" + str(dt.month).zfill(2) + "/" + str(dt.day).zfill(2) + " "
   date = date + str(dt.hour).zfill(2) + ":" + str(dt.minute).zfill(2) + ":" + str(dt.second).zfill(2)
   txt.write(str(date)) 							# date write
   txt.write(",") 
   try:
     txt.write(kana_buf.decode('utf-16')) 		   	# kana write (SJIS converted)
   except:
     txt.write(str(kana_buf))
   txt.write(",")
   try:
     txt.write(kanji_buf.decode('utf-16')) 	  	 	# kanji write (SJIS converted)
   except:
     txt.write(str(kanji_buf))
   txt.write("\n")                					# CRLF  write
   kana_buf = ""
   kanji_buf = ""

 txt.close()
