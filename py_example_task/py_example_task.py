import numpy as np
import gym
import torch
from gym import spaces
from engine.pyalice import *
from PyController import PyController
from threading import Thread
import time
import subprocess
import json


class ExampleTaskENV(gym.Env):
  """
  Custom Environment that follows gym interface.
  This is a simple env where the agent must learn to go always left. 
  """
  # Because of google colab, we cannot implement the GUI ('human' render mode)
  metadata = {'render.modes': ['console']}
  # Define constants for clearer code

  def __init__(self, isaac_app, input_shape):
    super(ExampleTaskENV, self).__init__()

    # set the isaac controller here
    self.isaac_app            = isaac_app
    self.latest_state_pubtime = 0
    self.latest_result_pubtime= 0
    self.input_shape          = input_shape

    # Define action and observation space
    # They must be gym.spaces objects
    # In the lidar task that translates to an array which contains all the lidar beams as well as (current vel, position, ray to goal etc.)

    high = np.array([np.inf] * self.input_shape)
    # our actions are continuous now, i.e. linear and angular velocity for the isaac joystick command in the range between -1 and 1
    self.action_space      = spaces.Box(np.array([-1, -1]), np.array([1, 1]), dtype=np.float32)
    self.observation_space = spaces.Box(-high, high, dtype=np.int32)
    
  
  def reset(self, test=False):
    """
    Important: the observation must be a numpy array
    :return: (np.array) 
    """
    self.current_reward       = 0
    self.previous_action      =  np.array([0,0])
    # send the reset message - notice the [1] is tells the py_controller to reset
    reset_msg = self.tensor_buffer(buffers=np.array([1]).astype(np.float32))
    if(test):
      reset_msg = self.tensor_buffer(buffers=np.array([-1]).astype(np.float32))
    self.isaac_app.publish("py_controller", "PyCodelet",  "env_reset", reset_msg) 

    # wait for a reply from the simulation
    state_buffer = self.get_valid_buffer("py_controller", "PyCodelet", "state_tensor", self.latest_state_pubtime)
    

    #save the state pubtime
    self.latest_state_pubtime = state_buffer.pubtime # reset the publish timestamp of the latest message to avoid using this message twice
    state_tensor = np.frombuffer(state_buffer.buffers[0], dtype=np.uint16)
    state_tensor = np.array(state_tensor).astype(np.int32)
    time.sleep(0.05)
    return state_tensor

  def get_valid_buffer(self, node, component, tag, pubtime):
    """warning this cycle blocks until a valid buffer was received"""
    buffer = self.isaac_app.receive(node,component,tag)
    while(buffer is None):
      time.sleep(0.05)
      buffer = self.isaac_app.receive(node,component,tag)
    while(pubtime == buffer.pubtime):
      buffer = self.isaac_app.receive(node,component,tag)
      time.sleep(0.05)
    return buffer


  def step(self, action):
    done = 0
    reward = 0

    #publish action message
    action = np.array(action)
    action_message = self.tensor_buffer(sizes=[1,action.shape[0]] ,buffers=action.astype(np.float32),elementType="float32")
    self.isaac_app.publish("py_controller", "PyCodelet",  "env_action_command", action_message) 

    #### now the controller has finished its action, therefore we can receive the current state as our resulting observation
    # wait for a reply from the simulation
    state_buffer = self.get_valid_buffer("py_controller", "PyCodelet", "state_tensor", self.latest_state_pubtime)
    # save the state pubtime
    self.latest_state_pubtime = state_buffer.pubtime # reset the publish timestamp of the latest message to avoid using this message twice
    # cast the buffer to a tensor, this is our observation resulting from the given action
    state_tensor = np.frombuffer(state_buffer.buffers[0], dtype=np.uint16)
    state_tensor = np.array(state_tensor).astype(np.int32)

    #### now we check the result 
    # wait for a reply from the simulation
    result_buffer = self.get_valid_buffer("py_controller", "PyCodelet", "result", self.latest_result_pubtime)
    # save the result pubtime
    self.latest_result_pubtime = result_buffer.pubtime # reset the publish timestamp of the latest message to avoid using this message twice
    # cast the buffer to a tensor, this is our observation resulting from the given action
    result_tensor = np.frombuffer(result_buffer.buffers[0], dtype=np.int32)
    
    # do something with your reward
    reward = 0.1
  

    done   = 1   if (result_tensor[0]==1)  else 0
    # Optionally we can pass additional info
    info = {}
    return state_tensor, self.current_reward, done, info

  def render(self, mode='console'):
    """
        We are using the unity3d simulation for rendering therefore this functions simply retruns NotImplementedError
    """
    raise NotImplementedError()


  def close(self):
    """closing is also not supported because of the unity3d environment"""
    pass

  def tensor_buffer(self, sizes=[1,1],buffers=np.array([1]).astype(np.float32), elementType="float32"):
    ## use this function to create a Tensor proto message for communication with isaac
    send_msg = Message.create_message_builder("TensorProto")
    send_msg.proto.elementType = elementType
    send_msg.proto.sizes = sizes
    send_msg.proto.dataBufferIndex = 0
    send_msg.buffers = [buffers]
    return send_msg



app = Application("apps/py_example_task/py_example_task.app.json")

def main():
  #create application and create node
  
  app.nodes["py_controller"].add(PyController)
 
  
  #receive messages
  app.connect('simulation.interface/output',                             'bodies',              'py_controller/PyCodelet',    'bodies')
  app.connect("simulation.interface/input",                              'base_command',        'py_controller/PyCodelet',    'base_command')


  #send control messages
  app.connect('py_controller/PyCodelet',                                'diff_command',         'simulation.interface/input',                     'base_command')
  app.connect('py_controller/PyCodelet',                                'teleport_robot',       'Teleportation/Teleport_robot',                   'relative_frame')
  app.start_wait_stop()



from numpy import savetxt
from datetime import datetime

if __name__ == '__main__':
    # we start the isaac application in a seperate thread:
    isaac_thread = Thread(target=main,args=())
    isaac_thread.start()
    time.sleep(1)

    # we initialize the env with a reference to our isaac app:
    env = ExampleTaskENV(app,36)


    ### and we start with basic interaction:

    state = env.reset()
    print("received state from env: ", state)
    state_after_action = env.step([1,0])
    print("received state after action: ", state_after_action)



    print("now we randomly sample actions and print the result")

    for x in range(10):
      for i in range(100):
        rnd_action = np.random.random(2)*2 -1
        state = env.step(rnd_action)
      env.reset()


    


    





