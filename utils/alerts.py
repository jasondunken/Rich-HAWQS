from time import sleep

from rich.panel import Panel

def alert(console, message, delay=3):
    console.print(Panel(message), style='red')
    sleep(delay)