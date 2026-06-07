from ..utils.utils import Shell_Colors 
from ..utils.tool_suite_initializer import ToolSuiteInitializer
import json

class Cesare:

    def __init__(self, tool_suite: ToolSuiteInitializer):
        self.colors = Shell_Colors()
        if not tool_suite:
            raise RuntimeError(self.colors.red('Cannot call Dora with None configs!'))
        self.TOOL = tool_suite
        self.creds_counter = 0

    def add_cred(self, cred: dict): # Fresh cred without id
        if not cred:
            message = '[CESARE - ADD CRED] Cannot process empty credentials'
            print(self.colors.red(message))
            self.log_actions(message)
            return

        try:
            with open(f'{self.TOOL.CREDS_PATH}/creds.json', 'r') as creds_file:
                creds = json.load(creds_file)
        except (FileNotFoundError, json.JSONDecodeError):
            creds = {}

        try:
            creds[self.creds_counter] = cred
            self.creds_counter += 1

            with open(f'{self.TOOL.CREDS_PATH}/creds.json', 'w') as creds_file:
                json.dump(creds, creds_file, indent=4)
        except Exception as e:
            message = f'[CESARE - ADD CRED] Error: {e}'
            self.log_actions(message)
            raise RuntimeError(self.colors.red(message))
        
    def update_cred(self, cred: dict): # Old cred with id (id: cred)
        if not cred:
            message = '[CESARE - UPDATE CRED] Cannot process empty credentials'
            print(self.colors.red(message))
            self.log_actions(message)
            return

        try:
            with open(f'{self.TOOL.CREDS_PATH}/creds.json', 'r') as creds_file:
                creds = json.load(creds_file)
        except (FileNotFoundError, json.JSONDecodeError):
            message = '[CESARE - UPDATE CRED] Cannot process empty crads.json file!'
            print(self.colors.red(message))
            self.log_actions(message)
            return

        try:
            creds[cred.keys()[0]] = cred['id']

            with open(f'{self.TOOL.CREDS_PATH}/creds.json', 'w') as creds_file:
                json.dump(creds, creds_file, indent=4)
        except Exception as e:
            message = f'[CESARE - UPDATE CRED] Error: {e}'
            self.log_actions(message)
            raise RuntimeError(self.colors.red(message))
        
    def find_cred(self, param: str):
        try:
            with open(f'{self.TOOL.CREDS_PATH}/creds.json', 'r') as creds_file:
                creds = json.load(creds_file)
                if not param or param.strip().isspace():
                    return creds
                else:
                    for key, value in creds.items():
                        if param == key or param in value['referred_url'] or param in value['username'] or param in value['password'] or param in value['notes']:
                            return value
                    return None
        except (FileNotFoundError, json.JSONDecodeError):
            message = '[CESARE - FIND CRED] Cannot process empty crads.json file!'
            print(self.colors.red(message))
            self.log_actions(message)
            return