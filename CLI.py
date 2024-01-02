import re

class Command_Line_Interface():
    #high level running of the CLI
    def __init__(self): #create the command line interface
        self.create_cli_options()
        
    def run(self):
        print("Welcome to Henry's Air Travel Simulator, a program for simulating the flow of aircraft traffic around the world")
        while True:
            user_input = self.lower_case_input("Please enter a command to begin : ")
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
        "hard_exit" : self.hard_exit,
        "options" : self.base_options,
        "help" : self.base_help,
        "man" : self.base_help,
        "manual" : self.base_help
        }
    
    #parse input from the cli and see if it is valid
    def parse_option_cli(self,user_input,option_dict):
        stop_dialogue = False
        split_input = user_input.split()
        if len(split_input)==0:
            key_word = ""
        else:
            key_word = split_input[0]
        if len(split_input)==0:
            arguments = []
        else:
            arguments = split_input[1:]
        if key_word in option_dict:
           stop_dialogue = option_dict[key_word](False,arguments) #execute the user input
        else:
            print(user_input, " is not a valid option. To see a list of valid options, enter options")
        return stop_dialogue
    
    #thin wrapper around help for the base menu
    def base_help(self,help_mode,additional_prompt):
        self.display_help(help_mode,self.base_cli_options,additional_prompt)
        return False

    #display the list of options for the base menu, this is just a thin wrapper around the generic options function
    def base_options(self,help,additional_prompt):
        self.display_options(help,self.base_cli_options)
        return False


    #exit the program, after checking conditions (at the moment we just ask them if they really want to leave)
    def exit(self,help,additional_prompt):
        if help:
            print("Exit the program, will provide the option to save your work and confirm first")
            return False
        else:
            user_input = self.lower_case_input("Do you wish to exit, enter y to confirm : ")
            if user_input=="y":
                stop_program = self.hard_exit(False,[])
            else:
                stop_program = False
            return stop_program

    #immediately exit the program
    def hard_exit(self,help,additional_prompt):
        if help:
            print("Immediately exit the program, no second chances, I'm that sort of a program ")
            return False
        else:
            print("Thanks for using the Air Travel Simulator . . ")
            return True #true indicates quit

    #HELPER FUNCTIONS, can be used anywhere in the CLI

    #get user input to a selected prompt in lowercase format
    def lower_case_input(self,prompt):
        user_input = input(prompt)
        user_input = user_input.lower()
        return user_input

    def display_options(self,help,option_dictionary):
        if help:
            print("the options command displays all options available in this menu")
            return False
        else:    
            print("available options are . . .")
            for name,function in option_dictionary.items():
                print(name)
            
            return False
    
    #get useful information about options
    def display_help(self,help,help_dict,additional_prompt):
        if help:
            print("Type help followed by another option eg 'help exit' to display information about that option. You can also enter a series of options at once")
            return False
        elif len(additional_prompt)==0:
            print("What do you wish to be helped with? Please enter help followed by another eg 'help exit', to display information about that option. You can also enter a series of options at once ")
            return False
        else:
            for word in additional_prompt:
                print(word," : ",end='')
                if word in help_dict:
                    help_dict[word](True,[])
                else:
                    print(word, " is not a valid option. To see a list of valid options, enter options")
            return False


if __name__ == "__main__":
    CLI = Command_Line_Interface()
    CLI.run()

