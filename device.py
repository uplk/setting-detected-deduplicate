import logging
import os
import re
import subprocess
import sys
import time
import uiautomator2 as u2
from threading import Thread

class MyThread(Thread):
    def __init__(self, func, args):
        super(MyThread, self).__init__()
        self.func = func
        self.args = args

    def run(self):
        self.result = self.func(*self.args)

    def get_result(self):
        try:
            return self.result
        except Exception:
            return None
"""
Record the information of the device
"""
class Device(object):

    def __init__(self, device_num=None,device_serial=None, is_emulator=True, rest_interval=None):
        self.device_num = device_num
        self.device_serial = device_serial
        self.is_emulator = is_emulator
        self.use = None
        self.state = None
        self.last_state = None
        self.strategy = "screen"
        self.crash_logcat = ""
        self.last_crash_logcat = ""
        self.language = "en"
        self.rest_interval = rest_interval
        self.wifi_state =True
        self.gps_state = True
        self.sound_state = True
        self.battery_state = False
        self.game_mode = True
        self.blue_light = False
        self.notification = True
        self.permission = True
        self.hourformat = "12h"

    def set_strategy(self,strategy):
        self.strategy = strategy
        self.error_num = 0
        self.wrong_num = 0

    def set_thread(self,execute_event,args):
        if execute_event is not None:
            self.thread = MyThread(execute_event, args)
        else:
            self.thread = None
    
    def restart(self,emulator_path,emulator_name):
        port = self.device_serial[self.device_serial.find("-")+1:len(self.device_serial)]
        print("----"+port)
        subprocess.run(["adb","-s",self.device_serial,"emu","kill"], stdout=subprocess.PIPE)
        time.sleep(self.rest_interval*20)
        os.popen(emulator_path+" -avd "+emulator_name+" -read-only -port "+port)
        print("wait-for-device")
        subprocess.run(["adb","-s",self.device_serial,"wait-for-device"], stdout=subprocess.PIPE)
        print("wait-for-device end")
        time.sleep(self.rest_interval*10)
    
    def make_strategy(self,root_path):
        if not os.path.isdir(root_path+"strategy_"+self.strategy+"/"):
            os.makedirs(root_path+"strategy_"+self.strategy+"/")
        self.f_error = open(root_path+"strategy_"+self.strategy+'/error_realtime.txt','w',encoding='utf-8')
        self.f_wrong = open(root_path+"strategy_"+self.strategy+'/wrong_realtime.txt','w',encoding='utf-8')

    def make_strategy_runcount(self,run_count,root_path):
        self.path=root_path+"strategy_"+self.strategy+"/"+str(run_count)+"/"
        if not os.path.isdir(self.path):
            os.makedirs(self.path)
        if not os.path.isdir(self.path+"screen/"):
            os.makedirs(self.path+"screen/")
        self.f_read_trace = open(self.path+'/read_trace.txt','w',encoding='utf-8')
        self.f_trace = open(self.path+'/trace.txt','w',encoding='utf-8')

        self.error_event_lists = []
        self.wrong_event_lists = []
        self.wrong_flag = True

    def connect(self):
        self.use = u2.connect_usb(self.device_serial)
        self.use.implicitly_wait(5.0)

    def install_app(self,app):
        print(app)
        subprocess.run(["adb","-s",self.device_serial,"install",app], stdout=subprocess.PIPE)

    def initialization(self):
        self.use.set_orientation("n")
    
    def initial_setting(self):
        print("initial setting")

    def screenshot_and_getstate(self,path,event_count):
        self.screenshot_path = path+str(event_count)+'_'+self.device_serial+'.png'
        self.use.screenshot(path+str(event_count)+'_'+self.device_serial+'.png')
        xml = self.use.dump_hierarchy()
        f = open(path+str(event_count)+'_'+self.device_serial+'.xml','w',encoding='utf-8')
        f.write(xml)
        f = open(path+str(event_count)+'_'+self.device_serial+'.xml','r',encoding='utf-8')
        lines=f.readlines()
        f.close()
        return lines
    
    def update_state(self,state):
        self.last_state=self.state
        self.state=state
    
    def stop_app(self,app):
        self.use.app_stop(app.package_name)

    def clear_app(self,app,is_login_app):
        if is_login_app == 0 :
            self.use.app_stop(app.package_name)
        else:
            self.use.app_clear(app.package_name)
    
    def start_app(self,app):
        self.use.app_start(app.package_name)
        subprocess.run(["adb","-s",self.device_serial,"shell","am","start","-n",app.package_name+"/"+app.main_activity], stdout=subprocess.PIPE)
        # self.use.app_wait(app.package_name, front=True, timeout=2.0)
        return True
    
    def click(self,view,strategy_list):
        try:
            if self.strategy != "language":
                if view.description!="":
                    self.use(description=view.description,packageName=view.package).click()
                    return "description"
                elif view.text!="":
                    self.use(text=view.text,packageName=view.package).click()
                    return "text"
                elif view.instance == 0:
                    self.use(className=view.className,resourceId=view.resourceId,packageName=view.package).click()
                    return "classNameresourceId"
                else:
                    self.use.click(view.x ,view.y)
                    return "xy"
            elif view.instance == 0:
                self.use(className=view.className,resourceId=view.resourceId,packageName=view.package).click()
                return "classNameresourceId"
            else:
                self.use.click(view.x ,view.y)
                return "xy"
        except:
            self.use.click(view.x ,view.y)
            return "xy"
    
    def longclick(self,view,strategy_list):
        try:
            if self.strategy != "language":
                if view.description!="":
                    self.use(description=view.description,packageName=view.package).long_click()
                    return
                elif view.text!="":
                    self.use(text=view.text,packageName=view.package).long_click()
                    return
                elif view.instance == 0:
                    self.use(className=view.className,resourceId=view.resourceId,packageName=view.package).long_click()
                else:
                    self.use.long_click(view.x ,view.y)
            elif view.instance == 0:
                self.use(className=view.className,resourceId=view.resourceId,packageName=view.package).long_click()
            else:
                self.use.long_click(view.x ,view.y)
        except:
            self.use.long_click(view.x ,view.y)
            # print("x:"+str(view.x)+",y:"+str(view.y))
            return
    
    def edit(self,view,strategy_list,text):
        if "language" not in strategy_list:
            self.use(className=view.className,resourceId=view.resourceId,packageName=view.package).set_text(text)
        else:
            self.use(className=view.className,resourceId=view.resourceId,packageName=view.package).set_text(text)
    
    def scroll(self,view,strategy_list):
        if view.action == "scroll_backward":
            self.use(className=view.className,resourceId=view.resourceId,packageName=view.package).scroll.vert.backward(steps=100)
        elif view.action == "scroll_forward":
            self.use(className=view.className,resourceId=view.resourceId,packageName=view.package).scroll.vert.forward(steps=100)
        elif view.action == "scroll_right":
            self.use(className=view.className,resourceId=view.resourceId,packageName=view.package).scroll.horiz.toEnd(max_swipes=10)
        elif view.action == "scroll_left":
            self.use(className=view.className,resourceId=view.resourceId,packageName=view.package).scroll.horiz.toBeginning(max_swipes=10)

    def close_keyboard(self):
        subprocess.run(["adb","-s",self.device_serial,"shell","input","keyevent","111"], stdout=subprocess.PIPE)

    def add_file(self,resource_path,resource,path):
        subprocess.run(["adb","-s",self.device_serial,"logcat","-c"], stdout=subprocess.PIPE)
        subprocess.run(["adb","-s",self.device_serial,"push",resource_path+"/"+resource,path], stdout=subprocess.PIPE)

    def log_crash(self,path):
        os.popen("adb -s "+self.device_serial+" logcat -b crash >"+path)


    # through adb command to change settings
    def adb_setting(self, str):
        if str == "network_immediate_1":
            subprocess.run(["adb", "-s", self.device_serial, "shell", "svc", "wifi", "disable"], stdout=subprocess.PIPE)
            subprocess.run(["adb", "-s", self.device_serial, "shell", "settings", "put", "global", "airplane_mode_on", "1"],
                           stdout=subprocess.PIPE)
            subprocess.run(["adb", "-s", self.device_serial, "shell", "settings", "put", "global", "airplane_mode_on", "0"],
                           stdout=subprocess.PIPE)
            subprocess.run(["adb", "-s", self.device_serial, "shell", "svc", "wifi", "enable"], stdout=subprocess.PIPE)
        elif str == "network_lazy_1_1":
            subprocess.run(["adb", "-s", self.device_serial, "shell", "settings", "put", "global", "airplane_mode_on", "0"],
                           stdout=subprocess.PIPE)
        elif str == "network_lazy_1_2":
            subprocess.run(["adb", "-s", self.device_serial, "shell", "settings", "put", "global", "airplane_mode_on", "1"],
                           stdout=subprocess.PIPE)
        elif str == "network_lazy_2_1":
            subprocess.run(["adb", "-s", self.device_serial, "shell", "svc", "wifi", "disable"], stdout=subprocess.PIPE)
        elif str == "network_lazy_2_2":
            subprocess.run(["adb", "-s", self.device_serial, "shell", "svc", "wifi", "enable"], stdout=subprocess.PIPE)
        elif str == "location_lazy_1_1":
            subprocess.run(["adb", "-s", self.device_serial, "shell", "settings", "put", "secure", "location_providers_allowed", "-gps"],
                           stdout=subprocess.PIPE)
            subprocess.run(["adb", "-s", self.device_serial, "shell", "settings", "put", "secure", "location_providers_allowed", "-network"],
                           stdout=subprocess.PIPE)
        elif str == "location_lazy_1_2":
            subprocess.run(["adb", "-s", self.device_serial, "shell", "settings", "put", "secure", "location_providers_allowed", "+gps"],
                           stdout=subprocess.PIPE)
            subprocess.run(["adb", "-s", self.device_serial, "shell", "settings", "put", "secure", "location_providers_allowed", "+network"],
                           stdout=subprocess.PIPE)
            self.adb_get_gps_state()
        elif str == "location_lazy_2_1":
            subprocess.run(
                ["adb", "-s", self.device_serial, "shell", "settings", "put", "secure", "location_providers_allowed", "+network"],
                stdout=subprocess.PIPE)
            subprocess.run(
                ["adb", "-s", self.device_serial, "shell", "settings", "put", "secure", "location_providers_allowed",
                 "-network"],
                stdout=subprocess.PIPE)
        elif str == "location_lazy_2_2":
            subprocess.run(
                ["adb", "-s", self.device_serial, "shell", "settings", "put", "secure", "location_providers_allowed",
                 "+gps"],
                stdout=subprocess.PIPE)
            subprocess.run(
                ["adb", "-s", self.device_serial, "shell", "settings", "put", "secure", "location_providers_allowed",
                 "+network"],
                stdout=subprocess.PIPE)
        elif str == "open_gps":
            self.adb_setting("close_gps")
            subprocess.run(
                ["adb", "-s", self.device_serial, "shell", "settings", "put", "secure", "location_providers_allowed",
                 "+gps"],
                stdout=subprocess.PIPE)
        elif str == "close_gps":
            subprocess.run(
                ["adb", "-s", self.device_serial, "shell", "settings", "put", "secure", "location_providers_allowed",
                 "-network"],
                stdout=subprocess.PIPE)
            subprocess.run(
                ["adb", "-s", self.device_serial, "shell", "settings", "put", "secure", "location_providers_allowed",
                 "-gps"],
                stdout=subprocess.PIPE)
        elif str == "gps_accuracy":
            subprocess.run(
                ["adb", "-s", self.device_serial, "shell", "settings", "put", "secure", "location_providers_allowed",
                 "+network"],
                stdout=subprocess.PIPE)
        elif str == "gps_device":
            subprocess.run(
                ["adb", "-s", self.device_serial, "shell", "settings", "put", "secure", "location_providers_allowed",
                 "-network"],
                stdout=subprocess.PIPE)
        elif str == "language_en":
            subprocess.run(
                ["adb", "-s", self.device_serial, "shell", "am", "broadcast", "-a", "com.android.intent.action.SET_LOCALE",
                 "--es", "com.android.intent.extra.LOCALE", "\"zh_CN\"" ,"com.android.customlocale2"],
                stdout=subprocess.PIPE)
        elif str == "language_ch":
            subprocess.run(
                ["adb", "-s", self.device_serial, "shell", "am", "broadcast", "-a",
                 "com.android.intent.action.SET_LOCALE",
                 "--es", "com.android.intent.extra.LOCALE", "\"en_US\"", "com.android.customlocale2"],
                stdout=subprocess.PIPE)

    def adb_permission(self, package, choice):
        permission = ["READ_CALENDAR",
                      "WRITE_CALENDAR",
                      "READ_CALL_LOG",
                      "WRITE_CALL_LOG",
                      "PROCESS_OUTGOING_CALLS",
                      "CAMERA",
                      "READ_CONTACTS",
                      "WRITE_CONTACTS",
                      "GET_ACCOUNTS",
                      "ACCESS_FINE_LOCATION",
                      "ACCESS_COARSE_LOCATION",
                      "ACCESS_BACKGROUND_LOCATION",
                      "RECORD_AUDIO",
                      "READ_PHONE_STATE",
                      "READ_PHONE_NUMBERS",
                      "CALL_PHONE",
                      "ANSWER_PHONE_CALLS",
                      "ADD_VOICEMAIL",
                      "USE_SIP",
                      "ACCEPT_HANDOVER",
                      "BODY_SENSORS",
                      "ACTIVITY_RECOGNITION",
                      "SEND_SMS",
                      "RECEIVE_SMS",
                      "READ_SMS",
                      "RECEIVE_WAP_PUSH",
                      "RECEIVE_MMS",
                      "READ_EXTERNAL_STORAGE",
                      "WRITE_EXTERNAL_STORAGE",
                      "ACCESS_MEDIA_LOCATION"]
        if choice == "ON":
            for p in permission:
                p = "android.permission." + p
                subprocess.run(["adb", "-s", self.device_serial, "-d", "shell", "pm", "grant", package, p], stdout=subprocess.PIPE)
        else:
            for p in permission:
                p = "android.permission." + p
                subprocess.run(["adb", "-s", self.device_serial, "-d", "shell", "pm", "revoke", package, p], stdout=subprocess.PIPE)

    def adb_get_gps_state(self):
        res = os.popen(
            "adb -s " + self.device_serial + " shell settings get secure location_providers_allowed").read()
        print(self.device_serial + " " + res)
        if res == "\n":
            return False
        else:
            return True

    def init_frida(self, frida_path):
        os.popen("adb -s " + self.device_serial + " push \"" + frida_path + "\" /data/local/tmp")
        print("adb -s " + self.device_serial + " push \"" + frida_path + "\" /data/local/tmp")
        os.popen(
            "adb -s " + self.device_serial + " shell \"su 0 chmod 777 data/local/tmp/frida-server-14.2.18-android-x86\"")
        print(
            "adb -s " + self.device_serial + " shell \"su 0 chmod 777 data/local/tmp/frida-server-14.2.18-android-x86\"")
        time.sleep(1)
        self.fridathread = os.popen(
            "adb -s " + self.device_serial + " shell \"su 0 /data/local/tmp/frida-server-14.2.18-android-x86\"")
        print("adb -s " + self.device_serial + " shell \"su 0 /data/local/tmp/frida-server-14.2.18-android-x86\"")

    def close_frida(self):
        self.fridathread.close()

    def record_frida(self, record_path, package_name):
        time.sleep(2)
        print(
            "start frida-trace -D " + self.device_serial + " -j \"*NetworkInfo*!*isConnected*\" " + package_name + " -o \"" + record_path + "/network_frida.txt\"")
        os.system(
            "start frida-trace -D " + self.device_serial + " -j \"*NetworkInfo*!*isConnected*\" " + package_name + " -o \"" + record_path + "/network_frida.txt\"")
        time.sleep(1)
        print(
            "start frida-trace -D " + self.device_serial + " -j \"*anager*!*checkPermission*\" " + package_name + " -o \"" + record_path + "/permission_frida.txt\"")
        os.system(
            "start frida-trace -D " + self.device_serial + " -j \"*anager*!*checkPermission*\" " + package_name + " -o \"" + record_path + "/permission_frida.txt\"")
        time.sleep(1)
        print(
            "start frida-trace -D " + self.device_serial + " -j \"*LocationManager*!*getAllProviders*\" -j \"*Location*!*getLatitude*\" " + package_name + " -o \"" + record_path + "/location_frida.txt\"")
        os.system(
            "start frida-trace -D " + self.device_serial + " -j \"*LocationManager*!*getAllProviders*\" -j \"*Location*!*getLatitude*\" " + package_name + " -o \"" + record_path + "/location_frida.txt\"")


    


