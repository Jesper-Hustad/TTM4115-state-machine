
import PySimpleGUI as sg
from mqtt import MQTT 

# sg.theme("SystemDefault1")
sg.theme("SystemDefaultForReal")

team_number = int(input("WRITE TEAM NUMBER: "))

MQTT_TOPIC_INPUT = f'ttm4115/17/team{team_number}'
MQTT_TOPIC_OUTPUT = 'ttm4115/17/ta'


mqtt = MQTT()

ratStarted = False
# secondsLeft = 60 * 10
TIMER_AMOUNT = 60 * 10
secondsLeft = TIMER_AMOUNT
currentTask = 1
ta_coming = False

def TASentMessage(mqtt, msg):
    global ratStarted, ta_coming
    command = msg.get("command")
    if command == "start_rat":
        print("rat started")
        ratStarted = True
    if command == "ta_respond":
        print("TA is coming!")
        ta_coming = True

mqtt.subscribe(MQTT_TOPIC_INPUT, TASentMessage)

def resetTimer():
    global secondsLeft
    secondsLeft = TIMER_AMOUNT

def getTimeString(sec):
    minutes = secondsLeft // 60
    seconds = secondsLeft - minutes*60
    return str(minutes) + ":" + str(seconds)

def requestHelp():
    mqtt.publish(MQTT_TOPIC_OUTPUT, '{"command" : "request_help", "team": '+str(team_number)+'}')

def progress_update():
    # print("progress update")
    # global currentTask
    # currentTask = 1 + checkboxes.index(type)
    resetTimer()
    mqtt.publish(MQTT_TOPIC_OUTPUT, '{"command" : "finished_task", "team":'+str(team_number)+'}')

buttons = {
    '❗ Request help': lambda: requestHelp(),
    '✅ Finished Task' : lambda: progress_update()
    }   


checkboxes = [
    'Team needs help',
    'Finished Task',
]

createButton = lambda name: [sg.Button(name,size=(15,2),font=('Arial Bold', 19))]
buttonLayout = [[createButton(x)] for x in buttons.keys()]

text = lambda t, k=" ": [sg.Text(t, key=k, enable_events=True, font=('Arial Bold', 19), justification='center', expand_x=True)]

layout = [
    text("Team " + str(team_number)),
    text("", "-TASK-"),
    # text("TIME REMAINING:"),
    text("--------", "-TIMER-"),
    *buttonLayout
]


window = sg.Window('Multiple Checkboxes and Progress Bar', layout)




while True:

    event, values = window.read(timeout=1000)
    if event == sg.WIN_CLOSED:
        break

    # if ratStarted:
    #     if secondsLeft == 0 and currentTask <= len(checkboxes):
    #         resetTimer()
    #         currentTask+=1
    #         window["-TIMER-"].update("Timer completed")
    #     else:
    #         secondsLeft -= 1
    #         window["-TIMER-"].update(getTimeString(secondsLeft))

    ta_status = "TA is coming" if ta_coming else "---"
    window["-TIMER-"].update(ta_status)
    
    # window["-TASK-"].update(checkboxes[currentTask])

    if event in buttons.keys():
        ta_coming = False
        buttons[event]()

    if type(event) is None:
        break
        
window.close()
# if(msg.get("command") == "123"):
        #     mqtt.publish(MQTT_TOPIC_OUTPUT, '{"command": "WAS 123"}')