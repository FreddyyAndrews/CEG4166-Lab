#!/usr/bin/env python3

import sys
import os
from tkinter import *
from subprocess import call
import threading
import time

window=Tk()

window.title("CEG4166 Labs DEMO")
window.geometry('650x220')

def lab1():
    os.system('sudo killall pigpiod')
    os.system('sudo pigpiod')
    os.system('cd')
    os.system('cd Desktop/CEG4166/Lab1')
    os.system('python3 rotationSpeed_Graph.py')

def lab2_part1():
    os.system('sudo killall pigpiod')
    os.system('sudo pigpiod')
    os.system('cd')
    os.system('cd Desktop/CEG4166/Lab2')
    os.system('python3 lab2_paths.py')
    
def lab2_part2():
    os.system('sudo killall pigpiod')
    os.system('sudo pigpiod')
    os.system('cd')
    os.system('cd Desktop/CEG4166/Lab2')
    os.system('python3 lab2_sonar.py')

def lab3_1():
    os.system('sudo killall pigpiod')
    os.system('sudo pigpiod')
    os.system('cd')
    os.system('cd Desktop/CEG4166/Lab3')
    os.system('python3 objectDetection_Keyboard.py')
    
def lab3_2():
    os.system('sudo killall pigpiod')
    os.system('sudo pigpiod')
    os.system('cd')
    os.system('cd Desktop/CEG4166/Lab3')
    os.system('python3 rotationGraph_Lab4.py')

def lab4_a():
    os.system('python3 detect_test.py')
    
def lab4_b():
    os.system('python3 faces_input.py')
    
def lab4_c():
    os.system('python3 model.py')

def lab4_d():
    os.system('python3 final_FaceRecog.py')    
    
def lab5():
    os.system('python3 maze_go.py')    
    
    
label1= Label(window, text="Lab-1 Demo -", borderwidth=3, relief="raised")
label1.grid(row=0, column=0)

label2= Label(window, text="Lab-2 Demo -", borderwidth=3, relief="raised")
label2.grid(row=1)

label3= Label(window, text="Lab-3 Demo -", borderwidth=3, relief="raised")
label3.grid(row=2)

label4= Label(window, text="Lab-4 Demo -", borderwidth=3, relief="raised")
label4.grid(row=3)

label5= Label(window, text="Lab-5 Demo -", borderwidth=3, relief="raised")
label5.grid(row=4)    
    
###lab1
btn1 = Button(window, text="Plot Encoders Graph", bg="orange", fg="black",command=lab1)
btn1.grid(column=1, row=0, sticky='ew')

###lab2
btn2_a = Button(window, text="Path Control", bg="green", fg="black",command=lab2_part1)
btn2_a.grid(column=1, row=1,sticky='ew')

btn2_b = Button(window, text="Keyboard Control", bg="yellow", fg="black",command=lab2_part2)
btn2_b.grid(column=2, row=1, sticky='ew')

###lab3
btn3_b = Button(window, text="Plot Sonar Graph", bg="cyan", fg="black",command=lab3_1)
btn3_b.grid(column=1, row=2, sticky='ew')

btn3_a = Button(window, text="Object Detection", bg="orange", fg="black",command=lab3_2)
btn3_a.grid(column=2, row=2, sticky='ew')

###lab4
btn4_a = Button(window, text="Face Detection Test", bg="yellow", fg="black",command=lab4_a)
btn4_a.grid(column=1, row=3, sticky='ew')

btn4_b = Button(window, text="Enrolment", bg="red", fg="black",command=lab4_b)
btn4_b.grid(column=2, row=3, sticky='ew')

btn4_c = Button(window, text="Model Training", bg="orange", fg="black",command=lab4_c)
btn4_c.grid(column=3, row=3, sticky='ew')

btn4_d = Button(window, text="Face Recognition", bg="cyan", fg="black",command=lab4_d)
btn4_d.grid(column=4, row=3, sticky='ew')

###lab5
btn5 = Button(window, text="Maze Travel", bg="green", fg="black",command=lab5)
btn5.grid(column=1, row=4, sticky='ew')

window.mainloop()




# infunc
# threading.Thread(target=call, args=("python inference.py",), ).start()
# threading.Thread(target=call, args=("python extract_frames.py",), ).start()