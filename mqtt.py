import paho.mqtt.client as mqtt
import stmpy
import logging
from threading import Thread
import json

MQTT_BROKER = 'mqtt20.iik.ntnu.no'
MQTT_PORT = 1883

MQTT_TOPIC_INPUT = 'ttm4115/team_x/command'

# MQTT_TOPIC_OUTPUT = 'ttm4115/team_x/answer'
MQTT_TOPIC_OUTPUT = 'ttm4115/team_x/command'


class MQTT:


    def on_connect(self, client, userdata, flags, rc):
        pass
        # self._logger.debug('MQTT connected to {}'.format(client))


    def publish(self,output,  msg):
        self.mqtt_client.publish(output, msg)


    # get subscribed messages in JSON format
    def on_message(self, client, userdata, msg):
        message = msg.payload.decode("utf-8")
        # print("Recieved message :\n" + message)
        try:
            payload = json.loads(msg.payload.decode("utf-8"))
        except Exception as err:
            print("error in JSON format")
            # self._logger.error('Message sent to topic {} had no valid JSON. Message ignored. {}'.format(msg.topic, err))
            return
        self.custom_callback(self, payload)
        

    def subscribe(self, input, custom_callback):
        self.mqtt_client.subscribe(input)
        self.custom_callback = custom_callback


    def __init__(self):
        # get the logger object for the component
        # self._logger = logging.getLogger(__name__)
        # print('logging under name {}.'.format(__name__))
        # self._logger.info('Starting Component')

        # input and output
        self.input = input

        # create a new MQTT client
        # self._logger.debug('Connecting to MQTT broker {} at port {}'.format(MQTT_BROKER, MQTT_PORT))
        self.mqtt_client = mqtt.Client()
        # callback methods
        self.mqtt_client.on_connect = self.on_connect
        # self.custom_callback = custom_callback
        self.mqtt_client.on_message = self.on_message
        # Connect to the broker
        self.mqtt_client.connect(MQTT_BROKER, MQTT_PORT)
        # subscribe to proper topic(s) of your choice
        # self.mqtt_client.subscribe("ttm4115/team_x/command")
        # start the internal loop to process MQTT messages
        self.mqtt_client.loop_start()

        # we start the stmpy driver, without any state machines for now
        self.stm_driver = stmpy.Driver()
        self.stm_driver.start(keep_active=True)
        # self._logger.debug('Component initialization finished')



    def stop(self):
        """
        Stop the component.
        """
        # stop the MQTT client
        self.mqtt_client.loop_stop()

        # stop the state machine Driver
        self.stm_driver.stop()


# logging.DEBUG: Most fine-grained logging, printing everything
# logging.INFO:  Only the most important informational log items
# logging.WARN:  Show only warnings and errors.
# logging.ERROR: Show only error messages.



# LOGGING
# debug_level = logging.DEBUG
# logger = logging.getLogger(__name__)
# logger.setLevel(debug_level)
# ch = logging.StreamHandler()
# ch.setLevel(debug_level)
# formatter = logging.Formatter('%(asctime)s - %(name)-12s - %(levelname)-8s - %(message)s')
# ch.setFormatter(formatter)
# logger.addHandler(ch)
