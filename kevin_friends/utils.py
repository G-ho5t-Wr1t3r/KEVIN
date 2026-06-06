from .colors import Shell_Colors
from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn
import shlex
import subprocess
import time

class Utils:

    def __init__(self):
        self.colors = Shell_Colors()

    def run_with_spinner(self, name: str, cmd: str):

        proc = subprocess.Popen(
            shlex.split(cmd),
            shell=False,
            stdout=subprocess.DEVNULL,  
            stderr=subprocess.DEVNULL   
        )

        with Progress(
            SpinnerColumn(),
            TextColumn(f'[green]Process {name}...'),
            TimeElapsedColumn()
        ) as progress:
            task = progress.add_task(name)
            while proc.poll() is None:
                progress.advance(task)
                time.sleep(0.1)

        return proc