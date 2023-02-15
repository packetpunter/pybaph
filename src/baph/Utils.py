from dataclasses import dataclass
from ipaddress import ip_network
from re import search
import dns.resolver
from dns.exception import DNSException
from enum import StrEnum, auto
from datetime import datetime
import os

@dataclass
class ValidAddress(str):
    validated_ip = ""

    def __init__(self, input_address="127.0.0.1"):
        if input_address == "127.0.0.1":
            print("setting default IP to localhost")
            self.validated_ip = input_address
        else:
            try:
                _temp_target = ip_network(input_address)
                if(_temp_target.prefixlen == 32): 
                    self.validated_ip = str(_temp_target.network_address)
                else:
                    _t = _temp_target.network_address + 1
                    print(f"Target is network address. Targeting first host")
                    self.validated_ip = str(_t)
            except ValueError as v:
                if("host bits" in repr(v)):
                    print(f"Target was for a CIDR. Setting to first host in network.")
                    self.validated_ip = str(ip_network(input_address, strict=False).network_address + 1)

                if("does not appear to be" in repr(v)):
                    # source oreilly
                    # source url https://www.oreilly.com/library/view/regular-expressions-cookbook/9781449327453/ch08s15.html
                    domain_regex = "\A([a-z0-9]+(-[a-z0-9]+)*\.)+[a-z]{2,}\Z"
                    match_result = search(domain_regex, input_address)
                    if match_result:
                        real_result = match_result.string
                        try:
                            dns_response = dns.resolver.resolve(real_result, "A")
                            # source https://stackoverflow.com/questions/49509431/returning-a-dns-record-in-dnspython
                            resolved_ip = "".join([str(dns_response[0], ), ""])
                            self.validated_ip = resolved_ip
                        except DNSException as e:
                            print(f"{e}")       
            finally:
                if self.validated_ip == "":
                    print(f"Invalid target {input_address}, setting to localhost")
                    self.validated_ip = "127.0.0.1"
                if self.validated_ip == "0.0.0.0":
                    print(f"DNS returned an invalid response for {input_address},\n returning address 0.0.0.0..\nThis is likely a network security block.\nSetting to localhost")
                    self.validated_ip = "127.0.0.1"

    def __repr__(self):
        return self.validated_ip


class PanScopeCmd(StrEnum):
    WEEK = "show running resource-monitor week last {x}"
    DAY = "show running resource-monitor day last {x}"
    HOUR = "show running resource-monitor hour last {x}"
    MINUTE = "show running resource-monitor minute last {x}"
    SECOND = "show running resource-monitor second last {x}"
    
    def __repr__(self):
        return self.value


class DataLogger():
    import os
    def __init__(self):
        self._base = os.getcwd() + "/logdata/"
        self._now = datetime.now()
        self._fday = self._now.strftime("%Y/%m/%d")
        self._ftime = self._now.strftime("%H:%M")
        self._fpath = self._base + self._fday + "/"
        os.makedirs(self._fpath, exist_ok=True)

    def store_json(self, host: str, json_msg: str):
        _date = self._fday + "-T-" + self._ftime
        _fname = self._fpath + host + "_"+ self._ftime + ".json"
        print(f"storing message in {_fname}")
        
        cleaned = json.loads(json_msg)
        entry = (_date, host, cleaned)

        with open(_fname, "a") as log_file:
            json.dump(cleaned, log_file)

    def store_baseline(self, host: str, baseline_data: dict) -> None:
        _bpath = self._fpath + "baseline/" 
        os.makedirs(_bpath, exist_ok=True)
        _bfname = _bpath + host + "_"+self._ftime + ".csv"
        print(f"storing baseline {baseline_data} for {host} in {_bfname}")
        #with open(_bfname, "a") as file:
            #w = csv.DictWriter(file, fieldnames=baseline_data.keys())
            #w.writeheader()
            #w.writerow(baseline_data)

    def get_json_by_day_and_time(self, host: str, date_time: datetime):
        _fpath = self._base + date_time.strftime("%Y") + "/" + date_time.strftime("%m") + "/" + date_time.strftime("%d")
        _fname = self._fpath + host + "_"+ self._ftime + ".json"
        _datas = []
        print(f"[DT] opening json file {_fname}")
        with open(_fname, "r") as file:
            jd = json.load(file)
            return jd

    def get_jsons_by_day(self, host: str, date_time: datetime) -> []:
        _fpath = self._base + date_time.strftime("%Y") + "/" + date_time.strftime("%m") + "/" + date_time.strftime("%d")
        #_fname = self._fpath + host + "_"+ self._ftime + ".json"
        _datas = []
        for file in os.listdir(_fpath):
            if host in file:
                _fname = _fpath + "/" + file
                print(f"[D] opening json file {_fname}")
                with open(_fname, "r") as file:
                    jd = json.load(file)
                    _datas.append(jd)
        return _datas
