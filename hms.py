from time import sleep

from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt
from rich.json import JSON


class HMSTest:
    def __init__(self, console):
        self.console = console

    def test(self):
        self.console.print(Panel("test not implemented!"))
        sleep(3)