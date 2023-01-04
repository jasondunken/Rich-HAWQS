import http.client
import json
import os

from dotenv import load_dotenv

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt
from rich.json import JSON

load_dotenv()
DEFAULT_API_URL = os.getenv('DEFAULT_API_URL')
hawqsAPIUrl = DEFAULT_API_URL
DEFAULT_API_KEY = os.getenv('DEFAULT_API_KEY')
hawqsAPIKey = os.getenv('DEFAULT_API_KEY')

connection = http.client.HTTPSConnection(hawqsAPIUrl)

currentJobID = None

console = Console(color_system='auto')

table = Table(box=None)
tableMeta = {
    'columns': [
        { 'header': "", 'justify': "center", 'style': "yellow", 'width': 3 },
        { 'header': "", 'justify': "center", 'style': "blue", 'width': None },
        { 'header': "", 'justify': None, 'style': "magenta", 'width': None },
        { 'header': "", 'justify': None, 'style': "green", 'width': None },
    ],
    'rows': [
        { 'selector': "1", 'action': "Check HAWQS API Status", 'type': "GET", 'endpoint': "test/clientget" },
        { 'selector': "2", 'action': "Get Input Definitions", 'type': "GET", 'endpoint': "projects/input-definitions" },
        { 'selector': "3", 'action': "Submit a test Project", 'type': "POST", 'endpoint': "projects/submit" },
        { 'selector': "4", 'action': "Check Project Execution Status", 'type': "GET", 'endpoint': "projects/:jobId" },
        { 'selector': "5", 'action': "Get Completed Project data", 'type': "GET", 'endpoint': "projects/data/:jobId" },
        { 'selector': "6", 'action': "Edit API URL", 'type': None, 'endpoint': None },
        { 'selector': "7", 'action': "Edit API Key", 'type': None, 'endpoint': None },
        { 'selector': "e", 'action': "[red]Exit Application[/]", 'type': None, 'endpoint': None },
    ]
}
menuChoices = [row['selector'] for row in tableMeta['rows']]

for column in tableMeta['columns']:
    table.add_column(column['header'], justify=column['justify'], style=column['style'], width=column['width'])
for row in tableMeta['rows']:
    if row['type']:
        table.add_row(f"<{row['selector']}>", row['action'], f"[{row['type']}]", row['endpoint'])
    else:
        table.add_row(f"<{row['selector']}>", row['action'])

def showMenu():
    console.print(Panel(f"HAWQS API URL: [cyan]{hawqsAPIUrl}[/] \nHAWQS API Key: [cyan]{hawqsAPIKey}[/]"))

    if currentJobID:
        console.print(f"[green italic]Current Job ID:[/] [red]{currentJobID}[/]", justify="center")
    
    console.print(table)
    executeChoice(Prompt.ask(" Make Selection >", choices=menuChoices, show_choices=False))

def executeChoice(choice):
    console.print()
    if choice == "1":
        console.print("[green] Fetching API Status")
        getAPIStatus()
    if choice == "2":
        console.print("[green] Fetching Input Definitions")
        getInputDefinitions()
    if choice == "3":
        console.print("[green] Submitting Project")
        submitProject()
    if choice == "4":
        if isCurrentJob():
            console.print("[green] Fetching Project Status")
            getProjectStatus()
        else:
            showMenu()
    if choice == "5":
        if isCurrentJob():
            console.print("[green] Fetching Project Data")
            getProjectData()
        else:
            showMenu()
    if choice == "6":
        console.print("[green] Edit URL")
        editApiUrl()
    if choice == "7":
        console.print("[green] Edit Key")
        editApiKey()
    if choice == "e":
        console.print("[red] Exit Application")
        exitApplication()

def getAPIStatus():
    headers = { 'X-API-Key': hawqsAPIKey }
    with console.status("[bold green] Processing request...[/]") as _:
        connection.request('GET', '/test/clientget', None, headers)
        response = connection.getresponse()
        console.print(Panel(JSON(response.read().decode())))
        console.print(Panel(f"[green]Request Status:[/] {response.status}"))

    showMenu()

