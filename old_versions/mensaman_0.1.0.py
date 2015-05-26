import urllib2
import shutil
import urlparse
import os
import time
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
menus = ['Menue','Vegetarisch','Eintopf/Stammessen']
download("http://www.studentenwerk.uni-siegen.de/index.php?uid=650&uid2=&cat_show=2&user=www006&mensa_week_value=0",targetfile)
today = date.today()

file = open(targetfile,'r')
content = file.read().replace('<br>',' ').replace('&nbsp;',' ').replace('<STRONG>','').replace(r'</STRONG>','')

match = content.find('tabDay')+8
print 'Willkommen\nSchauen wir mal, was es heute in der Mensa gibt'
for i in range(1,11):
  DayOfWeek = content[match:match+2]
  Date = content[content.find('tabDate',match)+9:content.find('tabDate',match)+16]
  
  if int(Date[0:2]) == today.day and int(Date[4:6]) == today.month:
    
    print today
    for j in range(0,3):
      print ''
      print menus[j],':'
      match = content.find('>',content.find('tablebmenu',match))
      print content[match+1: content.find('td>',match)-2]
    
  match = content.find('tabDay',match)+8
  
os.remove(targetfile)