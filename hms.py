import http.client
import json
import os

from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt
from rich.json import JSON

from utils.alerts import alert

import project

class HMSTests:
    hmsBaseUrl = os.getenv("DEV_HMS_HAWQS_BASE_URL")
    hawqsAPIKey = os.getenv("DEFAULT_API_KEY")

    def __init__(self, console):
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
                { 'selector': "0", 'action': "HMS/HAWQS project setup", 'type': "GET", 'endpoint': "HMS/hawqs/project/inputs" },
                { 'selector': "1", 'action': "HMS/HAWQS submit project", 'type': "POST", 'endpoint': "HMS/hawqs/project/submit" },
                { 'selector': "2", 'action': "HMS/HAWQS project status", 'type': "GET", 'endpoint': "HMS/hawqs/project/status/:id" },
                { 'selector': "3", 'action': "Get HMS/HAWQS Project Data", 'type': "GET", 'endpoint': "HMS/hawqs/project/data/:id" },
                { 'selector': "4", 'action': "Previous Project Data Files", 'type': "", 'endpoint': "" },
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
        if choice == "0":
            self.checkStatus()
        if choice == "1":
            self.setup()
        if choice == "2":
            self.submit()
        if choice == "3":
            self.status()
        if choice == "4":
            self.data()
        if choice == "5":
            self.history()
        if choice == "e":
            return

        self.showHMSMenu()

    def checkStatus(self):
        self.console.print(Panel("[green]Check API Status"))
        self.getAPIStatus()

    def setup(self):
        self.console.print(Panel("[green]Project Setup"))
        self.getInputDefinitions()

    def submit(self):
        self.console.print(Panel("[green]Submitting Project"))
        self.submitProject()

    def status(self):
        self.console.print(Panel("[green]Submitting Project"))
        self.getProjectStatus()

    def data(self):
        self.console.print(Panel("[green]Get Project Data"))
        self.getProjectData()

    def getAPIStatus(self):
        connection = http.client.HTTPSConnection(self.hmsBaseUrl)
        with self.console.status("[bold green] Processing request...[/]") as _:
            connection.request('GET', "status", None)
            response = connection.getresponse()
            self.console.print(Panel(JSON(response.read().decode())))
            self.console.print(Panel(f"[green]Request Status:[/] {response.status}"))


    def getInputDefinitions(self):
        connection = http.client.HTTPSConnection(self.hmsBaseUrl)
        headers = { 'X-API-Key': self.hawqsAPIKey }
        with self.console.status("[bold green] Processing request...[/]") as _:
            connection.request('GET', "project/inputs", None, headers)
            response = connection.getresponse()
            self.console.print(Panel(JSON(response.read().decode())))
            self.console.print(Panel(f"[green]Request Status:[/] {response.status}"))

    def submitProject(self):
        self.currentProject = None
        self.currentProjectCompleted = False
        self.currentJobID = None
        self.currentStatus = None

        connection = http.client.HTTPSConnection(self.hmsBaseUrl)
        with self.console.status("[bold green] Processing request...[/]") as _:
            headers = { 'X-API-Key': self.hawqsAPIKey, 'Content-type': 'application/json' }
            connection.request('POST', "project/submit", json.dumps(project.inputData), headers)
            response = connection.getresponse()
            currentProject = response.read().decode()
            self.console.print(Panel(JSON(currentProject)))
            self.console.print(Panel(f"[green] Request Status:[/] {response.status}"))

            self.currentProject = json.loads(currentProject)
            if self.currentProject['id']:
                self.currentJobID = self.currentProject['id']

    def getProjectStatus(self):
        connection = http.client.HTTPSConnection(self.hmsBaseUrl)
        with self.console.status("[bold green] Processing request...[/]") as _:
            headers = { 'X-API-Key': self.hawqsAPIKey }
            connection.request('GET', "project/status", None, headers)
            response = connection.getresponse()
            currentStatus = response.read().decode()
            self.console.print(Panel(JSON(currentStatus)))
            self.console.print(Panel(f"[green] Request Status:[/] {response.status}"))

            self.currentStatus = json.loads(currentStatus)
            if self.currentStatus['id']:
                self.currentJobID = self.currentProject['id']
    
    def getProjectData(self):
        connection = http.client.HTTPSConnection(self.hmsBaseUrl)
        with self.console.status("[bold green] Processing request...[/]") as _:
            headers = { 'X-API-Key': self.hawqsAPIKey }
            connection.request('GET', "project/data", None, headers)
            response = connection.getresponse()
            currentProject = response.read().decode()
            self.console.print(Panel(JSON(currentProject)))
            self.console.print(Panel(f"[green] Request Status:[/] {response.status}"))

            self.currentProject = json.loads(currentProject)
            if self.currentProject['id']:
                self.currentJobID = self.currentProject['id']

    def setKey(self, newKey):
        self.hawqsAPIKey = newKey