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


# ==============================================
# HELPER FUNCTIONS
# ==============================================

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

def linecount(text):
  return sum(1 for line in text)

# ==============================================
# NETWORK FUNCTIONS
# ==============================================


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
  
# ==============================================
# TEXT FUNCTIONS
# ==============================================

def GetBraketLimits(description, lbrace='(',rbrace=')', nmax=-1):
  # remove kontent in brakets
  level = 0
  start = -1
  end   = -1
  limits = [0]
  
  ncount = 0

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
      
      ncount+=1
      
    if ncount >= nmax and nmax != -1:
      break

  # append full length of string otherwise last element will be missing
  limits.append(len(description))
  
  return limits
  
def GetBraketContent(description, lbrace='(', rbrace=')'):
  # extract limits from description
  limits = GetBraketLimits(description, lbrace, rbrace)
  
  info = ""
  # remove first and last element
  if len(limits) >= 4:
    limits = limits[1:-1]
  else:
    return info
    
  
  # cut out everything out of specified brakets
  for element in range(0, len(limits),2):
    info += description[limits[element]:limits[element+1]]
    
  return info
  
def RemoveBraketedContent(description, lbrace='(', rbrace=')'):
  # extract limits from description
  limits = GetBraketLimits(description, lbrace, rbrace)
  
  # cut out everything in specified brakets
  info = ""
  for element in range(0, len(limits),2):
    info += description[limits[element]:limits[element+1]]

  return info
  
# ==============================================
# FORMATING AND DISPLAYING FUNCTIONS
# ==============================================
  
def PrintDateMenu(content, today, options):
    # options - numeric value
    # binary component --- meaning
    # 001 --- enable graphics
    # 002 --- enable extra information
    # 004 --- unused
    # 008 --- unused
    # 016 --- unused
    # 032 --- unused
    # 064 --- unused
    # 128 --- unused
    
    menus = ['Fleisch/Fisch','Vegetarisch/Vegan','Aktion','Eintopf']

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

          # get content in brakets
          addinfo = GetBraketContent(description)  # extract braket content
          addinfo = RemoveBraketedContent(addinfo,'<','>')   # remove HTML tags
          addinfo = addinfo.replace(')(',',').replace(') ',',').replace('(','').replace(')','').replace(' ','') # format string
          addinfo = addinfo.decode("ISO-8859-1") # decode
          addinfo = list(set(addinfo.split(','))) # create list, remove double entries, recreate list
          #print "braketed: ", addinfo
          
          # remove braketed content from description
          if options & 2 == 0: description = RemoveBraketedContent(description)
          description = RemoveBraketedContent(description,'<','>')
          
          description = re.sub('  ',' ',description,0)
          description = re.sub(' , ',', ', description,0)

          # remove - endings on the end of line
          description = re.sub('(- und)','ABCD',description,0)
          description = re.sub('(- )','',description,0)
          description = re.sub('ABCD','- und', description,0)

          description = description.strip()
          if (description != "- * - * - *"  and description != "Heute nicht im Angebot!"):
            print ''
            print menus[j],':'
            print description.decode("ISO-8859-1")
            
            if options & 1 != 0:
             ascii_art = ''
             tmp = ''
             
             for einfo in addinfo:
               if not isnumeric(einfo) and not einfo.startswith('A'):
                 tmp = GetAciiArt(einfo)
                 
                 if not ascii_art == '':
                   ascii_art = JoinAsciiArt(ascii_art, tmp)
                 else:
                   ascii_art = tmp
             print '\n',ascii_art
        
      match = content.find('tabDay',match)+8
      
def JoinAsciiArt(aAll, aNew):
  if aAll.count('\n') !=  aNew.count('\n'):
    return aAll + '\n' + aNew
  
  
  new = ''
  cLines = aAll.count('\n')
  l1 = aAll.split('\r\n')
  l2 = aNew.split('\r\n')
  for k in range(0, len(l1)):
    new += l1[k] + l2[k] + '\n'
    
  return new
      
def GetAciiArt(val):
  sourcepath = '/nfs/munch_3/home/dehn/public/forAll/Mensaman/ascii_art/' + val + '.txt'
  
  if not os.path.exists(sourcepath):
    print 'Warning: Ascii Art',val,'ist nicht unterstützt.'
    return 0
    
  f = open(sourcepath,'r')
  lines = f.read()
  
  return lines
      
    
# ==============================================
# COMMAND LINE ARGUMENT PROCESSING ROUTINES
# ==============================================

