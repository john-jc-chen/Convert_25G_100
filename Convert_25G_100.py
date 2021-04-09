import serial_rx_tx
import time
import sys
import re
import os
#import logging
from datetime import datetime
from Write_FRU_Field import Write_FRU

import _thread

logFile = None
write_able = False

username = "ADMIN"
passwd = "ADMIN"
comport = "COM5"
baudrate = "9600"
FRU_fields ={}
config_file = sys.argv[1]
with open(config_file, 'r') as file:
    for comm in file.readlines():
        if comm.startswith("COM Port:"):
            comport = comm.split(':')[1].rstrip()
            break

#print(comport, username, mask, Part_Num)

serialPort = serial_rx_tx.SerialPort()

def OnReceiveSerialData():
    time.sleep(1.0)
    while serialPort.serialport.in_waiting > 0:
        print(serialPort.serialport.read(serialPort.serialport.in_waiting).decode("utf-8"))
        time.sleep(1.0)
def OpenCommand():
    global comport
    global baudrate
    serialPort.Open(comport,baudrate)
    print("COM Port Opened\r\n")

def login(username, passwd):
    serialPort.Send("")
    time.sleep(0.5)
    data = serialPort.serialport.readline().decode("utf-8", errors='ignore')
    while 'login:' not in data:
        print(data)
        data = serialPort.serialport.readline().decode("utf-8", errors='ignore')
    print(data)
    time.sleep(3.0)
    serialPort.Send("")
    serialPort.Send("")
    serialPort.Send("")
    time.sleep(1.0)
    OnReceiveSerialData()
    serialPort.Send(username)
    time.sleep(0.5)
    data = serialPort.serialport.readline().decode("utf-8", errors='ignore')
    print(data)
    serialPort.Send(passwd)
    time.sleep(1.0)
    data = serialPort.serialport.read(serialPort.serialport.in_waiting).decode("utf-8", errors='ignore')
    print(data)
    if "SMIS#" not in data:
        print("Failed to login with the password \"" + passwd + "\"\n Leave scrip!!!")
        serialPort.Close()
        sys.exit()
    #data = serialPort.serialport.read(serialPort.serialport.inWaiting())
    #print(data)

def logout():
    str = "exit\r"
    serialPort.serialport.write(str.encode("utf-8"))
    time.sleep(1.0)

def writeCommand(command):
    serialPort.Send(command)
    time.sleep(0.5)

def SetNetwork(IP, TFTP, Gateway):
    serialPort.Send_raw('o')
    OnReceiveSerialData()
    backspace = bytearray([8 for i in range(20)])
    serialPort.serialport.write(backspace)
    time.sleep(0.5)
    OnReceiveSerialData()
    serialPort.Send(IP)
    OnReceiveSerialData()
    serialPort.Send("")
    OnReceiveSerialData()
    serialPort.serialport.write(backspace)
    time.sleep(0.5)
    serialPort.Send(Gateway)
    OnReceiveSerialData()
    serialPort.serialport.write(backspace)
    time.sleep(0.5)
    serialPort.Send(TFTP)
    OnReceiveSerialData()
    serialPort.Send("y")
    OnReceiveSerialData()

def write_log(serial_number, message):
    if os.name == 'posix':
        log_dir = os.getcwd() + '/log'
    else:
        log_dir = os.getcwd() + "\\log"
    if not os.path.isdir(log_dir):
        os.mkdir(log_dir)

    if os.name == 'posix':
        file_name =log_dir + '/' + serial_number + '.log'
    else:
        file_name =log_dir + "\\" + serial_number + '.log'

    with open(file_name, 'w') as f:
        f.write("{}\n {}\n".format(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), message))

