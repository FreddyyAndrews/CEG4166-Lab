import math
import matplotlib.pyplot as plt
import matplotlib.animation as animation

class DummyPlotData:
    def __init__(self, samples, xmax):
        self.samples = samples
        self.xmax = xmax
        # Create a figure with two subplots for left and right encoders
        self.fig, (self.ax1, self.ax2) = plt.subplots(2, 1, figsize=(8, 6))
        self.ax1.set_title("Left Encoder")
        self.ax2.set_title("Right Encoder")
        self.ax1.set_xlim(0, self.xmax)
        self.ax1.set_ylim(0, 100)
        self.ax2.set_xlim(0, self.xmax)
        self.ax2.set_ylim(0, 100)
        
        # Initialize data arrays and a counter for the x-axis
        self.xdata = []
        self.left_current = []
        self.left_total = []
        self.right_current = []
        self.right_total = []
        self.counter = 0

        # Create line objects for current and total distances on both axes
        self.p011, = self.ax1.plot([], [], label="Left Current")
        self.p012, = self.ax1.plot([], [], label="Left Total")
        self.p021, = self.ax2.plot([], [], label="Right Current")
        self.p022, = self.ax2.plot([], [], label="Right Total")
        self.ax1.legend()
        self.ax2.legend()

    def updateData(self):
        # Increment time counter and add to xdata
        self.counter += 1
        self.xdata.append(self.counter)
        
        # Generate dummy 'current' distances using sine and cosine functions
        left_current_val = 5 + 2 * math.sin(self.counter / 10.0)
        right_current_val = 5 + 2 * math.cos(self.counter / 10.0)
        
        # Compute cumulative (total) distances by summing current values
        if self.left_total:
            left_total_val = self.left_total[-1] + left_current_val
            right_total_val = self.right_total[-1] + right_current_val
        else:
            left_total_val = left_current_val
            right_total_val = right_current_val

        self.left_current.append(left_current_val)
        self.left_total.append(left_total_val)
        self.right_current.append(right_current_val)
        self.right_total.append(right_total_val)

        # Keep only the most recent 'samples' points
        if len(self.xdata) > self.samples:
            self.xdata = self.xdata[-self.samples:]
            self.left_current = self.left_current[-self.samples:]
            self.left_total = self.left_total[-self.samples:]
            self.right_current = self.right_current[-self.samples:]
            self.right_total = self.right_total[-self.samples:]
            # Adjust x-axis to display the latest window of data
            self.ax1.set_xlim(self.xdata[0], self.xdata[-1])
            self.ax2.set_xlim(self.xdata[0], self.xdata[-1])

        # Update the line objects with the new data
        self.p011.set_data(self.xdata, self.left_current)
        self.p012.set_data(self.xdata, self.left_total)
        self.p021.set_data(self.xdata, self.right_current)
        self.p022.set_data(self.xdata, self.right_total)

    def getLines(self):
        # Return all line objects for the animation update
        return [self.p011, self.p012, self.p021, self.p022]

# Parameters (using the same settings as the original code)
samples = 5
xmax = 5
plotData = DummyPlotData(samples, xmax)

def update(frame):
    plotData.updateData()
    return plotData.getLines()

# Create and run the animation
ani = animation.FuncAnimation(
    plotData.fig, update, frames=200, interval=20, blit=False, repeat=False
)

plt.tight_layout()
plt.show()
print("Finished")
plt.close()