def getInputDefinitions():
    headers = { 'X-API-Key': hawqsAPIKey }
    with console.status("[bold green] Processing request...[/]") as _:
        connection.request('GET', '/projects/input-definitions', None, headers)
        response = connection.getresponse()
        console.print(Panel(JSON(response.read().decode())))
        console.print(Panel(f"[green]Request Status:[/] {response.status}"))

    showMenu()

def submitProject():
    inputData = {
	'dataset': 'HUC8',
	'downstreamSubbasin': '07100009',
	'setHrus': {
		'method': 'area',
		'target': 2,
		'units': 'km2'
	},
	'weatherDataset': 'NCDC NWS/NOAA',
    'startingSimulationDate': '1961-01-01',
    'endingSimulationDate': '1965-12-31',
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

    headers = { 'X-API-Key': hawqsAPIKey, 'Content-type': 'application/json' }
    with console.status("[bold green] Processing request...[/]") as _:
        connection.request('POST', '/projects/submit', json.dumps(inputData), headers)
        response = connection.getresponse()
        console.print("[green] Submit Project Response[/] " + response.read().decode())
        console.print(f"[green] Request Status:[/] {response.status}")

    showMenu()

def isCurrentJob():
    if currentJobID:
        return True
    
    console.print("[red] There must be a stored job ID. Submit a project to create job ID")
    return False

def getProjectStatus():
    None

def getProjectData():
    None

def editApiUrl():
    global hawqsAPIUrl 
    console.print(f" [green]The current HAWQS API URL is:[/] {hawqsAPIUrl}")
    console.print(f" [green]Enter a new URL, [white]reset[/] to reset URL to the default, or [white]exit[/] to cancel")
    newUrl = Prompt.ask(" >")
    if newUrl.lower() == "exit":
        console.print(f" [yellow]Edit URL cancelled")
    elif newUrl.lower() == "reset":
        hawqsAPIUrl = DEFAULT_API_URL
        console.print(f' [green]API URL reset to default: [white]{hawqsAPIUrl}')
    else:
        hawqsAPIUrl = newUrl
        console.print(f' [green]API URL updated to: [white]{hawqsAPIUrl}')
    showMenu()

def editApiKey():
    global hawqsAPIKey
    console.print(f" The current HAWQS API Key is {hawqsAPIKey}")
    console.print(f" Enter a new Key, [white]reset[/] to reset to the default, or [white]exit[/] to cancel")
    newKey = Prompt.ask(" >")
    if newKey.lower() == "exit":
        console.print(f" [yellow]Edit Key cancelled")
    elif newKey.lower() == "reset":
        hawqsAPIKey = DEFAULT_API_KEY
        console.print(f' [green]API Key reset to default: [white]{hawqsAPIKey}')
    else:
        hawqsAPIKey = newKey
        console.print(f' [green]API Key updated to: [white]{hawqsAPIKey}')
    showMenu()

def exitApplication():
    console.print("exiting [italic red]HAWQS[/italic red] Web API test application", justify="center")

if __name__ == "__main__":
    console.print("\n\n\n\n\n")

    #  _____ _____ _____   _ _____ _____ _ _ _ _____ _____    _____ _____ _____ 
    # |  |  |     |   __| / |  |  |  _  | | | |     |   __|  |  _  |  _  |     |
    # |     | | | |__   |/ /|     |     | | | |  |  |__   |  |     |   __|-   -|
    # |__|__|_|_|_|_____|_/ |__|__|__|__|_____|__  _|_____|  |__|__|__|  |_____|
    #                                            |__|                           
    asciiString = f"[white] _____ _____ _____   _ _____ _____ _ _ _ _____ _____    _____ _____ _____ \n" + \
                  f"[bright_yellow]|  |  |     |   __| / |  |  |  _  | | | |     |   __|  |  _  |  _  |     |\n" + \
                  f"[bright_cyan]|     | | | |__   |/ /|     |     | | | |  |  |__   |  |     |   __|-   -|\n" + \
                  f"[bright_blue]|__|__|_|_|_|_____|_/ |__|__|__|__|_____|__  _|_____|  |__|__|__|  |_____|\n" + \
                  f"[bright_magenta]                |__|                           "
    console.print(Panel.fit(asciiString), justify='center', style='red')

    console.print("[italic red]HAWQS[/italic red] Web API test application", justify="center")
    console.print()
    showMenu()