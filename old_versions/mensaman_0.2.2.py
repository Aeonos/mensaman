#!/usr/bin/python
# -*- coding: utf-8 -*-

import urllib2
import shutil
import urlparse
import os
import time
import re

from string import maketrans
from datetime import date

def download(url, fileName=None):
    def getFileName(url,openUrl):
        if 'Content-Disposition' in openUrl.info():
            # If the response has Content-Disposition, try to get filename from it
            cd = dict(map(
                lambda x: x.strip().split('=') if '=' in x else (x.strip(),''),
                openUrl.info().split(';')))
            if 'filename' in cd:
                filename = cd['filename'].strip("\"'")
                if filename: return filename
        # if no filename was found above, parse it out of the final URL.
        return os.path.basename(urlparse.urlsplit(openUrl.url)[2])

    r = urllib2.urlopen(urllib2.Request(url))
    try:
        fileName = fileName or getFileName(url,r)
        with open(fileName, 'wb') as f:
            shutil.copyfileobj(r,f)
    finally:
        r.close()
        
        
targetfile = "futter.htm"
#menus = ['Menue','Vegetarisch','Eintopf/Stammessen']
menus = ['Menue','Vegetarisch','Stammessen','Eintopf']
download("http://www.studentenwerk.uni-siegen.de/index.php?uid=650&uid2=&cat_show=2&user=www006&mensa_week_value=0",targetfile)
today = date.today()

file = open(targetfile,'r')
content = file.read().replace('<br>',' ').replace('&nbsp;',' ').replace('<STRONG>','').replace(r'</STRONG>','')

match = content.find('tabDay')+8
print 'Willkommen\nSchauen wir mal, was es heute in der Mensa gibt'
for i in range(1,6):
  DayOfWeek = content[match:match+2]

  Date = content[content.find('tabDate',match)+9:content.find('tabDate',match)+16]
  Date = ''.join(Date.split())  # remove white space

  if int(Date[0:2]) == today.day and int(Date[3:5]) == today.month:

    print today
    for j in range(0,4):
      match = content.find('>',content.find('tablebmenu',match))
      description = content[match+1: content.find('td>',match)-2]
#      doesnt work
#      description = description.replace('ä','ae').replace('ö','oe').replace('ü','ue').replace('ß','ss').replace('Ä','Ae').replace('Ö','Oe').replace('Ü','Ue')

#      print description

      # remove kontent in brakets
      level = 0
      start = -1
      end   = -1
      limits = [0]

      for k in range(0,len(description)):
        char = description[k]
        if char == '(':
          if start == -1:
            start = k
          level +=1
        if char == ')':
          end = k
          level -= 1

        if start != -1 and end != -1 and level == 0:
          limits.append(start)
          limits.append(end+1)
          start = -1
          end = -1

      # append full length of string otherwise last element will be missing
      limits.append(len(description))

      info = ""
      for element in range(0, len(limits),2):
        info += description[limits[element]:limits[element+1]]

      description = info
      description = re.sub('  ',' ',description,0)
      description = re.sub(' , ',', ', description,0)

#      for k in description:
#        print ord(k)

      # remove - endings on the end of line
      description = re.sub('(- und)','ABCD',description,0)
      description = re.sub('(- )','',description,0)
      description = re.sub('ABCD','- und', description,0)

      description = description.strip()
      if (description != "- * - * - *"  and description != "Heute nicht im Angebot!"):
        print ''
        print menus[j],':'
        print description
    
  match = content.find('tabDay',match)+8
  
os.remove(targetfile)
