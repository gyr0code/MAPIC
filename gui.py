from tkinter import *
import tkinter.ttk as ttk
import numpy
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import serial
from array import array
import datetime
import APICfns as F

apic = F.APIC('COM3',10,('192.168.4.1',8080))

### SETUP ###
root = Tk()
root.title('APIC')
#root.wm_iconbitmap('dAPIC.bmp')

### DEFINE FRAMES ###
I2Cframe = LabelFrame(root,text='I2C Digital Potentiometer Control')
I2Cframe.grid(row=1,column=1,columnspan=6,rowspan=4)

ADCframe = LabelFrame(root,text='Measurement Tools')
ADCframe.grid(row=5,column=1,columnspan=5,rowspan=3,sticky=W)

diagnostic = LabelFrame(root,text='Diagnostic Message:')
diagnostic.grid(row=6,column=6,rowspan=2)

### I2C TOOLS FRAME ###
def read():
    apic.readI2C()
    Ireadlabel.config(text='Gain: %i , Width: %i' % (apic.posGAIN,apic.posWIDTH))
def scan():
    apic.scanI2C()
    Iscanlabel.config(text=str(apic.I2Caddrs))

Iread = Button(I2Cframe,text='Potentiometer Values',command=read).grid(row=1,column=1)
Ireadlabel = Label(I2Cframe,text='---')
Ireadlabel.grid(row=2,column=1)

Iscan = Button(I2Cframe,text='I2C Addresses',command=scan).grid(row=3,column=1)
Iscanlabel = Label(I2Cframe,text='---',bd=10)
Iscanlabel.grid(row=4,column=1)

divide = Label(I2Cframe,text='                ').grid(row=1,column=2,rowspan=6,columnspan=2)

# WRITE 8 BIT VALUES TO POTENTIOMETERS
var0 = IntVar()
var1 = IntVar()

def write0():
    gain = var0.get()-1
    apic.writeI2C(gain,0)
def write1():
    width = var1.get()-1
    apic.writeI2C(width,1)

# GAIN POT
W0B = Button(I2Cframe,text='Set Gain Value',command=write0).grid(row=1,column=4,rowspan=2)
W0S = Scale(I2Cframe,orient=HORIZONTAL,tickinterval=32,resolution=1,
    from_=1,to=256,length=300,variable=var0)
W0S.grid(row=1,column=5,rowspan=2)
# THRESHOLD POT
W1B = Button(I2Cframe,text='Set Width Value',command=write1).grid(row=3,column=4,rowspan=2)
W1S = Scale(I2Cframe,orient=HORIZONTAL,tickinterval=32,resolution=1,
    from_=1,to=256,length=300,variable=var1)
W1S.grid(row=3,column=5,rowspan=2)

### ADC Control Frame ###
numadc=StringVar()

def ADCi():
    datapoints = int(numadc.get())          # get desired number of samples from the tkinter text entry
    apic.ADCi(datapoints)                   # take data using ADCi protocol
    adcidata = apic.data
    histogram = plt.Figure(dpi=100)
    global ax1                              # allow changes to ax1 outside of ADCi()
    ax1 = histogram.add_subplot(111)
    hdat = numpy.average(adcidata,axis=1)   # average the ADC peak data over the columns
    #hdat = hdat[hdat!=0]                   # remove zeros
    #hdat = apic.ps_correction(hdat)        # correct to a voltage
    ax1.hist(hdat,200,(100,4000),color='b',edgecolor='black')
    ax1.set_title('Energy Spectrum')
    ax1.set_xlabel('ADC Count')
    ax1.set_ylabel('Counts')
    #plt.savefig('histdata\histogram'+str(apic.raw_dat_count)+'.png')
    apic.raw_dat_count+=1
    bar1 = FigureCanvasTkAgg(histogram, root)
    bar1.get_tk_widget().grid(row=1,column=7,columnspan=1,rowspan=10)
    apic.drain_socket()     # drain socket to clear interrupt overflows


ADCil = Label(ADCframe, text='Interrupt Samples:')
ADCil.grid(row=1,column=1)

ADCie = Entry(ADCframe,textvariable=numadc)
ADCie.grid(row=1,column=2)

ADCout = Button(ADCframe, command=ADCi,text='Start')
ADCout.grid(row=1,column=3)

def pselect():
    apic.polarity(polarity=POL.get())

POL = IntVar()
    
divide = Label(ADCframe,text='Polarity:').grid(row=1,column=5)

# CHANGE CIRCUIT POLARITY
ppolarity = Radiobutton(ADCframe,command=pselect,text='Positive',value=1,variable=POL)
ppolarity.grid(row=2,column=5,sticky=W)
npolarity = Radiobutton(ADCframe,command=pselect,text='Negative',value=0,variable=POL)
npolarity.grid(row=3,column=5,sticky=W)

divide = Label(ADCframe,text='                   ').grid(row=1,
    column=4,rowspan=6)

### DIAGNOSTIC FRAME ###
errorbox = Message(diagnostic,text='Error messages.',
    bg='white',relief=RIDGE,width=220)
errorbox.grid(row=1,column=1)

def f(x,a,b,c):
    return a*x**2 + b*x + c

def calibrate():
    apic.calibration()
    cf1, cf2  = curve_fit(f, apic.inputpulses, apic.outputpulses)
    a,b,c = cf1
    fig = plt.figure()
    global ax2
    ax2 = fig.add_subplot(111)
    ax2.plot(apic.inputpulses,apic.outputpulses,label='raw data')
    ax2.plot(apic.inputpulses,f(apic.inputpulses,a,b,c),label='y=%fx^2 + %fx + %fc' % (a,b,c),linestyle='--')
    ax2.legend()
    fig.savefig('calibration.png')

calibration = Button(diagnostic,text='Gain Calibration',
    command=calibrate)
calibration.grid(row=2,column=1)

progress = ttk.Progressbar(ADCframe,value=0,maximum=100)
progress.grid(row=2,column=1)

### TOP MENU BAR ###
menubar = Menu(root)

# create a pulldown menu, and add it to the menu bar
filemenu = Menu(menubar, tearoff=0)
filemenu.add_command(label="Connect")
filemenu.add_command(label="IP info")
filemenu.add_command(label="Disconnect")
filemenu.add_separator()
filemenu.add_command(label="Exit", command=root.quit)
menubar.add_cascade(label="Connection", menu=filemenu)

helpmenu = Menu(menubar, tearoff=0)
helpmenu.add_command(label="About")
menubar.add_cascade(label="Help", menu=helpmenu)

root.config(menu=menubar)       # display menubar
root.mainloop()                 # run main gui program