#!/usr/bin/env python3

import argparse
from kevin_friends.dora import Dora
from kevin_friends.utils import Shell_Colors
from kevin_friends.tool_suite_initializer import ToolSuiteInitializer

def kevin():
    
    colors = Shell_Colors()

    def print_banner():
        try:
            with open(file='.assets/ascii_art.txt', mode='r') as banner_file:
                banner = banner_file.read()
                print(colors.red(banner))
        except Exception as e:
            print(colors.red('=== KEVIN (offensive toolsuite) === '))

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
        "--udp",
        action="store_true",
        required=False,
        help='Runs nmap udp scan'
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
    parser.add_argument(
        "--alias",
        type=str,
        required=False,
        help='Creates alias "kevin" in specified file'
    )
    parser.add_argument(
        "-d",
        action="store_true",
        required=False,
        help='Debug mode'
    )

    
    args = parser.parse_args()
    
    ip = args.ip
    common_name = args.common_name 
    host_name = args.host_name
    DEBUG = args.d
    udp_scan = args.udp
    alias_path = args.alias # es. --alias '~/.bashrc'
    workspace_path = args.workspace # es. --workspace '~/EH'
    vpn_path = args.vpn
    CLEAN = args.clean_log

    try:
        # ================================================================== #

        print_banner()

        tool_suite = ToolSuiteInitializer(
            DEBUG=DEBUG, 
            CLEAN=CLEAN, 
            IP=ip, 
            COMMON_NAME=common_name, 
            HOST_NAME=host_name, 
            UDP_SCAN=udp_scan,
            WORKSPACE_PATH=workspace_path, 
            VPN_PATH=vpn_path, 
            ALIAS=alias_path
        )
        tool_suite.routine()
        
        dora = Dora(
            tool_suite=tool_suite
        )
        dora.go_bastard()

        # ================================================================== #
    except Exception as e:
        print(e)
    finally:
        import time
        timeout = 120
        print(f'You have {timeout}s before closing and cleaning files!')
        time.sleep(timeout)
        print('Adios    >^.^<')
        tool_suite.turn_off_vpn() # TODO togliere
        tool_suite.clean_hosts() # TODO togliere

if __name__ == "__main__":
    kevin()
