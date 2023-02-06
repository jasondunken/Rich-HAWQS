from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt

import hms
import hawqs

class HAWQSTestClient:
    console = Console(color_system='auto', width=80)
    hawqsTests = hawqs.HAWQSTests(console)
    hmsTests = hms.HMSTests(console)

    def showMenu(self):
        self.console.print(Panel(f"[green]HAWQS API URL: [cyan]{self.hawqsTests.getUrl()}[/] \nHAWQS API Key: [cyan]{self.hawqsTests.getKey()}[/]"), style='yellow')

        table = Table(box=None)
        tableMetadata = {
            'columns': [
                { 'header': "", 'justify': "center", 'style': "yellow", 'width': 3 },
                { 'header': "", 'justify': None, 'style': "blue", 'width': None },
            ],
            'rows': [
                { 'selector': "0", 'action': "[bright_cyan]HAWQS Tests" },
                { 'selector': "1", 'action': "[royal_blue1]HMS Tests" },
                { 'selector': "2", 'action': "Edit HAWQS API URL" },
                { 'selector': "3", 'action': "Edit HAWQS API Key" },
                { 'selector': "e", 'action': "[red]Exit Application" },
            ]
        }
        menuChoices = [row['selector'] for row in tableMetadata['rows']]

        for column in tableMetadata['columns']:
            table.add_column(column['header'], justify=column['justify'], style=column['style'], width=column['width'])
        for row in tableMetadata['rows']:
            table.add_row(f"<{row['selector']}>", row['action'])
        
        self.console.print(table)
        self.executeChoice(Prompt.ask(" Make Selection >", choices=menuChoices, show_choices=False))

    def executeChoice(self, choice):
        self.console.print()
        if choice == "0":
            self.hawqsTests.showHAWQSMenu()
        if choice == "1":
            self.hmsTests.showHMSMenu()
        if choice == "2":
            self.editApiUrl()
        if choice == "3":
            self.editApiKey()
        if choice == "e":
            self.console.print("[red] Exit Application")
            self.exitApplication()

        self.showMenu()

    def editApiUrl(self):
        self.console.print("[yellow] Edit URL")
        self.console.print(f" [green]The current HAWQS API URL is:[/] [cyan]{self.hawqsTests.getUrl()}")
        self.console.print(f" [green]Enter a new URL, ([white]r[/])eset to reset to the default, or ([white]e[/])xit to cancel")
        newUrl = Prompt.ask(" >")
        if newUrl.lower() == "exit" or newUrl.lower() == "e":
            self.console.print(f" [yellow]Edit URL cancelled")
        elif newUrl.lower() == "reset" or newUrl.lower() == "r":
            self.hawqsTests.restoreDefaultUrl()
            self.console.print(f' [green]API URL reset to default: [cyan]{self.hawqsTests.getUrl()}')
        else:
            self.hawqsTests.setUrl(newUrl)
            self.console.print(f' [green]API URL updated to: [cyan]{self.hawqsTests.getUrl()}')
            
        self.console.print()

    def editApiKey(self):
        self.console.print("[yellow] Edit Key")
        self.console.print(f" [green]The current HAWQS API Key is:[/] [cyan]{self.hawqsTests.getKey()}")
        self.console.print(f" [green]Enter a new Key, ([white]r[/])eset to reset to the default, or ([white]e[/])xit to cancel")
        newKey = Prompt.ask(" >")
        if newKey.lower() == "exit" or newKey.lower() == "e":
            self.console.print(f" [yellow]Edit Key cancelled")
        elif newKey.lower() == "reset" or newKey.lower() == "r":
            self.hawqsTests.restoreDefaultKey()
            self.console.print(f' [green]API Key reset to default: [cyan]{self.hawqsTests.getKey()}')
        else:
            self.hawqsTests.setKey(newKey)
            self.hmsTests.setKey(newKey)
            self.console.print(f' [green]API Key updated to: [cyan]{self.hawqsTests.getKey()}')
            
        self.console.print()

    def welcome(self):
        self.console.print("\n\n\n\n\n")

        #  _____ _____ _____   _ _____ _____ _ _ _ _____ _____    _____ _____ _____ 
        # |  |  |     |   __| / |  |  |  _  | | | |     |   __|  |  _  |  _  |     |
        # |     | | | |__   |/ /|     |     | | | |  |  |__   |  |     |   __|-   -|
        # |__|__|_|_|_|_____|_/ |__|__|__|__|_____|__  _|_____|  |__|__|__|  |_____|
        #                                            |__|                           
        asciiString = f"[white] _____ _____ _____   _ _____ _____ _ _ _ _____ _____    _____ _____ _____ \n" + \
                    f"[bright_yellow]|  |  |     |   __| / |  |  |  _  | | | |     |   __|  |  _  |  _  |     |\n" + \
                    f"[bright_cyan]|     | | | |__   |/ /|     |     | | | |  |  |__   |  |     |   __|-   -|\n" + \
                    f"[bright_blue]|__|__|_|_|_|_____|_/ |__|__|__|__|_____|__  _|_____|  |__|__|__|  |_____|\n" + \
                    f"[blue]                |__|                           "
        self.console.print(Panel.fit(asciiString), justify='center', style='red')

        self.console.print("[bright_cyan]HMS[/]/[red]HAWQS[/] Web API test application", justify="center")
        self.showMenu()

    def exitApplication(self):
        self.console.print("exiting [italic red]HAWQS[/italic red] Web API test application", justify="center")
        exit()

if __name__ == "__main__":
    hawqsTest = HAWQSTestClient()
    hawqsTest.welcome()