# Visual_Navigation_RL

# Hello, This repository is a introduction to learned visual navigation based on the IsaacSDK and Isaac Sim! <img src="https://raw.githubusercontent.com/MartinHeinz/MartinHeinz/master/wave.gif" width="30px">

## This Tutorial gives hints about how to combine OpenAI Gym [1] and the Nvidia IsaacSDK [2] 
## PLEASE BE AWARE THAT THE ISAAC SDK REQUIRES A MEMBERSHIP WHICH CAN BE OBTAINED HERE:  https://developer.nvidia.com/login


Once you have created a developer account, you will have access to all resources that will be needed to implement basic interaction between your Reinforcement Learning 
Algorithms and the Isaac SDK & Sim.

# Prerequisites
## We will use a archived version of the Isaac SDK: 2020.1 since version 2020.2 introduced many structural changes to the SDK




First you will have to download both the Isaac SDK and the IsaacSim which you can find here:
https://developer.nvidia.com/isaac/downloads (klick on "archive" to find previous versions)


Once you have downloaded the Isaac SDK you will find a script /isaac/engine/build/scripts/install_dependencies.sh that automatically installs all dependencies on your system
### While the installation is pretty well documented we will still give some recommendations here.


* Currently only Ubuntu 18.04 LTS is supported
* Please make sure to install recent NVIDIA graphics card drivers on your workstation -> version 440 is recommended
* In our case CUDA 10.1 has shown to be the most stable version 



Resources
=========


[1] https://developer.nvidia.com/isaac-sdk
[2] https://github.com/openai/gym
[3] https://arxiv.org/abs/1812.05905v2
