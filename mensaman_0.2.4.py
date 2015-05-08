#!/usr/bin/python
# -*- coding: utf-8 -*-

import urllib2
import socket
import shutil
import urlparse
import os
import datetime
import time
import re
import sys

from string import maketrans
from datetime import date

def download(url, fileName=None, twait=5):
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

    # check if file is accessable
    try:
        urllib2.urlopen(urllib2.Request(url), timeout = twait )
    except urllib2.URLError, e:
        print "\nThere was an error downloading the requested information."
        print "Please check your network connection and/or the original website.\n"
        
        return False
        # for Python 2.6
#        if isinstance(e.reason, socket.timeout):
#            raise MyException("There was an error: %r" % e)
        #else:
            # reraise the original error
         #   raise
    '''   
    except socket.timeout, e:
        # for Python 2.7
        raise MyException("There was an error: %r" % e)
    '''
    r = urllib2.urlopen(urllib2.Request(url), timeout = twait )
    try:    
        fileName = fileName or getFileName(url,r)
        with open(fileName, 'wb') as f:
            shutil.copyfileobj(r,f)
    finally:
        r.close()
    
    return True

def isnumeric(value):
  if value.isdigit():
    return True
  else:
    if arg[0:1] == "+" or arg[0:1] == "-":
      if arg[1:].isdigit():
        return True
      else:
        return False
    else:
      return False

def ExtractDateOffset(arg):

  offset = 0

  # check for numerical expression
  if isnumeric(arg):
      try:
          offset = int(arg)
      except ValueError:
          offset = 0
  if offset != 0: return offset


  # check for relative string offset
  offset_tag_relative = ['übermorgen', 'morgen', 'heute', 'gestern', 'vorgestern', 'day after tomorrow', 'tomorrow', 'today', 'yesterday']
  offset_val_relative = [+2          , +1      , 0      , -1       , -2          , +2                 , +1        , 0      , -1         ]
  try:
    arr_index = offset_tag_relative.index(arg)
  except ValueError:
    offset = 0
  else:
    offset = offset_val_relative[arr_index]

  if offset != 0:
    return offset


  # check for absolute string offset
  curr_index = datetime.datetime.today().weekday()
  

  index_tag  = [ 'sunday', 'monday', 'tuesday', 'wendsday', 'thursday', 'friday', 'saturday', 'sonntag', 'montag', 'dienstag', 'mittwoch', 'donnerstag', 'freitag', 'samstag']
  index_val  = [ 6       , 0       , 1        , 2         , 3         , 4       , 5         , 6        , 0       , 1         , 2         , 3           , 4        , 5        ]


  try:
    arr_index = index_tag.index(arg)
  except ValueError:
    next_index = -1
  else:
    next_index = index_val[arr_index]


  if next_index < 0:
    offset = next_index
  else:
    offset = next_index - curr_index

  return offset
  
def RemoveBraketedContent(description, lbrace='(', rbrace=')'):
  # remove kontent in brakets
  level = 0
  start = -1
  end   = -1
  limits = [0]

  for k in range(0,len(description)):
    char = description[k]
    if char == lbrace:
      if start == -1:
        start = k
      level +=1
    if char == rbrace:
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

  return info
  
def PrintDateMenu(content, today):
    menus = ['Fleisch/Fisch','Vegetarisch/Vegan','Eintopf','Aktion']

    match = content.find('tabDay')+8
    for i in range(1,6):
      DayOfWeek = content[match:match+2]

      Date = content[content.find('tabDate',match)+9:content.find('tabDate',match)+16]
      Date = ''.join(Date.split())  # remove white space

      if int(Date[0:2]) == today.day and int(Date[3:5]) == today.month:

        print "Am", today
        for j in range(0,4):
          match = content.find('>',content.find('tablebmenu',match))
          description = content[match+1: content.find('td>',match)-2]
    #      doesnt work
    #      description = description.replace('ä','ae').replace('ö','oe').replace('ü','ue').replace('ß','ss').replace('Ä','Ae').replace('Ö','Oe').replace('Ü','Ue')

    #      print description

	  '''
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

          description = info'''
          description = RemoveBraketedContent(description)
          description = RemoveBraketedContent(description,'<','>')
          
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
            print description.decode("ISO-8859-1")
        
      match = content.find('tabDay',match)+8
    

# analyse arguments
offsets = []
for arg in sys.argv[1:]:
  arg = arg.strip().lower()
  offsets.append(ExtractDateOffset(arg))
  
# reduce the list to unique entries, sort them and reconvert it into a list
offsets = list(set(offsets))
if len(offsets) == 0: offsets.append(0)

sourcelink = "http://www.studentenwerk.uni-siegen.de/index.php?uid=650&uid2=&cat_show=2&user=www006&mensa_week_value=0"
targetfile = "futter.htm"

if download(sourcelink, targetfile):
  file = open(targetfile,'r')
  content = file.read().replace('<br>',' ').replace('&nbsp;',' ').replace('<STRONG>','').replace(r'</STRONG>','').replace('&euro;','Euro')

  print 'Willkommen\nSchauen wir mal, was es in der Mensa gibt'

  for offset in offsets:
      day = date.today() + datetime.timedelta(days=offset)
      
      if day.weekday() > 4:
          print "Am", day
          print "WOCHENENDE - Mach dir selbst etwas leckeres!"
      PrintDateMenu(content, day)
      print "\n\n"
    
  os.remove(targetfile)
