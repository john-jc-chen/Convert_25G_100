import subprocess
import re
import argparse
import sys
import os
from os import path
import time
import copy
import logging
import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext
from tkinter import messagebox

inter_files = []
logging.basicConfig(format='%(asctime)s : %(message)s', level=logging.INFO , filename='Write_FRU_Field.log')

def Write_FRU(ip,username,passwd,slot, field, value):
    slot_map = {'CMM':'1','Midplane':'2','A1':'3', 'A2':'4', 'B1':'5', 'B2':'6'}
    fields = {'Product Serial Number':'PS', 'Product Part Number':'PPM', 'Product Name':'PN','Board Serial Number':'BS','Board Part Number':'BP',
              'Board Product Name':'BPN', 'Product Version':'PV', 'Asset Tag':'PAT', 'Board Mfg. Date/Time':'BDT', 'Board Manufacturer':'BM', 'Product Manufacturer':'PM'}
    if sys.platform.lower() == 'win32':
        tool_cmd = f'SMCIPMITool.exe'
    else:
        tool_cmd = 'SMCIPMITool'
    com = [tool_cmd, ip, username, passwd]
    c1 = copy.deepcopy(com)

    if slot != 'CMM' and slot != 'Midplane':
        slot_txt = slot.lower()
        slot_txt= slot_txt.replace(' switch', '')

        run_SMCIPMITool(c1 + ['ipmi','raw', '30', '33', '28', slot_txt, '0'])
    msg = run_SMCIPMITool(c1 + ['ipmi', 'fruidw', slot_map[slot], fields[field], value], True)
    #print(f"{msg}\n{fields[field]}\n")

    #run_SMCIPMITool(c1 + ['ipmi', 'raw', '30', '6', '1'])
    if slot != 'CMM' and slot != 'Midplane':
        run_SMCIPMITool(c1 + ['ipmi','raw', '30', '33', '28', slot_txt, '1'])
    lines = msg.split("\n")
    for line in lines:
        result = re.search(r'^.*?\(' + fields[field] + '\)\s+\=\s?(.+?)$', line)
        if result:
            print(line)
            if value != result.group(1).rstrip().lstrip():
                #print("Failed to write {}.".format(fields[field]))
                print(f"Failed to write {fields[field]}. {value} {result.group(1)}")
                #logging.error("Field value not identical in {}. {} vs {}".format(fields[field], value, result.group(1).rstrip().lstrip()))
                return False
            else:
                return True
    return False

