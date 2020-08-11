from simple_pid import PID
import tkinter
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg)
import serial
import time as timeLib
import beepy

###############################
###############################
# setup

#temperature profile
timePoints = [0,260,300,380,400,460]
tempQuidance =[23,140,150,150,160,250]


port = "COM13"

#end of setup
##############################
##############################


def exitHandler():
    print("at exit handler")
    com.close()
    ani.event_source.stop()
    root.destroy()


def startButtonClick():
    print("start")
    ani.event_source.start()


def stopButtonClick():
    print("stop")
    ani.event_source.stop()
    updateHeaterStatus(0)
    ArduinoSend(0)


def ArduinoSend(data):
    com.write(data.to_bytes(1,'big'))

def ArduinoRead():
    if com.in_waiting:
        data = com.read().decode('ascii').strip()
    return data


def ArduinoReadLine():
    if com.in_waiting:
        data = com.readline().decode('ascii').strip()
        data = com.readline().decode('ascii').strip()
        return data


def flushBuffer():
    while com.in_waiting:
        #print ("{} bytes in buffer".format (com.in_waiting))
        ArduinoRead()

def readTemperature():

        flushBuffer()

        ArduinoSend(101)

        while (1):
            while com.in_waiting < 1:
                #print("read temp - com.in_waiting < 1")
                timeLib.sleep(0.1)
                ArduinoSend(101)


            q = ArduinoReadLine()



            if (q.startswith('Temp: ')):
                w = q[6:-1]
                #print("q.startswith('Temp:")
                #print(q)
                return float(w)



def updateTimeLabel(time = -99):
    timeLabel.config(text= "Time: {:.2f}".format (time))

def updateTargetTempLabel(temp = -99) :
    targetTempLabel.config(text="Target temp: \n {} ".format (temp))

def updateCurrentTempLabel(temp = -99) :
    currentTempLabel.config(text="Current temp: \n {} ".format (temp))

def updateHeaterStatus(control):
    if (control > 0):
        heaterStatusLabel.config(text="Heater: \n" + str(control), bg= "lawn green")
    else:
        heaterStatusLabel.config(text="Heater: \n Off", bg= "grey")

def calculateTarget(time):
    global timePoints, tempQuidance, targetTemp,currentTarget

    #find current slope and calculate the target temp
    for i in range (len(timePoints)-1):
        if (timePoints[i] < time < timePoints[i+1]):
            slope = (tempQuidance[i+1] - tempQuidance[i]) / (timePoints[i+1] -timePoints[i])
            currentTarget = (time -timePoints[i]) * slope + tempQuidance[i]
            return currentTarget

    return  currentTarget


def animate(i):
    global timePoints,tempQuidance,timestamps,measuredTemp, time, lastTargetGained
    time = time + 0.2

    targetTemperature = calculateTarget(time)

    if time>timePoints[-1]:
        pid.Kd = 0
        pid.Ki = 0

        if (measuredTemp[-1] > targetTemperature):
            lastTargetGained=True
            targetTemperature = 0
            beepy.beep(sound='ready')

    measuredTemp.append(readTemperature())
    timestamps.append(time)

    if lastTargetGained:
        targetTemperature = 0

    ax.clear()
    ax.plot(timePoints,tempQuidance)
    ax.plot(timestamps, measuredTemp)
    canvas.draw()

    updateTimeLabel(time)


    updateTargetTempLabel(targetTemperature)
    updateCurrentTempLabel(measuredTemp[-1])


    pid.setpoint = targetTemperature
    control = int(pid(measuredTemp[-1]))

    print("time: {:.2f}, targettemp:{}, measuredtemp {}, PID: {}".format (time,targetTemperature,measuredTemp[-1],control))


    ArduinoSend(control)

    updateHeaterStatus(control)


global measuredTemp, timestamps, time, targetTemp,lastTargetGained,currentTarget
time = 0
measuredTemp=[]
timestamps=[]
targetTemp = 0
lastTargetGained = False #used to get last target after time > timepoints[-1] see animate function
currentTarget=0




root=tkinter.Tk()
root.title('Reflow oven controller')
#root.geometry("1600x800")

controlFrame = tkinter.LabelFrame(root,width = 300, borderwidth = 3, padx = 5, pady = 5)
plotFrame = tkinter.LabelFrame(root,padx=5,pady=5)



controlFrame.grid(row = 0, column = 0 )
#controlFrame.grid_propagate(0)
plotFrame.grid(row = 0, column= 1)

timeLabel=tkinter.Label(plotFrame,text = "Time: ")
targetTempLabel = tkinter.Label(plotFrame,text = "Target temp")
currentTempLabel = tkinter.Label(plotFrame,text = "Current temp")
heaterStatusLabel = tkinter.Label(plotFrame,text = "Heater status: \n unknown")
heaterStatusLabel.config(font=("Arial", 20) )

timeLabel.grid(row= 0, column=0)
targetTempLabel.grid(row=0, column= 1)
currentTempLabel.grid(row=0, column= 2)
heaterStatusLabel.grid(row = 0, column = 3)


# serial

baud_rate = 9600

com = serial.Serial()
com.port = port
com.baudrate = baud_rate
com.open()
timeLib.sleep(1)

pid = PID(15,0,90, setpoint=1,output_limits=(0,100))










fig=plt.figure(figsize=(10,6))
ax = fig.add_subplot(1, 1, 1)
canvas = FigureCanvasTkAgg(fig,plotFrame)
canvas.get_tk_widget().grid(row=3,column=0,columnspan = 4)







startButton = tkinter.Button(controlFrame, text = "Start", command = startButtonClick)
stopButton = tkinter.Button(controlFrame, text="Stop", command = stopButtonClick)

startButton.grid(row = 0,column = 0)
stopButton.grid(row = 1 ,column= 0 )


ani = animation.FuncAnimation(fig, animate, interval=200) #run animation every 0.2s, animate func takes care of getting new values and GUI update
ani.event_source.stop()

root.protocol("WM_DELETE_WINDOW", exitHandler)
root.mainloop()