OpenCommand()
if serialPort.IsOpen():
    #serialPort.Send("")
    while True:
        time.sleep(2.0)
        while serialPort.serialport.in_waiting > 0:
            message = serialPort.serialport.read(serialPort.serialport.in_waiting).decode("utf-8", errors='ignore')
            message = message.rstrip()
            if " Boot Menu " in message:
                print(message)
                start_time = time.time()
                serialPort.Send_raw(" ")
                OnReceiveSerialData()

                with open(config_file, 'r') as file:
                    for comm in file.readlines():
                        if comm.startswith("CMM Password:"):
                            cmm_pwd = comm.split(':')[1].rstrip()
                        elif comm.startswith("Switch Password:"):
                            passwd = comm.split(':')[1].rstrip()
                        elif comm.startswith("IP:"):
                            IP = comm.split(':')[1].rstrip()
                        elif comm.startswith("Gateway:"):
                            gateway = comm.split(':')[1].rstrip()
                        elif comm.startswith("Change Value:"):
                            ModelValue = comm.split(':')[1].rstrip()
                        elif comm.startswith("Place:"):
                            SlotNumber = comm.split(':')[1].rstrip()
                        elif comm.startswith("CMM IP:"):
                            cmm_ip = comm.split(':')[1].rstrip()
                        elif comm.startswith("Board Product Name:"):
                            FRU_fields['Board Product Name'] = comm.split(':')[1].rstrip()
                        elif comm.startswith("Product Name:"):
                            FRU_fields['Product Name'] = comm.split(':')[1].rstrip()
                        elif comm.startswith("Product PartNum:"):
                            FRU_fields['Product Part Number'] = comm.split(':')[1].rstrip()
                        elif comm.startswith("Mask:"):
                            mask = comm.split(':')[1].rstrip()
                        else:
                            pass
                # if bootloader:
                #     print("Set boot loader name")
                #     serialPort.Send_raw('m')
                #     backspace = bytearray([8 for i in range(50)])
                #     OnReceiveSerialData()
                #     serialPort.serialport.write(backspace)
                #     time.sleep(1.0)
                #     OnReceiveSerialData()
                #     serialPort.Send(bootloader)
                #     OnReceiveSerialData()
                #     serialPort.Send('y')
                #     OnReceiveSerialData()
                # print("Set Firmware name")
                # serialPort.Send_raw('n')
                # OnReceiveSerialData()
                # backspace = bytearray([8 for i in range(50)])
                # serialPort.serialport.write(backspace)
                # time.sleep(1.0)
                # OnReceiveSerialData()
                # serialPort.Send(firmware)
                # OnReceiveSerialData()
                # serialPort.Send('y')
                # OnReceiveSerialData()
                # print("Set TFTP server")
                # SetNetwork(IP,TFTP,gateway)
                # if bootloader:
                #     print("Updating bootloader ...")
                #     fail = True
                #     serialPort.Send_raw('j')
                #     while True:
                #         time.sleep(3.0)
                #         message = serialPort.serialport.read(serialPort.serialport.in_waiting)
                #         try:
                #             message = message.decode("utf-8", errors='ignore')
                #
                #             #print(message)
                #             if "PROGRAM SUCCEEDED" in message:
                #                 fail = False
                #                 print("Updated bootloader")
                #
                #             if "Please press any Enter to continue..." in message:
                #                 serialPort.Send("")
                #                 break
                #         except:
                #             print('decode error')
                #
                #     if fail:
                #         print("Failed to flash bootloader!! Leave script!")
                #         serialPort.Close()
                #         sys.exit()
                #
                # print("Updating Firmware ...")
                # fail = True
                # serialPort.Send_raw('k')
                # while True:
                #     time.sleep(2.0)
                #     message = serialPort.serialport.read(serialPort.serialport.in_waiting)
                #     try:
                #         message = message.decode("utf-8", errors='ignore')
                #         print(message, end='', flush=True)
                #         #print(message)
                #         if "FW PROGRAM NORMAL SUCCEEDED" in message:
                #             fail = False
                #         if "Please press Enter key to continue..." in message:
                #             print("Finished updated normal firmware")
                #
                #             print("")
                #             serialPort.Send("")
                #             break
                #     except:
                #         print('decode error')
                # if fail:
                #     print("Failed to flash firmware!! Leave script!")
                #     sys.exit(0)
                # time.sleep(0.5)
                # serialPort.Send_raw('l')
                # backspace = bytearray([8 for i in range(5)])
                # serialPort.serialport.write(backspace)
                # time.sleep(0.5)
                # OnReceiveSerialData()
                # serialPort.Send('1')
                # time.sleep(0.5)
                # OnReceiveSerialData()
                # serialPort.Send('y')
                # OnReceiveSerialData()
                # time.sleep(0.5)
                # serialPort.Send_raw('k')
                # while True:
                #     time.sleep(2.0)
                #     message = serialPort.serialport.read(serialPort.serialport.in_waiting)
                #     try:
                #         message = message.decode("utf-8", errors='ignore')
                #         print(message, end='', flush=True)
                #         # print(message)
                #         if "FW PROGRAM FALLBACK SUCCEEDED" in message:
                #             fail = False
                #         if "Please press Enter key to continue..." in message:
                #             print("Finished updated fallback firmware")
                #             print("")
                #             serialPort.Send("")
                #             break
                #     except:
                #         print('decode error')
                # if fail:
                #     print("Failed to flash firmware!! Leave script!")
                #     sys.exit(0)
                # time.sleep(0.5)
                #
                # serialPort.Send_raw('l')
                # backspace = bytearray([8 for i in range(5)])
                # serialPort.serialport.write(backspace)
                # time.sleep(0.5)
                # OnReceiveSerialData()
                # serialPort.Send('0')
                # time.sleep(0.5)
                # OnReceiveSerialData()
                # serialPort.Send('y')
                # OnReceiveSerialData()
                # time.sleep(0.5)
                # SetNetwork('172.31.30.102', '172.31.33.5', '172.31.0.1')
                print("Converting the model")
                serialPort.Send_raw('q')
                OnReceiveSerialData()
                time.sleep(1.0)
                serialPort.Send("dbg")
                while serialPort.serialport.in_waiting > 0:
                    message =serialPort.serialport.read(serialPort.serialport.in_waiting).decode("utf-8", errors='ignore')
                    print(message)
                    if "=>" in message:
                        break
                    time.sleep(1.0)
                serialPort.Send("")
                time.sleep(2.0)
                OnReceiveSerialData()
                serialPort.Send(f"sys_eeprom set 0x6E {ModelValue}")
                OnReceiveSerialData()
                time.sleep(1.0)
                serialPort.Send("sys_eeprom write")
                OnReceiveSerialData()
                time.sleep(0.5)
                serialPort.Send("bootmenu")
                time.sleep(2.0)
                message = serialPort.serialport.read(serialPort.serialport.in_waiting)
                print(message.decode("utf-8", errors='ignore'))
                serialPort.Send_raw(" ")
                time.sleep(1.0)
                serialPort.Send_raw('q')
                OnReceiveSerialData()
                time.sleep(1.0)
                serialPort.Send("esc")
                #serialPort.serialport.write("bootmenu\r".encode("utf-8"))
                #OnReceiveSerialData()
                #message = serialPort.serialport.read(serialPort.serialport.in_waiting).decode("utf-8", errors='ignore')
                message = serialPort.serialport.readline().decode("utf-8", errors='ignore')
                while " Supermicro Switch" not in message:
                    print(message)
                    message =serialPort.serialport.readline().decode("utf-8", errors='ignore')
                time.sleep(5.0)
                login(username, passwd)
                print("Setting networking IP")
                serialPort.Send("c t")
                OnReceiveSerialData()
                time.sleep(1.0)
                serialPort.Send(f"ip address {IP} {mask}")
                OnReceiveSerialData()
                #time.sleep(1.0)
                serialPort.Send(f"ip gateway {gateway}")
                OnReceiveSerialData()
                #time.sleep(1.0)
                serialPort.Send('ex')
                OnReceiveSerialData()
                serialPort.Send('write startup-config')
                OnReceiveSerialData()
                time.sleep(5.0)
                # serialPort.Send_raw('y')
                # OnReceiveSerialData()
                # time.sleep(1.0)
                serialPort.Send("show system information")
                time.sleep(0.5)
                serial_number = ''
                message = ''
                while serialPort.serialport.in_waiting > 0:
                    strs = serialPort.serialport.read(serialPort.serialport.in_waiting).decode("utf-8", errors='ignore')
                    message += strs
                    m = re.findall(r"Serial\s+Number\s+\:\s?(\w+)", strs)
                    if m:
                        serial_number = m[0]
                    time.sleep(1.0)
                serialPort.Send_raw('q')
                write_log(serial_number, message)
                OnReceiveSerialData()
                serialPort.Send("show version")
                time.sleep(1.0)
                message = ''
                while serialPort.serialport.in_waiting > 0:
                    message += serialPort.serialport.read(serialPort.serialport.in_waiting).decode("utf-8")
                    time.sleep(1.0)
                print('Updating FRU information')
                
                for i in FRU_fields.keys():
                    Write_FRU(cmm_ip, 'ADMIN', cmm_pwd, SlotNumber, i, FRU_fields[i])
                time.sleep(20.0)
                serialPort.serialport.reset_input_buffer()
                serialPort.serialport.reset_output_buffer()
                print(message + "\nUpdate Finshed!\nTotal time: %s seconds" % (time.time() - start_time))

else:
    print("Not sent - COM port is closed\r\n")


