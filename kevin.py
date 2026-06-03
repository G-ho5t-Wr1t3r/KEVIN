#!/usr/bin/env python3

import argparse
from datetime import datetime
import os
import subprocess

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

class ToolSuite:

    def __init__(self, DEBUG, CLEAN, IP: str, COMMON_NAME: str, HOST_NAME: str, ALIAS: str):
        self.DEBUG = DEBUG
        self.CLEAN = CLEAN
        self.IP = IP
        self.COMMON_NAME = COMMON_NAME
        self.HOST_NAME = HOST_NAME
        self.ALIAS = os.path.expanduser(ALIAS) if ALIAS else None
        self.PATH = os.path.abspath(__file__)
    
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

    def test_connection(self):
        cmd = f"ping -c 4 '{self.HOST_NAME}'"
        response = subprocess.run(cmd, shell=True, capture_output=True, check=False)
        output = response.stdout.decode()
        if '4 received' not in output:
            self.log_actions(f'[TEST CONNECTION] {output}')
            print(red(f'Host {self.HOST_NAME} is unreachable! Aborting...'))
            exit(1)
        else:
            self.log_actions(f'[TEST CONNECTION] {output}')
            print(green(f'Host {self.HOST_NAME} successfully reached!'))

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
            process = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE, text=True)
            process.communicate(input=''.join(new_lines))
            
            self.log_actions(f"[+] Host removed from {path}")
        except Exception as e:
            self.log_actions(f"[-] Error while removing host configuration: {e}")


    def routine(self):
        self.alias()
        self.add_to_hosts()
        self.test_connection()
        self.clean_hosts()


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
        "--clean-log",
        action="store_true",
        help='Overwrites the existing log file'
    )

    
    args = parser.parse_args()
    
    ip = args.ip
    common_name = args.common_name 
    host_name = args.host_name
    DEBUG = args.d
    alias = args.alias # es. --alias '~/.bashrc'
    CLEAN = args.clean_log

    tool = ToolSuite(DEBUG, CLEAN, ip, common_name, host_name, alias)
    tool.routine()

if __name__ == "__main__":
    main()
