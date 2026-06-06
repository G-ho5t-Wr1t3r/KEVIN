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