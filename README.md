# Visual_Navigation_RL

# Hello, This repository is a introduction to learned visual navigation based on the IsaacSDK and Isaac Sim! <img src="https://raw.githubusercontent.com/MartinHeinz/MartinHeinz/master/wave.gif" width="30px">

## This Tutorial gives hints about how to combine OpenAI Gym [1] and the Nvidia IsaacSDK [2] 
### PLEASE BE AWARE THAT THE ISAAC SDK REQUIRES A MEMBERSHIP WHICH CAN BE OBTAINED HERE:  https://developer.nvidia.com/login


Once you have created a developer account, you will have access to all resources that will be needed to implement basic interaction between your Reinforcement Learning 
Algorithms and the Isaac SDK & Sim.

# Prerequisites
## We will use a archived version of the Isaac SDK: 2020.1 since version 2020.2 introduced many structural changes to the SDK




First you will have to download both the Isaac SDK and the IsaacSim which you can find here:
https://developer.nvidia.com/isaac/downloads (klick on "archive" to find previous versions)


Once you have downloaded the Isaac SDK, you can extract it to a folder of your choice. You will find a script called  **/isaac/engine/build/scripts/install_dependencies.sh**
that automatically installs all dependencies on your system
### While the installation is pretty well documented we will still give some recommendations here


* Currently only Ubuntu 18.04 LTS is supported
* Please make sure to install recent NVIDIA graphics card drivers on your workstation -> version 440 is recommended
* In our case CUDA 10.1 has shown to be the most stable version 
* To be able to create you own environments you will have to create a Unity account and install UnityHub : https://id.unity.com/en/conversations/951360fa-40fa-4423-919f-a349bf23a3a401af  https://forum.unity.com/threads/unity-hub-v-1-3-2-is-now-available.594139/


After you completed the installation process, you can run one of the many sample applications provided by the SDK by running the **bazel run** command
**inside of your isaac folder** for example:

```
bob@desktop:~/isaac$ bazel run //apps/samples/stereo_dummy
```



## Setting up your environment in Unity

The introduced message protos for the communication with the Isaac Sim need to be specified inside of the Unity App. You can find more information about how to use the Unity
App here: https://docs.nvidia.com/isaac/archive/2020.1/doc/simulation/unity3d.html#getting-started-with-editor-mode



![Unity Robot](https://github.com/BeneHei/Visual_Navigation_RL/blob/main/Unity_Robot.PNG)

You can find the Str robot inside **Packages/NVIDIA Isaac Sim for Unity 3d (Samples)/Robots** it comes equipped with two Lidar sensors, a frontal RGB-D camera and 
a differential drive base simulation

![Unity Topics1](https://github.com/BeneHei/Visual_Navigation_RL/blob/main/Unity_Topic.PNG)

If you want to know where to send, or where to receive messages you can simply leftklick on the corresponding sensors, here we highlight where to receive the images of the color
camera. Camera images can thus be received under **navsim/output/color**. 

![Unity Topics2](https://github.com/BeneHei/Visual_Navigation_RL/blob/main/Unity_Topic_receiver.PNG)

Messages that controll the STR robot have to be sent to **navsim/input/base_command**
If you want these topics to have different names you can simply change them inside the unity editor. 

Even simpler is the use of the already provided **small_warehouse** scene, this scene comes with almost everything you need to try out our example project.
You just have to add a **Teleport script** to the robot you want to teleport when the reset function is triggered. In the end your robot should have the following 
parts:


![Unity Topics3](https://github.com/BeneHei/Visual_Navigation_RL/blob/main/Unity_topics_example_project.png)

### After you finished creating your unity environment in the editor mode, we recommend building the application

https://docs.nvidia.com/isaac/archive/2020.1/doc/simulation/unity3d.html#build

When the build process is finished, you can run your environment with the **--timeScale** command, which basically scales the speed of the physics computation. 


# Your first Project

Now we will show you a exemplary basic interaction project using python, Isaac and Isaac Sim. In this repository you will find a very basic example 
on how to create a RL state flow. But first we recommend working through the basic getting started part of the isaac SDK
https://docs.nvidia.com/isaac/archive/2020.1/doc/getting_started.html to learn about the bulding process of Isaac Apps and specifically the part aobut 
creating a python app https://docs.nvidia.com/isaac/archive/2020.1/doc/getting_started.html#python-application-support since our example project is also written in python.


As you might know, Reinforcement Learning is based on continous interaction between an agent and its environment:


![Basic RL interaction](https://github.com/BeneHei/Visual_Navigation_RL/blob/main/RL_interact.png)



We will need to implement the following parts:

* A reward signal provided by the environment
* A Agent that is able to take actions
* A way to enable an agent to observe its environment


In our sample application called py_example_task, all that is given as:


* A constant dummy reward 
* Linear and Angular target velocity as actions
* The current pose of the robot as observation 


The actions will be send to the Isaac Sim which will then use those actions to accellerate the robot
The robot pose will be received from the Isaac Sim


### To run our demo RL application, you have to put the provided py_example_task folder into your local isaac/apps folder

Then start a unity simulation (either in editor or in play mode) that has the following parts available:

* A differential base simulation
* A pose publisher (bodies)
* A Teleport script

Then run the following command inside your isaac folder:


```
bob@desktop:~/isaac$ bazel run //apps/py_example_task
```


## Some of our Results

We used two different modalities throughout our experiments. The first one uses the simulated lidar sensor called **Raycast Lidar Flatscan (Script)** in IsaacSim
Unity. The second one uses simulated RGB and Depth Cameras.

When concatenating four camera images the following state representation can be used:


<img src="https://github.com/BeneHei/Visual_Navigation_RL/blob/main/InputStates_DepthandGray.gif" width="300px">


<img src="https://github.com/BeneHei/Visual_Navigation_RL/blob/main/Depth_short.gif" width="300px">





## Resources
=========


[1] https://developer.nvidia.com/isaac-sdk
[2] https://github.com/openai/gym
[3] https://arxiv.org/abs/1812.05905v2
[4] https://developer.nvidia.com/isaac/downloads
[5] https://developer.nvidia.com/login
[6] https://id.unity.com/en/conversations/951360fa-40fa-4423-919f-a349bf23a3a401af
[7] https://forum.unity.com/threads/unity-hub-v-1-3-2-is-now-available.594139
[8] https://docs.nvidia.com/isaac/archive/2020.1/doc/getting_started.html
[9] https://docs.nvidia.com/isaac/archive/2020.1/doc/getting_started.html#python-application-support
[10] https://docs.nvidia.com/isaac/archive/2020.1/doc/simulation/unity3d.html#getting-started-with-editor-mode
[11] https://docs.nvidia.com/isaac/archive/2020.1/doc/simulation/unity3d.html#build
