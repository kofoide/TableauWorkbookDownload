# Tableau Workbook Download

I want to be able to do a global find in all my Tableau Workbooks for specific database objects that are used. If I have them all downloaded from my Tableau server on my harddrive as .twb files, then I can do this fairly easily.

The DownloadWorkbooks code will download all the workbooks as .twb.
The DownloadFullWorkbooks will download all the workbooks as .twbx

You will need to create your own config.ini:

    [Tableau]
    URL = https://
    login = login
    password = password
    sitename = XXX
    downloadfolder = /Users/Shared/TableauWorkbooks/twb
    downloadfolderfull = /Users/Shared/TableauWorkbooks/twbx
