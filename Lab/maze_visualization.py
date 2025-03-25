import tkinter as tk
from tkinter import ttk
import threading
import time
import queue
import traceback

class MazeVisualization:
    def __init__(self, root, grid_size=15, cell_size=30):
        self.root = root
        self.root.title("Maze Solver Visualization")
        
        # Set up the visualization parameters
        self.grid_size = grid_size  # Size of the maze grid
        self.cell_size = cell_size  # Size of each cell in pixels
        
        # Set up data structures
        self.robot_position = [grid_size // 2, grid_size // 2]  # Start in the middle
        self.robot_direction = 0  # 0: North, 1: East, 2: South, 3: West
        self.visited_cells = set()      # All visited cells
        self.revisited_cells = set()    # Cells that have been visited more than once
        self.obstacle_cells = set()     # Cells marked as obstacles
        self.data_queue = queue.Queue()
        
        # Direction vectors (North, East, South, West)
        self.dx = [0, 1, 0, -1]
        self.dy = [-1, 0, 1, 0]
        
        # Sensor direction (same as robot direction initially)
        self.sensor_direction = 0
        
        # Last measured distance (to display sensor beam)
        self.last_distance = 0
        self.max_sensor_range = 50  # Maximum range to display in grid units
        
        # Create the canvas for drawing
        canvas_width = grid_size * cell_size
        canvas_height = grid_size * cell_size
        self.canvas = tk.Canvas(root, width=canvas_width, height=canvas_height, bg="white")
        self.canvas.pack(pady=10)
        
        # Create control panel
        self.control_frame = ttk.Frame(root)
        self.control_frame.pack(fill="x", padx=10, pady=5)
        
        # Distance display
        self.distance_var = tk.StringVar(value="Distance: -- cm")
        distance_label = ttk.Label(self.control_frame, textvariable=self.distance_var, font=("Arial", 12))
        distance_label.pack(side="left", padx=10)
        
        # Status display
        self.status_var = tk.StringVar(value="Status: Idle")
        status_label = ttk.Label(self.control_frame, textvariable=self.status_var, font=("Arial", 12))
        status_label.pack(side="right", padx=10)
        
        # Add reset button
        reset_button = ttk.Button(self.control_frame, text="Reset View", command=self.reset_visualization)
        reset_button.pack(side="bottom", pady=5)
        
        # Add a clear obstacles button
        clear_button = ttk.Button(self.control_frame, text="Clear Obstacles", command=self.clear_obstacles)
        clear_button.pack(side="bottom", pady=5)
        
        # Add a clear path button
        clear_path_button = ttk.Button(self.control_frame, text="Clear Path", command=self.clear_path)
        clear_path_button.pack(side="bottom", pady=5)
        
        # Draw initial grid
        self.draw_grid()
        self.draw_robot()
        
        # Set up the update loop - process updates in the main thread to avoid Tkinter threading issues
        self.running = True
        self.root.after(50, self.process_queue)
    
    def clear_obstacles(self):
        """Clear all obstacles from the map"""
        for x, y in list(self.obstacle_cells):
            self.update_cell(x, y, 'clear')
        print("Cleared all obstacles")
    
    def process_queue(self):
        """Process updates from the queue in the main thread"""
        try:
            # Process up to 10 updates per cycle to prevent lag
            for _ in range(10):
                if not self.data_queue.empty():
                    update_type, data = self.data_queue.get(block=False)
                    
                    if update_type == 'move':
                        self.move_robot(data)
                    elif update_type == 'distance':
                        self.update_distance(data)
                        # Store the distance for sensor beam visualization
                        self.last_distance = data
                        # Redraw the robot with updated sensor beam
                        self.draw_robot()
                    elif update_type == 'status':
                        self.update_status(data)
                        # Update sensor direction based on status message
                        if "Looking at angle" in data:
                            angle = float(data.split("angle ")[1])
                            if angle <= 5.0:  # Left position
                                self.sensor_direction = (self.robot_direction - 1) % 4
                            elif angle >= 10.0:  # Right position
                                self.sensor_direction = (self.robot_direction + 1) % 4
                            else:  # Center position
                                self.sensor_direction = self.robot_direction
                            self.draw_robot()  # Redraw to show sensor direction
                    elif update_type == 'obstacle':
                        # Get position in the direction the sensor is looking
                        x, y = self.robot_position
                        # Calculate position in front of the sensor
                        front_x = x + self.dx[self.sensor_direction]
                        front_y = y + self.dy[self.sensor_direction]
                        if 0 <= front_x < self.grid_size and 0 <= front_y < self.grid_size:
                            self.update_cell(front_x, front_y, 'obstacle')
                            # Also highlight the detection in status
                            self.update_status(f"Obstacle at {front_x},{front_y}")
                else:
                    break
        except Exception as e:
            print(f"Error in GUI update: {e}")
            traceback.print_exc()
        
        # Schedule the next update if still running
        if self.running and self.root.winfo_exists():
            self.root.after(50, self.process_queue)
    
    def draw_grid(self):
        """Draw the grid lines"""
        for i in range(self.grid_size + 1):
            # Vertical lines
            x = i * self.cell_size
            self.canvas.create_line(x, 0, x, self.grid_size * self.cell_size, fill="gray")
            
            # Horizontal lines
            y = i * self.cell_size
            self.canvas.create_line(0, y, self.grid_size * self.cell_size, y, fill="gray")
    
    def draw_robot(self):
        """Draw the robot at its current position"""
        x, y = self.robot_position
        cell_x = x * self.cell_size
        cell_y = y * self.cell_size
        
        # Clear previous robot and sensor beam
        self.canvas.delete("robot")
        self.canvas.delete("sensor_beam")
        
        # Draw robot body
        self.canvas.create_oval(
            cell_x + 5, cell_y + 5, 
            cell_x + self.cell_size - 5, cell_y + self.cell_size - 5, 
            fill="blue", tags="robot"
        )
        
        # Draw direction indicator (robot movement direction)
        direction_x = cell_x + self.cell_size/2 + self.dx[self.robot_direction] * 10
        direction_y = cell_y + self.cell_size/2 + self.dy[self.robot_direction] * 10
        self.canvas.create_line(
            cell_x + self.cell_size/2, cell_y + self.cell_size/2,
            direction_x, direction_y,
            fill="white", width=3, tags="robot"
        )
        
        # Draw sensor direction indicator 
        sensor_x = cell_x + self.cell_size/2 + self.dx[self.sensor_direction] * 8
        sensor_y = cell_y + self.cell_size/2 + self.dy[self.sensor_direction] * 8
        self.canvas.create_line(
            cell_x + self.cell_size/2, cell_y + self.cell_size/2,
            sensor_x, sensor_y,
            fill="yellow", width=2, tags="robot"
        )
        
        # Draw sensor beam based on last measured distance
        if self.last_distance > 0:
            # Convert distance from cm to grid units (approximate)
            grid_distance = min(self.last_distance / 10, self.max_sensor_range)
            beam_end_x = cell_x + self.cell_size/2 + self.dx[self.sensor_direction] * grid_distance * self.cell_size / 2
            beam_end_y = cell_y + self.cell_size/2 + self.dy[self.sensor_direction] * grid_distance * self.cell_size / 2
            
            # Draw the sensor beam
            self.canvas.create_line(
                cell_x + self.cell_size/2, cell_y + self.cell_size/2,
                beam_end_x, beam_end_y,
                fill="lightblue", width=1, dash=(3, 2), tags="sensor_beam"
            )
            
            # Draw endpoint of beam
            self.canvas.create_oval(
                beam_end_x - 3, beam_end_y - 3,
                beam_end_x + 3, beam_end_y + 3,
                fill="cyan", outline="", tags="sensor_beam"
            )
    
    def update_cell(self, x, y, cell_type):
        """Update a cell's visual representation
        cell_type: 'visited', 'revisited', 'obstacle', or 'clear'
        """
        if x < 0 or x >= self.grid_size or y < 0 or y >= self.grid_size:
            return  # Out of bounds
        
        cell_x = x * self.cell_size
        cell_y = y * self.cell_size
        
        # Remove existing cell
        self.canvas.delete(f"cell_{x}_{y}")
        
        if cell_type == 'visited':
            self.visited_cells.add((x, y))
            self.canvas.create_rectangle(
                cell_x + 1, cell_y + 1,
                cell_x + self.cell_size - 1, cell_y + self.cell_size - 1,
                fill="lightgreen", outline="", tags=f"cell_{x}_{y}"
            )
        elif cell_type == 'revisited':
            self.revisited_cells.add((x, y))
            self.canvas.create_rectangle(
                cell_x + 1, cell_y + 1,
                cell_x + self.cell_size - 1, cell_y + self.cell_size - 1,
                fill="yellow", outline="", tags=f"cell_{x}_{y}"
            )
        elif cell_type == 'obstacle':
            self.obstacle_cells.add((x, y))
            self.canvas.create_rectangle(
                cell_x + 1, cell_y + 1,
                cell_x + self.cell_size - 1, cell_y + self.cell_size - 1,
                fill="red", outline="", tags=f"cell_{x}_{y}"
            )
            # Add a small text label to show coordinates
            self.canvas.create_text(
                cell_x + self.cell_size/2, cell_y + self.cell_size/2,
                text=f"{x},{y}", fill="white", font=("Arial", 8),
                tags=f"cell_{x}_{y}"
            )
        elif cell_type == 'clear':
            if (x, y) in self.visited_cells:
                self.visited_cells.remove((x, y))
            if (x, y) in self.revisited_cells:
                self.revisited_cells.remove((x, y))
            if (x, y) in self.obstacle_cells:
                self.obstacle_cells.remove((x, y))
    
    def move_robot(self, direction):
        """Move the robot in the specified direction
        direction: 'forward', 'right', 'left', 'backward'
        """
        # Get current position
        x, y = self.robot_position
        
        # Check if we've already visited this cell
        if (x, y) in self.visited_cells:
            # Mark as revisited (will be shown in yellow)
            self.revisited_cells.add((x, y))
            self.update_cell(x, y, 'revisited')
        else:
            # Mark as visited for the first time (will be shown in green)
            self.visited_cells.add((x, y))
            self.update_cell(x, y, 'visited')
        
        # Update robot direction
        if direction == 'right':
            self.robot_direction = (self.robot_direction + 1) % 4
        elif direction == 'left':
            self.robot_direction = (self.robot_direction - 1) % 4
        elif direction == 'backward':
            self.robot_direction = (self.robot_direction + 2) % 4
        
        # Move forward in the current direction
        if direction == 'forward' or direction == 'backward':
            new_x = x + self.dx[self.robot_direction]
            new_y = y + self.dy[self.robot_direction]
            
            # Check if the new position is valid
            if 0 <= new_x < self.grid_size and 0 <= new_y < self.grid_size:
                if (new_x, new_y) not in self.obstacle_cells:
                    self.robot_position = [new_x, new_y]
        
        # Redraw the robot
        self.draw_robot()
    
    def update_distance(self, distance):
        """Update the displayed distance"""
        self.distance_var.set(f"Distance: {distance} cm")
    
    def update_status(self, status):
        """Update the displayed status"""
        self.status_var.set(f"Status: {status}")
    
    def add_update(self, update_type, data):
        """Add an update to the queue"""
        self.data_queue.put((update_type, data))
    
    def stop(self):
        """Stop the visualization thread"""
        self.running = False
    
    def reset_visualization(self):
        """Reset the visualization to initial state"""
        # Clear all cells
        for x, y in list(self.visited_cells) + list(self.revisited_cells) + list(self.obstacle_cells):
            self.update_cell(x, y, 'clear')
        
        # Reset data structures
        self.visited_cells.clear()
        self.revisited_cells.clear()
        self.obstacle_cells.clear()
        
        # Reset robot position
        self.robot_position = [self.grid_size // 2, self.grid_size // 2]
        self.robot_direction = 0
        self.sensor_direction = 0
        self.last_distance = 0
        self.draw_robot()
        
        # Reset displays
        self.distance_var.set("Distance: -- cm")
        self.status_var.set("Status: Reset")
    
    def clear_path(self):
        """Clear only the path history but keep obstacles"""
        for x, y in list(self.visited_cells) + list(self.revisited_cells):
            # Only clear if it's not an obstacle
            if (x, y) not in self.obstacle_cells:
                self.canvas.delete(f"cell_{x}_{y}")
        
        # Reset visited data
        self.visited_cells.clear()
        self.revisited_cells.clear()
        
        # Update status
        self.status_var.set("Status: Path cleared")
        print("Path history cleared")


def start_visualization():
    """Start the visualization in a separate thread"""
    try:
        root = tk.Tk()
        root.protocol("WM_DELETE_WINDOW", lambda: None)  # Disable window close button
        viz = MazeVisualization(root)
        
        # This function returns the visualization object so it can be controlled
        # from the main program
        return viz, root
    except Exception as e:
        print(f"Error starting visualization: {e}")
        traceback.print_exc()
        # Return dummy objects if visualization fails
        class DummyViz:
            def add_update(self, *args): pass
            def stop(self): pass
        return DummyViz(), None


if __name__ == "__main__":
    # Test the visualization
    viz, root = start_visualization()
    
    # Example updates
    def test_updates():
        time.sleep(1)
        viz.add_update('status', 'Moving forward')
        viz.add_update('distance', 25)
        viz.add_update('move', 'forward')
        time.sleep(1)
        viz.add_update('distance', 15)
        viz.add_update('status', 'Obstacle detected')
        viz.add_update('obstacle', None)
        time.sleep(1)
        viz.add_update('status', 'Turning right')
        viz.add_update('move', 'right')
        time.sleep(1)
        viz.add_update('status', 'Moving forward')
        viz.add_update('move', 'forward')
    
    threading.Thread(target=test_updates).start()
    
    # Start the main loop
    root.mainloop() 