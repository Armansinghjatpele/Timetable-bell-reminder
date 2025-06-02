import requests
from kivymd.app import MDApp
from kivymd.uix.screen import Screen
from kivymd.uix.list import MDList, OneLineListItem
from kivymd.uix.scrollview import ScrollView
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.textfield import MDTextField
from kivymd.uix.boxlayout import BoxLayout
from kivymd.uix.selectioncontrol import MDSwitch
from kivymd.uix.label import MDLabel
from kivy.clock import Clock
from plyer import notification
from datetime import datetime

# Function to send class reminder to FastAPI backend
def show_notification(class_name, time_str):
    data = {
        "class_name": class_name,
        "time": time_str
    }

    # Send request to FastAPI
    response = requests.post("http://127.0.0.1:8000/add_reminder", json=data)
    
    # Debugging Response
    print(response.status_code, response.text)

# Example usage (replace with actual Kivy input values)
show_notification("Math Class", "10:30 AM")
show_notification("English", "10:30 AM")


timetable = {}
today = datetime.today().strftime("%A")

def convert_to_24_hour(time_str, is_pm):
    time_obj = datetime.strptime(time_str, "%I:%M")
    if is_pm and time_obj.hour < 12:
        time_obj = time_obj.replace(hour=time_obj.hour + 12)
    elif not is_pm and time_obj.hour == 12:
        time_obj = time_obj.replace(hour=0)
    return time_obj.strftime("%H:%M")

def check_timetable():
    now = datetime.now().strftime("%H:%M")
    for time_slot, subject in timetable.get(today, []):
        if time_slot == now:
            send_reminder(subject)

def show_notification(subject):
    notification.notify(
        title="Class Reminder",
        message=f"Time for {subject}!",
        timeout=10
    )

class BellReminderApp(MDApp):
    def build(self):
        self.screen = Screen()
        self.scroll = ScrollView()
        self.list_view = MDList()
        self.scroll.add_widget(self.list_view)
        self.screen.add_widget(self.scroll)

        add_btn = MDRaisedButton(
            text="Add Class Reminder",
            pos_hint={"center_x": 0.5, "center_y": 0.1},
            on_release=self.show_add_reminder_dialog
        )
        self.screen.add_widget(add_btn)

        self.update_list()
        Clock.schedule_interval(lambda dt: check_timetable(), 60)

        return self.screen

    def update_list(self):
        self.list_view.clear_widgets()
        classes_today = timetable.get(today, [])

        if not classes_today:
            self.list_view.add_widget(OneLineListItem(text="No Classes Today!"))
        else:
            for time_slot, subject in classes_today:
                self.list_view.add_widget(OneLineListItem(text=f"{time_slot} - {subject}"))

    def show_add_reminder_dialog(self, instance):
        layout = BoxLayout(orientation="vertical", spacing=15, padding=20, size_hint_y=None)
        layout.height = 200  # Ensuring proper height to fit all elements

        self.time_input = MDTextField(
            hint_text="Enter Time (HH:MM)", 
            size_hint_x=1,
            mode="rectangle"
        )
        self.class_input = MDTextField(
            hint_text="Enter Class Name", 
            size_hint_x=1,
            mode="rectangle"
        )

        pm_layout = BoxLayout(orientation="horizontal", size_hint_y=None, height=50)
        pm_label = MDLabel(text="PM:", size_hint_x=None, width=40)
        self.pm_switch = MDSwitch(size_hint_x=None, width=40)
        pm_layout.add_widget(pm_label)
        pm_layout.add_widget(self.pm_switch)

        layout.add_widget(self.time_input)
        layout.add_widget(self.class_input)
        layout.add_widget(pm_layout)

        self.dialog = MDDialog(
            title="Add Class Reminder",
            type="custom",
            content_cls=layout,
            buttons=[
                MDRaisedButton(text="Add", on_release=self.add_reminder),
                MDRaisedButton(text="Cancel", on_release=lambda x: self.dialog.dismiss())
            ]
        )
        self.dialog.open()

    def add_reminder(self, instance):
        time_slot = self.time_input.text.strip()
        subject = self.class_input.text.strip()
        is_pm = self.pm_switch.active

        if time_slot and subject:
            try:
                time_slot = convert_to_24_hour(time_slot, is_pm)
                timetable.setdefault(today, []).append((time_slot, subject))
                self.update_list()
                self.dialog.dismiss()
            except ValueError:
                print("Error: Invalid Time Format! Use HH:MM format.")
        else:
            print("Error: Time or Subject is empty!")

if __name__ == "__main__":
    BellReminderApp().run()