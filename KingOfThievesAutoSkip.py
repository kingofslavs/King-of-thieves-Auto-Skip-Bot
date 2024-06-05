import kivy
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.clock import Clock

import pymem
import pymem.process
from pynput.mouse import Button as MouseButton, Controller

# Имя процесса, к которому вы хотите подключиться
process_name = "Ld9BoxHeadless.exe"

# Словарь для хранения значений по адресам
values = {}

# Словарь адресов и соответствующих переменных
addresses = {
    "address1": 0x330F797C,
    "address2": 0xB4E2AF44,
    "address3": 0xB4E2AF6C,
    "address4": 0xB4E2AF94,
    "address5": 0x330F7950
}

# Координаты для клика мыши
click_coords = (1692, 959)

class MemoryReaderApp(App):
    def build(self):
        self.layout = BoxLayout(orientation='vertical')

        # Labels for displaying values
        self.gem1_label = Label(text="Gem 1 value: ")
        self.gem2_label = Label(text="Gem 2 value: ")
        self.gem3_label = Label(text="Gem 3 value: ")
        self.total_label = Label(text="Total sum of values: ")
        self.gold_label = Label(text="Gold amount: ")
        self.notification_label = Label(text="")  # Label for notifications

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
        self.mouse = Controller()

        # Variable to keep track of whether the updating is ongoing
        self.updating = False

        # Variable to store the threshold value
        self.threshold = 5000

        self.goldTarget = 5000

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
            self.update_button.text = "Stop Searching"
            Clock.schedule_interval(self.update_values, 0.5)  # Update every 1 second
        else:
            self.updating = False
            self.update_button.text = "Search Values"
            Clock.unschedule(self.update_values)

    def update_values(self, dt):
        pid = self.get_pid_by_name(process_name)
        if pid:
            pm = pymem.Pymem()
            pm.open_process_from_id(pid)

            for key, addr in addresses.items():
                try:
                    value = pm.read_int(addr)
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
                self.gem1_label.text = f"Gem 1 value: {encryptedvalue1 if encryptedvalue1 <= 1000000 else 0}"
                self.gem2_label.text = f"Gem 2 value: {encryptedvalue2 if encryptedvalue2 <= 1000000 else 0}"
                self.gem3_label.text = f"Gem 3 value: {encryptedvalue3 if encryptedvalue3 <= 1000000 else 0}"
                self.total_label.text = f"Total sum of values: {total_sum if encryptedvalue1 <= 1000000 else 0}"
                self.gold_label.text = f"Gold amount: {value5}"

                # Check if any gem value reaches the threshold
                if (encryptedvalue1 >= self.threshold or encryptedvalue2 >= self.threshold or encryptedvalue3 >= self.threshold or value5 >= self.goldTarget) and encryptedvalue1 < 1000000:
                    if (encryptedvalue1 >= self.threshold or encryptedvalue2 >= self.threshold or encryptedvalue3 >= self.threshold):
                        self.notification_label.text = f"A gem value has reached {self.threshold}!"
                    else:
                        self.notification_label.text = f"A gold value has reached {self.goldTarget}!"
                    self.updating = False
                    self.update_button.text = "Search Values"
                    Clock.unschedule(self.update_values)  # Stop updating once the condition is met
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
    MemoryReaderApp().run()