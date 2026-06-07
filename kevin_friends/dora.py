from utils.tool_suite_initializer import ToolSuiteInitializer
from utils.utils import Utils, Shell_Colors
import re

class Dora:

    def __init__(self, tool_suite: ToolSuiteInitializer):
        self.colors = Shell_Colors()
        if not tool_suite:
            raise RuntimeError(self.colors.red('Cannot call Dora with None configs!'))
        self.TOOL = tool_suite
        self.THREAD_NUMBER = tool_suite.GOBUSTER_THREAD_NUMBER

    
    def get_exclude_length(self, url: str, mode: str = 'dir', samples: int = 5) -> str:
        if not url:
            message = 'Dora cannot handle null url, exiting...'
            print(self.colors.red(message))
            self.TOOL.log_actions(f'[DORA]: {message} -> get_exclude_length')
            raise RuntimeError(self.colors.red(message))
            
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

    def parse_vhost_output(self) -> list[str]:
        vhost_file = f'{self.TOOL.GOBUSTER_PATH}/vhost_out.txt'
        found = []

        try:
            with open(vhost_file, 'r') as f:
                for line in f:
                    # Match "Found: <vhost> Status: ..."
                    match = re.match(r'^Found:\s+(\S+)\s+Status:', line)
                    if match:
                        found.append(match.group(1))
            message = f'[DORA] {len(found)} vhost found!'
            self.TOOL.log_actions(message)
            print(self.colors.green(message))
            message = f'[DORA] URLs: {' - '.join(found)}'
            self.TOOL.log_actions(message)
            print(self.colors.green(message))
        except FileNotFoundError:
            message = '[DORA] vhost_out.txt not found!'
            self.TOOL.log_actions(message)
            print(self.colors.red(message))
            raise RuntimeError(self.colors.red(message))

        return found

    def go_bastard(self, dora_opt):
        utils = Utils()
        try:
            target = self.TOOL.HOST_NAME
            url = f'http://{target}'
            output_dir = self.TOOL.GOBUSTER_PATH

            exclude_dir   = self.get_exclude_length(url=url, mode='dir')
            exclude_vhost = self.get_exclude_length(url=url, mode='vhost')

            commands = {}

            if 'd' in dora_opt:
                commands['dir'] = f'gobuster dir -u {url} -w {self.TOOL.GOBUSTER_DIR_WORDLIST} -x php,html,txt,bak -t {self.TOOL.GOBUSTER_THREAD_NUMBER} --exclude-length {exclude_dir} -o {output_dir}/dir_out.txt'
            if 'v' in dora_opt:
                commands['vhost'] = f'gobuster vhost -u {url} -w {self.TOOL.GOBUSTER_VHOST_WORDLIST} --append-domain -t {self.TOOL.GOBUSTER_THREAD_NUMBER} --exclude-length {exclude_vhost} -o {output_dir}/vhost_out.txt'
            if 'f' in dora_opt:
                commands['fuzz'] = f'gobuster fuzz -u "{url}/FUZZ" -w {self.TOOL.SECLIST_PATH}/Discovery/Web-Content/common.txt --exclude-length 0 -t {self.TOOL.GOBUSTER_THREAD_NUMBER} -o {output_dir}/fuzz_out.txt'

            # TODO ATTUALMENTE DNS TROPPO LENTO ---> 'dns': f'gobuster dns -d {target} -w {self.TOOL.SECLIST_PATH}/Discovery/DNS/subdomains-top1million-110000.txt --wildcard --show-ips --no-error -t {self.TOOL.GOBUSTER_THREAD_NUMBER} -o {output_dir}/dns_out.txt'

            message = '[GO_BASTARD] Starting Gobuster\'s processes'
            print(self.colors.yellow(message))
            self.TOOL.log_actions(message)

            for name, cmd in commands.items():
                self.TOOL.log_actions(f'[DORA] Launching gobuster {name}')
                msg_name = f'[GO_BASTARD] Executing gobuster {name}'
                utils.run_with_spinner(name=msg_name, cmd=cmd)
                self.TOOL.log_actions(f'[DORA] gobuster {name} done')
        except Exception as e:
            message = f'[DORA] An error occurred {e}'
            print(self.colors.red(message))
            self.TOOL.log_actions(message)
            raise RuntimeError(self.colors.red(message))
        
        found_vhost = self.parse_vhost_output()
        found_dirs = [] #TODO self.parse_dirs_output()
        self.TOOL.take_note(data={utils.machine_vhosts(): found_vhost})
        self.TOOL.take_note(data={utils.machine_dirs(): found_dirs})
        print(self.colors.blue('Kevin need your password to modify hosts file!'))
        for url in found_vhost:
            self.TOOL.add_to_hosts(host_name=url)