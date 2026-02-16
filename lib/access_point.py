import network


class AccessPoint:
    def __init__(self, ssid: str, password: str):
        self.ssid = ssid
        self.password = password
        self.ap = network.WLAN(network.AP_IF)

    def start(self):
        if not self.ap.active():
            self.ap.active(True)

        self.ap.config(essid=self.ssid, password=self.password, authmode=3)

        ip = self.ap.ifconfig()[0]
        print("AP started")
        print("SSID:", self.ssid)
        print("IP:", ip)

        return ip
