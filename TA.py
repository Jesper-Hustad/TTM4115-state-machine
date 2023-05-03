
from mqtt import MQTT 
import PySimpleGUI as sg


MQTT_TOPIC_INPUT = 'ttm4115/17/team17'
MQTT_TOPIC_OUTPUT = 'ttm4115/17/ta'

checkIndex = 0
changed = False
updateCheckmark = ""


def studentSentMessage(mqtt, msg):
    global updateCheckmark, changed
    command = msg.get("command")
    if command == "finished_task":
        taskType =  msg.get("type")
        print("student finished " + taskType)
        updateCheckmark = taskType
        changed = True


mqtt = MQTT()
mqtt.subscribe(MQTT_TOPIC_INPUT, studentSentMessage)


def startRAT():
    mqtt.publish(MQTT_TOPIC_OUTPUT, '{"command" : "request_help", "team": 17}')


checkboxes = [
    'Team needs help',
    'Individual RAT',
    'Team RAT',
    'Task 1',
    'Task 2'
]

text = lambda t: [sg.Text(t, key='-OUT-', enable_events=True, font=('Arial Bold', 16), justification='center', expand_x=True)]


chx = [[sg.Checkbox(x, key=x)] for x in checkboxes]

layout = [
    text("Teaching assistant"),
    [sg.Button("startRAT",size=(20,4))],
    *chx
    ]

window = sg.Window('Multiple Checkboxes and Progress Bar', layout)

while True:

    event, values = window.read(timeout=1000)
    if event == sg.WIN_CLOSED:
        break

    if event == "startRAT":
        mqtt.publish(MQTT_TOPIC_OUTPUT, '{"command" : "start_rat", "team": 17}')
        print("got start RAT command")


    if event == 'Press me':
        window['checkbox'].update(True)

    if changed:
        window[updateCheckmark].update(True)
        changed = False

    if type(event) is None:
        break
        
window.close()


# if(msg.get("command") == "123"):
        #     mqtt.publish(MQTT_TOPIC_OUTPUT, '{"command": "WAS 123"}')