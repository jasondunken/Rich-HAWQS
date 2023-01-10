import http.client
import json
import os
from time import sleep

from dotenv import load_dotenv

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt
from rich.json import JSON

import hms

from utils.alerts import alert

load_dotenv()
DEFAULT_API_URL = os.getenv('DEFAULT_API_URL')
hawqsAPIUrl = DEFAULT_API_URL
DEFAULT_API_KEY = os.getenv('DEFAULT_API_KEY')
hawqsAPIKey = DEFAULT_API_KEY

dataDownloadPath = os.getenv("DATA_DOWNLOAD_PATH")
historyFilePath = os.getenv('HISTORY_FILE_PATH')
historyFileName = "data-file-history.hst"

currentProject = None
currentProjectCompleted = False
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
            { 'selector': "0", 'action': "Check HAWQS API Status", 'type': "GET", 'endpoint': "HAWQS/test/clientget" },
            { 'selector': "1", 'action': "Get Input Definitions", 'type': "GET", 'endpoint': "HAWQS/projects/input-definitions" },
            { 'selector': "2", 'action': "Submit a Test Project", 'type': "POST", 'endpoint': "HAWQS/projects/submit" },
            { 'selector': "3", 'action': "Check Project Execution Status", 'type': "GET", 'endpoint': "HAWQS/projects/:id" },
            { 'selector': "4", 'action': "Get Current Project Data", 'type': "GET", 'endpoint': "HAWQS/api-files/api-projects/epaDevAccess/" },
            { 'selector': "5", 'action': "Previous Project Data Files", 'type': "", 'endpoint': "" },
            { 'selector': "6", 'action': "[bright_black]HMS Test", 'type': "", 'endpoint': "" },
            { 'selector': "7", 'action': "Edit API URL", 'type': None, 'endpoint': None },
            { 'selector': "8", 'action': "Edit API Key", 'type': None, 'endpoint': None },
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
    if choice == "0":
        console.print("[green] Fetching API Status")
        getAPIStatus()
    if choice == "1":
        console.print("[green] Fetching Input Definitions")
        getInputDefinitions()
    if choice == "2":
        console.print("[green] Submitting Project")
        submitProject()
    if choice == "3":
        if isCurrentJob():
            console.print("[green] Fetching Project Status")
            getProjectStatus()
        else:
            alert(console, "[red] There must be a stored job ID. Submit the test project to create job ID")
            showMenu()
    if choice == "4":
        if currentProjectCompleted:
            console.print("[green] Fetch Project Data")
            getProjectData()
        else:
            alert(console, "[red] Project progress must be 100% complete to get data. Check status again")
            showMenu()
    if choice == "5":
        console.print("[green] Fetch Previous Project Data")
        showFileHistory()
    if choice == "6":
        console.print("[cyan] Running HMS Test")
        hmsTest = hms.HMSTest(console)
        hmsTest.test()
    if choice == "7":
        console.print("[yellow] Edit URL")
        editApiUrl()
    if choice == "8":
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
    global currentProject, currentProjectCompleted, currentJobID, currentStatus
    currentProject = None
    currentProjectCompleted = False
    currentJobID = None
    currentStatus = None

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
            global currentProjectCompleted
            if currentStatus and not currentProjectCompleted:
                if currentStatus['status']['progress'] >= 100:
                    currentProjectCompleted = True
                    updateHistory()

    except Exception as e:
        console.print(Panel("some kind of exception occurred", e))

def updateHistory():
    with open(os.path.join(historyFilePath, historyFileName), 'a+') as historyFile:
        for file in currentStatus['output']:
            historyFile.write(f"{file['url']}\n")

def clearHistory():
    try:
        with open(os.path.join(historyFilePath, historyFileName), "w") as historyFile:
            historyFile.write("")
    except Exception as ex:
        alert(console, "History already cleared")
        return

def getProjectData():
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
    for x, file in enumerate(currentStatus['output']):
        project, name, url = parseUrl(file['url'])
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
        console.print(table)
        fileChoice = Prompt.ask(" Download file >", choices=choices, show_choices=False)

        if fileChoice == "e": break
        if fileChoice == "a": getAllDataFiles(fileMetadata)
        else :
            fileData = fileMetadata[int(fileChoice)]
            console.print(Panel(f"Fetching {fileData['name']}..."))
            getDataFile(fileData)

def showFileHistory():
    urls = None
    try:
        with open(os.path.join(historyFilePath, historyFileName), "r") as file:
            urls = file.readlines()
    
    except Exception as ex:
        alert(console, "There is currently no project history")
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
        project, name, url = parseUrl(url)

        
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
        console.print(table)
        fileChoice = Prompt.ask(" Download file >", choices=choices, show_choices=False)

        if fileChoice == "e": break
        if fileChoice == "c": clearHistory()
        else :
            fileData = tableMetadata['rows'][int(fileChoice)]
            console.print(Panel(f"Fetching {fileData['name']}..."))
            getDataFile(fileData)

def getAllDataFiles(fileData):
    for file in fileData:
        getDataFile(file)

def getDataFile(fileData):
    try:
        content = None
        connection = http.client.HTTPSConnection(hawqsAPIUrl)
        headers = { 'X-API-Key': hawqsAPIKey }
        with console.status("[bold green] Processing request...") as _:
            connection.request('GET', fileData['url'], None, headers)
            response = connection.getresponse()
            console.print(Panel(f"{fileData['name']} received"))
            content = response.read()
            console.print(Panel(f"[green]Request Status:[/] {response.status}"))

        with console.status("[bold green] Saving file...") as _:
            if content:
                projectName = fileData['project']
                downloadFolderPath = os.path.join(dataDownloadPath, projectName)
                if not os.path.exists(downloadFolderPath):
                    os.makedirs(downloadFolderPath)
                fileName = fileData['name']
                with open(os.path.join(downloadFolderPath, fileName), 'wb+') as f:
                    f.write(content)

                console.print(Panel(f"{fileName} saved"))

    except Exception as e:
        console.print(Panel("some kind of exception occurred", e))

def parseUrl(url):
    url = url.rstrip()
    # gets from after second to last / to end => projectname/filename
    urlEnd = url[url.rfind("/", 0, url.rfind("/")):][1:]
    project = urlEnd[:urlEnd.find("/")]
    name = urlEnd[urlEnd.find("/"):][1:]

    return project, name, url

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