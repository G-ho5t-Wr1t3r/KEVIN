#!/usr/bin/env python3

import argparse
from datetime import datetime
import json
import os
import re
import subprocess
import time

RED = '\033[91m' 
GREEN = '\033[92m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def red(msg:str):
    return f'{RED}{msg}{RESET}'

def green(msg:str):
    return f'{GREEN}{msg}{RESET}'

def yellow(msg:str):
    return f'{YELLOW}{msg}{RESET}'

def blue(msg:str):
    return f'{BLUE}{msg}{RESET}'

def reset(msg:str):
    return f'{RESET}'

class ToolSuiteInitializer:

    def __init__(self, DEBUG, CLEAN, IP: str, COMMON_NAME: str, HOST_NAME: str, WORKSPACE_PATH: str, VPN_PATH: str, ALIAS: str):
        self.DEBUG = DEBUG
        self.CLEAN = CLEAN
        self.IP = IP
        self.COMMON_NAME = COMMON_NAME
        self.HOST_NAME = HOST_NAME
        self.WORKSPACE_PATH = os.path.expanduser(WORKSPACE_PATH) if WORKSPACE_PATH else None
        self.VPN_PATH = os.path.expanduser(VPN_PATH) if VPN_PATH else None
        
        # TODO only open vpn and wireguard supported for now ;)
        if self.VPN_PATH.split('.')[-1] == 'ovpn':
            self.VPN = 'OPENVPN'
        else:
            self.VPN = 'WG'

        self.ALIAS = os.path.expanduser(ALIAS) if ALIAS else None
        self.PATH = os.path.abspath(__file__)

        self.extract_settings()
    
    def print_banner(self):
        try:
            with open(file='.assets/ascii_art.txt', mode='r') as banner_file:
                banner = banner_file.read()
                print(red(banner))
        except Exception as e:
            print(red('=== KEVIN (offensive toolsuite) === '))

    def extract_settings(self):
        config_labels = ['user_settings', 'theme', 'seclist_path']
        try:
            with open(file='.assets/config.json', mode='r') as config_file:
                config_file = json.load(config_file)
                self.THEME = config_file[config_labels[0]][config_labels[1]]
                self.SECLIST_PATH = config_file[config_labels[0]][config_labels[2]]
                self.log_actions(f'[SETTINGS] Theme Color: {self.THEME}')
                self.log_actions(f'[SETTINGS] Seclist\'s Path: {self.SECLIST_PATH}')
        except Exception as e:
            message = f'[CRITICAL] Error: config file not found or some config is missing!\nMandatory configs: {config_labels}'
            print(red(message))
            self.log_actions(f'{message}\n{e}')
            exit(1)


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


    def setup_workspace(self):
        mkdir_nmap = f'mkdir -p {self.WORKSPACE_PATH}/nmap'
        mkdir_gobuster = f'mkdir -p {self.WORKSPACE_PATH}/gobuster'
        mkdir_notes_creds_logs = f'mkdir -p {self.WORKSPACE_PATH}/notes/creds {self.WORKSPACE_PATH}/notes/logs'
        
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
            print(red('[-] Error while creating nmap dir'))
            exit(1)

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
            print(red('[-] Error while creating gobuster dir'))
            exit(1)

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
            print(red('[-] Error while creating notes and nested dirs'))
            exit(1)


    def alias(self):
        if self.ALIAS:
            self.log_actions(message=f'[INFO] Creating alias in {self.ALIAS}')
            try:
                with open (file=self.ALIAS, mode='a') as config_file:
                    alias_cmd = f"\n# EH-Toolsuite's Alias\nalias kevin='python3 \"{self.PATH}\"'\n"
                    config_file.write(alias_cmd)
                    self.log_actions(f"[+] Added alias to {self.ALIAS}")
            except Exception as e:
                self.log_actions(f"[-] Error while saving alias: {e}")


    def add_to_hosts(self):
        self.log_actions(message=f'[NEW_MACHINE] IP: {self.IP} COMMON NAME: {self.COMMON_NAME} HOST NAME: {self.HOST_NAME}')
        try:
            path = '/etc/hosts'
            hsots_config = f"\n#@@@@@begin-eh-toolsuite@@@@@\n# Configurations for {self.HOST_NAME} (auto-added by eh-toolsuite)\n{self.IP} {self.COMMON_NAME if self.COMMON_NAME else self.HOST_NAME} {self.HOST_NAME if self.COMMON_NAME else ''}\n#@@@@@end-eh-toolsuite@@@@@"
            
            cmd = f"sudo tee -a {path} > /dev/null"
            process = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE, text=True)
            process.communicate(input=hsots_config)
            
            self.log_actions(f"[+] Host added to {path}")
        except Exception as e:
            self.log_actions(f"[-] Error while saving host configuration: {e}")


    def turn_on_vpn(self):
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
        self._wait_for_vpn()

    def _wait_for_vpn(self):
        print(yellow('[*] Waiting for VPN connection...'))
        if self.VPN == 'OPENVPN':
            for line in iter(self.vpn_process.stdout.readline, ''): 
                self.log_actions(f'[VPN] {line.strip()}')
                if 'Initialization Sequence Completed' in line:
                    print(green('[+] VPN connected!'))
                    return
            
            # Fallback if you are lucky
            timeout = 30
            for attempt in range(timeout):
                result = subprocess.run(
                    ['ping', '-c', '1', '-W', '1', self.IP],
                    capture_output=True
                )
                if result.returncode == 0:
                    self.log_actions(f'[+] VPN connected! (after {attempt+1}s)')
                    return
                time.sleep(1)
            
            self.log_actions(f'[-] VPN unreachable after {timeout}s')
            message = '[-] Failed connection to VPN'
            self.log_actions(message)
            print(red(message))
            exit(1)
        else:
            time.sleep(2)
            message = '[+] VPN connected!' 
            self.log_actions(message)
            print(green(message))


    def turn_off_vpn(self):
        if self.vpn_process:
            self.vpn_process.terminate()
            self.vpn_process.wait()
            self.vpn_process = None


    def test_connection(self):
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
            print(red(f'[+] Host {self.HOST_NAME} is unreachable! Aborting...'))
            exit(1)
        else:
            self.log_actions(f'[TEST CONNECTION] {output}')
            print(green(f'[+] Host {self.HOST_NAME} successfully reached!'))


    def clean_hosts(self):
        self.log_actions(message=f'[REMOVING_MACHINE] HOST NAME: {self.HOST_NAME}')
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
            print(yellow(message))
            self.log_actions(f'[NMAP] {message}')
            return OS


        self.log_actions('[NMAP] Starting nmap routine...')

        full_port_path = f'{self.NMAP_PATH}/allports.txt'
        full_port_cmd = f'sudo nmap -p- --min-rate 5000 -T4 -oN {full_port_path} {self.IP}'

        print(yellow('Waiting for full port scanning...'))
        subprocess.run(
            full_port_cmd,
            shell=True,
            capture_output=True,
            text=True,
            check=True
        )        

        ports = parse_open_ports(full_port_path)
        print(yellow(f'Active ports: {ports.replace(',',', ')}'))
        self.log_actions(f'[NMAP] Full scan done, active ports: {ports}')

        detailed_scan_path = f'{self.NMAP_PATH}/detailded'
        detailed_scan_cmd = f'sudo nmap -sV -sC -O -p{ports} -oA {detailed_scan_path} {self.IP}'

        print(yellow('Scanning active ports...'))
        subprocess.run(
            detailed_scan_cmd,
            shell=True,
            capture_output=True,
            text=True,
            check=True
        )   
        self.log_actions('[NMAP] Detailed scan done!')

        udp_scan_path = f'{self.NMAP_PATH}/udp_scan.txt'
        udp_scan_cmd = f'sudo nmap -sU --top-ports 100 -oN {udp_scan_path} {self.IP}'

        print(yellow('Waiting for UDP scanning...'))
        subprocess.run(
            udp_scan_cmd,
            shell=True,
            capture_output=True,
            text=True,
            check=True
        )   
        self.log_actions('[NMAP] UDP scan done!')

        self.OS = detect_OS()

        # TODO implementare azioni utili!


    def routine(self):
        try: 
            self.print_banner()

            # ==== SETUP ==== #
            self.setup_workspace()
            self.alias()
            self.add_to_hosts()
            self.turn_on_vpn()


            self.test_connection()
            self.call_nmap()
        except Exception as e:
            print(red(e))   
        finally:
            # ==== SETDOWN ==== #
            self.turn_off_vpn() # TODO togliere
            self.clean_hosts() # TODO togliere


