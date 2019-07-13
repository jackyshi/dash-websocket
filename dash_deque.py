# -*- coding: utf-8 -*-
"""
Created on Sat Jul 13 03:19:07 2019

@author: admin
"""

"""
Producer/Controller Dash Outline
Copyright 2018 Steve Korson
"""
import dash
from dash.dependencies import Output, Input, State
import dash_core_components as dcc
import dash_html_components as html
import plotly
import random
import plotly.graph_objs as go
from collections import deque
import threading as th
import time as t
import random as rnd


class producer(th.Thread):
    def __init__(self, threadID):
        th.Thread.__init__(self)
        self.threadID = threadID
        self.done = False
        self.sleep_time = 0.250
        self.data = []
        self.resetData()
        self.pause = False
        self.fakeRspTime = 0
        self.busy = False
    def stop(self):
        self.done = True
    def run(self):
        while self.done == False:
            # Main loop
            self.busy = self.__update(timeout=0.250)
            t.sleep(self.sleep_time)
        # Cleanup
    def __update(self,timeout=0.250):
        """  Here the producer would access some data inbound socket/IO
        Faking asynchronous data below.
        """
        # -------------------------
        if self.pause:
            # Emulate paused, busy
            return True
        else:
            fakeDelay = rnd.randint(1,4)
            if self.fakeRspTime < fakeDelay:
                t.sleep(timeout)
                self.fakeRspTime = self.fakeRspTime+1
                # Emulate busy
                return True
            else:
                self.fakeRspTime = 0
                # Emulate data ready (not busy)
                # Emulate updating data from producer
                self.data = self.data[1:]
                fakeData = self.data[-1] + (rnd.randint(1,10)-5)
                self.data.append(fakeData)
                if self.data[-1] < 0:
                    self.data[-1] = 0
                if self.data[-1] >30:
                    self.data[-1] = 30
                return False
        # -------------------------
    def getData(self):
        print("INFO: Data Request. Busy?", self.busy)
        return self.data
    def pauseData(self, state):
        self.pause = state
    def resetData(self):
        self.data = [0,0,0,0,0,0,0,0]

class controller(th.Thread):
    def __init__(self, threadID,target):
        # Passing in producer target here for demo
        # Typical system has controller and producer connected external
        th.Thread.__init__(self)
        self.threadID = threadID
        self.done = False
        self.target = target
        self.sleep_time = 0.250
        self.busy = False
        self.__newCmd = False
        self.fakeRspTime = 0
        self.paused = False
    def stop(self):
        self.done = True
    def run(self):
        while self.done == False:
        # Main loop
            if self.__newCmd:
                self.__newCmd = False
                self.__procCmd()
            if self.busy:
                self.busy = self.__check_for_rsp(timeout=0.250)
            t.sleep(self.sleep_time)
        # Cleanup
    def send_cmd(self, cmd):
        """ Method used by callers to send commands to the command interface """
        if self.busy == False:
            self.busy = True
            self.__newCmd = True
            self.__cmd = cmd;
            return True
        else:
            raise UserWarning("Command interpreter is busy.")
    def __procCmd(self):
        """ Emulate sending a commnd out a socket or other IPC
        """
        # -----------------------------
        self.busy = True
        if self.__cmd == 'P': # Pause
            if self.paused:
                self.paused = False
            else:
                self.paused = True
            self.target.pauseData(self.paused)
            
        if self.__cmd == 'R':
            self.target.resetData()
        # -----------------------------
    def __check_for_rsp(self,timeout):
        """ Once command is sent out the interface, await a response (or timeout) """
        # For now emulate checking for a response
        #---------------------------------
        # This can take a random amount of loops (not time really)
        # before setting a non-busy result.
        fakeDelay = rnd.randint(1,4)
        if self.fakeRspTime < fakeDelay:
            t.sleep(timeout)
            self.fakeRspTime = self.fakeRspTime+1
            return True
        else:
            self.fakeRspTime = 0
            return False
        #---------------------------------


app = dash.Dash(__name__)
app.layout = html.Div(
    [
      dcc.Graph(id='live-graph', animate=False),
      dcc.Interval(
        id='graph-update',
        interval=1*1000,
        n_intervals=25
        ),
      html.Button('Pause/Resume', id='buttonPause',),
      html.Button('Reset', id='buttonReset',),
      dcc.Checklist(
          id='status',
          options=[
              {'label': 'Producer Paused', 'value': 'P'},
              {'label': 'Controller Busy', 'value': 'B'},
          ],
          values=[]
      ),
    ]
    )

@app.callback(Output('live-graph','figure'),
              [Input('graph-update', 'n_intervals')])
def update_graph(n):
    x = [1,2,3,4,5,6,7,8]
    y = producerObj.getData()
    data = go.Scatter(
        x = x,
        y = y,
        name = 'myScatter',
        mode = 'lines+markers'
    )
    return {'data':[data],'layout': go.Layout(xaxis = dict(range=[0.9*min(x),1.1*max(x)]),
                                              yaxis = dict(range=[0,32]))}

@app.callback(Output('status','values'),
              [Input('graph-update', 'n_intervals')])
def update_status(n):
    newValues = []
    if controllerObj.busy:
        newValues.append('B')
    if producerObj.pause:
        newValues.append('P')
    return newValues

@app.callback(Output('buttonReset', 'children'),
              [Input('buttonReset', 'n_clicks')],)
def send_reset(n_clicks):
    # Optionally to try and except, you could semaphore protect the calls (with fileIO rather than globals)
    try:
        controllerObj.send_cmd('R')
    except:
        print("Interface is busy. Handle the exception.")
    return 'Reset'

@app.callback(Output('buttonPause', 'children'),
              [Input('buttonPause', 'n_clicks')])
def send_pause(n_clicks):
    # Optionally to try and except, you could semaphore protect the calls (with fileIO rather than globals)
    try:
        controllerObj.send_cmd('P')
    except:
        print("Interface is busy. Handle the exception.")
    return 'Pause/Resume'
pass


if __name__ == "__main__":
    producerObj = producer(1)
    controllerObj = controller(2,producerObj)

    producerObj.start()
    controllerObj.start()

    app.run_server(debug=True)

    producerObj.stop()
    controllerObj.stop()
    
    print("Fin.")