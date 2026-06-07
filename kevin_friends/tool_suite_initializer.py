from datetime import datetime
import json
import os
import re
import subprocess
import time
import threading
from .utils import Utils, Shell_Colors

class ToolSuiteInitializer:

    def __init__(self, DEBUG, CLEAN, IP: str, COMMON_NAME: str, HOST_NAME: str, UDP_SCAN, WORKSPACE_PATH: str, VPN_PATH: str, ALIAS: str):
        self.colors = Shell_Colors()
        self.DEBUG = DEBUG
        self.CLEAN = CLEAN
        self.IP = IP
        self.COMMON_NAME = COMMON_NAME
        self.HOST_NAME = HOST_NAME
        self.UDP_SCAN = UDP_SCAN
        self.WORKSPACE_PATH = os.path.expanduser(WORKSPACE_PATH) if WORKSPACE_PATH else None
        self.VPN_PATH = os.path.expanduser(VPN_PATH) if VPN_PATH else None
        
        # TODO only open vpn and wireguard supported for now ;)
        if self.VPN_PATH.split('.')[-1] == 'ovpn':
            self.VPN = 'OPENVPN'
        else:
            self.VPN = 'WG'

        self.ALIAS = os.path.expanduser(ALIAS) if ALIAS else None
        self.PATH = os.path.abspath(__file__)
        self.CHEATSHEET_FOLDER = os.path.abspath(path='.assets/EH_CHEATSHEETS')

        self.extract_settings()
    

    def extract_settings(self):
        config_labels = { 'user_settings': ['theme', 'seclist_path', 'dirbuster', 'dirb'],
                         'functional_settings': {
                            'gobuster': ['gobuster_thread', 'fuzz_mode', 'dir_wordlist', 'vhost_wordlist']
                        }
                    }
        try:
            with open(file='.assets/config.json', mode='r') as config_file:
                config_file = json.load(config_file)
                self.THEME = config_file['user_settings'][config_labels['user_settings'][0]]
                self.SECLIST_PATH = config_file['user_settings'][config_labels['user_settings'][1]]
                self.DIRBUSTER_PATH = config_file['user_settings'][config_labels['user_settings'][2]]
                self.DIRB_PATH = config_file['user_settings'][config_labels['user_settings'][3]]
                self.GOBUSTER_THREAD_NUMBER = int(config_file['functional_settings']['gobuster'][config_labels['functional_settings']['gobuster'][0]])
                self.GOBUSTER_FUZZ_MODE = int(config_file['functional_settings']['gobuster'][config_labels['functional_settings']['gobuster'][1]])
                self.GOBUSTER_DIR_WORDLIST = config_file['functional_settings']['gobuster'][config_labels['functional_settings']['gobuster'][2]]
                self.GOBUSTER_VHOST_WORDLIST = config_file['functional_settings']['gobuster'][config_labels['functional_settings']['gobuster'][3]]

                self.log_actions(f'[SETTINGS] Theme Color: {self.THEME}')
                self.log_actions(f'[SETTINGS] Seclist\'s Path: {self.SECLIST_PATH}')
                self.log_actions(f'[SETTINGS] Dirbuster\'s Path: {self.DIRBUSTER_PATH}')
                self.log_actions(f'[SETTINGS] Dirb\'s Path: {self.DIRB_PATH}')
                self.log_actions(f'[SETTINGS] Gobuster\'s thread number: {self.GOBUSTER_THREAD_NUMBER}')
                self.log_actions(f'[SETTINGS] Gobuster fuzz mode: {self.GOBUSTER_FUZZ_MODE}')
                self.log_actions(f'[SETTINGS] Gobuster dir wordlist: {self.GOBUSTER_DIR_WORDLIST}')
                self.log_actions(f'[SETTINGS] Gobuster vhost wordlist: {self.GOBUSTER_VHOST_WORDLIST}')

        except Exception as e:
            message = f'[CRITICAL] Error: config file not found or some config is missing!\nMandatory configs: {config_labels}'
            print(self.colors.red(message))
            self.log_actions(f'{message}\n{e}')
            raise RuntimeError(self.colors.red(message))


    def log_actions(self, message: str):
        if self.CLEAN and self.DEBUG:
            with open (file=f'logs/logs_{datetime.now().strftime("%d%m%Y")}.log', mode='w') as log_file:
                log_file.write(f'{datetime.now().strftime("%H:%M:%S")} |---> {message}\n')
                self.CLEAN = False
        elif not self.CLEAN and self.DEBUG:
            with open (file=f'logs/logs_{datetime.now().strftime("%d%m%Y")}.log', mode='a') as log_file:
                log_file.write(f'{datetime.now().strftime("%H:%M:%S")} |---> {message}\n')
        else:
            return

    def setup_workspace(self) -> bool:
        touch_info_file = f'touch {self.WORKSPACE_PATH}/info.json' 
        touch_frank_file = f'touch {self.WORKSPACE_PATH}/frank_says.txt' 
        mkdir_nmap = f'mkdir -p {self.WORKSPACE_PATH}/nmap'
        mkdir_gobuster = f'mkdir -p {self.WORKSPACE_PATH}/gobuster'
        mkdir_notes_creds_logs = f'mkdir -p {self.WORKSPACE_PATH}/notes/creds {self.WORKSPACE_PATH}/notes/logs'
        
        subprocess.run(
                    touch_info_file,
                    shell = True, 
                    capture_output = True, 
                    check = False
                )
        self.log_actions('[+] Successfully created info.json')
        self.INFO_FILE = f'{self.WORKSPACE_PATH}/info.json'

        subprocess.run(
                    touch_frank_file,
                    shell = True, 
                    capture_output = True, 
                    check = False
                )
        self.log_actions('[+] Successfully created frank_says.txt')
        self.FRANK_FILE = f'{self.WORKSPACE_PATH}/frank_says.txt'

        try:
            if not os.path.exists(f'{self.WORKSPACE_PATH}/nmap'):
                subprocess.run(
                    mkdir_nmap,
                    shell = True, 
                    capture_output = True, 
                    check = True
                )
                self.log_actions('[+] Successfully created nmap dir')
            self.NMAP_PATH = f'{self.WORKSPACE_PATH}/nmap'
        except Exception as e:
            raise RuntimeError(self.colors.red('[-] Error while creating nmap dir'))
            return False
        
        try:
            if not os.path.exists(f'{self.WORKSPACE_PATH}/gobuster'):
                subprocess.run(
                    mkdir_gobuster,
                    shell = True, 
                    capture_output = True, 
                    check = True
                )
                self.log_actions('[+] Successfully created gobuster dir')
            self.GOBUSTER_PATH = f'{self.WORKSPACE_PATH}/gobuster'
        except Exception as e:
            raise RuntimeError(self.colors.red('[-] Error while creating gobuster dir'))
            return False
        
        try:
            if not os.path.exists(f'{self.WORKSPACE_PATH}/notes'): 
                subprocess.run(
                    mkdir_notes_creds_logs,
                    shell = True, 
                    capture_output = True, 
                    check = True
                )
                self.NOTES_PATH = f'{self.WORKSPACE_PATH}/notes'
                self.CREDS_PATH = f'{self.WORKSPACE_PATH}/notes/creds'
                self.LOGS_PATH = f'{self.WORKSPACE_PATH}/notes/logs'
                self.log_actions('[+] Successfully created notes, creds and logs dirs')
            self.GOBUSTER_PATH = f'{self.WORKSPACE_PATH}/gobuster'
        except Exception as e:
            raise RuntimeError(self.colors.red('[-] Error while creating notes and nested dirs'))
            return False
        return True


    def take_note(self, data: dict = None):
        if not data:
            message = '[NOTE INFO] Cannot process empty informations'
            print(self.colors.red(message))
            self.log_actions(message)
            return

        try:
            with open(self.INFO_FILE, 'r') as info_file:
                informations = json.load(info_file)
        except (FileNotFoundError, json.JSONDecodeError):
            informations = {}

        try:
            for key, value in data.items():
                informations[key] = value

            with open(self.INFO_FILE, 'w') as info_file:
                json.dump(informations, info_file, indent=4)
        except Exception as e:
            message = f'[NOTE INFO] Error: {e}'
            self.log_actions(message)
            raise RuntimeError(self.colors.red(message))


    def get_info(self, info: str = None):
        if not info:
            return None

        try:
            with open(self.INFO_FILE, 'r') as info_file:
                informations = json.load(info_file)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            message = f'[INFO GETTER] Invalid or missing info file: {e}'
            print(self.colors.red(message))
            self.log_actions(message)
            return None

        if info not in informations:
            message = f'[INFO GETTER] Key "{info}" not found in info file'
            print(self.colors.red(message))
            self.log_actions(message)
            return None

        return informations[info]


    def alias(self) -> bool:
        if self.ALIAS:
            self.log_actions(message=f'[INFO] Creating alias in {self.ALIAS}')
            try:
                with open (file=self.ALIAS, mode='a') as config_file:
                    alias_cmd = f"\n# EH-Toolsuite's Alias\nalias kevin='python3 \"{self.PATH}\"'\n"
                    config_file.write(alias_cmd)
                    self.log_actions(f"[+] Added alias to {self.ALIAS}")
                return True
            except Exception as e:
                self.log_actions(f"[-] Error while saving alias: {e}")
                return False

    def keep_sudo_alive(self):
        '''
        This function keeps alive sudo util the tool is running
        '''
        def refresh():
            while True:
                result = subprocess.run('sudo -v', shell=True, capture_output=True)
                if result.returncode != 0:
                    self.log_actions('[VPN] sudo -v refresh failed!')
                time.sleep(60)

        t = threading.Thread(target=refresh, daemon=True)
        t.start()

    def add_to_hosts(self, ip = None, common_name = None, host_name = None) -> bool:
        if not host_name:
            message = '[HOSTS FILE WRITER] Host Name is mandatory!'
            self.log_actions(message)
            raise RuntimeError(self.colors.red(message))
        if not ip:
            ip = self.IP
        self.log_actions(message=f'[HOSTS FILE WRITER] IP: {ip} COMMON NAME: {common_name if common_name else "---"} HOST NAME: {host_name}')
        try:
            path = '/etc/hosts'
            hsots_config = f"\n#@@@@@begin-eh-toolsuite@@@@@\n# Configurations for {host_name} (auto-added by eh-toolsuite)\n{ip} {common_name if common_name else host_name} {host_name if common_name else ''}\n#@@@@@end-eh-toolsuite@@@@@"
            
            cmd = f"sudo tee -a {path} > /dev/null"
            process = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE, text=True)
            process.communicate(input=hsots_config)
            
            self.log_actions(f"[+] Host added to {path}")
            return True
        except Exception as e:
            self.log_actions(f"[-] Error while saving host configuration: {e}")
            return False

    def turn_on_vpn(self) -> bool:
        self.log_actions(f'[VPN] VPS type: {self.VPN}')
        if self.VPN == 'OPENVPN':
            cmd = ['sudo', 'openvpn', '--config', self.VPN_PATH]
        else:
            cmd = ['sudo', 'wg-quick', 'up', self.VPN_PATH]

        self.vpn_process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,                
            bufsize=1 # pop out the row when it comes
        )
        try:
            response = self._wait_for_vpn()
            return response
        except Exception as e:
            return False

    def _wait_for_vpn(self) -> bool:
        print(self.colors.yellow('[*] Waiting for VPN connection...'))
        if self.VPN == 'OPENVPN':
            for line in iter(self.vpn_process.stdout.readline, ''): 
                self.log_actions(f'[VPN] {line.strip()}')
                if 'Initialization Sequence Completed' in line:
                    print(self.colors.green('[+] VPN connected!'))
                    return True
            
            # Fallback if you are lucky
            timeout = 30
            for attempt in range(timeout):
                result = subprocess.run(
                    ['ping', '-c', '1', '-W', '1', self.IP],
                    capture_output=True
                )
                if result.returncode == 0:
                    self.log_actions(f'[+] VPN connected! (after {attempt+1}s)')
                    return True
                time.sleep(1)
            
            self.log_actions(f'[-] VPN unreachable after {timeout}s')
            message = '[-] Failed connection to VPN'
            self.log_actions(message)
            raise RuntimeError(self.colors.red(message))
        else:
            time.sleep(2)
            message = '[+] VPN connected!' 
            self.log_actions(message)
            print(self.colors.green(message))
            return True


    def turn_off_vpn(self):
        if self.vpn_process:
            self.vpn_process.terminate()
            self.vpn_process.wait()
            self.vpn_process = None


    def test_connection(self) -> bool:
        cmd = f"ping -c 4 '{self.HOST_NAME}'"
        response = subprocess.run(
            cmd, 
            shell = True, 
            capture_output = True, 
            check = False
        )
        output = response.stdout.decode()
        if '4 received' not in output:
            self.log_actions(f'[TEST CONNECTION] {output}')
            raise RuntimeError(self.colors.red(f'[+] Host {self.HOST_NAME} is unreachable! Aborting...'))
        else:
            self.log_actions(f'[TEST CONNECTION] {output}')
            print(self.colors.green(f'[+] Host {self.HOST_NAME} successfully reached!'))
            return True


    def clean_hosts(self):
        self.log_actions(message=f'[HOSTS FILE CLEANER] HOST NAME: {self.HOST_NAME}')
        try:
            path = '/etc/hosts'
            
            result = subprocess.run(
                f"sudo cat {path}",
                shell=True,
                capture_output=True,
                text=True,
                check=True
            )
            lines = result.stdout.splitlines(keepends=True)
            
            new_lines = []
            skip = False
            
            for line in lines:
                if '#@@@@@begin-eh-toolsuite@@@@@' in line:
                    skip = True
                elif '#@@@@@end-eh-toolsuite@@@@@' in line:
                    skip = False
                    continue
                elif not skip:
                    new_lines.append(line)
            
            cmd = f"sudo tee {path} > /dev/null"
            process = subprocess.Popen(
                cmd, 
                shell = True, 
                stdin = subprocess.PIPE, 
                text = True
            )
            process.communicate(input=''.join(new_lines))
            
            self.log_actions(f"[+] Host removed from {path}")
        except Exception as e:
            self.log_actions(f"[-] Error while removing host configuration: {e}")


    def call_nmap(self):

        def parse_open_ports(nmap_file: str) -> str:
            with open(nmap_file, 'r') as f:
                lines = f.readlines()

            ports = []
            for line in lines:
                match = re.match(r'^(\d+)/tcp\s+open', line)
                if match:
                    ports.append(match.group(1))

            return ','.join(ports)
        
        def detect_OS():
            print(self.colors.yellow('Detecting OS...'))
            detect_OS_cmd = f'sudo nmap -O --osscan-guess {self.IP}'
            response = subprocess.run(
                detect_OS_cmd,
                shell=True,
                capture_output=True,
                text=True,
                check=True
            ) 

            output = response.stdout
            if 'Linux' in output:
                OS = 'Linux'
            elif 'Windows' in output:
                OS = 'Windows'
            else:
                OS = 'Exotic_Banana' # TODO Not supported yet!
            
            message = f'Machine OS: {OS}'
            print(self.colors.green(f' [+] {message}'))
            self.log_actions(f'[NMAP] {message}')
            return OS

        utils = Utils()
        self.log_actions('[NMAP] Starting nmap routine...')

        full_port_path = f'{self.NMAP_PATH}/allports.txt'
        full_port_cmd = f'sudo nmap -p- --min-rate 5000 -T4 -oN {full_port_path} {self.IP}'

        print(self.colors.yellow('Waiting for full port scanning...'))
        utils.run_with_spinner(name='Full port scan', cmd=full_port_cmd, shell=True)
        '''
        subprocess.run(
            full_port_cmd,
            shell=True,
            capture_output=True,
            text=True,
            check=True
        )        
        '''

        ports = parse_open_ports(full_port_path)
        print(self.colors.yellow(f'Active ports: {ports.replace(',',', ')}'))
        self.log_actions(f'[NMAP] Full scan done, active ports: {ports.replace(',',', ')}')
        self.take_note(data={utils.active_ports_KEY(): ports.split(',')})

        detailed_scan_path = f'{self.NMAP_PATH}/detailded'
        detailed_scan_cmd = f'sudo nmap -sV -sC -O -p{ports} -oA {detailed_scan_path} {self.IP}'

        print(self.colors.yellow('Scanning active ports...'))
        utils.run_with_spinner(name='Active ports scan', cmd=detailed_scan_cmd, shell=True)
        '''
        subprocess.run(
            detailed_scan_cmd,
            shell=True,
            capture_output=True,
            text=True,
            check=True
        )   
        '''
        self.log_actions('[NMAP] Detailed scan done!')

        if self.UDP_SCAN:
            udp_scan_path = f'{self.NMAP_PATH}/udp_scan.txt'
            udp_scan_cmd = f'sudo nmap -sU --top-ports 100 -oN {udp_scan_path} {self.IP}'
            print(self.colors.yellow('Waiting for UDP scanning...'))
            utils.run_with_spinner(name='UDP ports scan', cmd=udp_scan_cmd, shell=True)
            '''
            subprocess.run(
                udp_scan_cmd,
                shell=True,
                capture_output=True,
                text=True,
                check=True
            )
            '''   
            self.log_actions('[NMAP] UDP scan done!')

        self.OS = detect_OS()
        self.take_note(data={utils.machine_OS_KEY(): self.OS})


    def setup(self):
        try: 
            setup = self.setup_workspace()
            alias = self.alias()
            print(self.colors.blue('Kevin need your password to modify hosts file!'))
            subprocess.run('sudo -v', shell=True, check=True)  
            self.keep_sudo_alive()
            
            hosts = self.add_to_hosts(self.IP, self.COMMON_NAME, self.HOST_NAME)
            vpn = self.turn_on_vpn()
            connection = self.test_connection()
            return setup and alias and hosts and vpn and connection
        except Exception as e:
            print(self.colors.red(e))  
            return False 