def run_SMCIPMITool(com, check=False):
    #print(com)
    try:
        output = subprocess.run(com, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # os.system(cmd)
    except Exception as e:
        #print("Error has occurred in updating FRU. " + str(e))
        print( "Error has occurred in updating FRU. " + str(e))
        #logging.warning("Error has occurred in updating FRU. " + str(e))
        #root.update()
        return False
    if output.returncode != 0:
        #print("Failed running SMCIPMITool " + output.stdout.decode("utf-8", errors='ignore'))
        print("Failed running SMCIPMITool " + output.stdout.decode("utf-8", errors='ignore'))
        #logging.error("Failed running SMCIPMITool " +  output.stdout.decode("utf-8", errors='ignore'))
        #sroot.update()
        return False
    if check:
        return output.stdout.decode("utf-8", errors='ignore')
    return True

def check_connectivity(ip):
    if sys.platform.lower() == 'win32':
        res = subprocess.run(['ping','-n','3', ip], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    else:
        res = subprocess.run(['ping', '-c', '3', ip], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if res.returncode  != 0:
        return False
    else:
        out_text = res.stdout.decode("utf-8", errors='ignore')
        #print(out_text)
        if 'Destination host unreachable' in out_text:
            return False
        else:
            return True

def main(data, text_area):

    ip = data['CMM IP']
    username = data['CMM User Name']
    password = data['CMM Password']
    text_area.insert(tk.INSERT, "Checking connectivity to {}\n\n".format(ip))
    root.update()
    if not check_connectivity(ip):
        #print("Failed to access to {}. Leave program!!".format(ip))
        text_area.insert(tk.INSERT, "Failed to access to {}.Please check the IP address!\n\n".format(ip))
        root.update()
        return

    write_info = data['data']

    if sys.platform.lower() == 'win32':
        tool_cmd = f'SMCIPMITool.exe'
    else:
        tool_cmd = 'SMCIPMITool'
    com = [tool_cmd, ip, username, password]

    if run_SMCIPMITool(com + ['ipmi', 'raw', '30', '6', '0'], text_area):
        for line in write_info:
            slot, field, value = line
            #print("va \'{}\'".format(value))
            if value == '':
                continue
            text_area.insert(tk.INSERT, "Writing {} to {} on {}\n".format(value, field, slot))
            logging.info("Writing {} to {}".format(value, slot))
            root.update()
            if Write_FRU(ip, username, password, slot, field, value, text_area):
                #print("Program successfully in {}".format(slot))
                text_area.insert(tk.INSERT, "Programmed successfully on {}\n\n".format(slot))
                logging.info("Programmed successfully on {}".format(slot))
                root.update()
                time.sleep(0.5)

    run_SMCIPMITool(com + ['ipmi', 'raw', '30', '6', '1'], text_area)
    text_area.insert(tk.INSERT, "Done!\n")

class App(tk.Frame):

    def __init__(self, master, *args, **kwargs):
        tk.Frame.__init__(self, master, *args, **kwargs)
        self.master = master
        self.label_frame = tk.Frame(self.master)
        self.label_frame.grid()

        self.label_list = []
        self.data = {}

        self.places = ('CMM', 'Midplane', 'A1 Switch', 'A2 Switch', 'B1 Switch', 'B2 Switch')
        self.fields = ('Product Serial Number', 'Product Part Number', 'Product Name', 'Product Version'
                       , 'Board Serial Number', 'Board Part Number', 'Board Product Name', 'Asset Tag', 'Board Mfg. Date/Time', 'Board Manufacturer', 'Product Manufacturer')

        self.label_list.append(tk.Label(self.label_frame, text="CMM IP", justify=tk.LEFT))
        self.label_list[0].grid(sticky = tk.W,row=0)
        self.label_list.append(tk.Label(self.label_frame, text="CMM User Name", justify=tk.LEFT))
        self.label_list[1].grid(sticky = tk.W,row=1)
        self.label_list.append(tk.Label(self.label_frame, text="CMM Password", justify=tk.LEFT))
        self.label_list[2].grid(sticky = tk.W,row=2)

        self.e1 = tk.Entry(self.label_frame)
        self.e2 = tk.Entry(self.label_frame)
        self.e3 = tk.Entry(self.label_frame)
        self.e1.grid(row=0, column=1)
        self.e2.grid(row=1, column=1)
        self.e3.grid(row=2, column=1)

        self.label_list.append(tk.Button(self.label_frame, text="Add Update Value", command=self.add_new_data))
        self.label_list[3].grid(row=3)

        self.label_list.append(tk.Label(self.label_frame, text="Update Place", justify=tk.LEFT))
        self.label_list[4].grid( row=4)
        self.label_list.append(ttk.Combobox(self.label_frame))
        self.label_list[5]['values']= self.places
        self.label_list[5].current(0)
        self.label_list[5].grid(row=4, column=1)

        self.label_list.append(tk.Label(self.label_frame, text="Field", justify=tk.LEFT))
        self.label_list[6].grid(row=4, column=2)
        self.label_list.append(ttk.Combobox(self.label_frame))
        self.label_list[7]['values'] = self.fields
        self.label_list[7].current(0)
        self.label_list[7].grid(row=4, column=3)

        self.label_list.append(tk.Label(self.label_frame, text="Value", justify=tk.LEFT))
        self.label_list[8].grid(row=4, column=4)
        self.label_list.append(tk.Entry(self.label_frame))
        self.label_list[9].grid(row=4, column=5)

        self.write = tk.Button(self.label_frame, text="Write", command=self.write_fru)
        self.exit = tk.Button(self.label_frame, text="Exit", command=self.exit)
        self.text_area = scrolledtext.ScrolledText(self.label_frame)
        self.write.grid(row=5, column=0)
        self.exit.grid(row=5, column=4)
        self.text_area.grid(row=6,columnspan=6)

    def add_new_data(self):
        # for widget in self.label_frame.children.values():
        self.text_area.grid_forget()
        self.write.grid_forget()
        self.exit.grid_forget()

        i = len(self.label_list)
        print(self.label_list[9].get())
        self.label_list.append(tk.Label(self.label_frame, text="Update Place", justify=tk.LEFT))
        self.label_list[i].grid(row=i-5)
        self.label_list.append(ttk.Combobox(self.label_frame))
        self.label_list[i+1]['values'] = self.places
        self.label_list[i+1].current(0)
        self.label_list[i+1].grid(row=i-5, column=1)

        self.label_list.append(tk.Label(self.label_frame, text="Field", justify=tk.LEFT))
        self.label_list[i+2].grid(row=i-5, column=2)
        self.label_list.append(ttk.Combobox(self.label_frame))
        self.label_list[i+3]['values'] = self.fields
        self.label_list[i+3].current(0)
        self.label_list[i+3].grid(row=i-5, column=3)

        self.label_list.append(tk.Label(self.label_frame, text="Value", justify=tk.LEFT))
        self.label_list[i+4].grid(row=i-5, column=4)
        self.label_list.append(tk.Entry(self.label_frame))
        self.label_list[i+5].grid(row=i-5, column=5)

        self.write.grid(row=i - 4, column = 0)
        self.exit.grid(row=i - 4, column = 4)
        self.text_area.grid(row=i - 3, columnspan=6)

    def write_fru(self):
        if not self.e1.get():
            messagebox.showerror("showerror", "CMM IP is empty")
            return
        self.data['CMM IP'] = self.e1.get()
        if not self.e2.get():
            messagebox.showerror("showerror", "CMM User Name is empty")
            return
        self.data['CMM User Name'] = self.e2.get()
        if not self.e3.get():
            messagebox.showerror("showerror", "CMM Password is empty")
            return
        self.data['CMM Password'] = self.e3.get()
        l = []
        data = []
        for i in range(3, len(self.label_list)):
            if self.label_list[i].widgetName == 'label':
                if self.label_list[i]['text'] == 'Update Place':
                    if data:
                        l.append(data)
                    data = [self.label_list[i+1].get()]
                else:
                    data.append(self.label_list[i+1].get())
        if data:
            l.append(data)

        self.data['data'] = l
        main(self.data, self.text_area)
    def exit(self):
        sys.exit(0)

if __name__ == '__main__':
    root = tk.Tk()
    root.title('Write FRU Field')
    #my_app = App(root)
    App(root)
    root.mainloop()
    main()
