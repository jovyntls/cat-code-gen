import os
from dotenv import load_dotenv
import dill
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
    last_message = str(msg.payload) + str(datetime.now())
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
        self.in_loop = False
    def assign_variable(self, varname, value, vartype=None):
        if varname in self.variables:
            self.variables[varname].reassign(value, vartype)
        else:
            self.variables[varname] = Variable(varname, value, vartype)
    def get_new_var_name(self):
        return chr(len(self.variables) + 97)

class Variable:
    def __init__(self, varname, value, vartype):
        self.varname = varname
        self.value = value
        self.vartype = vartype
    def reassign(self, value, vartype):
        self.value = value
        if vartype != None: self.vartype = vartype

class VariableAssignment():
    TOTAL_STAGES = 3

    def __init__(self):
        self.current_stage = 0
        self.var_type = None
        self.var_name = None
        self.var_value = None

    def execute(self, num, stack, env):
        if self.current_stage == 0: stack += [self.execute]*(VariableAssignment.TOTAL_STAGES)
        self.current_stage += 1
        if self.current_stage > VariableAssignment.TOTAL_STAGES:
            return self.close(num, stack, env)
        elif self.current_stage == 1:
            return self.choose_type(num)
        elif self.current_stage == 2:
            return self.choose_varname(num, env)
        elif self.current_stage == 3: 
            return self.choose_value(num, stack, env)

    def choose_type(self, num):
        self.var_type = Type.get_type(num)
        return ''

    def choose_varname(self, num, env):
        # randomly selects one from the env, or a new one
        var_names_in_env = [v.varname for v in env.variables.values()]
        if num == 0: # new variable
            new_var_name = chr(97 + len(var_names_in_env))
        else:
            selected = (num-1) % len(var_names_in_env) 
            new_var_name = var_names_in_env[selected]
        self.var_name = new_var_name
        return '\t'*env.indent_level + f'{self.var_name} = '

    def choose_value(self, num, stack, env):
        var = self.var_type()
        return var.execute(num, stack, env)

    def close(self, num, stack, env):
        env.assign_variable(self.var_name, self.var_value, vartype=self.var_type)
        next_node = choose_one_or_none_from(num, Nodes.nodes)
        if next_node != None: stack.append(next_node().execute)
        return '\n'

class Number:
    TOTAL_STAGES = 1
    def __init__(self):
        self.current_stage = 0
    def execute(self, num, stack, env):
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
    def execute(self, num, stack, env):
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
    def execute(self, num, stack, env):
        self.current_stage += 1
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
    def execute(self, num, stack, env):
        self.current_stage += 1
        if self.current_stage == 1:
            return self.get_size(num, stack)
        if self.current_stage == 2:
            return self.get_type(num)
        if self.current_stage == 3:
            return self.get_value(num, stack, env)
        if self.current_stage < self.size + 2:
            return ', ' + self.get_value(num, stack, env)
        if self.current_stage == self.size + 2:
            return ', ' + self.get_value(num, stack, env) 
        if self.current_stage > self.size + 2:
            return self.close()
    def get_type(self, num):
        self.type = Type.get_type(num)
        return '['
    def get_size(self, num, stack):
        self.size = num
        stack += [self.execute]*(self.size + 2)
        return ''
    def get_value(self, num, stack, env):
        return self.type().execute(num, stack, env) 
    def close(self):
        return ']'

class Type:
    types = [Number, String, Boolean, Array]

    def get_type(num):
        return choose_from(num, Type.types)

class Function:
    def __init__(self):
        self.current_stage = 0
        self.num_params = None
    def execute(self, num, stack, env):
        self.current_stage += 1
        if self.current_stage == 1:
            return self.get_num_params(num, stack)
        if self.current_stage == 2:
            return '(' + self.init_params(num, env)
        if self.current_stage > 1 and self.current_stage <= self.num_params + 1:
            return ', ' + self.init_params(num, env)
        if self.current_stage == self.num_params + 2:
            return self.close(num, stack, env)
        if self.current_stage == self.num_params + 3:
            return self.return_statement(num, env)
    def get_num_params(self, num, stack):
        self.num_params = num
        stack += [self.execute]*(self.num_params + 1)
        return 'def function_name'
    def init_params(self, num, env):
        # assume we start with no other params
        var_name = env.get_new_var_name()
        var_type = Type.get_type(num)
        env.assign_variable(var_name, None, vartype=var_type)
        return var_name
    def close(self, num, stack, env):
        next_node = choose_from(num, Nodes.nodes)
        stack.append(next_node().execute)
        env.indent_level += 1
        return '):\n'
    def return_statement(self, num, env):
        var_to_return = choose_from(num, env.variables.values())
        return '\t'*env.indent_level + 'return ' + var_to_return.varname


class ExecutableStatement:
    def __init__(self):
        self.current_stage = 0
        self.statement_type = None
    def execute(self, num, stack, env):
        self.current_stage += 1
        if env.in_loop:
            if num%2 == 0: stack.append(LoopControlStatement().execute)
            else: stack.append(PrintStatement().execute)
        else:
            stack.append(PrintStatement().execute)
        return ''

class LoopControlStatement:
    def __init__(self):
        self.current_stage = 0
    def execute(self, num, stack, env):
        if num % 2 == 0: return '\t'*env.indent_level + 'continue\n'
        else: return '\t'*env.indent_level + 'break\n'

