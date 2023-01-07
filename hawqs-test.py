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
hawqsAPIKey = DEFAULT_API_KEY

currentProject = None
currentJobID = None
currentStatus = None

console = Console(color_system='auto')

def showMenu():
    console.print(Panel(f"[green]HAWQS API URL: [cyan]{hawqsAPIUrl}[/] \nHAWQS API Key: [cyan]{hawqsAPIKey}[/]"), style='yellow')

    if currentJobID:
        console.print(f"[green italic]Current Job ID:[/] [red]{currentJobID}[/]", justify="center")

    table = Table(box=None)
    tableMetadata = {
        'columns': [
            { 'header': "", 'justify': "center", 'style': "yellow", 'width': 3 },
            { 'header': "Action", 'justify': "center", 'style': "blue", 'width': None },
            { 'header': "", 'justify': None, 'style': "magenta", 'width': None },
            { 'header': "Endpoint", 'justify': None, 'style': "green", 'width': None },
        ],
        'rows': [
            { 'selector': "1", 'action': "Check HAWQS API Status", 'type': "GET", 'endpoint': "test/clientget" },
            { 'selector': "2", 'action': "Get Input Definitions", 'type': "GET", 'endpoint': "projects/input-definitions" },
            { 'selector': "3", 'action': "Submit a test Project", 'type': "POST", 'endpoint': "projects/submit" },
            { 'selector': "4", 'action': "Check Project Execution Status", 'type': "GET", 'endpoint': "projects/:id" },
            { 'selector': "5", 'action': "Get Completed Project data", 'type': "GET", 'endpoint': "api-files/api-projects/epaDevAccess/" },
            { 'selector': "6", 'action': "Edit API URL", 'type': None, 'endpoint': None },
            { 'selector': "7", 'action': "Edit API Key", 'type': None, 'endpoint': None },
            { 'selector': "e", 'action': "[red]Exit Application[/]", 'type': None, 'endpoint': None },
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
        # if isProjectCompleted():
        if True:
            console.print("[green] Fetch Project Data")
            getProjectData()
        else:
            showMenu()
    if choice == "6":
        console.print("[yellow] Edit URL")
        editApiUrl()
    if choice == "7":
        console.print("[yellow] Edit Key")
        editApiKey()
    if choice == "e":
        console.print("[red] Exit Application")
        exitApplication()

    showMenu()

def getAPIStatus():
    connection = http.client.HTTPSConnection(hawqsAPIUrl)
    headers = { 'X-API-Key': hawqsAPIKey }
    with console.status("[bold green] Processing request...[/]") as _:
        connection.request('GET', '/test/clientget', None, headers)
        response = connection.getresponse()
        console.print(Panel(JSON(response.read().decode())))
        console.print(Panel(f"[green]Request Status:[/] {response.status}"))

def getInputDefinitions():
    connection = http.client.HTTPSConnection(hawqsAPIUrl)
    headers = { 'X-API-Key': hawqsAPIKey }
    with console.status("[bold green] Processing request...[/]") as _:
        connection.request('GET', '/projects/input-definitions', None, headers)
        response = connection.getresponse()
        console.print(Panel(JSON(response.read().decode())))
        console.print(Panel(f"[green]Request Status:[/] {response.status}"))

def submitProject():
    global currentProject, currentJobID, currentProgress
    currentProject = None
    currentJobID = None
    currentProgress = 0

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

    connection = http.client.HTTPSConnection(hawqsAPIUrl)
    with console.status("[bold green] Processing request...[/]") as _:
        headers = { 'X-API-Key': hawqsAPIKey, 'Content-type': 'application/json' }
        connection.request('POST', '/projects/submit', json.dumps(inputData), headers)
        response = connection.getresponse()
        currentProject = response.read().decode()
        console.print(Panel(JSON(currentProject)))
        console.print(Panel(f"[green] Request Status:[/] {response.status}"))

        currentProject = json.loads(currentProject)
        if currentProject['id']:
            currentJobID = currentProject['id']

def isCurrentJob():
    if currentJobID:
        return True
    
    console.print(Panel("[red] There must be a stored job ID. Submit the test project to create job ID"), style='red')
    return False

def getProjectStatus():
    try:
        connection = http.client.HTTPSConnection(hawqsAPIUrl)
        headers = { 'X-API-Key': hawqsAPIKey }
        with console.status("[bold green] Processing request...[/]") as _:
            connection.request('GET', f'/projects/{currentJobID}', None, headers)
            response = connection.getresponse()
            global currentStatus
            currentStatus = response.read().decode()
            console.print(Panel(JSON(currentStatus)))
            console.print(Panel(f"[green]Request Status:[/] {response.status}"))

            currentStatus = json.loads(currentStatus)
    except Exception as e:
        console.print(Panel("some kind of exception occurred", e))

def isProjectCompleted():
    if currentStatus['status']['progress'] >= 100:
        return True

    console.print(Panel("[red] Project progress must be 100% complete to get data. Check status again"), style='red')
    return False

testOutput = [
    { 
        'name': 'Project input/output files', 
        'url': 'https://dev-api.hawqs.tamu.edu/api-files/api-projects/epaDevAccess/70_api-project-epadevaccess-2023-01-06-164844/huc8-07100009.7z', 
        'format': '7zip'
    }, 
    { 
        'name': 'Metadata for daily averages by month (output.rch)',
        'url': 'https://dev-api.hawqs.tamu.edu/api-files/api-projects/epaDevAccess/70_api-project-epadevaccess-2023-01-06-164844/output_rch_daily_avg_metadata.csv',
        'format': 'csv'
    },
    {
        'name': 'Daily averages by month (output.rch)', 
        'url': 'https://dev-api.hawqs.tamu.edu/api-files/api-projects/epaDevAccess/70_api-project-epadevaccess-2023-01-06-164844/output_rch_daily_avg.csv',
        'format': 'csv'
    },
    {
        'name': 'Daily averages by month (output.rch)',
        'url': 'https://dev-api.hawqs.tamu.edu/api-files/api-projects/epaDevAccess/70_api-project-epadevaccess-2023-01-06-164844/output_rch_daily_avg.nc', 
        'format': 'netcdf'
    }]

def getProjectData():
    tableMetadata = {
        'columns': [
            { 'header': "", 'justify': "center", 'style': "yellow", 'width': 3 },
            { 'header': "File Name", 'justify': None, 'style': "cyan", 'width': None },
            { 'header': "Format", 'justify': "center", 'style': "green", 'width': None },
        ],
        'rows': []
    }
    choices = []
    for x, file in enumerate(testOutput):
        tableMetadata['rows'].append({
            'selector': x,
            'name': file['name'],
            'url': file['url'],
            'file-format': file['format']
        })
        choices.append(str(x))
    tableMetadata['rows'].append({ 'selector': 'a', 'name': "Download all files", 'file-format': ""})
    choices.append("a")
    tableMetadata['rows'].append({ 'selector': 'e', 'name': "[red]Exit to Main Menu", 'file-format': ""})
    choices.append("e")

    table = Table(box=None)
    for column in tableMetadata['columns']:
        table.add_column(column['header'], justify=column['justify'], style=column['style'], width=column['width'])
    for row in tableMetadata['rows']:
        table.add_row(f"<{row['selector']}>", row['name'], f"{row['file-format']}")

    while True:
        console.print(table)
        fileChoice = Prompt.ask(" Download file >", choices=choices, show_choices=False)

        if fileChoice == "e": break
        if fileChoice == "a": getAllDataFiles(tableMetadata['rows'])
        else :
            fileData = tableMetadata['rows'][int(fileChoice)]
            console.print(Panel(f"Fetching {fileData['name']}..."))
            getDataFile(fileData)

def getAllDataFiles(fileData):
    None

def getDataFile(fileData):
    try:
        connection = http.client.HTTPSConnection(hawqsAPIUrl)
        headers = { 'X-API-Key': hawqsAPIKey }
        with console.status("[bold green] Processing request...[/]") as _:
            connection.request('GET', fileData['url'], None, headers)
            response = connection.getresponse()
            console.print(Panel(f"{fileData['name']} received"))
            console.print(Panel(f"[green]Request Status:[/] {response.status}"))
    except Exception as e:
        console.print(Panel("some kind of exception occurred", e))

def editApiUrl():
    global hawqsAPIUrl 
    console.print(f" [green]The current HAWQS API URL is:[/] [cyan]{hawqsAPIUrl}")
    console.print(f" [green]Enter a new URL, ([white]r[/])eset to reset to the default, or ([white]e[/])xit to cancel")
    newUrl = Prompt.ask(" >")
    if newUrl.lower() == "exit" or newUrl.lower() == "e":
        console.print(f" [yellow]Edit URL cancelled")
    elif newUrl.lower() == "reset" or newUrl.lower() == "r":
        hawqsAPIUrl = DEFAULT_API_URL
        console.print(f' [green]API URL reset to default: [cyan]{hawqsAPIUrl}')
    else:
        hawqsAPIUrl = newUrl
        console.print(f' [green]API URL updated to: [cyan]{hawqsAPIUrl}')
        
    console.print()

def editApiKey():
    global hawqsAPIKey
    console.print(f" [green]The current HAWQS API Key is:[/] [cyan]{hawqsAPIKey}")
    console.print(f" [green]Enter a new Key, ([white]r[/])eset to reset to the default, or ([white]e[/])xit to cancel")
    newKey = Prompt.ask(" >")
    if newKey.lower() == "exit" or newKey.lower() == "e":
        console.print(f" [yellow]Edit Key cancelled")
    elif newKey.lower() == "reset" or newKey.lower() == "r":
        hawqsAPIKey = DEFAULT_API_KEY
        console.print(f' [green]API Key reset to default: [cyan]{hawqsAPIKey}')
    else:
        hawqsAPIKey = newKey
        console.print(f' [green]API Key updated to: [cyan]{hawqsAPIKey}')
        
    console.print()

def exitApplication():
    console.print("exiting [italic red]HAWQS[/italic red] Web API test application", justify="center")
    exit()

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

    console.print("[bright_cyan]HMS[/]/[red]HAWQS[/] Web API test application", justify="center")
    showMenu()