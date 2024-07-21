import kivy
import re
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.clock import Clock

import pymem
import pymem.process
from pynput.mouse import Button as MouseButton, Controller as MouseController
from pynput import keyboard

process_name = "Ld9BoxHeadless.exe"

values = {}

addresses = {
    "address1": 0x0,
    "address2": 0x0,
    "address3": 0x0,
    "address4": 0x0,
    "address5": 0x0
}

click_coords = (1692, 959)


class AddressCatcher(App):
    def build(self):
        self.title = "Address Catcher"
        self.Addresslayout = BoxLayout(orientation='vertical')

        self.BaseGemAdressInput = TextInput(hint_text="Enter a base gem address", multiline=False)
        self.Addresslayout.add_widget(self.BaseGemAdressInput)

        self.EncryptedGemValueAdress1Input = TextInput(hint_text="Enter a encrypted gem address 1", multiline=False)
        self.Addresslayout.add_widget(self.EncryptedGemValueAdress1Input)

        self.EncryptedGemValueAdress2Input = TextInput(hint_text="Enter a encrypted gem address 2", multiline=False)
        self.Addresslayout.add_widget(self.EncryptedGemValueAdress2Input)

        self.EncryptedGemValueAdress3Input = TextInput(hint_text="Enter a encrypted gem address 3", multiline=False)
        self.Addresslayout.add_widget(self.EncryptedGemValueAdress3Input)

        self.GoldValueAdressInput = TextInput(hint_text="Enter a gold value address", multiline=False)
        self.Addresslayout.add_widget(self.GoldValueAdressInput)

        self.save_button = Button(text="Save Addresses")
        self.save_button.bind(on_press=self.save_addresses)
        self.Addresslayout.add_widget(self.save_button)

        self.message_label = Label()
        self.Addresslayout.add_widget(self.message_label)

        return self.Addresslayout

    def save_addresses(self, instance):
        base_address = self.BaseGemAdressInput.text
        encrypted_address1 = self.EncryptedGemValueAdress1Input.text
        encrypted_address2 = self.EncryptedGemValueAdress2Input.text
        encrypted_address3 = self.EncryptedGemValueAdress3Input.text
        gold_address = self.GoldValueAdressInput.text

        base_address = self.add_prefix(base_address)
        encrypted_address1 = self.add_prefix(encrypted_address1)
        encrypted_address2 = self.add_prefix(encrypted_address2)
        encrypted_address3 = self.add_prefix(encrypted_address3)
        gold_address = self.add_prefix(gold_address)

        if (self.is_valid_address(base_address) and
                self.is_valid_address(encrypted_address1) and
                self.is_valid_address(encrypted_address2) and
                self.is_valid_address(encrypted_address3) and
                self.is_valid_address(gold_address)):

            addresses["address1"] = base_address
            addresses["address2"] = encrypted_address1
            addresses["address3"] = encrypted_address2
            addresses["address4"] = encrypted_address3
            addresses["address5"] = gold_address
            self.message_label.text = "Addresses saved successfully!"

            if all(addresses.values()):
                print(addresses)
                App.get_running_app().stop()
                MemoryReaderApp().run()
        else:
            self.message_label.text = "One or more addresses are invalid!"

        print(addresses)

    def is_valid_address(self, address):
        pattern = re.compile(r'^0x[0-9A-Fa-f]{8}$')
        return bool(pattern.match(address))

    def add_prefix(self, address):
        if not address.startswith("0x"):
            address = "0x" + address
        return address


