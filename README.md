# IOT Final Project

In this project we are building a monitoring system using Raspberry pi, Pi Camera, and cloud services. After setting up the system, the camera can detect moving intruders at home and send alerting emails to the user, and the user is able to preview the pictures captured by the camera on mobile apps.

## System blocks 
![iot_blocks_dark](https://github.com/HelenaShen/IOT_Final/assets/104816632/acfdc6a4-9c62-45c6-a24b-f42ea038db30)

The `camera_connect.py` is running on Raspberry Pi, and files in `drive_server` are running on a Linux computer

## Setup

Required hardwares
 - Raspberry Pi
 - Pi camera
 - Linux computer as Drive server

Cloud services
 - Google Cloud and Google Drive
 - Twilio SendGrid

Authentication
 - ssh between Raspberry Pi and Drive Server. It's necessary to put ssh pub key into known_host, otherwise we need to input password manually each time
 - A Google cloud project with enabled Google Drive api. An authentication key in json format should be stored under `drive_server` directory
 - An active Twilio SendGrid account and api key used for sending emails. Then we need copy the key string to `email_utils.py`

Steps to run the system
 1. Execute `drive_service.py` on Driver Server. There will pop up a Google Cloud authentication window, which is required for executing Google Drive apis
 2. Put the camera in a proper place at home
 3. ssh to Raspberry pi from Drive Server and execute `camera_connect.py`

After those steps, the system is good to run and you can wait for the emails and images sent to your mobile apps.
