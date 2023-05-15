# -*- coding: utf-8 -*-
"""
Created on Thu Apr 20 09:06:06 2023

@author: henri
"""

# Importerer pakker
import openlab
import numpy as np
import matplotlib.pyplot as plt

# Kobler til Openlab-klienten
session = openlab.http_client(username="henrik_2203@hotmail.com", apikey="38019860924EDFAA279988875E00419FE1C51B8E360F35C5707E231E2AB0D40A", licenseguid="cf9e0be9-9670-493e-8753-381c12f423f3", environment="dev")


# Setter opp simuleringen
config_name = "2500m+2500m"
sim_name = "STANDARD_5000"
initial_depth = 5000

#PI controller settings
referenceBHPPressure = 380 *100000 # Pa
initialChokeOpening = 1 # 0 = closed , 1 = open

kp = -0.005 # first try for tuning the pi controller (try with 0.02 afterwards)
ki = kp/10
ts = 1
pi = openlab.piController.Controler(kp, ki, ts, referenceBHPPressure,initialChokeOpening)

# results we want 
tags=["SPP", "DownholeECD", "FlowRateOut", "ChokeOpening", "DownholePressure"]


# Lager simuleringen
sim = session.create_simulation(config_name,sim_name,initial_depth)
timeStep = 1

#units
FLOW_UNIT_CONV_FACTOR= 1.66666667 * 0.00001#float("10e-5") # l/min --> m^3/s
PRESSURE_CONV_FACTOR= 100000.0 # float("10e5") # bar-->pascal






#configure plot 
fig, ((plot_q, plot_choke), (plot_bhp,plot_spp)) = plt.subplots(2, 2,sharex=True)

startTime = timeStep
endTime = startTime + 150

plot_q.set_xlim(startTime,endTime)
plot_bhp.set_xlim(startTime,endTime)
plot_q.set_ylim(1500,3000) #3000 l/min
plot_choke.set_ylim(0,0.5)   #fraction
plot_bhp.set_ylim(300,400) #500 bar
plot_spp.set_ylim(0,500) #500 bar

plot_q.set_title('Flow Rate Out (l/min)')
plot_choke.set_title('Choke Opening')
plot_bhp.set_title('Downhole Pressure(bar)')
plot_spp.set_title('SPP (bar)')
plot_bhp.set_xlabel('Time Step (seconds)')
plot_spp.set_xlabel('Time Step (seconds)')

plt.ion() #make plot interactive
plt.show()
fig.canvas.draw()




#empty lists for plots
steps_ = list()
spps_ = list()
qs_= list()
chokes_= list()
ps_ = list()

rampStartTime = timeStep + 60
initialFlowRate = 2500/60000
targetFlowRate = 2500/60000

for timeStep in range(startTime,endTime):  
    if timeStep >= rampStartTime:
        if timeStep == rampStartTime:
            #reset PI controller before usage, set reference value and initial output = initial choke opening
            pi.reset(referenceBHPPressure, sim.results.ChokeOpening[timeStep-1])
            flowRateIn = targetFlowRate
        
        chokeOpening = pi.getOutput(sim.results.DownholePressure[timeStep-1])

    else: #constant flow rate and choke opening
        flowRateIn = initialFlowRate
        chokeOpening = initialChokeOpening

    #set setpoints 
    sim.setpoints.FlowRateIn = flowRateIn
    sim.setpoints.ChokeOpening = chokeOpening
    
    #step simulator
    sim.step(timeStep)       

    #ask results
    sim.get_results(timeStep,tags)

    spp = sim.results.SPP[timeStep]/PRESSURE_CONV_FACTOR
    p = sim.results.DownholePressure[timeStep]/PRESSURE_CONV_FACTOR
    q = sim.results.FlowRateOut[timeStep]/FLOW_UNIT_CONV_FACTOR
    choke = sim.results.ChokeOpening[timeStep]
    
    #plot_q.scatter(timeStep , q, c='b', s= 1) #c = color; s = size
    #plot_choke.scatter(timeStep,choke, c='b', s = 1)
    #plot_bhp.scatter(timeStep,p, c='b',s=1)
    #plot_spp.scatter(timeStep,spp, c='b',s=1)
    
    #fig.canvas.draw()   # draw
    
    #advance the simulation    
    timeStep = timeStep + 1