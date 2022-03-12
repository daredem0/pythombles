# -*- coding: utf-8 -*-
"""
Created on Wed Feb 16 18:41:27 2022

@author: LEUZE
"""

from kivy.clock import Clock
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.resources import resource_add_path
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder

import sys, os, random, decorator

def cast_channel(fn):
    def wrapper(self, channel: int, *args):
        chan = TypeA.intToChannel(channel)
        return fn(self, chan, *args)
    return wrapper

class Devices:
    TYPE_A = list(["Some device with options"])
    TYPE_B = list(["Some empty device"])
    def __init__(self):
        pass

class Channel:
    def __init__(self):
        self._state = False
        self._amp = 0
        self._volt = 0

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, state: bool):
        self._state = state

    @property
    def amp(self):
        return self._amp

    @amp.setter
    def amp(self, amp):
        self._amp = amp

    @property
    def volt(self):
        return self._volt

    @volt.setter
    def volt(self, volt):
        self._volt = volt


class TypeA:
    MAX_CHAN = 3 +1
    CHAN_COM = [dig for dig in range(1, MAX_CHAN)]
    def __init__(self, resource):
        super().__init__()
        self._session = None
        print("Cannot open visa device. Dummy mode.")
        self._init = False
        self._chans = dict()


    def init(self, channels):
        self._init = True
        for chan in channels:
            self._chans[chan] = Channel()


    def get_init(self):
        return self._init

    @staticmethod
    def get_channels():
        return ["Channel " + str(dig) for dig in TypeA.CHAN_COM]

    @staticmethod
    def channelToInt(channel: str):
        hit = [dig for dig in TypeA.CHAN_COM if channel == "Channel " + str(dig)]
        if len(hit) > 0:
            return hit[0]
        else:
            return 1

    @staticmethod
    def intToChannel(channel: int):
        return TypeA.get_channels()[channel-1]

    def _sel_inst(self, channel):
        pass

    @cast_channel
    def get_volt(self, channel):
        if self._init:
            return format(self._chans[channel].volt, '.4f')
        else:
            return "0"

    @cast_channel
    def set_volt(self, channel, volt):
        self._chans[channel].volt = volt

    @cast_channel
    def set_amp(self, channel, amp):
        self._chans[channel].amp = amp

    @cast_channel
    def set_out(self, channel):
        self._chans[channel].state = True

    @cast_channel
    def clear_out(self, channel):
        self._chans[channel].state = False

    def query_error(self):
        pass

    @cast_channel
    def query_output(self, channel):
        if self._init:
            return self._chans[channel].state
        else:
            return False

    @cast_channel
    def get_current(self, channel):
        if self._init:
            return format(self._chans[channel].amp, '.4f')
        else:
            return "0"

    @cast_channel
    def measure_current(self, channel):
        if self._init:
            if not self._chans[channel].state:
                return self.get_amp(channel)
            return format(random.uniform(self._chans[channel].amp - 0.02, self._chans[channel].amp + 0.02), '.4f')
        else:
            return "0"

    @cast_channel
    def measure_voltage(self, channel):
        if self._init:
            if not self._chans[channel].state:
                return self.get_volt(channel)
            return format(random.uniform(self._chans[channel].volt - 0.02, self._chans[channel].volt + 0.02), '.4f')
        else:
            return "0"

    def __del__(self):
        print("Cleaning up")

class Scope(Screen):
    pass


