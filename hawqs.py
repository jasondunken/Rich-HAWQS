import http.client
import json
import os

from dotenv import load_dotenv

from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt
from rich.json import JSON

from utils.ui import alert, showResponse

import project

class HAWQSTests:
    def __init__(self, console):
        load_dotenv()
        self.DEFAULT_API_URL = os.getenv("DEFAULT_API_URL")
        self.hawqsAPIUrl = self.DEFAULT_API_URL
        self.DEFAULT_API_KEY = os.getenv("DEFAULT_API_KEY")
        self.hawqsAPIKey = self.DEFAULT_API_KEY
        
        self.dataDownloadPath = os.getenv("DATA_DOWNLOAD_PATH")
        self.historyFilePath = os.getenv('HISTORY_FILE_PATH')
        self.historyFileName = "data-file-history.hst"
        
        self.currentProject = None
        self.currentProjectCompleted = False
        self.currentJobID = None
        self.currentStatus = None
        
        self.console = console

    def showHAWQSMenu(self):
        if self.currentJobID:
            self.console.print(f"[green italic]Current HAWQS Job ID:[/] [red]{self.currentJobID}[/]", justify="center")

        table = Table(box=None)
        tableMetadata = {
            'columns': [
                { 'header': "", 'justify': "center", 'style': "yellow", 'width': 3 },
                { 'header': "HAWQS Tests", 'justify': None, 'style': "blue", 'width': None },
                { 'header': "", 'justify': None, 'style': "magenta", 'width': None },
                { 'header': "Endpoint", 'justify': None, 'style': "green", 'width': None },
            ],
            'rows': [
                { 'selector': "0", 'action': "Check HAWQS API Status", 'type': "GET", 'endpoint': "HAWQS/test/clientget" },
                { 'selector': "1", 'action': "Get Input Definitions", 'type': "GET", 'endpoint': "HAWQS/projects/input-definitions" },
                { 'selector': "2", 'action': "Submit a Test Project", 'type': "POST", 'endpoint': "HAWQS/projects/submit" },
                { 'selector': "3", 'action': "Check Project Execution Status", 'type': "GET", 'endpoint': "HAWQS/projects/:id" },
                { 'selector': "4", 'action': "Get Current Project Data", 'type': "GET", 'endpoint': "HAWQS/api-files/api-projects/epaDevAccess/" },
                { 'selector': "5", 'action': "Previous Project Data Files", 'type': "", 'endpoint': "" },
                { 'selector': "e", 'action': "[red]Back to Main Menu", 'type': None, 'endpoint': None },
            ]
        }
        menuChoices = [row['selector'] for row in tableMetadata['rows']]

        for column in tableMetadata['columns']:
            table.add_column(column['header'], justify=column['justify'], style=column['style'], width=column['width'])
        for row in tableMetadata['rows']:
            if row['type']:
                table.add_row(f"<{row['selector']}>", row['action'], f"[{row['type']}]", row['endpoint'])
            else:
                table.add_row(f"<{row['selector']}>", row['action'])
        
        self.console.print(table)
        self.executeChoice(Prompt.ask(" Make Selection >", choices=menuChoices, show_choices=False))
    
    def executeChoice(self, choice):
        self.console.print()
        if choice == "0":
            self.console.print("[green] Fetching API Status")
            self.getAPIStatus()
        if choice == "1":
            self.console.print("[green] Fetching Input Definitions")
            self.getInputDefinitions()
        if choice == "2":
            self.console.print("[green] Submitting Project")
            self.submitProject()
        if choice == "3":
            if self.isCurrentJob():
                self.console.print("[green] Fetching Project Status")
                self.getProjectStatus()
            else:
                alert(self.console, "[red] There must be a stored job ID. Submit the test project to create job ID")
                self.showHAWQSMenu()
        if choice == "4":
            if self.currentProjectCompleted:
                self.console.print("[green] Fetch Project Data")
                self.getProjectData()
            else:
                alert(self.console, "[red] Project progress must be 100% complete to get data. Check status again")
                self.showHAWQSMenu()
        if choice == "5":
            self.console.print("[green] Fetch Previous Project Data")
            self.showFileHistory()
        if choice == "e":
            return

        self.showHAWQSMenu()
    
    def getAPIStatus(self):
        connection = http.client.HTTPSConnection(self.hawqsAPIUrl)
        headers = { 'X-API-Key': self.hawqsAPIKey }
        with self.console.status("[bold green] Processing request...[/]") as _:
            connection.request('GET', '/test/clientget', None, headers)
            response = connection.getresponse()
            showResponse(self.console, response.read().decode(), response.status)

    def getInputDefinitions(self):
        connection = http.client.HTTPSConnection(self.hawqsAPIUrl)
        headers = { 'X-API-Key': self.hawqsAPIKey }
        with self.console.status("[bold green] Processing request...[/]") as _:
            connection.request('GET', '/projects/input-definitions', None, headers)
            response = connection.getresponse()
            showResponse(self.console, response.read().decode(), response.status)

    def submitProject(self):
        self.currentProject = None
        self.currentProjectCompleted = False
        self.currentJobID = None
        self.currentStatus = None

        connection = http.client.HTTPSConnection(self.hawqsAPIUrl)
        with self.console.status("[bold green] Processing request...[/]") as _:
            headers = { 'X-API-Key': self.hawqsAPIKey, 'Content-type': 'application/json' }
            connection.request('POST', '/projects/submit', json.dumps(project.inputData), headers)
            response = connection.getresponse()
            currentProject = response.read().decode()
            showResponse(self.console, currentProject, response.status)

            self.currentProject = json.loads(currentProject)
            if self.currentProject['id']:
                self.currentJobID = self.currentProject['id']

    def isCurrentJob(self):
        if self.currentJobID:
            return True

    def getProjectStatus(self):
        try:
            connection = http.client.HTTPSConnection(self.hawqsAPIUrl)
            headers = { 'X-API-Key': self.hawqsAPIKey }
            with self.console.status("[bold green] Processing request...[/]") as _:
                connection.request('GET', f'/projects/{self.currentJobID}', None, headers)
                response = connection.getresponse()
                currentStatus = response.read().decode()
                showResponse(self.console, currentStatus, response.status)

                self.currentStatus = json.loads(self.currentStatus)
                if self.currentStatus and not self.currentProjectCompleted:
                    if self.currentStatus['status']['progress'] >= 100:
                        self.currentProjectCompleted = True
                        self.updateHistory()

        except Exception as e:
            self.console.print(Panel("some kind of exception occurred", e))

    def updateHistory(self):
        with open(os.path.join(self.historyFilePath, self.historyFileName), 'a+') as historyFile:
            for file in self.currentStatus['output']:
                historyFile.write(f"{file['url']}\n")

    def clearHistory(self):
        try:
            with open(os.path.join(self.historyFilePath, self.historyFileName), "w") as historyFile:
                historyFile.write("")
        except Exception as ex:
            alert(self.console, "History already cleared")
            return

    def getProjectData(self):
        tableMetadata = {
            'columns': [
                { 'header': "", 'justify': "center", 'style': "yellow", 'width': 3 },
                { 'header': "Data", 'justify': None, 'style': "cyan", 'width': None },
                { 'header': "Format", 'justify': "center", 'style': "green", 'width': None },
            ],
            'rows': []
        }
        choices = []

        fileMetadata = []
        for x, file in enumerate(self.currentStatus['output']):
            project, name, url = self.parseUrl(file['url'])
            fileMetadata.append({
                'project': project,
                'name': name,
                'url': url
            })

            tableMetadata['rows'].append({
                'selector': x,
                'name': file['name'],
                'url': url,
                'format': file['format']
            })
            choices.append(str(x))
        tableMetadata['rows'].append({ 'selector': 'a', 'name': "Download all files", 'format': ""})
        choices.append("a")
        tableMetadata['rows'].append({ 'selector': 'e', 'name': "[red]Exit to Main Menu", 'format': ""})
        choices.append("e")

        table = Table(box=None)
        for column in tableMetadata['columns']:
            table.add_column(column['header'], justify=column['justify'], style=column['style'], width=column['width'])
        for row in tableMetadata['rows']:
            table.add_row(f"<{row['selector']}>", row['name'], f"{row['format']}")

        while True:
            self.console.print(table, justify="center")
            fileChoice = Prompt.ask(" Download file >", choices=choices, show_choices=False)

            if fileChoice == "e": break
            if fileChoice == "a": self.getAllDataFiles(fileMetadata)
            else :
                fileData = fileMetadata[int(fileChoice)]
                self.console.print(Panel(f"Fetching {fileData['name']}..."))
                self.getDataFile(fileData)

    def showFileHistory(self):
        urls = None
        try:
            with open(os.path.join(self.historyFilePath, self.historyFileName), "r") as file:
                urls = file.readlines()
        
        except Exception as ex:
            alert(self.console, "There is currently no project history")
            return

        tableMetadata = {
            'columns': [
                { 'header': "", 'justify': "right", 'style': "yellow", 'width': 7 },
                { 'header': "Project", 'justify': None, 'style': "green", 'width': None },
                { 'header': "File", 'justify': None, 'style': "cyan", 'width': None },
            ],
            'rows': []
        }
        choices = []
        for x, url in enumerate(urls):
            project, name, url = self.parseUrl(url)

            
            tableMetadata['rows'].append({ 
                "selector": x,
                "project": project,
                "name": name,
                "url": url })
            choices.append(str(x))
        tableMetadata['rows'].append({ 'selector': 'c', 'project': "[blue]Clear history", 'name': "" })
        choices.append("c")
        tableMetadata['rows'].append({ 'selector': 'e', 'project': "[red]Exit to Main Menu", 'name': "" })
        choices.append("e")

        table = Table(box=None)
        for column in tableMetadata['columns']:
            table.add_column(column['header'], justify=column['justify'], style=column['style'], width=column['width'])
        for row in tableMetadata['rows']:
            table.add_row(f"<{row['selector']}>", row['project'], row['name'])

        while True:
            self.console.print(table, justify="center")
            fileChoice = Prompt.ask(" Download file >", choices=choices, show_choices=False)

            if fileChoice == "e": break
            if fileChoice == "c": self.clearHistory()
            else :
                fileData = tableMetadata['rows'][int(fileChoice)]
                self.console.print(Panel(f"Fetching {fileData['name']}..."))
                self.getDataFile(fileData)

    def getAllDataFiles(self, fileData):
        for file in fileData:
            self.getDataFile(file)

    def getDataFile(self, fileData):
        try:
            content = None
            connection = http.client.HTTPSConnection(self.hawqsAPIUrl)
            headers = { 'X-API-Key': self.hawqsAPIKey }
            with self.console.status("[bold green] Processing request...") as _:
                connection.request('GET', fileData['url'], None, headers)
                response = connection.getresponse()
                self.console.print(Panel(f"{fileData['name']} received"))
                content = response.read()
                self.console.print(Panel(f"[green]Request Status:[/] {response.status}"))

            with self.console.status("[bold green] Saving file...") as _:
                if content:
                    projectName = fileData['project']
                    downloadFolderPath = os.path.join(self.dataDownloadPath, projectName)
                    if not os.path.exists(downloadFolderPath):
                        os.makedirs(downloadFolderPath)
                    fileName = fileData['name']
                    with open(os.path.join(downloadFolderPath, fileName), 'wb+') as f:
                        f.write(content)

                    self.console.print(Panel(f"{fileName} saved"))

        except Exception as e:
            self.console.print(Panel("some kind of exception occurred", e))

    def getUrl(self):
        return self.hawqsAPIUrl

    def setUrl(self, newUrl):
        self.hawqsAPIUrl = newUrl

    def restoreDefaultUrl(self):
        self.hawqsAPIUrl = self.DEFAULT_API_URL

    def getKey(self):
        return self.hawqsAPIKey
    
    def setKey(self, newKey):
        self.hawqsAPIKey = newKey

    def restoreDefaultKey(self):
        self.hawqsAPIKey = self.DEFAULT_API_KEY

    def parseUrl(url):
        url = url.rstrip()
        # gets from after second to last / to end => projectname/filename
        urlEnd = url[url.rfind("/", 0, url.rfind("/")):][1:]
        project = urlEnd[:urlEnd.find("/")]
        name = urlEnd[urlEnd.find("/"):][1:]

        return project, name, url
