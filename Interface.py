import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext
from tkinter import messagebox

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
                       , 'Board Serial Number', 'Board Part Number', 'Board Product Name', 'Asset Tag')

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
        print(self.data)
    def exit(self):
        # print("cancel")
        exit(0)

if __name__ == "__main__":
    root = tk.Tk()
    root.title('Write FRU Field')
    my_app = App(root)
    root.mainloop()