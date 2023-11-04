#!/usr/bin/env python

import customtkinter
from clustering import clustering_routine

customtkinter.set_appearance_mode("dark") #Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme("dark-blue") #Themes: "blue" (standard), "green", "dark-blue"

app = customtkinter.CTk()
app.geometry("450x850")
app.title("Chania Traffic Flow Simulator")

def message_update(choice):
    label_message.configure(text="") #update error message when changing options on option menus

def radiobutton_event():
    label_message.configure(text="") #update error message when changing options on radio buttons

def button_callback():
    #------Construct Time to AM/PM------#
    am_to_pm1 = int(optionmenu_from.get().split(":")[0]) #get first two digits of starting time
    am_to_pm2 = int(optionmenu_to.get().split(":")[0]) #get first two digits of ending time

    if radiobutton_var_from.get() == 2 and optionmenu_from.get() != "12:00":
        am_to_pm1 += 12 #go from am to pm by adding 12
        start_time = str(am_to_pm1) + ":00" #reconstruct time
    elif radiobutton_var_from.get() == 1 and optionmenu_from.get() == "12:00":
        am_to_pm1 -= 12 #12 am is 00:00
        start_time = str(am_to_pm1) + "0:00" #reconstruct time
    elif radiobutton_var_from.get() == 1 and am_to_pm1 < 10:
        start_time = "0" + str(am_to_pm1) + ":00" #for the range 1-9 am add a 0 in the beginning to reconstruct time   
    else:
        start_time = optionmenu_from.get()

    if radiobutton_var_to.get() == 2 and optionmenu_to.get() != "12:00":
        am_to_pm2 += 12 #go from am to pm by adding 12
        end_time = str(am_to_pm2) + ":00" #reconstruct time
    elif radiobutton_var_to.get() == 1 and optionmenu_to.get() == "12:00":
        am_to_pm2 -= 12 #12 am is 00:00
        end_time = str(am_to_pm2) + "0:00" #reconstruct time
    elif radiobutton_var_to.get() == 1 and am_to_pm2 < 10:
        end_time = "0" + str(am_to_pm2) + ":00" #for the range 1-9 am add a 0 in the beginning to reconstruct time
    else:
        end_time = optionmenu_to.get()

    #------Get Time Parameter------#
    if optionmenu_interval.get().split(" ")[1] != "hour":
        parameter = int(int(optionmenu_interval.get().split(" ")[0]) / 10) #for test file: parameter=interval/5 as we get a measurement every 5 minutes, for original: parameter=interval/10 as we get a measurement every 10 minutes
    else:
        parameter = 6 #for test file: parameter=12 because 1hour = 60minutes = 12 x 5minutes(per measurement), for original: parameter=6 because 1hour = 60minutes = 6 x 10minutes(per measurement)

    input_file = "data/"+optionmenu_month.get()+"/"+optionmenu_day.get()+".csv" #construct input file path from app options
    relationships = optionmenu_relationships.get()
    print(f"Input File: {input_file}\nFrom: {start_time}\nTo: {end_time}\nInterval: {optionmenu_interval.get()}, parameter: {parameter}, traffic relationships: {relationships}\n")
    
    try:
        clustering_routine(input_file, start_time, end_time, parameter, relationships)
    except:
        label_message.configure(text="Invalid options.\nTry again!", text_color="red")

#------ For information check: https://customtkinter.tomschimansky.com ------#
frame_1 = customtkinter.CTkFrame(master=app)
frame_1.pack(pady=30, padx=50, fill="both", expand=True)

label_month = customtkinter.CTkLabel(master=frame_1, text="Month of Interest")
label_month.pack(pady=(30,0), padx=10)

optionmenu_month = customtkinter.CTkOptionMenu(frame_1, width=200, values=["January","February","March","April","May","June","July","August","September","October","November","December"], command=message_update)
optionmenu_month.pack(pady=0, padx=10)

label_day = customtkinter.CTkLabel(master=frame_1, text="Day of Interest")
label_day.pack(pady=(20,0), padx=10)

optionmenu_day = customtkinter.CTkOptionMenu(frame_1, width=200, values=["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"], command=message_update)
optionmenu_day.pack(pady=0, padx=10)

label_from = customtkinter.CTkLabel(master=frame_1, text="From")
label_from.pack(pady=(40,0), padx=10)

optionmenu_from = customtkinter.CTkOptionMenu(frame_1, values=["1:00","2:00","3:00","4:00","5:00","6:00","7:00","8:00","9:00","10:00","11:00","12:00"], command=message_update)
optionmenu_from.pack(pady=0, padx=10)

radiobutton_var_from = customtkinter.IntVar(value=1)

radiobutton_from1 = customtkinter.CTkRadioButton(master=frame_1, text="AM", variable=radiobutton_var_from, value=1, command=radiobutton_event)
radiobutton_from1.pack(pady=5, padx=10)

radiobutton_from2 = customtkinter.CTkRadioButton(master=frame_1, text="PM", variable=radiobutton_var_from, value=2, command=radiobutton_event)
radiobutton_from2.pack(pady=0, padx=10)

label_to = customtkinter.CTkLabel(master=frame_1, text="To")
label_to.pack(pady=(20,0), padx=10)

optionmenu_to = customtkinter.CTkOptionMenu(frame_1, values=["1:00","2:00","3:00", "4:00", "5:00", "6:00", "7:00","8:00", "9:00", "10:00", "11:00", "12:00"], command=message_update)
optionmenu_to.pack(pady=0, padx=10)

radiobutton_var_to = customtkinter.IntVar(value=1)

radiobutton_to1 = customtkinter.CTkRadioButton(master=frame_1, text="AM", variable=radiobutton_var_to, value=1, command=radiobutton_event)
radiobutton_to1.pack(pady=5, padx=10)

radiobutton_to2 = customtkinter.CTkRadioButton(master=frame_1, text="PM", variable=radiobutton_var_to, value=2, command=radiobutton_event)
radiobutton_to2.pack(pady=0, padx=10)

label_interval = customtkinter.CTkLabel(master=frame_1, text="Time Interval")
label_interval.pack(pady=(40,0), padx=10)

optionmenu_interval = customtkinter.CTkOptionMenu(frame_1, width=180, values=["10 minutes", "20 minutes", "30 minutes", "1 hour"], command=message_update)
optionmenu_interval.pack(pady=0, padx=10)

label_relationships = customtkinter.CTkLabel(master=frame_1, text="Traffic Relationships")
label_relationships.pack(pady=(20,0), padx=10)

optionmenu_relationships = customtkinter.CTkOptionMenu(frame_1, width=180, values=["Both", "Propagates", "Splits/Merges"], command=message_update)
optionmenu_relationships.pack(pady=(0,10), padx=10)

label_message = customtkinter.CTkLabel(master=frame_1, text="")
label_message.pack(pady=(20,0), padx=10)

button_1 = customtkinter.CTkButton(master=frame_1, text="Show Results", fg_color="green", border_width=1, border_color="white", width=80, command=button_callback)
button_1.pack(pady=(30,0), padx=10)

app.mainloop()