class MemoryReaderApp(App):
    def build(self):
        self.layout = BoxLayout(orientation='vertical')

        # Labels for displaying values
        self.gem1_label = Label(text="Gem 1 value: ")
        self.gem2_label = Label(text="Gem 2 value: ")
        self.gem3_label = Label(text="Gem 3 value: ")
        self.total_label = Label(text="Total sum of values: ")
        self.gold_label = Label(text="Gold amount: ")
        self.notification_label = Label(text="")

        # Adding labels to the layout
        self.layout.add_widget(self.gem1_label)
        self.layout.add_widget(self.gem2_label)
        self.layout.add_widget(self.gem3_label)
        self.layout.add_widget(self.total_label)
        self.layout.add_widget(self.gold_label)
        self.layout.add_widget(self.notification_label)

        # TextInput for threshold value
        self.threshold_input = TextInput(hint_text="Enter gem value", multiline=False)
        self.layout.add_widget(self.threshold_input)

        # Text Input for gold target
        self.goldTraget_input = TextInput(hint_text="Enter gold amount", multiline=False)
        self.layout.add_widget(self.goldTraget_input)

        # Button to set the threshold value
        self.set_threshold_button = Button(text="Set gem value")
        self.set_threshold_button.bind(on_press=self.set_threshold)
        self.layout.add_widget(self.set_threshold_button)

        # Button to set the gold target
        self.set_goldTarget_button = Button(text="Set gold amount")
        self.set_goldTarget_button.bind(on_press=self.set_gold_target)
        self.layout.add_widget(self.set_goldTarget_button)

        # Button for updating values
        self.update_button = Button(text="Search Values")
        self.update_button.bind(on_press=self.start_updating_values)
        self.layout.add_widget(self.update_button)

        # Mouse controller for clicking
        self.mouse = MouseController()

        # Variable to keep track of whether the updating is ongoing
        self.updating = False

        # Variable to store the threshold value
        self.threshold = 5000

        self.goldTarget = 5000

        # Setting up the keyboard listener
        self.keyboard_listener = keyboard.Listener(on_press=self.on_key_press)
        self.keyboard_listener.start()

        return self.layout

    def get_pid_by_name(self, name):
        process_list = pymem.process.list_processes()
        for process in process_list:
            if process.szExeFile.decode('utf-8') == name:
                return process.th32ProcessID
        return None

    def click_at_coords(self):
        self.mouse.position = click_coords
        self.mouse.click(MouseButton.left, 1)

    def set_threshold(self, instance):
        try:
            self.threshold = int(self.threshold_input.text)
            self.notification_label.text = f"Gem value set to {self.threshold}"
        except ValueError:
            self.notification_label.text = "Invalid gem value! Please enter a valid number."

    def set_gold_target(self, instance):
        try:
            self.goldTarget = int(self.goldTraget_input.text)
            self.notification_label.text = f"Gold amount set to {self.goldTarget}"
        except ValueError:
            self.notification_label.text = "Invalid gold amount! Please enter a valid number."

    def start_updating_values(self, instance):
        if not self.updating:
            self.updating = True
            self.update_button.text = "Stop Searching (press q)"
            Clock.schedule_interval(self.update_values, 1)  # Update every 0.2 second
        else:
            self.stop_updating_values()

    def stop_updating_values(self):
        self.updating = False
        self.update_button.text = "Search Values"
        Clock.unschedule(self.update_values)

    def on_key_press(self, key):
        try:
            if key.char in ('q', 'Q', 'й', 'Й'):
                self.stop_updating_values()
        except AttributeError:
            pass

    def update_values(self, dt):
        pid = self.get_pid_by_name(process_name)
        if pid:
            pm = pymem.Pymem()
            pm.open_process_from_id(pid)

            for key, addr in addresses.items():
                try:
                    addr_int = int(addr, 16)
                    value = pm.read_int(addr_int)
                    values[key] = value
                except pymem.exception.MemoryReadError:
                    values[key] = None

            pm.close_process()

            value1 = values.get("address1")
            value2 = values.get("address2")
            value3 = values.get("address3")
            value4 = values.get("address4")
            value5 = values.get("address5")

            if all(value is not None for value in (value1, value2, value3, value4, value5)):
                encryptedvalue1 = value2 ^ value1
                encryptedvalue2 = value3 ^ value1
                encryptedvalue3 = value4 ^ value1
                total_sum = encryptedvalue1 + encryptedvalue2 + encryptedvalue3

                # Update labels with the new values
                self.gem1_label.text = f"Gem 1 value: {encryptedvalue1 if encryptedvalue1 < 1000000 else 0}"
                self.gem2_label.text = f"Gem 2 value: {encryptedvalue2 if encryptedvalue2 < 1000000 else 0}"
                self.gem3_label.text = f"Gem 3 value: {encryptedvalue3 if encryptedvalue3 < 1000000 else 0}"
                self.total_label.text = f"Total sum of values: {total_sum if encryptedvalue3 < 1000000 else 0}"
                self.gold_label.text = f"Gold amount: {value5}"

                # Check if any gem value reaches the threshold
                if (encryptedvalue1 >= self.threshold or encryptedvalue2 >= self.threshold or encryptedvalue3 >= self.threshold or value5 >= self.goldTarget) and encryptedvalue3 < 1000000:
                    if (encryptedvalue1 >= self.threshold or encryptedvalue2 >= self.threshold or encryptedvalue3 >= self.threshold):
                        self.notification_label.text = f"A gem value has reached {self.threshold}!"
                    else:
                        self.notification_label.text = f"A gold value has reached {self.goldTarget}!"
                    self.stop_updating_values()  # Stop updating once the condition is met
                else:
                    self.notification_label.text = ""
                    self.click_at_coords()  # Click the mouse at the specified coordinates

            else:
                self.gem1_label.text = "Failed to retrieve all values from the dictionary."
                self.gem2_label.text = ""
                self.gem3_label.text = ""
                self.total_label.text = ""
                self.gold_label.text = ""
                self.notification_label.text = ""

if __name__ == "__main__":
    AddressCatcher().run()
