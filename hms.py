from time import sleep

from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt
from rich.json import JSON

from utils.alerts import alert

class HMSTests:
    def __init__(self, console):
        self.console = console

    def showHMSMenu(self):
        table = Table(box=None)
        tableMetadata = {
            'columns': [
                { 'header': "", 'justify': "center", 'style': "yellow", 'width': 3 },
                { 'header': "Action", 'justify': None, 'style': "blue", 'width': None },
                { 'header': "", 'justify': None, 'style': "magenta", 'width': None },
                { 'header': "Endpoint", 'justify': None, 'style': "green", 'width': None },
            ],
            'rows': [
                { 'selector': "0", 'action': "HMS/HAWQS project setup", 'type': "GET", 'endpoint': "hms/rest/api/hawqs/project/inputs" },
                { 'selector': "1", 'action': "HMS/HAWQS submit project", 'type': "POST", 'endpoint': "hms/rest/api/hawqs/project/submit" },
                { 'selector': "2", 'action': "HMS/HAWQS project status", 'type': "GET", 'endpoint': "hms/rest/api/hawqs/project/status/:id" },
                { 'selector': "3", 'action': "Get HMS/HAWQS Project Data", 'type': "GET", 'endpoint': "hms/rest/api/hawqs/project/data/:id" },
                { 'selector': "4", 'action': "Previous Project Data Files", 'type': "", 'endpoint': "" },
                { 'selector': "e", 'action': "[red]Return to Main Menu", 'type': None, 'endpoint': None },
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
        
        self.console.print(table, justify="center")
        self.executeChoice(Prompt.ask(" Make Selection >", choices=menuChoices, show_choices=False))

    def executeChoice(self, choice):
        if choice == "0":
            self.setup()

    def setup(self):
        print("setup!")