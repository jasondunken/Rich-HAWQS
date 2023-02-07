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

        self.console = console
        
        self.currentProject = None
        self.currentProjectCompleted = False
        self.currentJobID = None
        self.currentStatus = None

    def showHMSMenu(self):
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
                { 'selector': "3", 'action': "HMS/HAWQS Project Status", 'type': "GET", 'endpoint': "HMS/hawqs/project/status/:id" },
                { 'selector': "x", 'action': "Cancel Project Execution", 'type': "GET", 'endpoint': "HMS/hawqs/project/cancel/:id" },
                { 'selector': "4", 'action': "Get HMS/HAWQS Project Data", 'type': "GET", 'endpoint': "HMS/hawqs/project/data/:id?process=(True/False)" },
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
        if choice == "x":
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
        self.cancelProjectExecution(Prompt.ask(" Enter id of project to cancel: "))

    def getInputDefinitions(self):
        connection = http.client.HTTPConnection(self.hmsBaseUrl)
        headers = { 'X-API-Key': self.hawqsAPIKey }
        try:
            with self.console.status("[bold green] Processing request...[/]") as _:
                connection.request('GET', "/hms/rest/api/hawqs/project/inputs", None, headers)
                response = connection.getresponse()
                if response.status == 200:
                    showResponse(self.console, response.read().decode(), response.status)
                else:
                    alert(self.console, "Request unsuccessful")
        except Exception as ex:
            alert(self.console, "Error! " + repr(ex))

    def submitProject(self):
        self.currentProject = None
        self.currentProjectCompleted = False
        self.currentJobID = None
        self.currentStatus = None

        hawqsSubmitObject = {
            "inputData": project.inputData
        }

        connection = http.client.HTTPConnection(self.hmsBaseUrl)
        headers = { 'X-API-Key': self.hawqsAPIKey , 'Content-type': 'application/json' }
        try:
            with self.console.status("[bold green] Processing request...[/]") as _:
                connection.request('POST', "/hms/rest/api/hawqs/project/submit", json.dumps(hawqsSubmitObject), headers)
                response = connection.getresponse()
                if response.status == 200:
                    currentProject = response.read().decode()
                    showResponse(self.console, currentProject, response.status)
                    self.currentProject = json.loads(currentProject)
                    if self.currentProject['id']:
                        self.currentJobID = self.currentProject['id']
                else:
                    alert(self.console, "Request unsuccessful")
        except Exception as ex:
            alert(self.console, "Error! " + repr(ex))

    def getProjectStatus(self, projectId):
        connection = http.client.HTTPConnection(self.hmsBaseUrl)
        headers = { 'X-API-Key': self.hawqsAPIKey }
        try:
            with self.console.status("[bold green] Processing request...[/]") as _:
                connection.request('GET', "/hms/rest/api/hawqs/project/status/" + projectId, None, headers)
                response = connection.getresponse()
                if response.status == 200:
                    currentStatus = response.read().decode()
                    showResponse(self.console, currentStatus, response.status)
                    if self.currentJobID and self.currentJobId == projectId:
                        self.currentStatus = json.loads(currentStatus)
                        if self.currentStatus['id']:
                            self.currentJobID = self.currentProject['id']
                else:
                    alert(self.console, "Request unsuccessful")
        except Exception as ex:
            alert(self.console, "Error! " + repr(ex))
    
    def getProjectData(self, process):
        connection = http.client.HTTPConnection(self.hmsBaseUrl)
        headers = { 'X-API-Key': self.hawqsAPIKey }
        try:
            with self.console.status("[bold green] Processing request...[/]") as _:
                connection.request('GET', "/hms/rest/api/hawqs/project/data/" + self.currentJobID + "?process=" + process, None, headers)
                response = connection.getresponse()
                if response.status == 200:
                    currentProject = response.read().decode()
                    showResponse(self.console, currentProject, response.status)

                    self.currentProject = json.loads(currentProject)
                    if self.currentProject['id']:
                        self.currentJobID = self.currentProject['id']
                else:
                    alert(self.console, "Request unsuccessful")
        except Exception as ex:
            alert(self.console, "Error! " + repr(ex))

    def cancelProjectExecution(self, projectId):
        connection = http.client.HTTPConnection(self.hmsBaseUrl)
        headers = { 'X-API-Key': self.hawqsAPIKey }
        try:
            with self.console.status("[bold green] Processing request...[/]") as _:
                connection.request('GET', "/hms/rest/api/hawqs/project/cancel/" + projectId, None, headers)
                response = connection.getresponse()
                if response.status == 200:
                    showResponse(self.console, response.decode(), response.status)
                else:
                    alert(self.console, "Request unsuccessful")
        except Exception as ex:
            alert(self.console, "Error! " + repr(ex))

    def getHistory(self):
        alert(self.console, "hms test project history not yet implemented!")

    def setKey(self, newKey):
        self.hawqsAPIKey = newKey