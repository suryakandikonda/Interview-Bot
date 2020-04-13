from tkinter import *
import tkinter.messagebox
from tkinter import ttk
from tkinter.ttk import *
import requests
import json
import PyPDF2
import os
import smtplib
import threading

usernameString = ""
passwordString = ""
title = ""
skills = ""
expDate = ""

global usrNameEntry
window = Tk()
window.title("HR Login")
window.geometry('400x400')
window.configure(background = "#006064")
usrNameLabel = Label(window ,text = "User Name", font=("Ubuntu", 12)) #.place(x=50, y=100)
usrNameLabel.grid(row=2,column=1,pady=20,padx=10)
pwdLabel = Label(window ,text = "Password", font=("Ubuntu", 12))#.place(x=50, y=135)
pwdLabel.grid(row=4,column=1,pady=20,padx=10)
usrNameEntry = Entry(window, font=("Ubuntu", 12))#.place(x=150, y=100)
usrNameEntry.grid(row=2,column=2,pady=20)
pwdEntry = Entry(window, show="*", font=("Ubuntu", 12))#.place(x=150, y=135)
pwdEntry.grid(row=4,column=2,pady=20)
window.grid_columnconfigure(0,weight=1)
window.grid_columnconfigure(5,weight=1)
window.grid_rowconfigure(0,weight=1)
window.grid_rowconfigure(7,weight=1)

def loading():
    tkinter.messagebox.showinfo("Running", "Bot Running")


def success():
   tkinter.messagebox.showinfo("Success", "Bot run successfully")

def bot(title,skills,expDate):
    try:
        t=threading.Thread(target=loading)
        t.daemon = True  # set thread to daemon ('ok' won't be printed in this case)
        t.start()
    except:
        print("Error: unable to start thread")
    
    try:
        
        cbURL = "https://backendbot.azurewebsites.net/api/CreateBatch"
        param = {"p":title,
                  "s":skills,
                  "ld":expDate}
        r = requests.get(url=cbURL,params=param)
        batch = r.text
        print(batch)
    except Exception as e:
        print(e)

    #Looping throught files
    try:
        for filename in os.listdir("C:/ResumesFolder/"):
            print(filename)
            if filename.endswith(".pdf"):
                name = filename.split(".")[0]
                print(name)
                pdfObj = open("C:/ResumesFolder/"+filename,'rb')
                pdfReader = PyPDF2.PdfFileReader(pdfObj)
                no = pdfReader.numPages
                pageText = ""
                for i in range(0,no):
                    pageObj = pdfReader.getPage(i)
                    pageText = pageText + pageObj.extractText()
                pdfObj.close()
                out = {"documents":[{"language":"en","id":"1","text":pageText[:5000]}]}
                out = json.dumps(out)

                #Keyword extraction
                try:
                    kwURL = "https://analyzer-based-skills.cognitiveservices.azure.com/text/analytics/v3.0-preview.1/entities/recognition/general"
                    header = {"Ocp-Apim-Subscription-Key":"ba3d475f6f5a41228139d7080ed4b478",
                          "Accept":"application/json",
                          "Content-Type":"application/json"}
                    r = requests.post(url=kwURL,headers=header,data=out)
                    processed = json.loads(r.text)

                    skill = skills.lower().split(",")
                    skillCount = len(skill)
                    hasCount = 0
                    result = ""
                    email = ""
                    for i in processed['documents'][0]['entities']:
                        if(i['type']=="Skill" and (i['text'].lower() in skill)):
                            hasCount = hasCount + 1
                            result = result + i['text'] + ","
                        elif(i['type']=="Email"):
                            email = i['text']
                    if(hasCount==skillCount):
                        #Insert Candidate
                        try:
                            icURL = "https://backendbot.azurewebsites.net/api/InsertCand"
                            param = {"b":batch,
                                     "n":name}
                            r = requests.get(url=icURL,params=param)
                            passw = r.text

                            #Send mail
                            s = smtplib.SMTP('smtp.gmail.com',587)
                            s.starttls()
                            s.login('bhanuphani100@gmail.com','chowd@ry')
                            mes = ("Subject : Shortlisted\n\n Dear "+name+",\n You have been shortlisted for the job profile of "+title
                                    +". Please login to the below link with given cedentials and attend the interview before "+expDate
                                    +"\nLink : https://autoview.azurewebsites.net/?b="+batch+"\n Username : "+name
                                    +"\nPassword : "+passw)
                            s.sendmail("bhanuphani100@gmail.com",email,mes)
                            s.quit()
                        except Exception as e:
                            print(e)
                            print("Here3")
                    else:
                        print("Candidate not selected")
                except Exception as e:
                    print(e)
                    print("Here2")
            
            else:
                pass
        success()
    except Exception as e:
        print(e)
        print("Here1")

def clicked():
    global window
    window.destroy()
    window = Tk()
    window.title("Welcome")
    window.geometry('400x400')
    window.configure(background = "#388E3C")
    TitleText = tkinter.Text(window, width=30, height=30, bg="#388E3C", bd=0, font=("Ubuntu", 16), fg="white")
    #TitleText.grid(row=1,column=1)
    #TitleText.insert(tkinter.END, "Welcome to panel")
    jobTitleLabel = Label(window, text="Enter job title: ", font=("Ubuntu", 12))#.place(x=70, y=150)
    jobTitleLabel.grid(row=2,column=2,padx=10,pady=20)
    jobTitleEntry = Entry(window, font=("Ubuntu", 12))#.place(x=200,y=150)
    jobTitleEntry.grid(row=2,column=4,padx=10,pady=20)

    skillsLabel = Label(window, text="Enter skills: ", font=("Ubuntu", 12))#.place(x=70, y=200)
    skillsLabel.grid(row=3,column=2,padx=10,pady=20)
    skillsEntry = Entry(window, font=("Ubuntu", 12))#.place(x=200, y=200)
    skillsEntry.grid(row=3,column=4,padx=10,pady=20)

    dateLabel = Label(window, text = "Date: ", font=("Ubuntu", 12))#.place(x=70, y=250)
    dateLabel.grid(row=4,column=2,padx=10,pady=20)
    dateEntry = Entry(window, font=("Ubuntu", 12))#.place(x=200, y=250)
    dateEntry.grid(row=4,column=4,padx=10,pady=20)
    btn = ttk.Button(window ,text="Submit",command = lambda:bot(jobTitleEntry.get(),skillsEntry.get(),dateEntry.get()))#.place(x=200, y=300)
    btn.grid(row=5,column = 4)
    window.grid_columnconfigure(0,weight=1)
    window.grid_columnconfigure(9,weight=1)
    window.grid_rowconfigure(0,weight=1)
    window.grid_rowconfigure(7,weight=1)

def clickJust():
    usernameString = usrNameEntry.get()
    passwordString = pwdEntry.get()
    if(usernameString=="root" and passwordString=="root"):
        clicked()

btn = ttk.Button(window ,text="Login",command = clickJust)#.place(x=200, y=200)
btn.grid(row=6,column=2)
window.mainloop()