def main():

    DEBUG = False

    parser = argparse.ArgumentParser(
        description="This program modifies your /etc/hosts file (appends <IP> <commonName> <hostName>)."
    )
    
    parser.add_argument(
        "--ip",
        type=str,
        required=True,
        help="Machine's IP"
    )
    parser.add_argument(
        "--common-name",
        type=str,
        required=False,
        help="Machine's Common Name"
    )
    parser.add_argument(
        "--host-name",
        type=str,
        required=True,
        help="Machine's Host Name"
    )
    parser.add_argument(
        "-d",
        action="store_true",
        help='Debug mode'
    )
    parser.add_argument(
        "--alias",
        type=str,
        required=False,
        help='Creates alias "kevin" in specified file'
    )
    parser.add_argument(
        "--workspace",
        type=str,
        required=True,
        help='Creates some management dirs at the specified path'
    )
    parser.add_argument(
        "--vpn",
        type=str,
        required=False,
        help='VPN\'s path'
    )
    parser.add_argument(
        "--clean-log",
        action="store_true",
        help='Overwrites the existing log file'
    )

    
    args = parser.parse_args()
    
    ip = args.ip
    common_name = args.common_name 
    host_name = args.host_name
    DEBUG = args.d
    alias_path = args.alias # es. --alias '~/.bashrc'
    workspace_path = args.workspace # es. --workspace '~/EH'
    vpn_path = args.vpn
    CLEAN = args.clean_log

    tool = ToolSuiteInitializer(DEBUG, CLEAN, ip, common_name, host_name, workspace_path, vpn_path, alias_path)
    tool.routine()

if __name__ == "__main__":
    main()
