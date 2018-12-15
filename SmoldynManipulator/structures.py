#!/usr/bin/python
# -*- coding: utf-8 -*-
class Surface(object):
	"""
		Aanpasbaar smoldyn surface object
		Joaquin van den Bemt: 25-11-2018
	"""
	_tab = "   "
	
	def __init__(self, name):
		self.name = name
		self.properties = {}
		self.panels = []
		self.neighbours = []
		
	def thickness(self, value):
		self.properties["thickness"] = int(value)
		return self
		
	def color(self, side, r, g, b, a=1.0):
		self.properties["color"] = (side, r, g, b, a)
		return self
	
	def set_property(self, property, value):
		self.properties[property] = value
		return self
		
	def __str_body__(self, appender):
		for prop, value in self.properties.items():
			line = (Surface._tab+prop+" ")
			if type(value) is list:
				line += (" ".join(map(str, value)))
			elif type(value) is tuple:
				line += (" ".join(map(str, value)))
			else:
				line += str(value)
			appender.append(line)
		for panel in self.panels:
			appender.append(Surface._tab+str(panel))
		for neighbour in self.neighbours:
			appender.append(Surface._tab+neighbour)
		
	
	def __str__(self):
		surface = ["start_surface "+self.name]
		self.__str_body__(surface)
		surface.append("end_surface")
		return "\n".join(surface)
		
	def add_panel(self, panel):
		if type(panel) is list:
			for p in panel:
				self.panels.append(p)
		else :
			self.panels.append(panel)
		return self
	
	def add_neighbours(self, neighbour):
		if type(neighbour) is list:
			for n in neighbour:
				self.neighbours.append(n)
		else :
			self.neighbours.append(neighbour)
		return self
			
	def clear_panels(self):
		self.panels = []
		return self

if __name__ == '__main__':
	surf = Surface("test")
	surf.thickness(1)
	surf.color("both", 0, 1, 0, .4)
	surf.add_panel(["panel tri 60 15 70 80 15 70 70 15 86",  # 1 2 3
	"panel tri 60 15 70 70 15 86 70 31 77",  			# 1 3 4
	"panel tri 70 15 86 80 15 70 70 31 77",  # 3 2 4
	"panel tri 80 15 70 60 15 70 70 31 77"])
	print(surf)