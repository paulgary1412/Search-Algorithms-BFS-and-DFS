import tkinter as tk
import math
from typing import List, Union, Tuple

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __add__(self, other):
        return Point(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Point(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar):
        return Point(self.x * scalar, self.y * scalar)

    def __truediv__(self, scalar):
        return Point(self.x / scalar, self.y / scalar)

    def __repr__(self):
        return f"Point({self.x}, {self.y})"

    def get_coords(self):
        return (self.x, self.y)

    def draw_point(self, canvas: tk.Canvas, fill="black", width=10):
        r = width / 2
        return canvas.create_oval(self.x - r, self.y - r, self.x + r, self.y + r, fill=fill)

    @staticmethod
    def from_coords_list(coords: list):
        points = [Point(x, y) for x, y in zip(coords[::2], coords[1::2])]
        return points

    @staticmethod
    def flatten_pts_list(points: list):
        return [point.get_coords() for point in points]

class Line:
    def __init__(self, start: Point, end: Point, other_points: List[Point]=None):
        self.start = start
        self.end = end
        self.points = [start]
        if other_points:
            self.points.extend(other_points)
        self.points.append(end)

    def __repr__(self):
        return f"Line({self.start}, {self.end})"

    def get_midpoint(self):
        return (self.start + self.end) / 2

    def get_angle(self):
        start = Point(0, 0)
        end = Point(self.end.x - self.start.x, (self.end.y - self.start.y) * -1)
        return math.atan2(end.y - start.y, end.x - start.x)

    def get_perpendicular_angle(self):
        return self.get_angle() + math.pi / 2

    def get_distance(self):
        return math.sqrt((self.end.x - self.start.x)**2 + (self.end.y - self.start.y)**2)

    def draw_line(self, canvas: tk.Canvas, show_points=False, point_color="black", width=2, **kwargs):
        if show_points:
            for point in self.points:
                point.draw_point(canvas, point_color)
        return canvas.create_line([point.get_coords() for point in self.points], width=width, smooth=True, **kwargs)

class LineBuilder:
    def __init__(self):
        self.start_point: Point = None
        self.end_point: Point = None

    def set_start_point(self, start_point: Union[Point, Tuple[float, float]]):
        self.start_point = self.to_point(start_point)
        return self

    def set_end_point(self, end_point: Union[Point, Tuple[float, float]]):
        self.end_point = self.to_point(end_point)
        return self

    def from_radians_and_length(self, start_point, angle, length):
        self.start_point = self.to_point(start_point)
        self.angle = angle
        self.length = length
        self.calc_end_point()
        return self.build()

    def from_degrees_and_length(self, start_point, angle, length):
        self.start_point = self.to_point(start_point)
        self.angle = math.radians(angle)
        self.length = length
        self.calc_end_point()
        return self.build()

    def calc_end_point(self):
        end_x = self.start_point.x + self.length * math.cos(self.angle)
        end_y = self.start_point.y - self.length * math.sin(self.angle)
        self.end_point = Point(end_x, end_y)

    def build(self):
        if any([self.start_point is None, self.end_point is None]):
            raise ValueError("Start point and end point must be set.")
        return Line(self.start_point, self.end_point)

    @staticmethod
    def to_point(point: Union[Point, Tuple[float, float]]):
        return point if isinstance(point, Point) else Point(*point)

class Ellipse:
    def __init__(self, center: Point, a, b, angle):
        self.center = center
        self.a = a
        self.b = b
        self.angle = angle

    def __repr__(self):
        return f"Ellipse({self.center}, {self.a}, {self.b})"

    def draw(self, canvas: tk.Canvas, **kwargs):
        points: List[Point] = []
        for i in range(0, 360, 15):
            angle = math.radians(i)
            x = self.center.x + self.a * math.cos(angle) * math.cos(self.angle) - self.b * math.sin(angle) * math.sin(self.angle)
            y = self.center.y - self.b * math.sin(angle) * math.cos(self.angle) - self.a * math.cos(angle) * math.sin(self.angle)
            points.append(Point(x, y))

        return canvas.create_polygon([point.get_coords() for point in points], smooth=True, **kwargs)

    def update_center(self, dx, dy):
        self.center.x += dx
        self.center.y += dy

    def contains(self, x, y):
        return ((x - self.center.x) ** 2) / (self.a ** 2) + ((y - self.center.y) ** 2) / (self.b ** 2) <= 1

    def get_point_from_angle(self, angle): 
        x = self.center.x + self.a * math.cos(angle) * math.cos(self.angle) - self.b * math.sin(angle) * math.sin(self.angle)
        y = self.center.y - self.b * math.sin(angle) * math.cos(self.angle) - self.a * math.cos(angle) * math.sin(self.angle)
        return Point(x, y)

    def draw_major_axis(self, canvas: tk.Canvas, color="black", **kwargs):
        angle = self.angle
        start_x = self.center.x + self.a * math.cos(angle)
        start_y = self.center.y - self.a * math.sin(angle)
        end_x = self.center.x - self.a * math.cos(angle)
        end_y = self.center.y + self.a * math.sin(angle)
        canvas.create_line(start_x, start_y, end_x, end_y, fill=color, **kwargs)

    def draw_minor_axis(self, canvas: tk.Canvas, color="red", **kwargs):
        angle = self.angle + math.pi / 2
        start_x = self.center.x + self.b * math.cos(angle)
        start_y = self.center.y - self.b * math.sin(angle)
        end_x = self.center.x - self.b * math.cos(angle)
        end_y = self.center.y + self.b * math.sin(angle)
        canvas.create_line(start_x, start_y, end_x, end_y, fill=color, **kwargs)

    def draw_axes(self, canvas: tk.Canvas, major_color="blue", minor_color="red", **kwargs):
        self.draw_major_axis(canvas, color=major_color, **kwargs)
        self.draw_minor_axis(canvas, color=minor_color, **kwargs)

class EllipseBuilder:
    def __init__(self):
        self.center: Point = None
        self.a = None
        self.b = None
        self.angle = None

    def set_center(self, center: Union[Point, Tuple[float, float]]):
        self.center = center if isinstance(center, Point) else Point(*center)
        return self

    def set_a(self, a):
        self.a = a
        return self

    def set_b(self, b):
        self.b = b
        return self

    def set_width_and_height(self, width, height):
        long_axis = max(width, height)
        short_axis = min(width, height)
        self.a = long_axis / 2
        self.b = short_axis / 2
        return self

    def set_radians(self, angle):
        self.angle = angle
        return self

    def set_degrees(self, angle):
        self.angle = math.radians(angle)
        return self

    def build(self):
        if self.angle is None:
            self.angle = 0
        if any([self.center is None, self.a is None, self.b is None]):
            raise ValueError("Center, a, b, and angle must be set.")
        return Ellipse(self.center, self.a, self.b, self.angle)
