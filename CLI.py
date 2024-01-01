#command line interface to the program

class Command_Line_Interface():
    def __init__(self): #create the command line interface
        pass
        

    def run(self):
        print("Welcome to Henry's Air Travel Simulator, a program for simulating the flow of aircraft traffic around the world")
        while True:
            user_input = input("Please enter a command to begin :")
            user_input = user_input.lower()
    
    def lower_case_input(self,prompt):
        user_input = input(prompt)
        user_input = user_input.lower()


    #exit the program, after 
    def exit(self):
        result = self.hard_exit()
        return result


    #immediately exit the program
    def hard_exit(self):
        print("Thanks for using the Air Travel Simulator . . ")
        return True #true indicates quit


if __name__ == "__main__":
    CLI = Command_Line_Interface()
    CLI.run()

