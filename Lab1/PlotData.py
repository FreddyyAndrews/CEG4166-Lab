# Import Libraries
from matplotlib.pylab import *
from mpl_toolkits.axes_grid1 import host_subplot
import matplotlib.animation as animation
import time

class multiplePlots:
    def __init__(self, leftEncoderCount, rightEncoderCount, samples, xmax):
        self.leftEncoderCount = leftEncoderCount
        self.rightEncoderCount = rightEncoderCount
        self.samples = samples
        self.xmax = xmax
        self.ymax = 200
        
        # Define sampleTime to calculate the speed and the tf variable, 
        # which represents the end time of the speed measuring
        self.sampleTime = 1
        self.tf = time.time() + self.sampleTime
        
        # Set font for figure
        self.font = {'size': 9}
        matplotlib.rc('font', **self.font)
        
        # Setup figure and subplots
        self.f0 = figure(num=0, figsize=(6, 4))
        self.f0.suptitle("Oscillation decay", fontsize=12)
        self.ax01 = subplot2grid((1, 2), (0, 0))
        self.ax02 = subplot2grid((1, 2), (0, 1))
        
        # Data Placeholders
        self.yp1 = zeros(0)
        self.yv1 = zeros(0)
        self.yp2 = zeros(0)
        self.yv2 = zeros(0)
        self.t = zeros(0)
        
        # Set plots
        self.p011, = self.ax01.plot(self.t, self.yp1, 'b-', label="LeftWheel")
        self.p012, = self.ax01.plot(self.t, self.yp2, 'g-', label="RightWheel")
        self.p021, = self.ax02.plot(self.t, self.yv1, 'b-', label="LeftWheel")
        self.p022, = self.ax02.plot(self.t, self.yv2, 'g-', label="RightWheel")
        
        # Set legends
        self.ax01.legend(
            [self.p011, self.p012], 
            [self.p011.get_label(), self.p012.get_label()]
        )
        self.ax02.legend(
            [self.p021, self.p022], 
            [self.p021.get_label(), self.p022.get_label()]
        )
        
        # Data Update
        self.xmin = 0.0
        self.x = 0.0
        
        # Set titles of subplots
        self.ax01.set_title('Distance vs Time')
        self.ax02.set_title('Speed(cm/s) vs Time')
        
        # Set y-limits
        self.ax01.set_ylim(0, 200)
        self.ax02.set_ylim(0, 50)
        
        # Set x-limits
        self.ax01.set_xlim(0, 5.0)
        self.ax02.set_xlim(0, 5.0)
        
        # Turn on grids
        self.ax01.grid(True)
        self.ax02.grid(True)
        
        # Set label names
        self.ax01.set_xlabel("t")
        self.ax01.set_ylabel("Distance")
        self.ax02.set_xlabel("t")
        self.ax02.set_ylabel("Ticks")
        
        # Start the variables with 0
        self.totLeftDist = 0
        self.totRightDist = 0
        self.leftSpeed = 0
        self.rightSpeed = 0
        self.ini_pos_left = 0
        self.ini_pos_right = 0 
    
    # Measure the speed of the robot
    def getSpeed(self):
        if (time.time() >= self.tf):
            self.tf = time.time() + self.sampleTime
            self.leftSpeed = (self.leftEncoderCount.getTotalDistance() -
                              self.ini_pos_left) / self.sampleTime
            self.rightSpeed = (self.rightEncoderCount.getTotalDistance() -
                               self.ini_pos_right) / self.sampleTime
            self.ini_pos_left = self.leftEncoderCount.getTotalDistance()
            self.ini_pos_right = self.rightEncoderCount.getTotalDistance()
    
    def teste(self):
        return self.xmax, self.yp1
    
    def updateData(self):
        self.totLeftDist = self.leftEncoderCount.getTotalDistance()
        self.totRightDist = self.rightEncoderCount.getTotalDistance()

        self.getSpeed()

        self.yp1 = append(self.yp1, self.totLeftDist)
        self.yv1 = append(self.yv1, self.leftSpeed)
        self.yp2 = append(self.yp2, self.totRightDist)
        self.yv2 = append(self.yv2, self.rightSpeed)
        self.t = append(self.t, self.x)
        self.x += 0.3
        self.p011.set_data(self.t, self.yp1)
        self.p012.set_data(self.t, self.yp2)
        self.p021.set_data(self.t, self.yv1)
        self.p022.set_data(self.t, self.yv2)
        
        # Actualizing data
        if self.yp1[-1] >= self.ymax - 40.00:
            self.p011.axes.set_ylim(self.yp1[-1] - self.ymax + 40.0, self.yp1[-1] + 40.0)
        if self.yp2[-1] >= self.ymax - 40.00:
            self.p011.axes.set_ylim(self.yp2[-1] - self.ymax + 40.0, self.yp2[-1] + 40.0)
        if self.yv1[-1] >= self.ymax - 40.00:
            self.p021.axes.set_ylim(self.yv1[-1] - self.ymax + 40.0, self.yv1[-1] + 40.0)
        if self.yv2[-1] >= self.ymax - 40.00:
            self.p021.axes.set_ylim(self.yv2[-1] - self.ymax + 40.0, self.yv2[-1] + 40.0)
        if self.x >= self.xmax - 1.00:
            self.p011.axes.set_xlim(self.x - self.xmax + 1.0, self.x + 1.0)
            self.p021.axes.set_xlim(self.x - self.xmax + 1.0, self.x + 1.0)
