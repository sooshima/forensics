'''
 Create PathList from fte_result.txt (※Export data from 'fte'.  'fte' is $MFT Parsing tool.)
  fte_result.txt' is delimited by "|" and its code is UTF-8(JP).
  fte --> http:#www.kazamiya.net/fte
'''

if __name__ == '__main__':

 import sys,io

 param = sys.argv
 if (len(param) == 3):
  pass
 else:
  print("\n")
  print("(Usage) : MFT-PathListGenerator.py  fte_result.txt  OutputTextFile")
  print("\n")
  sys.exit()

 # Initialize DB array
 fteDB = []

 # IN/OUT File Open
 ifile = param[1]
 ofile = param[2]
 dat = open(ifile, 'r', encoding="UTF-8")
 txt = open(ofile, 'w', encoding="UTF-8")
 txt.write("File-ID" + "," + "Path\n")

 ### Temp DB Create loop
 in_line = dat.readline()  # Header skip
 in_array = in_line.split("|")
 for in_line in dat:
   in_array = in_line.split("|")
   fteDB.append([int(in_array[3]),int(in_array[2]),in_array[0]])  # appending [File-parent-id, File-id, File-name]
 fteDB.sort(key=lambda x:(x[0],x[1]))
 
 ### Root Directory Search
 for DB_row in fteDB:
    if DB_row[0] == DB_row[1]:  #Root Directory (parent-id = id)
        Root = DB_row[0]
        break
 
 ### PathList Create loop
 for DB_row in fteDB:
    Search_pid = DB_row[0]  # File-parent-id
    File_id = DB_row[1]     # File-id
    File_Path = DB_row[2]   # File-name
    
    ### Parents Search
    while not Search_pid == Root:
      for DB_row in fteDB:
        if DB_row[1] == Search_pid:  # File-d = Searching pid
           Search_pid = DB_row[0]
           File_Path = DB_row[2] + "\\" + File_Path
           break
    ### PathList write to output-file
    txt.write(str(File_id) + "," + File_Path + "\n")

 txt.close()
