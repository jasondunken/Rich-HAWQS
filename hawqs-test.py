import http.client
import json
import os

from dotenv import load_dotenv

from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt

load_dotenv()
DEFAULT_API_URL = os.getenv('DEFAULT_API_URL')
hawqsAPIUrl = DEFAULT_API_URL
DEFAULT_API_KEY = os.getenv('DEFAULT_API_KEY')
hawqsAPIKey = DEFAULT_API_KEY

connection = http.client.HTTPSConnection(hawqsAPIUrl)

currentJobID = None

console = Console()
table = Table(box=None)

table.add_column("", justify='center', style="yellow", width=3)
table.add_column("", justify='center', style="blue")
table.add_column("", style="magenta")
table.add_column("", style="green")
table.add_row("<1>",  "Check API Status", "[GET]", "test/clientget")
table.add_row("<2>", "Get Input Definitions", "[GET]", "projects/input-definitions")
table.add_row("<3>", "Submit a test Project", "[POST]", "projects/submit")
table.add_row("<4>", "Check Project Execution Status", "[GET]", "projects/:jobId")
table.add_row("<5>", "Get Completed Project data", "[GET]", "projects/data")
table.add_row("<6>", "Edit API URL")
table.add_row("<7>", "Edit API Key")
table.add_row("<8>", "[red]Exit Application[/]")

def showMenu():
    console.print()
    console.print(f" HAWQS API URL: {hawqsAPIUrl}")
    console.print(f" HAWQS API Key: {hawqsAPIKey}")

    if currentJobID:
        console.print(f"[green italic]Current Job ID:[/] [red]{currentJobID}[/]", justify="center")
        console.print()
    
    console.print(table)
    executeChoice(Prompt.ask(" Make Selection", choices=["1", "2", "3", "4", "5", "6", "7", "8"], show_choices=False))

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
    if choice == "8":
        console.print("[red] Exit Application")
        exitApplication()

def getAPIStatus():
    headers = { 'X-API-Key': hawqsAPIKey }
    with console.status("[bold green] Processing request...[/]") as _:
        connection.request('GET', '/test/clientget', None, headers)
        response = connection.getresponse()
        console.print("[green] API Status[/] " + response.read().decode())
        console.print(f"[green] Request Status:[/] {response.status}")

    showMenu()

def getInputDefinitions():
    headers = { 'X-API-Key': hawqsAPIKey }
    with console.status("[bold green] Processing request...[/]") as _:
        connection.request('GET', '/projects/input-definitions', None, headers)
        response = connection.getresponse()
        console.print("[green] Input Definitions[/] " + response.read().decode())
        console.print(f"[green] Request Status:[/] {response.status}")

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
    newUrl = console.input(f" [green]Enter a new URL, [white]reset[/] to reset URL to the default, or [white]exit[/] to cancel: ")
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
    newKey = console.input(f" Enter a new Key, [white]reset[/] to reset to the default, or [white]exit[/] to cancel: ")
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
    console.print("exiting [italic red]HAWQS[/italic red] API test application", justify="center")

if __name__ == "__main__":
    console.print()
    console.print("[italic red]HAWQS[/italic red] API test application", justify="center")
    showMenu()