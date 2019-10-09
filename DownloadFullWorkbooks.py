import requests
import xmltodict
import json
import cgi
import os.path
import zipfile
import ConfigParser

# Globals
parser = ConfigParser.ConfigParser()
parser.read(u'config.ini')
tableauurl = parser.get('Tableau', 'URL')
login = parser.get('Tableau', 'login')
password = parser.get('Tableau', 'password')
sitename = parser.get('Tableau', 'sitename')
signinurl = tableauurl + '/api/2.4/auth/signin'
workbooksurl = tableauurl + '/api/2.4/sites/@siteid/workbooks?pageSize=500'
contenturlbase = tableauurl + '/api/2.4/sites/@siteid/workbooks/@workbookid/content'
downloadfolder = parser.get('Tableau', 'downloadfolderfull')

payload = "{\"credentials\": {\"name\": \"@login\" ,\"password\": \"@password\",\"site\": {\"contentUrl\": \"@sitename\"}}}"
payload = payload.replace("@login", login)
payload = payload.replace("@password", password)
payload = payload.replace("@sitename", sitename)

headers = {
    'Content-Type': "application/json",
    'cache-control': "no-cache",
    'Postman-Token': "2adb04e6-6a7a-42c6-befc-bfae21934550"
    }

response = requests.request("POST", signinurl, data=payload, headers=headers)

if response.status_code == 200:
    d = xmltodict.parse(response.text)
    result = json.dumps(d, indent=4)

    token = d["tsResponse"]["credentials"]["@token"]
    site = d["tsResponse"]["credentials"]["site"]["@id"]
    user = d["tsResponse"]["credentials"]["user"]["@id"]


headers = {
    'X-Tableau-Auth': token,
    'cache-control': 'no-cache'
}

workbooksurl = workbooksurl.replace('@siteid', site)
response = requests.request("GET", workbooksurl, headers=headers)
done = False
total = 0
pagenumber = 1

if response.status_code == 200:
    d = xmltodict.parse(response.text)

    pagesize = d["tsResponse"]["pagination"]["@pageSize"]
    totalavailable = d["tsResponse"]["pagination"]["@totalAvailable"]

    #Iterate through all the workbooks
    for k in d["tsResponse"]["workbooks"]["workbook"]:
        projectname = k['project']['@name'].replace(":", "").replace(" ", "")
        foldername = os.path.join(downloadfolder, projectname)

        # check if the project folder exists in download location
        if not os.path.exists(foldername):
            os.mkdir(foldername)
            print ""
            print "Creating folder " + projectname

        workbookid = k["@id"]
        workbookname = k["@name"]
        urlsite = contenturlbase.replace("@siteid", site)
        url = urlsite.replace("@workbookid", workbookid)
        response = requests.get(url, headers=headers, stream=True)

        if response.status_code == 200:
            cd = response.headers.get("Content-Disposition")
            value, params = cgi.parse_header(cd)
            filename = params["filename"].replace('/', '').replace(":", "")
            workbook = os.path.join(foldername, filename)

            ct = response.headers.get("Content-Type")

            if os.path.exists(workbook):
                print "Deleting workbook " + workbook
                os.remove(workbook)

            # if the file is twbx
            if ct == "application/octet-stream":
                print ""
                print "Downloading twbx " + workbook
                with open(workbook, "wb") as file:
                    for chunk in response.iter_content(chunk_size=1024):
                        if chunk:
                            file.write(chunk)
                    file.close()

            # else file is twb
            elif ct == "application/xml":
                with open(workbook, 'w') as file:
                    print ""
                    print "Downloading twb " + workbook
                    file.write(response.content)
                    file.close()            