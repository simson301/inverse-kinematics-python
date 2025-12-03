import math
from matplotlib import pyplot as plt

class Segment:
    def __init__(self, base, tip):
        self.base = base
        self.tip = tip
        self.length = Point3.distance(self.base, self.tip)

    def adjust_to_new_point(self, p):
        self.tip = p
        v = Vector3.from_points(self.tip, self.base)
        v = v.normalize()
        v = v.scalar(self.length)
        self.base = v.to_point(self.tip)
    
    def reverse(self): # reverse Segment used in backward wiggle
        buffer = self.base
        self.base = self.tip
        self.tip = buffer
    
    def angle(self): # calculate the xy and xz angle disregarding the other segments angles
        dx = self.tip.x - self.base.x 
        dy = self.tip.y - self.base.y
        dz = self.tip.z - self.base.z

        r_xy = math.sqrt(dx**2 + dy**2)
        r_xz = math.sqrt(dx**2 + dz**2)

        # Calculate angle using cosine
        cos_theta_xy = dx / r_xy
        angle_xy = math.acos(cos_theta_xy)

        cos_theta_xz = dx / r_xz
        angle_xz = math.acos(cos_theta_xz)

        # Adjust based on y- and z-position to account for full [0, 2π] range
        if dy < 0:
            angle_xy = -angle_xy
        if dz < 0:
            angle_xz = -angle_xz

        return (round(math.degrees(angle_xy)), round(math.degrees(angle_xz)))
        


class Arm:
    def __init__(self, segments=[]):
        self.segments = segments
    
    def addSegment(self, length):
        if len(self.segments) > 0:
            base = self.segments[-1].tip
            tip = Point3(base.x, base.y+length, base.z)
            self.segments.append(Segment(base, tip))
        else:
            base = Point3(0,0,0)
            tip = Point3(base.x, base.y+length, base.z)
            self.segments.append(Segment(base, tip))

    def addSegments(self, segment_lengths):
        for segment_length in segment_lengths:
            self.addSegment(segment_length)

    def wiggle(self, p, n):
        first_base = self.segments[0].base
        current_point = p
        l = len(self.segments)
        
        for i in range(n):
            current_point = p
            # forward wiggle
            for i in reversed(range(l)):
                segment = self.segments[i]
                segment.adjust_to_new_point(current_point)
                current_point = segment.base
           
            current_point = first_base
            
            # backward wiggle
            for i in range(l):
                segment = self.segments[i]
                segment.reverse()
                segment.adjust_to_new_point(current_point)
                current_point = segment.base

            for segment in self.segments:
                segment.reverse()  
    
    def map_value(value, from_low, from_high, to_low, to_high):
        # Calculate scaled value
        return (value - from_low) * (to_high - to_low) / (from_high - from_low) + to_low
        
    def calculate_servo_angles(self):
        # Calculate the Segments xy angles regarding the previous Segements
        angles = [self.segments[0].angle()[0]]
        for i in range(1, len(self.segments)):
            angles.append(Arm.map_value(self.segments[i].angle()[0], self.segments[i-1].angle()[0]-90, self.segments[i-1].angle()[0]+90, 0, 180))

        return angles
    
    def plot_xy(self): # Plot x and y positions
        plt.axis("equal")
        for s in self.segments:
            # Connect base → tip with a line
            plt.plot(
                [s.base.x, s.tip.x],
                [s.base.y, s.tip.y],
                color='black',
                marker='o'
            )

        plt.show()

    def plot_xz(self): # Plot x and z positions
        plt.axis("equal")
        for s in self.segments:
            # Connect base → tip with a line
            plt.plot(
                [s.base.x, s.tip.x],
                [s.base.z, s.tip.z],
                color='black',
                marker='o'
            )

        plt.show()
    
    def plot_xy_xz(self): # Plot both x, y and x, z positions using subplots
        fig, axes = plt.subplots(1, 2, figsize=(12, 6))  # 1 row, 2 columns

        # XY plot
        axes[0].set_title("XY Projection")
        axes[0].axis("equal")
        for s in self.segments:
            axes[0].plot(
                [s.base.x, s.tip.x],
                [s.base.y, s.tip.y],
                color='black',
                marker='o'
            )

        # XZ plot
        axes[1].set_title("XZ Projection")
        axes[1].axis("equal")
        for s in self.segments:
            axes[1].plot(
                [s.base.x, s.tip.x],
                [s.base.z, s.tip.z],
                color='black',
                marker='o'
            )

        plt.tight_layout()
        plt.show()

    def log(self):
        angles = self.calculate_servo_angles()

        print("============= SEGMENTS ============= ")
        
        for i in range(len(self.segments)):
            seg = self.segments[i]

            print(f"""SEGMENT {i+1}:
                  
Base X: {seg.base.x}, Y: {seg.base.y}, 
Tip X: {seg.tip.x}, Y: {seg.tip.y}, 
fixed Length: {seg.length}, 
current Length: {Point3.distance(seg.base, seg.tip)},
Rotation: {angles[i]}
""")
        print(f"\nRotation Z: {Arm.map_value(arm.segments[0].angle()[1], -90, 90, 0, 180)}")

        



class Point3: # A bit unnecessary Point class (could just use Vector3)
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
    
    def distance(p1, p2):
        return math.sqrt((p2.x-p1.x)**2 + (p2.y-p1.y)**2 + (p2.z-p1.z)**2)

class Vector3:
    @classmethod
    def from_points(cls, p1, p2):
        return cls(
            p2.x - p1.x,
            p2.y - p1.y,
            p2.z - p1.z
        )

    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
    
    def magnitude(self):
        return math.sqrt(self.x**2 + self.y**2 + self.z**2)
    
    def normalize(self):
        return Vector3(self.x / self.magnitude(), self.y / self.magnitude(), self.z / self.magnitude())
    
    def scalar(self, n):
        return Vector3(self.x * n, self.y * n, self.z * n)
    
    def to_point(self, p):
        return Point3(self.x+p.x, self.y+p.y, self.z+p.z)
    
"""
arm = Arm([
    Segment(Point3(0, 0, 0), Point3(0, 2, 0)), 
    Segment(Point3(0, 2, 0), Point3(0, 4, 0)), 
    Segment(Point3(0, 4, 0), Point3(0, 6, 0)), 
    Segment(Point3(0, 6, 0), Point3(0, 8, 0)), 
    Segment(Point3(0, 8, 0), Point3(0, 10, 0))
    ])
"""

arm = Arm()

arm.addSegments([2,2,2,2,2])
arm.wiggle(Point3(5, 7, 0), 10)
arm.log()
arm.plot_xy_xz()