class PrintStatement:
    def __init__(self):
        self.current_stage = 0
    def execute(self, num, stack, env):
        self.current_stage += 1
        if self.current_stage == 1:
            return self.choose_printable(num, stack, env)
        if self.current_stage == 2:
            return self.close(num, stack)
    def choose_printable(self, num, stack, env):
        num_vars = len(env.variables)
        to_print = list(env.variables.keys())[num % num_vars]
        stack.append(self.execute)
        return '\t'*env.indent_level + 'print(' + str(to_print)
    def close(self, num, stack):
        next_node = choose_one_or_none_from(num, Nodes.nodes)
        if next_node != None: stack.append(next_node().execute)
        return ')\n'

class Expression:
    # takes the form of A op B; for simplicity ensures A and B are of the same type
    ops = ['>', '<', '==', '+', '%', '//', '-', '/', '*']
    def __init__(self):
        self.current_stage = 0
        self.lhs_type = None
        self.lhs = None
    def execute(self, num, stack, env):
        self.current_stage += 1
        if self.current_stage == 1:
            return self.choose_lhs(num, stack, env)
        if self.current_stage == 2:
            return self.choose_op(num)
        if self.current_stage == 3:
            return self.choose_rhs(num, stack, env)
    def choose_lhs(self, num, stack, env):
        stack += [self.execute]*2
        self.lhs = choose_from(num, env.variables.values())
        self.lhs_type = self.lhs.vartype
        return self.lhs.varname
    def choose_op(self, num):
        self.op = choose_from(num, Expression.ops)
        return ' ' + self.op + ' '
    def choose_rhs(self, num, stack, env):
        possible_variables = [v for v in env.variables.values() if v.vartype == self.lhs_type] 
        if num == 0: # use a new literal instead
            stack.append(self.lhs_type().execute)
            return ''
        else:
            return choose_from(num, possible_variables).varname

class WhileBlock:
    def __init__(self):
        self.current_stage = 0
    def execute(self, num, stack, env):
        self.current_stage += 1
        if self.current_stage == 1:
            stack += [self.execute, Expression().execute]
            env.in_loop = True
            return '\t'*env.indent_level + 'while ' 
        if self.current_stage == 2:
            stack.append(self.execute)
            return self.next_line(num, stack, env)
        if self.current_stage == 3:
            return self.close(num, stack, env)
    def next_line(self, num, stack, env):
        next_node = choose_from(num, Nodes.nodes)
        stack.append(next_node().execute)
        env.indent_level += 1
        return ':\n'
    def close(self, num, stack, env):
        env.indent_level -= 1
        env.in_loop = False
        next_node = choose_from(num, Nodes.nodes)
        stack.append(next_node().execute)
        return ''

class IfElseBlock:
    def __init__(self):
        self.current_stage = 0
    def execute(self, num, stack, env):
        self.current_stage += 1
        if self.current_stage == 1:
            stack += [self.execute, self.execute, Expression().execute]
            return '\t'*env.indent_level + 'if ' 
        if self.current_stage == 2:
            return self.next_line(num, stack, env)
        if self.current_stage == 3:
            return self.else_block(num, stack, env)
        if self.current_stage == 4:
            return self.close(num, stack, env)
    def next_line(self, num, stack, env):
        next_node = choose_from(num, Nodes.nodes)
        stack.append(next_node().execute)
        env.indent_level += 1
        return ':\n'
    def else_block(self, num, stack, env):
        stack.append(self.execute)
        next_node = choose_from(num, Nodes.nodes)
        stack.append(next_node().execute)
        return '\t'*(env.indent_level - 1) + 'else: \n'
    def close(self, num, stack, env):
        env.indent_level -= 1
        next_node = choose_one_or_none_from(num, Nodes.nodes)
        if next_node != None: stack.append(next_node().execute)
        return ''

class Nodes:
    nodes = [ExecutableStatement, VariableAssignment, WhileBlock, IfElseBlock]

class Cat:
    def __init__(self):
        self.env = Environment()
        self.stack = []
        self.code = ''

def choose_from(num, arr):
    arr = list(arr)
    return arr[num % len(arr)]

def choose_one_or_none_from(num, arr):
    if num == 0: return None
    else: return choose_from(num, arr)

def retrieve_object():
    with open('my_c.pik', "rb") as f:
        cat = dill.load(f)
    return cat

def save_object(cat):
    with open('my_c.pik', "wb") as f:
        dill.dump(cat, f)
    return


global cat 
cat = Cat()
save_object(cat)

app = Flask(__name__)
print('app')

client.loop_start()

@app.route("/")
def index():
    return "Hello World!"

@app.route("/code", methods=["POST"])
def get_code():
    global cat
    if not cat.stack:
        starting_function = Function()
        cat.stack.append(starting_function.execute)
        cat.stack.append(starting_function.execute)
        save_object(cat)
    cat = retrieve_object()
    ex = cat.stack.pop()
    additional = ex(int(request.args['in']), cat.stack, cat.env)
    cat.code += additional
    save_object(cat)
    return cat.code

@app.route("/reset")
def reset_code():
    # s[0] = ''
    cat.code = ''
    vv = VariableAssignment(cat.env)
    cat.stack = [vv.execute]
    return ''

@app.route("/mqtt")
def get_last_message():
    print('/mqtt last message: ', last_message)
    print_something()
    return last_message

