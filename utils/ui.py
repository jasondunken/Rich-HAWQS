from time import sleep

from rich.panel import Panel
from rich.json import JSON

def alert(console, message, delay=3):
    console.print(Panel(message), style='red')
    sleep(delay)

def showResponse(console, response, status):
    console.print(Panel(JSON(response)))
    console.print(Panel(f"[green] Request Status:[/] {status}"))