def AliasReplace(arg):
  AliasOrig = ['week', 'woche']
  AliasReplace = [['monday','tuesday','wendsday','thursday','friday'],['montag','dienstag','mittwoch','donnerstag','freitag']]

  try:
    arr_index = AliasOrig.index(arg)
  except ValueError:
    result = False
  else:
    result = AliasReplace[arr_index]
    result = map(ExtractDateOffset, result)

  return result

# extract date offset from command line argument
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
    offset = 0
  else:
    offset = next_index - curr_index

  return offset
  

# separate settings from other arguemtns
def GetSetting(value):
  if isnumeric(value): return 0

  if value.startswith('--') and value in allowed_settings:
    return value

  return 0

# display the help text information on screen
def DisplayHelp(value):
  
  print "\n\nHelp manual for mensaman\n------------\n"
  print "Mensaman displays the menue of the EN campus in Siegen Germany."
  print "It will display the menue of the day in your shell. If no other date is specified"
  print "the menue of the current day will be displayed."
  
  print "\n------------\ntime arguments\n------------\n"
  print "specify a day by adding a numerical expression [+-n] or by naming the day"
  print "example:"
  print " mensaman.py +1"
  print " mensaman.py -2"
  print " mensaman.py monday"
  print " mensaman.py Freitag"
  print " mensaman.py GeSTern"
  print "\nwhere"
  print "  mensaman.py +1"
  print "  mensaman.py morgen"
  print "  mensaman.py tomorrow"
  print "produce the same result"
  print "\n it is also possible to combine dates"
  print " mensaman.py montag wendsday +3"
  
  print "\n------------\noptions\n------------"
  print " --help      print this help information page"
  print " --extra     includes extra information on every menue"
  print " --graphics  display ascii art of the animals used for cooking"
  
  print "\n written by Christian Dehn 2014\n\n"
  
  return value

# support the formated text with visual content
def AddGraphics(value):
  return value | 1

# display additional information for each item
def AddExtra(value):
  return value | 2

  
# ==============================================
# MAIN PROGRAM PART
# ==============================================


# ==============================================
# command line argument processing
#

# analyse arguments
offsets = []
settings = []
allowed_settings = ['--help','--graphics','--extra']
for arg in sys.argv[1:]:
  arg = arg.strip().lower()

  tmp = AliasReplace(arg)
  if tmp != False:
  
    # try if the return value is a list
    try:
      offsets.extend(tmp)
    # if not add the returned element
    except:
      offsets.append(tmp)

  else:
    offsets.append(ExtractDateOffset(arg))

  settings.append(GetSetting(arg))

  
# reduce the list to unique entries, sort them and reconvert it into a list
offsets = list(set(offsets))
if len(offsets) == 0: offsets.append(0)
offsets.sort()


# dictionary of functions
optionsvar = 0
options = {'--help': DisplayHelp,
           '--graphics': AddGraphics,
           '--extra': AddExtra}

# analyse program settings
for setting in settings:
  if setting != 0:
    optionsvar = options[setting](optionsvar)
    #print setting

#print optionsvar

# ==============================================
# working with input file
#

# prepare variables
content = ""
sourcelink = "http://www.studentenwerk.uni-siegen.de/index.php?uid=650&uid2=&cat_show=2&user=www006&mensa_week_value=0"
targetfile = "/tmp/futter.htm"

# check if file already exists and is up to date
bReload = False
if not os.path.exists(targetfile):
  bReload = True
else:
  filedate = datetime.datetime.fromtimestamp(os.path.getmtime(targetfile)).date()
  currdate = datetime.datetime.today().date()
  
  if filedate != currdate:
    os.remove(targetfile)
    bReload = True
    
# download file
if bReload:
  if not download(sourcelink, targetfile):
    print "Fehler beim Abrufen der Webseite. Programm wird beendet."
    exit()
    
# read file content
file = open(targetfile,'r')
content = file.read().replace('<br>',' ').replace('&nbsp;',' ').replace('<STRONG>','').replace(r'</STRONG>','').replace('&euro;','Euro')


# ==============================================
# display formated content
#

# print formated content
print '\nWillkommen\nSchauen wir mal, was es in der Mensa gibt'

for offset in offsets:
  
  day = date.today() + datetime.timedelta(days=offset)
  
  if day.weekday() > 4:
      print "Am", day
      print "WOCHENENDE - Mach dir selbst etwas Leckeres!"
  PrintDateMenu(content, day, optionsvar)
  print "\n\n"
      
