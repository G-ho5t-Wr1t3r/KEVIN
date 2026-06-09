#!/usr/bin/env python3

import argparse
from kevin_friends.dora import Dora
from kevin_friends.frank import Frank
from utils.utils import Shell_Colors
from utils.tool_suite_initializer import ToolSuiteInitializer
from pathlib import Path
import sys

def kevin():
    
    colors = Shell_Colors()
    kevin_path = Path(__file__).resolve().parent

    def print_banner():
        try:
            with open(file=f'{kevin_path}/.assets/ascii_art.txt', mode='r') as banner_file:
                banner = banner_file.read()
                print(colors.red(banner))
        except Exception as e:
            print(colors.red('=== KEVIN (offensive toolsuite) === '))

    def valid_dora_options(value: str) -> str:
        allowed = set('dvf')
        invalid = set(value) - allowed
        if invalid:
            raise argparse.ArgumentTypeError(
                f"Invalid options: {''.join(invalid)}. Valid options: d, v, f (mix them like 'dvf')"
            )
        return value
    
    def launch_gui():
        from GUI.pretty_kevin import launch_gui as start_gui
        start_gui(None)
    
    if len(sys.argv) == 1:
        launch_gui()
        return

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
        help="Machine's Host Name (e.g. name.htb)"
    )
    parser.add_argument(
        "--nmap",
        action="store_true",
        required=False,
        help='Runs nmap scan'
    )
    parser.add_argument(
        "--udp",
        action="store_true",
        required=False,
        help='Runs nmap udp scan'
    )
    parser.add_argument(
        "--dora",
        type=valid_dora_options,  
        required=False,
        help="To call Dora. Options: 'd' dir, 'v' vhost, 'f' fuzz (mix: 'dvf')"
    )
    parser.add_argument(
        "--frank",
        action="store_true",
        required=False,
        help='To raise Frank (the beast)'
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
        "--alias",
        type=str,
        required=False,
        help='Creates alias "kevin" in specified file'
    )
    parser.add_argument(
        "--gui",
        action="store_true",
        required=False,
        help="Opens Kevin's GUI"
    )
    parser.add_argument(
        "-d",
        action="store_true",
        required=False,
        help='Debug mode'
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
    udp_scan = args.udp
    nmap_scan = True #args.nmap
    dora_opt = args.dora
    raise_frank = args.frank
    alias_path = args.alias # es. --alias '~/.bashrc'
    workspace_path = args.workspace # es. --workspace '~/EH'
    vpn_path = args.vpn
    CLEAN = args.clean_log

    gui = args.gui # TODO gui senza setup

    if gui:
        from GUI.pretty_kevin import launch_gui as start_gui
        start_gui(args)
        return

    try:
        # ================================================================== #

        print_banner()

        tool_suite = ToolSuiteInitializer(
            DEBUG=DEBUG, 
            CLEAN=CLEAN, 
            base_path=kevin_path,
            IP=ip, 
            COMMON_NAME=common_name, 
            HOST_NAME=host_name, 
            UDP_SCAN=udp_scan,
            WORKSPACE_PATH=workspace_path, 
            VPN_PATH=vpn_path, 
            ALIAS=alias_path
        )
        setup = tool_suite.setup()
        if not setup: raise RuntimeError(colors.red('Something went wrong while setting-up the environment!'))
        if nmap_scan: tool_suite.call_nmap()
        
        if dora_opt:
            dora = Dora(
                tool_suite=tool_suite
            )
            
            dora.go_bastard(dora_opt)

        if raise_frank:
            frank = Frank(
                tool_suite=tool_suite
            )
            frank.enlight_me()

        # ================================================================== #
    except Exception as e:
        print('KEVIN ERROR')
        print(e)
    finally:
        close = False
        while not close:
            choice = str(input('Shut Down? (y/N) '))
            if choice.lower() == 'y':
                close = True
                print('Meow!    >^.^<')
                tool_suite.turn_off_vpn() 
                tool_suite.clean_hosts() 

if __name__ == "__main__":
    kevin()
