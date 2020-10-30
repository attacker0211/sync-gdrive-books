# sync-gdrive-books

I'm tired of clicking buttons to download and extract and upload to sync books accross my devices. 

And PEOPLE ON THE INTERNET CAN'T WRITE A SIMPLE ENOUGH SCRIPTS FOR ME TO USE. 

Like, I only want to upload/download pdf files and I also want to automate "python3 abcd.py arg1 arg2" CAUSE I'M LAZY. 

This script is flexible, can be changed for other file types.

### Generating Oauth Credentials
- Log into google developer console at [google console](https://console.developers.google.com/).
- Create new Project or use existing project.
- If the APIs & services page isn't already open, open the console left side menu and select APIs & services.
- On the left, click Credentials.
- Click New Credentials, then select OAuth client ID.
- Creating new OAuth 2.0 Credentials:
  - Select Application type "other".
  - Provide name for the new credentials. ( anything )
  - This would provide a new Client ID and Client Secret.
  - Download your credentials.json by clicking on the download button.
- Enable Google Drive API for the project under "Library".

### Usage
```
git clone https://github.com/attacker0211/sync-gdrive-books.git ~/drive
cd drive
# name your file "credentials.json" and move it to this folder.
# download
./book 
# upload
./book -u
```

The default folder on drive is `books` and the default local folder is `~/books`, can be changed in `book.sh`.
