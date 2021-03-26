'''
Copyright (c) 2019, NVIDIA CORPORATION. All rights reserved.

NVIDIA CORPORATION and its licensors retain all intellectual property
and proprietary rights in and to this software, related documentation
and any modifications thereto. Any use, reproduction, disclosure or
distribution of this software and related documentation without an express
license agreement from NVIDIA CORPORATION is strictly prohibited.
'''

from engine.pyalice import *
import numpy as np
import math
import random
import numpy as np

import json
import matplotlib.pyplot as plt





class PyController(Codelet):
    def start(self):
        """start up the py_controller codelet and create protos""" 
        # receive protos
        self.rx_robo_pose           = self.isaac_proto_rx("RigidBody3GroupProto",    "bodies")              # from simulation to PyController
        self.rx_env_action_command  = self.isaac_proto_rx("TensorProto",             "env_action_command")  # from env to PyController
        self.rx_env_reset           = self.isaac_proto_rx("TensorProto",             "env_reset")           # from env to PyController
        # transfer protos
        self.tx_joystick_direct     = self.isaac_proto_tx("StateProto",              "diff_command")        # form PyController to simulation
        self.tx_state               = self.isaac_proto_tx("TensorProto",             "state_tensor")        # state tensor to env
        self.tx_teleport_robot      = self.isaac_proto_tx("Pose3dProto",             "teleport_robot")  # Teleport commands

        # configs
        self.update_websight_config()

        # isaac defines
        self.tick_periodically(0.1) # tick every 100 ms

        # store latest pubtimes to prevent operating on old messages
        self.latest_reset_msg_pubtime   = 0
        self.latest_action_msg_pubtime  = 0
        self.robot_translation          = np.array([0,0,0]) # will constantly be updated when a pose message is received
        self.current_action             = np.array([0,0])
        self.current_tick_run               = 0 
        self.next_action_tick           = 0
        self.ticks_per_action           = 10 # this is the number of ticks for which a action will be carried 
        self.current_action_result_sent = False # indicates if a received action has been fully carried out jet



    def send_current_action_to_diffbase(self):
        l, a = self.current_action[0], self.current_action[1]
        self.send_diffbase_command(l,a)

    def tick(self):
        # receive messages
        self.update_websight_config()
        self.process_incoming_messages()

        # constantly send actions to the simulation
        self.send_current_action_to_diffbase()

        # if the current tick is equal to the next action tick (a action from the env was carried out for some time) 
        # then we send back the result of that action to the env (i.e. state, reward, done, info = env.step(action))
        if(self.current_tick_run == self.next_action_tick):
            if(self.current_action_result_sent is not True):
                self.send_state_tensor_to_env() # send the resulting state
                self.publish_current_result()   # send the result "indicates if the state was terminal or not"
                self.current_action_result_sent = True
                self.current_action = np.array([0,0])
        
        self.current_tick_run += 1




    def update_websight_config(self):
        # can be used to get configs from the PyController part in the py_example_task.app.json file
        self.name              = self.config["name"]
        self.start_position    = self.config["start_position"]


    ############## message processing ###############
    def process_incoming_messages(self):
        """ 
        processes all incoming rx_messages 
        is called periodically in the tick() method
        we received messages from the simulation and the env
        
        """ 
        self.process_incoming_pose_message()
        self.process_incoming_env_messages()


    def process_incoming_pose_message(self):
        """recieves a json message containing all object poses and translations"""
        rx_message = self.rx_robo_pose.message
        if rx_message is not None:
            
            pose_json = rx_message.json
            #print(pose_json)
            robot_trans = pose_json['bodies'][0]['refTBody']['translation']
            # print("received a pose message from simulation: ", robot_trans)
            self.robot_translation = np.array([robot_trans['x'],robot_trans['y'],robot_trans['z']])
            rx_message.buffers.clear()

    def process_incoming_env_messages(self):
        #reset message processing
        rx_message = self.rx_env_reset.message
        self.process_env_reset_message(rx_message)


        #action message processing
        rx_message = self.rx_env_action_command.message
        self.process_env_action_message(rx_message)


    def process_env_reset_message(self, rx_message):
        if rx_message is not None:
            if(rx_message.pubtime != self.latest_reset_msg_pubtime):
                    print("received a reset message from the openAI env")
                    self.latest_reset_msg_pubtime = rx_message.pubtime # reset the publish timestamp of the latest message to avoid using this message twice
                    self.reset()
                    self.send_state_tensor_to_env()

    
    def process_env_action_message(self, rx_message):

        if rx_message is not None:
            if(rx_message.pubtime != self.latest_action_msg_pubtime):
                print("received a action message from the openAI env")
                self.latest_action_msg_pubtime  = rx_message.pubtime # reset the publish timestamp of the latest message to avoid using this message twice
                self.current_action_result_sent = False
                self.next_action_tick           = self.current_tick_run + self.ticks_per_action
                self.current_action             = rx_message.tensor[0]
                print("current action tick: ", self.current_tick_run, "next tick: ", self.next_action_tick)
    
       

    def publish_current_result(self):
        "sends a dummy result indicator"
        dummy_result = 0
        send_msg = Message.create_message_builder("TensorProto")
        send_msg.proto.elementType = "int32"
        send_msg.proto.sizes = [1, 1]
        send_msg.proto.dataBufferIndex = 0
        send_msg.buffers = [np.array([dummy_result]).astype(np.int32)]
        self.app.publish("py_controller", "PyCodelet",  "result", send_msg)


    def teleport_to_position(self,x,y,z):
        proto_msg = self.tx_teleport_robot.init()
        proto_msg.proto.translation.x = x
        proto_msg.proto.translation.y = y
        proto_msg.proto.translation.z = z
        proto_msg.proto.rotation.q.w = 0
        proto_msg.proto.rotation.q.x = 0
        proto_msg.proto.rotation.q.y = 0
        proto_msg.proto.rotation.q.z = 0
        self.tx_teleport_robot.publish()


    ############## sending of commands ###############

    def send_diffbase_command(self, linear, angular):
    #Sends a target linear and angular velocity on the diff_command topic
        action = np.array([linear,angular])
        send_msg                        = Message.create_message_builder("TensorProto")
        send_msg.proto.elementType      = "float64"
        send_msg.proto.sizes            = action.shape
        send_msg.proto.dataBufferIndex  = 0
        send_msg.buffers                = [action.astype(np.float)]
        
        self.app.publish("py_controller", "PyCodelet",  "diff_command", send_msg)

    def send_state_tensor_to_env(self):
    # sends a dummy state to the env (used in step() )
        dummy_state = np.array([self.robot_translation[0],self.robot_translation[1]]) 
        send_msg                        = Message.create_message_builder("TensorProto")
        send_msg.proto.elementType      = "float64"
        send_msg.proto.sizes            = dummy_state.shape
        send_msg.proto.dataBufferIndex  = 0
        send_msg.buffers                = [np.array(dummy_state).astype(np.float64)]
        self.app.publish("py_controller", "PyCodelet",  "state_tensor", send_msg)

    def reset(self):
        # dummy reset function, in this case it just teleports the robot to a starting position
        self.teleport_to_position(self.start_position[0],self.start_position[1],self.start_position[2])
        return 0

