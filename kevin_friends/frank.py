from utils.tool_suite_initializer import ToolSuiteInitializer
from utils.utils import Utils, Shell_Colors
import os
import subprocess

class Frank:

    def __init__(self, tool_suite: ToolSuiteInitializer):
        self.utils = Utils()
        self.colors = Shell_Colors()
        if not tool_suite:
            raise RuntimeError(self.colors.red('Cannot rise Frank for nothing!'))
        self.TOOL = tool_suite
        self.PORTS = [int(port) for port in self.TOOL.get_info(self.utils.active_ports_KEY())]
        self.CHEATSHEETS = self.map_files()

    def map_files(self) -> dict:
        cheatsheet_folder = self.TOOL.CHEATSHEET_FOLDER
        result = {}

        for root, dirs, files in os.walk(cheatsheet_folder):
            for file in files:
                path = os.path.join(root, file)
                name_without_ext = os.path.splitext(file)[0]  
                result[name_without_ext] = path

        return result

    def label_ports(self) -> dict:

        PORT_MAP = {
            # ============ COMMON (Linux & Windows) ============
            21:    {'service': 'FTP',       'os': 'any',     'note': 'File Transfer — search for anonymous login',  'cheatsheet': None},
            22:    {'service': 'SSH',       'os': 'any',     'note': 'Secure Shell — try with weak credentials or keys',    'cheatsheet': None},
            23:    {'service': 'Telnet',    'os': 'any',     'note': 'Legacy, uncrypted — sniffable',   'cheatsheet': None},
            25:    {'service': 'SMTP',      'os': 'any',     'note': 'Mail server — usefull for user enumeration',  'cheatsheet': None},
            53:    {'service': 'DNS',       'os': 'any',     'note': 'DNS — try with zone transfer (axfr)',     'cheatsheet': None},
            80:    {'service': 'HTTP',      'os': 'any',     'note': 'HTTP Web server',     'cheatsheet': self.CHEATSHEETS['RECON_ENUM']},
            110:   {'service': 'POP3',      'os': 'any',     'note': 'Mail retrieval',  'cheatsheet': None},
            111:   {'service': 'RPCBind',   'os': 'linux',   'note': 'NFS enumeration — showmount -e',  'cheatsheet': None},
            143:   {'service': 'IMAP',      'os': 'any',     'note': 'Mail retrieval',  'cheatsheet': None},
            443:   {'service': 'HTTPS',     'os': 'any',     'note': 'Web server SSL — check the certificate',  'cheatsheet': self.CHEATSHEETS['RECON_ENUM']},
            993:   {'service': 'IMAPS',     'os': 'any',     'note': 'IMAP over SSL',   'cheatsheet': None},
            995:   {'service': 'POP3S',     'os': 'any',     'note': 'POP3 over SSL',   'cheatsheet': None},
            8080:  {'service': 'HTTP-Alt',  'os': 'any',     'note': 'Alternative Web — usually admin panel',   'cheatsheet': self.CHEATSHEETS['RECON_ENUM']},
            8443:  {'service': 'HTTPS-Alt', 'os': 'any',     'note': 'Alternative HTTPS',   'cheatsheet': self.CHEATSHEETS['RECON_ENUM']},

            # ============ LINUX ============
            2049:  {'service': 'NFS',       'os': 'linux',   'note': 'Network File System — try mount',     'cheatsheet': None},
            3306:  {'service': 'MySQL',     'os': 'linux',   'note': 'Database — try default credentials',  'cheatsheet': self.CHEATSHEETS['SQL_INJECTION']},
            5432:  {'service': 'PostgreSQL','os': 'linux',   'note': 'Database — try default credentials',  'cheatsheet': self.CHEATSHEETS['SQL_INJECTION']},
            6379:  {'service': 'Redis',     'os': 'linux',   'note': 'Sometimes without auth — Possible RCE',   'cheatsheet': None},
            27017: {'service': 'MongoDB',   'os': 'linux',   'note': 'Sometimes without auth',  'cheatsheet': None},
            9200:  {'service': 'Elasticsearch', 'os': 'linux','note': 'Sometimes exposed without auth',     'cheatsheet': None},

            # ============ WINDOWS ============
            88:    {'service': 'Kerberos',  'os': 'windows', 'note': 'AD — try AS-REP Roasting and Kerberoasting',  'cheatsheet': self.CHEATSHEETS['KERBEROASTING']},
            135:   {'service': 'RPC',       'os': 'windows', 'note': 'Legacy — rarely direct vector',   'cheatsheet': None},
            139:   {'service': 'NetBIOS',   'os': 'windows', 'note': 'SMB legacy — used in combo with 445',     'cheatsheet': self.CHEATSHEETS['AD_ENUMERATION']},
            389:   {'service': 'LDAP',      'os': 'windows', 'note': 'AD — Information Gathering, users dump',  'cheatsheet': self.CHEATSHEETS['AD_ENUMERATION']},
            445:   {'service': 'SMB',       'os': 'windows', 'note': 'Shared Folder — EternalBlue, enum shares',    'cheatsheet': self.CHEATSHEETS['AD_ENUMERATION']},
            464:   {'service': 'Kpasswd',   'os': 'windows', 'note': 'Kerberos password change',    'cheatsheet': None},
            636:   {'service': 'LDAPS',     'os': 'windows', 'note': 'LDAP over SSL',   'cheatsheet': self.CHEATSHEETS['AD_ENUMERATION']},
            593:   {'service': 'RPC-HTTP',  'os': 'windows', 'note': 'RPC over HTTP',   'cheatsheet': None},
            3268:  {'service': 'LDAP-GC',   'os': 'windows', 'note': 'Global Catalog LDAP',     'cheatsheet': self.CHEATSHEETS['AD_ENUMERATION']},
            3269:  {'service': 'LDAPS-GC',  'os': 'windows', 'note': 'Global Catalog LDAP over SSL',    'cheatsheet': self.CHEATSHEETS['AD_ENUMERATION']},
            3389:  {'service': 'RDP',       'os': 'windows', 'note': 'Remote Desktop — graphic remote login',   'cheatsheet': None},
            5985:  {'service': 'WinRM',     'os': 'windows', 'note': 'SSH di Windows — no interactive shell',   'cheatsheet': self.CHEATSHEETS['AD_ENUMERATION']},
            5986:  {'service': 'WinRM-SSL', 'os': 'windows', 'note': 'WinRM over HTTPS',    'cheatsheet': self.CHEATSHEETS['AD_ENUMERATION']},
            9389:  {'service': 'AD-WS',     'os': 'windows', 'note': 'Active Directory Web Services',   'cheatsheet': self.CHEATSHEETS['AD_ENUMERATION']},
            47001: {'service': 'WinRM-Alt', 'os': 'windows', 'note': 'Alternative WinRM',   'cheatsheet': self.CHEATSHEETS['AD_ENUMERATION']},
            49152: {'service': 'RPC-Dyn',   'os': 'windows', 'note': 'RPC dinamyc ports (49152-65535)',     'cheatsheet': None},
        }

        result = {}
        unknown = []
        file_content = ''

        for port in self.PORTS:
            if port in PORT_MAP:
                info = PORT_MAP[port]
                result[port] = info
                os_tag = f"[{info['os'].upper()}]" if info['os'] != 'any' else ''
                file_content += f'  {port:<6} {info["service"]:<15} {os_tag:<10} → {info["note"]:<100} → CHEATSHEERT: {info["cheatsheet"] if info["cheatsheet"] else 'No cheatsheet avaliable, sorry!'}\n'
                #file_content += f'  {port:<6} {info["service"]:<15} {os_tag:<10} → {info["note"]}\n'
            else:
                if 49152 <= port <= 65535:
                    result[port] = {'service': 'RPC-Dynamic', 'os': 'windows', 'note': 'Windows RPC dinamyc ports'}
                    file_content += f'  {port:<6} RPC-Dynamic    [WINDOWS]  → {"RPC dinamyc ports":<100} → CHEATSHEERT: {info["cheatsheet"] if info["cheatsheet"] else 'No cheatsheet avaliable, sorry!'}\n'
                    #file_content += f'  {port:<6} RPC-Dynamic    [WINDOWS]  → RPC dinamyc ports\n'
                else:
                    unknown.append(port)
                    file_content += f'  {port:<6} UNKNOWN        [-]        → {"Manual Investigation":<100} → CHEATSHEERT: {info["cheatsheet"] if info["cheatsheet"] else 'No cheatsheet avaliable, sorry!'}\n'
                    #file_content += f'  {port:<6} UNKNOWN        [-]        → Manual Investigation\n'

        if unknown:
            self.TOOL.log_actions(f'[LABEL_PORTS] Unknow port to investigate: {unknown}')

        self.TOOL.log_actions(f'[LABEL_PORTS] {len(result)} labeled port, {len(unknown)} unknown')
        return result, file_content
    
    def the_voice_of_frank(self, frank_report):
        print(self.colors.green(f'[FRANK SAYS] Hi you! Look here:\n{frank_report}'))
        with open(self.TOOL.FRANK_FILE, mode='w') as frank_speech:
            frank_speech.write(frank_report)

    def enlight_me(self):
        labeled_ports, frank_report = self.label_ports()
        self.the_voice_of_frank(frank_report)

    def export_file(self, filename: str):
        if not filename: return
        cp_CHEATSHEET = f'cp {self.CHEATSHEETS[filename]} {self.TOOL.WORKSPACE_PATH}/{filename}.md'
        subprocess.run(
            cp_CHEATSHEET,
            shell = True, 
            capture_output = True, 
            check = False
        )
        return