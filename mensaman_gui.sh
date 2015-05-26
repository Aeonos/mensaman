#!/bin/bash

MENSA="mensaman.py"
ZENITY=`which zenity`
HAS_ZENITY=1
KDIALOG=`which kdialog`
HAS_KDIALOG=1
REQUEST=""

function setup_environment {
  if [[ "$ZENITY" == "" ]]; then
    HAS_ZENITY=0
  else
    if [[ "$KDIALOG" == "" ]]; then
      HAS_KDIALOG=0
    fi
  fi

  if [[ "$HAS_ZANITY" == 0 && "$HAS_KDIALOG" == 0 ]]; then
    echo "warning - none of the required dialog resources where found on your system"
    echo "to use this script, you need to install zentiy or kdialog"
    echo "exiting program"
    exit
  fi
}

function get_week_dates_arguments {
  CURR_DAY=`date +%u`
  CURR_DATE=`date '+%d.%m.%Y'`

  if [[ "$HAS_ZENITY" -eq 1 ]]; then
    OPT_TRUE="TRUE"
    OPT_FALSE="FALSE"
  else
    OPT_TRUE="on"
    OPT_FALSE="off"
  fi

  for ((c=1-$CURR_DAY; c<=5-$CURR_DAY; c++))
  do
    if [ "$c" -ge 0 ]
      then
        c="+$c"
    fi

    CHANGE=`date '+%Y%m%d'`"$c days"
    DATE=`date '+%d.%m.%Y' -d "$CHANGE"`
    OPTION="$OPT_FALSE"

    if [[ "$DATE" == "$CURR_DATE" ]]; then
        OPTION="$OPT_TRUE"
    fi

    DAY=`date '+%A' -d "$CHANGE"`
    if [[ "$HAS_ZENITY" -eq 1 ]]; then
      REQUEST="$REQUEST $OPTION $DATE $DAY"
    else
      if [[ "$HAS_KDIALOG" -eq 1 ]]; then
        REQUEST="$REQUEST $DAY $DATE-$DAY $OPTION"
      fi
    fi
  done
}

setup_environment
get_week_dates_arguments


# ask user for days to be presented
if [[ "$HAS_ZENITY" -eq 1 ]]; then
  DAYS=`$ZENITY --list --separator=" "  --title="Choose one or more dates"  --text="Select one or more dates to display their menus."  --checklist  --width 530  --height 400  --print-column=3   --column="" --column="Datum" --column="Wochentag"  $REQUEST 2>/dev/null`
else
  if [[ "$HAS_KDIALOG" -eq 1 ]]; then
    DAYS=`$KDIALOG --checklist "Choose one or more days" $REQUEST --title "Mensaman Tageswahl" 2>/dev/null`
    DAYS=$(echo "$DAYS"|tr -d "\"")	# remove double quotes from output
  fi
fi

# fetch information from website
TEXTOUT=`python $MENSA $DAYS`

# display results
if [[ "$HAS_ZENITY" -eq 1 ]]; then
  echo "$TEXTOUT" | $ZENITY --text-info --width 580 --height 500 2>/dev/null
else
  if [[ "$HAS_KDIALOG" -eq 1 ]]; then
    echo "$TEXTOUT" > tmp.txt | $KDIALOG --textbox tmp.txt 580 500 --title "Universität Siegen ENC Mensa Menü" 2>/dev/null; rm tmp.txt
  fi
fi
