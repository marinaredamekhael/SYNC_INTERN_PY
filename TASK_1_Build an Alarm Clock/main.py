import tkinter as tk
from tkinter import messagebox, ttk
import datetime
from threading import Thread
from playsound import playsound
import time
import pygame


pygame.mixer.init()

class AlarmClock:

    def __init__(self, root):
        self.root = root
        self.root.title("Professional Alarm Clock")

        self.frame = ttk.Frame(self.root)
        self.frame.grid(padx=10, pady=10)

        # Dropdown menus for selecting hours, minutes, and seconds
        self.hour_var = tk.StringVar(root)
        self.minute_var = tk.StringVar(root)
        self.second_var = tk.StringVar(root)

        hours = [str(i).zfill(2) for i in range(24)]
        minutes_seconds = [str(i).zfill(2) for i in range(60)]

        ttk.Label(self.frame, text="Hour:").grid(row=0, column=0)
        self.hour_combo = ttk.Combobox(self.frame, values=hours, textvariable=self.hour_var)
        self.hour_combo.grid(row=0, column=1)

        ttk.Label(self.frame, text="Minute:").grid(row=1, column=0)
        self.minute_combo = ttk.Combobox(self.frame, values=minutes_seconds, textvariable=self.minute_var)
        self.minute_combo.grid(row=1, column=1)

        ttk.Label(self.frame, text="Second:").grid(row=2, column=0)
        self.second_combo = ttk.Combobox(self.frame, values=minutes_seconds, textvariable=self.second_var)
        self.second_combo.grid(row=2, column=1)

        self.set_button = ttk.Button(self.frame, text="Set Alarm", command=self.set_alarm)
        self.set_button.grid(row=3, column=0, columnspan=2, pady=10)

        self.snooze_button = ttk.Button(self.frame, text="Snooze (5 mins)", command=self.snooze, state=tk.DISABLED)
        self.snooze_button.grid(row=4, column=0, columnspan=2, pady=10)

        self.time_remaining_var = tk.StringVar(root, value='00:00:00')
        ttk.Label(self.frame, text="Time Remaining:").grid(row=5, column=0)
        ttk.Label(self.frame, textvariable=self.time_remaining_var).grid(row=5, column=1)

    def sound_alarm(self):
        pygame.mixer.music.load("alarm-clock.wav")
        for _ in range(5):  # Repeat for 5 times
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy() and self.is_playing:  # To ensure the sound plays completely
                pygame.time.Clock().tick(10)
            if not self.is_playing:  # Check if the alarm is snoozed or stopped
                break
        # Reset to initial state after sound stops playing
        # self.reset_ui()

    def reset_ui(self):
        # Remove the "Alarm Ringing" message
        if hasattr(self, "ringing_label"):
            self.ringing_label.destroy()

        # Disable the snooze and stop buttons
        self.snooze_button.config(state=tk.DISABLED)
        if hasattr(self, "stop_button"):
            self.stop_button.destroy()

    def set_alarm(self):
        self.alarm_time = f"{self.hour_var.get()}:{self.minute_var.get()}:{self.second_var.get()}"
        self.is_playing = True

        # If the alarm is set again, reset the UI
        self.reset_ui()

        self.alarm_thread = Thread(target=self.check_alarm)
        self.alarm_thread.start()

    def update_ui_for_alarm(self):
        self.ringing_label = ttk.Label(self.frame, text="Alarm Ringing!")
        self.ringing_label.grid(row=6, column=0, columnspan=2, pady=10)
        self.stop_button = ttk.Button(self.frame, text="Stop Alarm", command=self.stop_alarm)
        self.stop_button.grid(row=7, column=0, columnspan=2, pady=10)
        self.snooze_button.config(state=tk.NORMAL)
        self.sound_alarm_thread = Thread(target=self.sound_alarm)
        self.sound_alarm_thread.start()

    def check_alarm(self):
        while self.is_playing:
            current_time = datetime.datetime.now().strftime('%H:%M:%S')
            alarm_time_obj = datetime.datetime.strptime(self.alarm_time, '%H:%M:%S')
            current_time_obj = datetime.datetime.strptime(current_time, '%H:%M:%S')

            # If alarm time is set for the next day
            if alarm_time_obj < current_time_obj:
                alarm_time_obj += datetime.timedelta(days=1)

            time_difference = alarm_time_obj - current_time_obj
            hours, remainder = divmod(time_difference.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            time_str = f"{hours:02}:{minutes:02}:{seconds:02}"
            self.root.after(0, self.time_remaining_var.set, time_str)

            if current_time == self.alarm_time:
                self.is_playing = False
                self.root.after(0, self.update_ui_for_alarm)
                self.sound_alarm_thread = Thread(target=self.sound_alarm)
                self.sound_alarm_thread.start()
                break

            # Sleep for a second before checking the time again
            time.sleep(1)

    def stop_alarm(self):
        self.is_playing = False
        pygame.mixer.music.stop()  # Stop the sound
        if hasattr(self, 'sound_alarm_thread'):
            # Try to join the thread to ensure it completes
            self.sound_alarm_thread.join(timeout=1)
        self.reset_ui()

    def snooze(self):
        pygame.mixer.music.stop()  # Stop the sound
        if hasattr(self, 'sound_alarm_thread'):
            # Try to join the thread to ensure it completes
            self.sound_alarm_thread.join(timeout=1)
        self.is_playing = False
        snooze_time = datetime.datetime.now() + datetime.timedelta(minutes=5)
        self.hour_var.set(snooze_time.hour)
        self.minute_var.set(snooze_time.minute)
        self.second_var.set(snooze_time.second)
        self.set_alarm()

if __name__ == "__main__":
    root = tk.Tk()
    clock = AlarmClock(root)
    root.mainloop()
