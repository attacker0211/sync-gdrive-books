#!/bin/bash
if [ "$1" = "u" ] || [ "$1" = "-u" ] || [ "$1" = "upload" ]; then 
  python3 ~/drive/uploadRec.py pictures /pictures/ ".JPG"
  python3 ~/drive/uploadRec.py pictures /pictures/ ".CR3"  
else
  python3 ~/drive/downloadRec.py pictures /pictures/ JPG 
fi
