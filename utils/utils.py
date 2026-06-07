from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn
from rich.live import Live
from rich.text import Text
import shlex
import subprocess
import time

class Shell_Colors:

    def __init__(self):
        self.RED = '\033[91m' 
        self.GREEN = '\033[92m'
        self.YELLOW = '\033[93m'
        self.BLUE = '\033[94m'
        self.RESET = '\033[0m'

    def red(self, msg:str):
        return f'{self.RED}{msg}{self.RESET}'

    def green(self, msg:str):
        return f'{self.GREEN}{msg}{self.RESET}'

    def yellow(self, msg:str):
        return f'{self.YELLOW}{msg}{self.RESET}'

    def blue(self, msg:str):
        return f'{self.BLUE}{msg}{self.RESET}'

    def reset(self, msg:str):
        return f'{self.RESET}'

class Utils:

    def __init__(self):
        self.colors = Shell_Colors()
    
    def run_with_spinner(self, name: str, cmd: str, shell: bool = False):

        proc = subprocess.Popen(
            cmd if shell else shlex.split(cmd),
            shell=shell,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        start = time.time()

        with Live(refresh_per_second=10) as live:
            while proc.poll() is None:
                elapsed = time.time() - start
                mins = int(elapsed // 60)
                secs = int(elapsed % 60)
                live.update(Text(f' [*] Process {name}... {mins:02d}:{secs:02d}', style='yellow'))
                time.sleep(0.1)

        elapsed = time.time() - start
        mins = int(elapsed // 60)
        secs = int(elapsed % 60)
        print(self.colors.green(f' [+] {name} completed in {mins:02d}:{secs:02d}'))
        return proc

    def ip_KEY(self):
        return 'ip'
    
    def common_name_KEY(self):
        return 'common_name' 
    
    def host_name_KEY(self):
        return 'host_name'

    def active_ports_KEY(self):
        return 'active_ports'

    def machine_OS_KEY(self):
        return 'machine_OS'
    
    def machine_vhosts(self):
        return 'machine_vhosts'