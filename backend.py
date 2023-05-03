import paho.mqtt.client as mqtt
import stmpy
import logging
from threading import Thread
import json
import sys
from collections import deque
from mqtt import MQTT 

MQTT_BROKER = 'mqtt20.iik.ntnu.no'
MQTT_PORT = 1883

MQTT_TOPIC_PREFIX = 'ttm4115/17'

myMqtt = MQTT()
# mqtt.subscribe(MQTT_TOPIC_INPUT, studentSentMessage)

class TeamMachine:
    def __init__(self, team, course_manager):
        self.team = team
        self.course_manager = course_manager
        self.current_task = 0
        self.machine = stmpy.Machine(name=f"team{team}", transitions=[
            {"source": "initial", "target": "working_individual_rat"},
            {"source": "working_individual_rat", "target": "working_team_rat", "trigger": "complete_button", "effect": "request_help()"},
            {"source": "working_team_rat", "target": "working_task", "trigger": "complete_button", "effect": "start_task_timer()"},
            {"source": "working_team_rat", "target": "working_team_rat", "trigger": "ta_response"},
            {"source": "working_task", "target": "awaiting_help", "trigger": "request_help_button"},
            {"source": "working_task", "target": "awaiting_help", "trigger": "task_timer", "effect": "timer_out()"},
            {"source": "awaiting_help", "target": "working_task", "trigger": "dismiss_help_button", "effect": "dismiss_help()"},
            {"source": "awaiting_help", "target": "working_task", "trigger": "ta_response", "effect": "notify_ta_responded(); stop_task_timer()"},
            {"source": "working_task", "target": "working_task", "trigger": "complete_button", "effect": "next_task(); start_task_timer()"},
        ], states=[
            {"name": "awaiting_help", "entry": "request_help()", "task_timer":""}
        ], obj=self)
        
    def notify_ta_responded(self):
        # pass
        output = f"{MQTT_TOPIC_PREFIX}/team{self.team}"
        myMqtt.publish(output, '{"command" : "ta_respond" }')
        # self.course_manager.mqtt_client.publish(f"{MQTT_TOPIC_PREFIX}/team{self.team}", "A TA is on their way", 1)
        
    def start_task_timer(self):
        print(f"(Timer task:{ self.current_task+1} time:{self.course_manager.task_time_estimates[self.current_task]/1000})")
        self.machine.start_timer("task_timer", self.course_manager.task_time_estimates[self.current_task])
        
    def stop_task_timer(self):
        self.machine.stop_timer("task_timer")
        
    def next_task(self):
        self.current_task += 1
        
    def request_help(self):
        self.course_manager.request_help(self.team)
        
    def dismiss_help(self):
        self.course_manager.request_help(self.team)

    def timer_out(self):
        print(f"(Team #{self.team} has spent to much time on task {self.current_task+1})")

class CourseManagerComponent:
    def on_connect(self, client, userdata, flags, rc):
        pass

    def on_request_help(self, payload):
        team = payload["team"]
        self.teams[team].machine.send("request_help_button")
        
    def on_finished_task(self, payload):
        team = payload["team"]
        self.teams[team].machine.send("complete_button")
        
    COMMANDS = {
        "request_help": on_request_help,
        "finished_task": on_finished_task
    }

    def on_message(self, mqtt, payload):
        command = payload.get('command')
        self.COMMANDS[command](self, payload)
        
    def on_button_press(self):
        n = len(self.help_queue)
        if n > 0:
            team = self.help_queue.popleft()
            self.teams[team].machine.send("ta_response")
            print(f"Please help team #{team} 😇")
            if n != 1:
                print("More teams need help (ENTER when ready)")
        else:
            print("✓ no more teams require help ")
        
        
    def request_help(self, team):
        if len(self.help_queue) == 0:
            print("A team needs help (ENTER when ready)")
        self.help_queue.append(team)
        
    def dismiss_help(self, team):
        self.help_queue.remove(team)
        if len(self.help_queue) == 0:
            print("No more teams need help")

    def __init__(self, num_teams):
        myMqtt.subscribe(f"{MQTT_TOPIC_PREFIX}/ta", self.on_message)

        # initialize state machines
        self.stm_driver = stmpy.Driver()
        self.stm_driver.start(keep_active=True)
        self.teams = tuple((TeamMachine(i, self) for i in range(0, num_teams + 1)))
        for team in self.teams:
            self.stm_driver.add_machine(team.machine)
        self.help_queue = deque()

        self.task_time_estimates = [3000] * 10



t = CourseManagerComponent(17)
for _ in sys.stdin:
    t.on_button_press()