#!/bin/bash
if [ "$1" = "u" ] || [ "$1" = "-u" ] || [ "$1" = "upload" ]; then python3 ~/python/drive/upload.py books /books/
else
  python3 ~/python/drive/download.py books /books/
fi

