#command line interface to the program

class Command_Line_Interface():
    #high level running of the CLI
    def __init__(self): #create the command line interface
        self.create_cli_options()
        
    def run(self):
        print("Welcome to Henry's Air Travel Simulator, a program for simulating the flow of aircraft traffic around the world")
        while True:
            user_input = self.lower_case_input("Please enter a command to begin :")
            stop_program = self.parse_option_cli(user_input,self.base_cli_options)
            if stop_program:
                break
    
    #CLI OPTION FUNCTIONS - USE in RESPONSE TO USER INPUT

    #create the dictionaries storing all the functions used by options at the command line
    def create_cli_options(self): 
        self.create_base_cli_options()
    
    #TOP LEVEL CLI OPTION FUNCTIONS
        
    #create a dictionary storing all the options available at command line at the top level
    def create_base_cli_options(self):
        self.base_cli_options = {
        "exit" : self.exit,
        "hard exit" : self.hard_exit
        }
        
    def parse_option_cli(self,user_input,dict):
        stop_dialogue = False
        if user_input in dict:
           stop_dialogue = dict[user_input]() #execute the user input
        else:
            print(user_input, " is not a valid option. To see a list of valid options, enter options")
        return stop_dialogue
    
    #exit the program, after checking conditions (at the moment we just ask them if they really want to leave)
    def exit(self):
        user_input = self.lower_case_input("Do you wish to exit, enter y to confirm :")
        if user_input=="y":
            stop_program = self.hard_exit()
        else:
            stop_program = False
        return stop_program

    #immediately exit the program
    def hard_exit(self):
        print("Thanks for using the Air Travel Simulator . . ")
        return True #true indicates quit

    #HELPER FUNCTIONS, can be used anywhere in the CLI

    #get user input to a selected prompt in lowercase format
    def lower_case_input(self,prompt):
        user_input = input(prompt)
        user_input = user_input.lower()
        return user_input

if __name__ == "__main__":
    CLI = Command_Line_Interface()
    CLI.run()

