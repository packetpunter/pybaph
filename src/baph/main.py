#!env python

import fire
import json
from datetime import datetime
import os
import csv
import pandas as pd
import numpy as np
from netmiko import ConnectHandler
from getpass import getpass
from enum import StrEnum, auto
from .Utils import ValidAddress, PanScopeCmd, DataLogger

class PanRunner():
    
    def __init__(self, target_firewalls):
        
        self._username = input("Enter username to begin:  ")
        if len(self._username) == 0: input("Enter valid username:  ")
        self._target = target_firewalls
        self._dt = "paloalto_panos"
        self.history = DataLogger()

    def set_password(self):
        ''' set password for user specified in init'''

        self._password = getpass()    
    
    def get_resource_util(self, time_scope, length):
        
        real_target = self._target
        target = real_target
        device = {
            "device_type": self._dt,
            "host": real_target,
            "username": self._username,
            "password": ""
        }
    
        cmd = ""
        
        #TODO: self.validate_length(time_scope, length)

        match time_scope:
            case "week"|"weeks":
                cmd = PanScopeCmd.WEEK.format(x=length)
            case "minute"|"minutes":
                cmd = PanScopeCmd.MINUTE.format(x=length)
            case "hour"|"hours":
                cmd = PanScopeCmd.HOUR.format(x=length)
            case "day"|"days":
                cmd = PanScopeCmd.DAY.format(x=length)
            case "second"|"seconds":
                print("Second scope is not implemented by this program.")
                return
            case _:
                print("Unknown scope.")
                return
        
        #TODO: self._validate_device(device)

        check = input(f"Confirm Executing {cmd} on {target} as user {self._username}? [Y/y/N/n]:").lower()
        if "y" in check:
            device["password"] = self.set_password()
            #with ConnectHandler(**device) as nc:
            #    output = nc.send_command(cmd)
            self.history.store_baseline(device["host"], "fake data right now")
            return cmd
        else: return "Cancelled"


class Saver(object):

    def steal(self, source, amount, scale):
       # Logger = DataLogger()
        
        #Logger.store_json(host=host, json_msg=cleaned)

        #return "\n\nsaved data for host {h}".format(h=host)
        panr = PanRunner(source)
        a = panr.get_resource_util(scale, amount)
        return a 

class Pipeline(object):
    def __init__(self):
        self.covet = Saver()

def run():
    fire.Fire(Pipeline)

