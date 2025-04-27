import os, csv, time, traceback
from pynput import keyboard
from pynput.keyboard import Key, Controller


class WASender:
    
    def __init__(self, skip_verification:bool=False):
        self.skip_verification = skip_verification
        self.verification_status:bool = self.verify_with_user()
        if not self.verification_status:
            print(f"WhatsApp Desktop must be logged in for {self.app_name} to work!")
            return
        
        self.controller:Controller = Controller()
        self.app_name = "WA Sender"
        self.wanted_files:list = ['contacts.csv', 'message.txt']
        self.message:str = """"""
        self.logic_driver()
    
    def verify_with_user(self) -> bool:
        if self.skip_verification:
            return True
        wa_logged_in:str= input(
            "Is your WhatsApp Desktop application installed and logged in?\nIf not, login, come back here and press the 'y' key followed by the Enter key: "
        )
        return False if not wa_logged_in or wa_logged_in.lower() != 'y' else True
    
    def start_whatsapp(self):
        self.controller.tap(Key.cmd)
        time.sleep(3)
        self.controller.type("WhatsApp")
        time.sleep(3)
        self.controller.tap(Key.enter)
        time.sleep(3)
    
    def start_new_chat(self, contact_name:str) -> bool:
        try:
            with self.controller.pressed(Key.ctrl.value):
                self.controller.tap('n')
            time.sleep(0.5)
            self.controller.type(contact_name)
            time.sleep(2)
            self.controller.tap(key=Key.tab)
            time.sleep(1)
            self.controller.tap(key=Key.tab)
            time.sleep(1)
            self.controller.tap(key=Key.enter)
            time.sleep(1)
            return True
        except Exception as e:
            traceback.print_exc()
            print("Something went wrong while starting a new chat!", e)
            return False
    
    def send_message_in_chat(self, message:str, contact_name:str="", only_type:bool=False) -> bool:
        try:
            self.controller.type(message)
            time.sleep(1)
            if not only_type:
                self.controller.tap(key=Key.enter)
                time.sleep(1)
            print(f"Message sent{ f' to {contact_name.capitalize()}' if contact_name else '!'}")
            return True
        except Exception as e:
            traceback.print_exc()
            print("Something went wrong while sending your WhatsApp message!", e)
            return False
    
    def commit_message_to_memory(self, message_file_path:str) -> bool:
        try:
            with open(file=message_file_path, mode='r') as file:
                lines = file.readlines()
                for line in lines:
                    self.message += line
            print("Message commited to memory sucessfully!")
            return True
        
        except Exception as e:
            traceback.print_exc()
            print("Something went wrong while reading your message file!", e)
            return False
    
    def parse_and_send(self, csv_file_path:str) -> tuple[list,int,bool]:
        try:
            done_for:list = []
            fail_count:int = 0
            with open(file=csv_file_path, mode='r') as file:
                reader = csv.reader(file)
                for line in reader:
                    if "First" in line[0]:
                        continue
                    status:bool = True
                    name, _number = line[0], line[1] #TODO: Add number-based messaging support
                    while status:
                        status = self.start_new_chat(contact_name=name)
                        status = self.send_message_in_chat(message=self.message)
                        if status:
                            done_for.append((name,_number))
                            print(f"Message successfully sent to {name}!")
                        else:
                            fail_count += 1
                            print(f"Message sending failed to {name}!")
                        status = False
            
            return done_for, fail_count, False if fail_count else True
        
        except Exception as e:
            traceback.print_exc()
            print("Something went wrong while validating your Contacts List!", e)
            return [], 1000, False
    
    
    def validate_inputs(self, directory:str=os.getcwd()) -> tuple[bool, str]:
        try:
            data_subdirectory:str = os.path.join(directory, 'data')
            for i in range(len(self.wanted_files)):
                file:str = self.wanted_files[i]
                file_path:str = os.path.join(data_subdirectory,file)
                if not os.path.exists(file_path): 
                    return False, f"No file found at {file_path}! ensure that there a data folder with contact.csv and message.txt files in it!"
                elif not os.path.getsize(file_path):
                    return False, f"File {file_path} seems to be empty!"
                self.wanted_files[i] = file_path
            return True, "Input files seem to be correct!\nStarting messaging process now..."
        except Exception as e:
            traceback.print_exc()
            print("Something went wrong while validating your inputs!", e)
            return False, e
    


    def logic_driver(self):
        #TODO: Time the code
        try:
            status, message = self.validate_inputs()
            if not status:
                print(message)
                return status
            
            self.start_whatsapp()
            
            status = self.commit_message_to_memory(message_file_path=self.wanted_files[1])
            if not status:
                return status
            
            dones, fails,status = self.parse_and_send(csv_file_path=self.wanted_files[0])
            print("Successes: ", dones)
            print("Fails: ",fails)
            print("Final Status: ", status)
            return status

        except Exception as e:
            traceback.print_exc()
            print("Something went wrong!", e)
            return False, e

                




if __name__ == "__main__":
    manager:WASender = WASender(skip_verification=True)

