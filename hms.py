import http.client
import json
import os

from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt
from rich.json import JSON

from utils.alerts import alert

class HMSTests:
    hmsBaseUrl = os.getenv("DEV_HMS_HAWQS_BASE_URL")
    hmsInputsUrl = os.getenv("HMS_HAWQS_INPUTS_URL")
    hmsSubmitUrl = os.getenv("HMS_HAWQS_SUBMIT_URL")
    hmsStatusUrl = os.getenv("HMS_HAWQS_STATUS_URL")
    hmsDataUrl = os.getenv("HMS_HAWQS_DATA_URL")

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
            self.setup()
        if choice == "1":
            self.submit()
        if choice == "2":
            self.status()
        if choice == "3":
            self.data()
        if choice == "4":
            self.history()
        if choice == "e":
            return

        self.showHMSMenu()

    def setup(self):
        self.getInputDefinitions()

    def submit(self):
        self.submitProject()

    def status(self):
        print("status!")

    def data(self):
        print("data!")

    def getInputDefinitions(self):
        connection = http.client.HTTPSConnection(self.hmsBaseUrl)
        headers = { 'X-API-Key': self.hawqsAPIKey }
        with self.console.status("[bold green] Processing request...[/]") as _:
            connection.request('GET', self.hmsInputsUrl, None, headers)
            response = connection.getresponse()
            self.console.print(Panel(JSON(response.read().decode())))
            self.console.print(Panel(f"[green]Request Status:[/] {response.status}"))

    def submitProject(self):
        self.currentProject = None
        self.currentProjectCompleted = False
        self.currentJobID = None
        self.currentStatus = None

        inputData = {
            'dataset': 'HUC8',
            'downstreamSubbasin': '07100009',
            'setHrus': {
                'method': 'area',
                'target': 2,
                'units': 'km2'
            },
            'weatherDataset': 'PRISM',
            'startingSimulationDate': '1981-01-01',
            'endingSimulationDate': '1985-12-31',
            'warmupYears': 2,
            'outputPrintSetting': 'daily',
            'reportData': {
                'formats': [ 'csv', 'netcdf' ],
                'units': 'metric',
                'outputs': {
                    'rch': {
                        'statistics': [ 'daily_avg' ]
                    }
                }
            }
        }

        connection = http.client.HTTPSConnection(self.hmsBaseUrl)
        with self.console.status("[bold green] Processing request...[/]") as _:
            headers = { 'X-API-Key': self.hawqsAPIKey, 'Content-type': 'application/json' }
            connection.request('POST', self.hmsSubmitUrl, json.dumps(inputData), headers)
            response = connection.getresponse()
            currentProject = response.read().decode()
            self.console.print(Panel(JSON(currentProject)))
            self.console.print(Panel(f"[green] Request Status:[/] {response.status}"))

            self.currentProject = json.loads(currentProject)
            if self.currentProject['id']:
                self.currentJobID = self.currentProject['id']

    def setKey(newKey):
        self.hawqsAPIKey = newKey