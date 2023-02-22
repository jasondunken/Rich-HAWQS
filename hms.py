import http.client
import json
import os

from dotenv import load_dotenv

from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt

from utils.ui import alert, showResponse

import project

class HMSTests:
    def __init__(self, console):
        load_dotenv()
        self.hmsBaseUrl = os.getenv("DEV_HMS_HAWQS_BASE_URL")
        self.hawqsAPIKey = os.getenv("DEFAULT_API_KEY")
        
        self.dataDownloadPath = os.getenv("DATA_DOWNLOAD_PATH")
        self.historyFilePath = os.getenv('HISTORY_FILE_PATH')
        self.historyFileName = "hms-data-file-history.hst"

        self.console = console
        
        self.currentProject = None
        self.currentProjectCompleted = False
        self.currentJobID = None
        self.currentStatus = None

    def showHMSMenu(self):
        if self.currentJobID:
            self.console.print(f"[green italic]Current HMS/HAWQS Job ID:[/] [red]{self.currentJobID}[/]", justify="center")

        table = Table(box=None)
        tableMetadata = {
            'columns': [
                { 'header': "", 'justify': "center", 'style': "yellow", 'width': 3 },
                { 'header': "HMS Tests", 'justify': None, 'style': "blue", 'width': None },
                { 'header': "", 'justify': None, 'style': "magenta", 'width': None },
                { 'header': "Endpoint", 'justify': None, 'style': "green", 'width': None },
            ],
            'rows': [
                # { 'selector': "0", 'action': "HMS/HAWQS API Status", 'type': "GET", 'endpoint': "HMS/hawqs/status" },
                { 'selector': "1", 'action': "HMS/HAWQS Project Setup", 'type': "GET", 'endpoint': "HMS/hawqs/project/inputs" },
                { 'selector': "2", 'action': "HMS/HAWQS Submit Project", 'type': "POST", 'endpoint': "HMS/hawqs/project/submit" },
                { 'selector': "3", 'action': "HMS/HAWQS Project Status", 'type': "POST", 'endpoint': "HMS/hawqs/project/status/:id" },
                { 'selector': "c", 'action': "Cancel Project Execution", 'type': "POST", 'endpoint': "HMS/hawqs/project/cancel/:id" },
                { 'selector': "4", 'action': "Get HMS/HAWQS Project Data", 'type': "POST", 'endpoint': "HMS/hawqs/project/data/:id?process=(True/False)" },
                { 'selector': "5", 'action': "Previous Project Status", 'type': "", 'endpoint': "" },
                { 'selector': "6", 'action': "Previous Project Data Files", 'type': "", 'endpoint': "" },
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
        if choice == "1":
            self.setup()
        if choice == "2":
            self.submit()
        if choice == "3":
            self.status()
        if choice == "c":
            self.cancel()
        if choice == "4":
            self.data()
        if choice == "5":
            self.getPreviousStatus()
        if choice == "6":
            self.history()
        if choice == "e":
            return

        self.showHMSMenu()

    def setup(self):
        self.console.print(Panel("[green]Project Setup"))
        self.getInputDefinitions()

    def submit(self):
        self.console.print(Panel("[green]Submitting Project"))
        self.submitProject()

    def status(self):
        self.console.print(Panel("[green]Check Project Status"))
        if (self.currentJobID):
            self.getProjectStatus(self.currentJobID)
        else:
            alert(self.console, "No Project ID Stored")

    def data(self):
        self.console.print(Panel("[green]Get Project Data"))
        processChoices = ["y", "n"]
        if (self.currentProjectCompleted):
            processChoice = Prompt.ask(" Perform HMS/Aquatox data processing (y/n)? ", choices=processChoices, show_choices=False)
            self.getProjectData(processChoice == "y" and True or False) 
        else:
            alert(self.console, "No Completed Project")

    def getPreviousStatus(self):
        self.console.print(Panel("[green]Check Previous Project Status"))
        self.getProjectStatus(Prompt.ask(" Enter Project Id >"))

    def history(self):
        self.getHistory()

    def cancel(self):
        self.console.print(Panel("[green]Cancel Project Execution"))
        if self.isCurrentJob() and not self.currentProjectCompleted:
            self.cancelProjectExecution()
        elif self.isCurrentJob() and self.currentProjectCompleted:
            alert(self.console, "[red] The current project execution has completed")
        elif not self.isCurrentJob():
            alert(self.console, "There is no current job id stored")

    def getInputDefinitions(self):
        connection = http.client.HTTPConnection(self.hmsBaseUrl)
        try:
            with self.console.status("[bold green] Processing request...[/]") as _:
                connection.request('GET', "/hms/rest/api/hawqs/project/inputs")
                response = connection.getresponse()
                if response.status == 200:
                    showResponse(self.console, response.read().decode(), response.status)
                else:
                    alert(self.console, f"{response.status} Request unsuccessful")
        except Exception as ex:
            alert(self.console, "Error! " + repr(ex))

    def submitProject(self):
        self.currentProject = None
        self.currentProjectCompleted = False
        self.currentJobID = None
        self.currentStatus = None

        hawqsAPIObj = {
            'apiKey': self.hawqsAPIKey , 
            "inputData": json.dumps(project.inputData)
        }

        connection = http.client.HTTPConnection(self.hmsBaseUrl)
        headers = { 'Content-type': 'application/json' }
        try:
            with self.console.status("[bold green] Processing request...[/]") as _:
                connection.request('POST', "/hms/rest/api/hawqs/project/submit", json.dumps(hawqsAPIObj), headers)
                response = connection.getresponse()
                if response.status == 200:
                    currentProject = response.read().decode()
                    showResponse(self.console, currentProject, response.status)
                    self.currentProject = json.loads(currentProject)
                    if "id" in self.currentProject.keys():
                        self.currentJobID = self.currentProject['id']
                else:
                    alert(self.console, f"{response.status} Request unsuccessful")
        except Exception as ex:
            alert(self.console, "Error! " + repr(ex))

    def getProjectStatus(self, projectId):
        connection = http.client.HTTPConnection(self.hmsBaseUrl)
        headers = { 'Content-type': 'application/json' }

        hawqsAPIObj = {
            'apiKey': self.hawqsAPIKey
        }
        try:
            with self.console.status("[bold green] Processing request...[/]") as _:
                connection.request('POST', f"/hms/rest/api/hawqs/project/status/{projectId}", json.dumps(hawqsAPIObj), headers)
                response = connection.getresponse()
                if response.status == 200:
                    currentStatus = response.read().decode()
                    showResponse(self.console, currentStatus, response.status)
                    if self.currentJobID and self.currentJobID == projectId:
                        self.currentStatus = json.loads(currentStatus)
                        if self.currentStatus and not self.currentProjectCompleted:
                            if self.currentStatus['status']['progress'] >= 100:
                                self.currentProjectCompleted = True
                                self.updateHistory()
                else:
                    alert(self.console, f"{response.status} Request unsuccessful")
        except Exception as ex:
            alert(self.console, "Error! " + repr(ex))

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
    
    def getProjectData(self, process):
        connection = http.client.HTTPConnection(self.hmsBaseUrl)
        headers = { 'Content-type': 'application/json' }

        hawqsAPIObj = {
            'apiKey': self.hawqsAPIKey,
            "process": process
        }
        try:
            with self.console.status("[bold green] Processing request...[/]") as _:
                connection.request('POST', f"/hms/rest/api/hawqs/project/data/{self.currentJobID}", json.dumps(hawqsAPIObj), headers)
                response = connection.getresponse()
                if response.status == 200:
                    currentProject = response.read().decode()
                    showResponse(self.console, currentProject, response.status)

                    self.currentProject = json.loads(currentProject)
                    if "id" in self.currentProject.keys():
                        self.currentJobID = self.currentProject['id']
                else:
                    alert(self.console, f"{response.status} Request unsuccessful")
        except Exception as ex:
            alert(self.console, "Error! " + repr(ex))

    def cancelProjectExecution(self):
        connection = http.client.HTTPConnection(self.hmsBaseUrl)
        headers = { 'Content-type': 'application/json' }

        hawqsAPIObj = {
            'apiKey': self.hawqsAPIKey
        }
        try:
            with self.console.status("[bold green] Processing request...[/]") as _:
                connection.request('POST', f"/hms/rest/api/hawqs/project/cancel/{self.currentJobID}", json.dumps(hawqsAPIObj), headers)
                response = connection.getresponse()
                if response.status == 200:
                    showResponse(self.console, response.decode(), response.status)
                else:
                    alert(self.console, f"{response.status} Request unsuccessful")
        except Exception as ex:
            alert(self.console, "Error! " + repr(ex))

    def isCurrentJob(self):
        if self.currentJobID:
            return True

    def getHistory(self):
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

    def setKey(self, newKey):
        self.hawqsAPIKey = newKey