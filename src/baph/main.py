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
from datetime import datetime

class PanRunner():
    
    def __init__(self, target_firewalls):
        self._target = ValidAddress(target_firewalls)
        self._username = input("Enter username to begin:  ")
        self._secprompt = input("Enter [P] for password authentication or [C] for certificate authentication:  ")
        now = datetime.now().strftime("%H:%M")
        self.device = {
            "device_type": "paloalto_panos",
            "host": self._target,
            "username": self._username,
            "conn_timeout": 80,
            "session_log": f"Runner_{self._target}_{now}.log"
        }
        match self._secprompt:
            case "P":
                self.device["password"] = self.set_password()
            case "C":
                self._certpath = input(f"Enter FULL path of private key certificate (/home/{self._username}/.ssh/id_rsa): ")
                self._cpass = getpass(f"Enter passphrase for {self._certpath} if any: ")
                import os.path
                _valid_path_check = True
                while _valid_path_check:
                    if not os.path.isfile(self._certpath):
                        print(f"Path {self._certpath} does not reference a file")
                        self._certpath = input("Enter path proper: ")
                    else:
                        _valid_path_check = False
                self.device["passphrase"] = self._cpass
                self.device["use_keys"] = True
                self.device["key_file"] = self._certpath

        self.history = DataLogger()

    def set_password(self):
        ''' set password for user specified in init'''
        self._password = getpass()    
    
    def get_resource_util(self, time_scope, length):
           
        cmd = ""
        
        #TODO: self.validate_length(time_scope, length)

        match time_scope:
            case "week"|"weeks":
                cmd = PanScopeCmd.WEEK.format(x=length)
            case "minute"|"minutes"|"mins"|"min":
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

        check = input(f"Confirm Executing {cmd} on {self._target} as user {self._username}? [Y/y/N/n]:").lower()
        if "y" in check:
            with ConnectHandler(**self.device) as nc:
                output = nc.send_command(cmd)
                self.history.store_baseline(self.device["host"], output)
                return output
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

