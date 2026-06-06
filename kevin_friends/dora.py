from .colors import Shell_Colors
from .tool_suite_initializer import ToolSuiteInitializer
import subprocess

class Dora:

    def __init__(self, tool_suite: ToolSuiteInitializer):
        self.colors = Shell_Colors()
        if not tool_suite:
            print(self.colors.red('Cannot call Dora with None configs!'))
            exit(1)
        self.TOOL = tool_suite
        self.THREAD_NUMBER = tool_suite.GOBUSTER_THREAD_NUMBER

    
    def get_exclude_length(self, url: str, mode: str = 'dir', samples: int = 5) -> str:
        if not url:
            message = 'Dora cannot handle null url, exiting...'
            print(self.colors.red(message))
            self.TOOL.log_actions(f'[DORA]: {message} -> get_exclude_length')
            exit(1)
            
        import requests

        lengths = set()
        for _ in range(samples):
            try:
                if mode == 'dir':
                    r = requests.get(f'{url}/aaaaaaaaaaaaaaa123xyz', allow_redirects=False)
                elif mode == 'vhost':
                    r = requests.get(url, headers={'Host': f'aaaaaaaaaaaaaaa123.{self.TOOL.HOST_NAME}'}, allow_redirects=False)
                lengths.add(len(r.content))
            except requests.exceptions.ConnectionError:
                print(self.colors.red(f'[-] Cannot reach {url}'))
                self.TOOL.log_actions(f'[DORA] Connection refused on {url}')
                return '0'  

        result = ','.join(str(l) for l in lengths)
        self.TOOL.log_actions(f'[GOBUSTER] Exclude lengths ({mode}): {result}')
        return result

    def go_bastard(self):
        target = self.TOOL.HOST_NAME
        url = f'http://{target}'
        output_dir = self.TOOL.GOBUSTER_PATH

        exclude_dir   = self.get_exclude_length(url=url, mode='dir')
        exclude_vhost = self.get_exclude_length(url=url, mode='vhost')

        commands = {
            'dir': f'gobuster dir -u {url} -w /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt -x php,html,txt,bak -t {self.TOOL.GOBUSTER_THREAD_NUMBER} --exclude-length {exclude_dir} -o {output_dir}/dir_out.txt',
            'vhost': f'gobuster vhost -u {url} -w /usr/share/wordlists/seclists/Discovery/DNS/subdomains-top1million-110000.txt --append-domain -t {self.TOOL.GOBUSTER_THREAD_NUMBER} --exclude-length {exclude_vhost} -o {output_dir}/vhost_out.txt', 
            'dns': f'gobuster dns -d {target} -w /usr/share/wordlists/seclists/Discovery/DNS/subdomains-top1million-110000.txt --show-ips --no-error -t {self.TOOL.GOBUSTER_THREAD_NUMBER} -o {output_dir}/dns_out.txt',
        }
        if self.TOOL.GOBUSTER_FUZZ_MODE == 1:
            commands['fuzz'] = f'gobuster fuzz -u "{url}/FUZZ" -w /usr/share/wordlists/seclists/Discovery/Web-Content/common.txt --exclude-length 0 -t {self.TOOL.GOBUSTER_THREAD_NUMBER} -o {output_dir}/fuzz_out.txt'

        processes = []
        for name, cmd in commands.items():
            message = f'[*] Starting gobuster {name}...'
            print(self.colors.yellow(message))
            self.TOOL.log_actions(message)
            proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            processes.append((name, proc))
            self.TOOL.log_actions(f'[DORA - GOBASTARD] Launched {name}')

        for name, proc in processes:
            proc.wait()
            message = f'{name} completed successfully!'
            print(self.colors.green(f'[+] {message}'))
            self.TOOL.log_actions(f'[DORA - GOBASTARD] {message}')