class PowerSupply(Screen):
    s=None

    def __init__(self, name):
        super().__init__(name=name)
        self._visa_dev = None
        self._visa_connected = False
        self._scpi_devs =  tuple(["Dummy"])
        self.logger(str(self._scpi_devs))
        self._current_out = [False, False, False]
        self.updateSubSpinner(1, self._scpi_devs)
        Clock.schedule_interval(self._poll_current_values, 0.1)

    def logger(self, text, sep='\n'):
        old_text = self.ids['scroll_label'].text
        self.ids['scroll_label'].text = old_text + sep + text

    def updateSubSpinner(self, spinner_id, val):
        if spinner_id == 1:
            self.ids['spinner_1'].values = val
        if spinner_id == 2:
            self.ids['spinner_2'].values = val
            self.ids['spinner_2'].text = val[0]

    def btn_refresh_device(self):
        if self._visa_dev is not None:
            del self._visa_dev
        self._device = self.ids['spinner_1'].text
        self._visa_dev = TypeA(self._device)
        self._visa_dev.init(TypeA.get_channels())
        self._visa_connected = self._visa_dev.get_init()
        try:
            channels = TypeA.get_channels()
            self.updateSubSpinner(2, channels)
            self.btn_refresh_channel()
        except:
            pass

    def _refresh_curr_volt(self):
        if self._current_out[self._current_channel-1]:
            self._current_volt = self._visa_dev.measure_voltage(self._current_channel)
        else:
            self._current_volt = self._visa_dev.get_volt(self._current_channel)
        self.ids['lb_curr_volt'].text = self._current_volt
        #self.logger("Current Voltage: " + self._current_volt, sep="")

    def _refresh_curr_amp(self):
        if self._current_out[self._current_channel-1]:
            self._current_amp = self._visa_dev.measure_current(self._current_channel)
        else:
            self._current_amp = self._visa_dev.get_current(self._current_channel)
        self.ids['lb_curr_amp'].text = self._current_amp
        #self.logger("Current Amplitude: " + self._current_amp, sep="")

    def _refresh_curr_out(self):
        tempx = int(self._visa_dev.query_output(self._current_channel))
        if tempx == 0:
            self._current_out[self._current_channel-1] = False
        else:
            self._current_out[self._current_channel-1] = True

    def _refresh_curr_vals(self):
        self._refresh_curr_volt()
        self._refresh_curr_amp()
        self._refresh_curr_out()

    def btn_refresh_channel(self):
        self._current_channel = TypeA.channelToInt(self.ids['spinner_2'].text)
        self._refresh_curr_vals()
        self.update_btn_col()

    def _read_set_volt(self):
        set_volt = self.ids['ti_set_volt'].text
        if set_volt == "":
            set_volt = "0"
        self.logger(set_volt)
        volt_io = False
        if self._current_channel == 1:
            if 0 < float(set_volt) <= 8:
                volt_io = True
        elif self._current_channel == 2:
            if 0 < float(set_volt) <= 5.2:
                volt_io = True
        else:
            volt_io = True
        if volt_io:
            self.logger("Channel " + str(self._current_channel) + " Voltage acceptable")
            self._visa_dev.set_volt(self._current_channel, float(set_volt))
            self._refresh_curr_volt()
        else:
            self.logger("Channel " + str(self._current_channel) + " Voltage inacceptable")

    def _read_set_amp(self):
        set_amp = self.ids['ti_set_amp'].text
        if set_amp == "":
            set_amp = "0"
        self.logger(set_amp)
        amp_io = False
        if self._current_channel == 1:
            if 0 < float(set_amp) <= 2:
                amp_io = True
        elif self._current_channel == 2:
            if 0 < float(set_amp) <= 0.5:
                amp_io = True
        else:
            amp_io = True
        if amp_io:
            self.logger("Channel " + str(self._current_channel) + " Amplitude acceptable")
            self._visa_dev.set_amp(self._current_channel, float(set_amp))
            self._refresh_curr_amp()
        else:
            self.logger("Channel " + str(self._current_channel) + " Amplitude inacceptable")

    def btn_set(self):
        self._read_set_volt()
        self._read_set_amp()

    def update_btn_col(self, force_col=False):
        if force_col:
            self.ids['btn_set_out'].background_color = (0.1, 1, 0.4, 1)
        else:
            if self._current_out[self._current_channel-1] == True:
                self.ids['btn_set_out'].background_color = (0.1, 1, 0.4, 1)
            else:
                self.ids['btn_set_out'].background_color = (1, 1, 1, 1)

    def btn_out(self):
        if self._current_out[self._current_channel-1] == False:
            self.logger("Set " + str(self._current_channel) + "\n")
            self._visa_dev.set_out(self._current_channel)
            self._current_out[self._current_channel-1] = True
        else:
            self.logger("Reset " + str(self._current_channel) + "\n")
            self._visa_dev.clear_out(self._current_channel)
            self._current_out[self._current_channel-1] = False
        self.update_btn_col()

    def _poll_current_values(self, dt):
        if self._visa_dev is not None:
            self._refresh_curr_volt()
            self._refresh_curr_amp()

    def set_ip(self, ip):
        self.logger("Adding device with " + str(ip))
        self._scpi_devs = self._scpi_devs + tuple(["TCPIP::" + ip + "::INSTR"])
        self.updateSubSpinner(1, self._scpi_devs)

class VisaManager(ScreenManager):
    def __init__(self):
        super().__init__()
        self.add_widget(DeviceTypeScreen(name='device_type'))
        self._switch_screen("device_type")

    def facade(self, message_id, val):
        if message_id == 'mes_setting_ip':
            self.get_screen('device').set_ip(val)
        if message_id == "mes_device_type":
            self._set_device_type(val)

    def _switch_screen(self, val):
            self.switch_to(self.get_screen(val))

    def _set_device_type(self, val):
        if val in Devices.TYPE_A:
            if self.has_screen('device'):
                self.remove_widget(self.get_screen('device'))
            if self.has_screen('settings_ip'):
                self.remove_widget(self.get_screen('settings_ip'))
            self.add_widget(PowerSupply(name='device'))
            self.add_widget(AddIpScreen(name='settings_ip'))
            self._switch_screen("device")
        elif val in Devices.TYPE_B:
            if self.has_screen('device'):
                self.remove_widget(self.get_screen('device'))
            if self.has_screen('settings_ip'):
                self.remove_widget(self.get_screen('settings_ip'))
            self.add_widget(Scope(name='device'))
            self.add_widget(AddIpScreen(name='settings_ip'))
            self._switch_screen("device")
        elif val == "home":
            self.add_widget(DeviceTypeScreen(name='device_type'))
            self._switch_screen("device_type")

class AddIpScreen(Screen):
    def btn_ip(self):
        self.manager.facade('mes_setting_ip', self.ids['ti_setting_ip'].text)
        self.manager.current = "device"


class DeviceTypeScreen(Screen):
    def btn_refresh_device_type(self):
        self.manager.facade('mes_device_type', self.ids['spinner_device_type'].text)

class KivyExampleApp(App):
    kv_directory = './ui'
    def build(self):
        sm = VisaManager()
        return sm

if __name__ == "__main__":
    if hasattr(sys, '_MEIPASS'):
        resource_add_path(os.path.join(sys._MEIPASS))
    KivyExampleApp().run()

# class Visa(App):
#     kv_directory = './ui'
#     def build(self):
#         return MyGrid()


# if __name__ == "__main__":
#     if hasattr(sys, '_MEIPASS'):
#         resource_add_path(os.path.join(sys._MEIPASS))
#     Visa().run()
