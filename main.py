import os, csv, time, traceback
import pyperclip
from pynput.keyboard import Key, Controller
from threading import Thread
from playsound import playsound

class WASender:
    
    def __init__(self, skip_verification:bool=False, wait_multiplier:float=1.5):
        self.wait_multiplier = wait_multiplier
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
        time.sleep(self.wait_multiplier * 3)
        self.controller.type("WhatsApp")
        time.sleep(self.wait_multiplier * 3)
        self.controller.tap(Key.enter)
        time.sleep(self.wait_multiplier * 3)
    
    def start_new_chat(self, contact_number:str, contact_name:str) -> bool:
        try:
            with self.controller.pressed(Key.ctrl.value):
                self.controller.tap('n')
            time.sleep(self.wait_multiplier * 0.5)
            self.controller.type(contact_number if contact_number else contact_name)
            time.sleep(self.wait_multiplier * 2)
            self.controller.tap(key=Key.tab)
            time.sleep(self.wait_multiplier * 1)
            self.controller.tap(key=Key.tab)
            time.sleep(self.wait_multiplier * 1)
            self.controller.tap(key=Key.enter)
            time.sleep(self.wait_multiplier * 1)
            return True
        except Exception as e:
            traceback.print_exc()
            print("Something went wrong while starting a new chat!", e)
            return False
    
    def send_message_in_chat(self, message:str, should_paste:bool=True, contact_name:str="", only_type:bool=False) -> bool:
        try:
            time.sleep(self.wait_multiplier * 1)
            if should_paste:
                with self.controller.pressed(Key.ctrl.value):
                    self.controller.tap('v')
            else:
                self.controller.type(message)
            time.sleep(self.wait_multiplier * 1)
            if not only_type:
                self.controller.tap(key=Key.enter)
                time.sleep(self.wait_multiplier * 1)
            print(f"Message sent{ f' to {contact_name.capitalize()}' if contact_name else '!'}")
            return True
        except Exception as e:
            traceback.print_exc()
            print("Something went wrong while sending your WhatsApp message!", e)
            return False
    
    def commit_message_to_memory(self, message_file_path:str, copy_paste_mode:bool=True) -> bool:
        try:

            if copy_paste_mode:
                with open(message_file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                    pyperclip.copy(content)
                    print(f"Content of '{message_file_path}' copied to clipboard.")
            else:
                with open(file=message_file_path, mode='r', encoding='utf-8') as file:
                    lines = file.readlines()
                    for line in lines:
                        self.message += line
                print("Message commited to memory sucessfully!")
            return True
        
        except Exception as e:
            traceback.print_exc()
            print("Something went wrong while reading your message file!", e)
            return False
    
    def parse_and_send(self, csv_file_path:str) -> tuple[list,int,str]:
        try:
            done_for:list = []
            fail_count:int = 0
            with open(file=csv_file_path, mode='r') as file:
                reader = csv.reader(file)
                for line in reader:
                    if "First" in line[0]:
                        continue
                    status:bool = True
                    name, number = line[0], line[1] 
                    while status:
                        status = self.start_new_chat(contact_number=number, contact_name=name)
                        status = self.send_message_in_chat(message=self.message)
                        if status:
                            done_for.append((name,number))
                            print(f"Message successfully sent to {name}!")
                        else:
                            fail_count += 1
                            print(f"Message sending failed to {name}!")
                        status = False
            
            return done_for, fail_count, "failure" if fail_count else "success"
        
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
    

    def alert_user(self, alert_type:str):
        try:
            def play_thread_function():
                playsound(f"{alert_type}.mp3") #TODO: Find alternative library to play from path

            play_thread = Thread(target=play_thread_function)
            play_thread.start()
        except Exception as e:
            traceback.print_exc()
            print("Something went wrong while alerting user!", e)
            return False, e


    def logic_driver(self):
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
            self.alert_user(alert_type=status)
            return False if fails else True

        except Exception as e:
            traceback.print_exc()
            print("Something went wrong!", e)
            return False, e

                




if __name__ == "__main__":
    #TODO: add a completion or failure sound module
    manager:WASender = WASender(skip_verification=True)

