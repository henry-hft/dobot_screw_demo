from dobot_api import DobotApiDashboard, DobotApi, DobotApiMove, MyType
from time import sleep
import re
import sys
import os

class dobot_handler:
    def __init__(self, ip):
        self.restartEthernet(self)
        self.ip = ip
        self.dashboardPort = 29999
        self.movePort = 30003
        self.feedPort = 30004
        self.dashboard = DobotApiDashboard(ip, self.dashboardPort)
        self.move = DobotApiMove(ip, self.movePort)
        self.feed = DobotApi(ip, self.feedPort)

    def start(self):
        enableState = self.parseResultId(self.dashboard.EnableRobot())
        if enableState[0] != 0:
            raise Exception("Verbindung fehlgeschlagen")
        
        print("Verbindung erfolgreich")

        start_point = [300, 0, -50.3, 48] # x, y, z, r
        
        self.dashboard.EnableRobot()
        self.dashboard.ClearError()

        self.setDO(8, 1)
        sleep(0.5)
        self.setDO(8, 0)

        # move to start point
        move = self.moveToPoint(start_point)

    def setDO(self, port, value):
        self.dashboard.DOExecute(8, value)
        print(f"Port {port} set to {value}\n")

    def moveToPoint(self, point_list: list):
        move = self.move.MovL(
            point_list[0], point_list[1], point_list[2], point_list[3], 0, 0, 0)
        print("MovL ", move)
        commandArrID = self.parseResultId(move)
        return commandArrID
        
    def parseResultId(self, valueRecv):
        if valueRecv.find("Not Tcp") != -1: 
            print("Control mode is not TCP")
            return [1]
        recvData = re.findall(r'-?\d+', valueRecv)
        recvData = [int(num) for num in recvData]
        if len(recvData) == 0:
            return [2]
        return recvData
    
    def restartEthernet(self):
        print("Restart Ethernet Connection")
        os.system("/home/pi/bin/eth0_restart")
        sleep(1.0)