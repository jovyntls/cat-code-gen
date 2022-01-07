import os
from dotenv import load_dotenv
from flask import Flask
from flask import request
import paho.mqtt.client as paho
from paho import mqtt
from datetime import datetime

load_dotenv()
MQTT_USERNAME = os.getenv('MQTT_USERNAME')
MQTT_PASSWORD = os.getenv('MQTT_PASSWORD')
MQTT_HOST = os.getenv('MQTT_HOST')

# ------------ MQTT STUFF ----------------
def on_connect(client, userdata, flags, rc, properties=None):
    print("CONNACK received with code %s." % rc)
def on_publish(client, userdata, mid, properties=None):
    print("mid: " + str(mid))
def on_subscribe(client, userdata, mid, granted_qos, properties=None):
    print("Subscribed: " + str(mid) + " " + str(granted_qos))
def on_message(client, userdata, msg):
    global last_message
    last_message = str(msg.payload)
    print("Message received: " + msg.topic + " " + str(msg.qos) + " " + str(msg.payload))
def print_something():
    print('test print' + str(datetime.now()) + last_message)

client = paho.Client(client_id="", userdata=None, protocol=paho.MQTTv5)
client.on_connect = on_connect
client.tls_set(tls_version=mqtt.client.ssl.PROTOCOL_TLS)
client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
client.connect(MQTT_HOST, 8883)
client.on_subscribe = on_subscribe
client.on_message = on_message
client.on_publish = on_publish
# subscribe to all topics of sensor by using the wildcard "#"
client.subscribe("sensor/#", qos=1)
# a single publish, this can also be done in loops, etc.
client.publish("sensor/temperature", payload="hot", qos=1)

# ----------------------------------------

class Environment:
    def __init__(self):
        self.indent_level = 0
        self.variables = {}

class Node:
    def __init__(self, env):
        self.neighbours = []
        self.env = env

class VariableAssignment(Node):
    TOTAL_STAGES = 3
    neighbours = [1]

    def __init__(self, env):
        super(VariableAssignment, self).__init__(env)
        self.current_stage = 0
        self.var_type = None
        self.var_name = None
        self.var_value = None

    def execute(self, num, stack):
        if self.current_stage == 0: stack += [self.execute]*(VariableAssignment.TOTAL_STAGES - 1)
        self.current_stage += 1
        if self.current_stage > VariableAssignment.TOTAL_STAGES:
            return self.close()
        elif self.current_stage == 1:
            return self.choose_type(num)
        elif self.current_stage == 2:
            return self.choose_varname(num)
        elif self.current_stage == 3: 
            return self.choose_value(num, stack)

    def choose_type(self, num):
        self.var_type = Type.get_type(num)
        return ''

    def choose_varname(self, num):
        # TODO: generate this from string
        self.var_name = 'PLACEHOLDER_VARNAME'
        return '\t'*self.env.indent_level + f'{self.var_name} = '

    def choose_value(self, num, stack):
        var = self.var_type()
        return var.execute(num, stack)

    def close(self):
        # TODO: select next thing based on num and add to stack
        return '\n'

class Number:
    TOTAL_STAGES = 1
    def __init__(self):
        self.current_stage = 0
    def execute(self, num, stack):
        self.current_stage += 1
        if self.current_stage > 1:
            return self.close()
        if self.current_stage == 1:
            return self.get_value(num)
    def get_value(self, num):
        return str(num)
    def close(self):
        return ''

class String:
    def __init__(self):
        self.current_stage = 0
        self.size = None
    def execute(self, num, stack):
        self.current_stage += 1
        if self.current_stage == 1:
            return self.get_size(num, stack)
        if self.current_stage > self.size + 1:
            return self.close()
        if self.current_stage > 1:
            return self.get_value(num)
    def get_size(self, num, stack):
        self.size = num
        stack += [self.execute]*(self.size + 1)
        return '"'
    def get_value(self, num):
        return chr(num + 97)  # pad to start at 'a'
    def close(self):
        return '"'

class Boolean:
    TOTAL_STAGES = 1
    def __init__(self):
        self.current_stage = 0
    def execute(self, num, stack):
        self.current_stage += 1
        # if self.current_stage > 1:
        #     return self.close()
        if self.current_stage >= 1:
            return self.get_value(num) + self.close()
    def get_value(self, num):
        return 'True' if num % 2 == 0 else 'False'
    def close(self):
        return ''

class Array:
    def __init__(self):
        self.current_stage = 0
        self.size = None
        self.type = None
    def execute(self, num, stack):
        self.current_stage += 1
        if self.current_stage == 1:
            return self.get_size(num, stack)
        if self.current_stage == 2:
            return self.get_type(num)
        if self.current_stage == 3:
            return self.get_value(num, stack)
        if self.current_stage < self.size + 2:
            return ', ' + self.get_value(num, stack)
        if self.current_stage == self.size + 2:
            return ', ' + self.get_value(num, stack) 
        if self.current_stage > self.size + 2:
            return self.close()
    def get_type(self, num):
        self.type = Type.get_type(num)
        return '['
    def get_size(self, num, stack):
        self.size = num
        stack += [self.execute]*(self.size + 2)
        return ''
    def get_value(self, num, stack):
        # TODO: add to queue n*
        value = "PLACEHOLDER_ARR_VALUE"
        return self.type().execute(num, stack) 
    def close(self):
        return ']'

class Type:
    types = [Number, String, Boolean, Array]

    def get_type(num):
        return Type.types[num%len(Type.types)]

class Function:
    def __init__(self):
        self.current_stage = 0
        self.num_params = None
    def execute(self, num, stack):
        self.current_stage += 1
        if self.current_stage == 1:
            return self.get_num_params(num, stack)
        if self.current_stage > 1 and self.current_stage <= self.num_params + 1:
            return self.get_param_type(num)
        if self.current_stage > self.num_params + 1:
            return self.close()
    def get_num_params(self, num, stack):
        self.num_params = num
        stack += [self.execute]*(self.num_params + 1)
    def get_param_type(self,env):
        pass

class Cat:
    def __init__(self):
        self.env = Environment()
        self.stack = []


global cat 
global s
cat = Cat()
s = ['']

app = Flask(__name__)

# client.loop_start()

@app.route("/")
def index():
    return "Hello World!"

@app.route("/code", methods=["POST"])
def get_code():
    if not cat.stack:
        s[0] = ''
        vv = VariableAssignment(cat.env)
        cat.stack.append(vv.execute)
    ex = cat.stack.pop()
    additional = ex(int(request.args['in']), cat.stack)
    s[0] += additional
    return s[0]

@app.route("/reset")
def reset_code():
    s[0] = ''
    vv = VariableAssignment(cat.env)
    cat.stack = [vv.execute]
    return ''

@app.route("/mqtt")
def get_last_message():
    print('/mqtt last message: ', last_message)
    print_something()
    return last_message

