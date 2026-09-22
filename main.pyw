"""Schedulix — Console-free Windows launcher.

On Windows, the .pyw extension causes pythonw.exe to be used,
which launches the application without a terminal window.
"""
from gui.app import SchedulerApp

if __name__ == "__main__":
    SchedulerApp().mainloop()
