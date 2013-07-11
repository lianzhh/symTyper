import os
# RUNNABLE OBJECTS that we use in pool map by calling run instance on 
class ProgramRunner():
    

    commands = {
        "HMMER_COMMAND" : "/home/mahdi/programs/hmmer-3.0-linux-intel-x86_64/binaries/hmmscan %s %s > %s.out"
        }

    def __init__(self, program, params):
        self.program = program
        self.command = self.commands[program] % tuple(params)


    def run(self):
        os.system(self.command)

    def dryRun(self):
        return self.command
    

        
