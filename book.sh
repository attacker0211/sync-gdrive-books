#!/bin/bash
if [ "$1" = "u" ] || [ "$1" = "-u" ] || [ "$1" = "upload" ]; then python3 ~/drive/upload.py books /books/ ".pdf"
else
  python3 ~/drive/download.py books /books/ pdf
fi

