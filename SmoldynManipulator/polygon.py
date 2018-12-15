from structures import *
import math as m
import numpy as np

class Polygon(Surface):
	"""
	name: 			naam
	centre: 		centrum van polygon
	n_corners:		aantal hoeken
	rib:			lengte een rib
	length:			lengte polygon op z-as
	n_segments:		hoeveelheid subdevision op z-as
	"""
	def __init__(self, name, centre = (0, 0, 0), n_corners = 0, rib = 0, length = 0, n_segments = 2):
		super(Polygon, self).__init__(name)
		self.set_shape(centre, n_corners, rib, length, n_segments)
		
	def set_shape(self, centre, n_corners, rib, length, n_segments = 2):
		self.centre = centre
		self.n_corners = n_corners
		self.rib = rib
		self.length = length
		self.n_segments = n_segments
	
	def __generate_polygon(self, appender):
		#calculating the twelve hexagon points for surface definition
		centre = self.centre
		corners = self.n_corners
		rib = self.rib
		length = self.length
		n_segments = self.n_segments
		
		points = []
		thetaList = np.arange(0, 2*m.pi, 2*m.pi/corners, dtype=np.dtype(float))
		segments = []
		z_vals = np.arange(centre[2]-length/2, centre[2]+length/2+1, length/(n_segments-1))
		# create polygon rings in xy-plane
		for n, z in enumerate(z_vals):
			segment = []
			for theta in thetaList:
				x=round(centre[0]+m.cos(theta)*rib, 1)
				y=round(centre[1]+m.sin(theta)*rib, 1)
				segment.append(" ".join((str(x),str(y),str(z))))
			segments.insert(n, segment)
		
		# join rings on the z-axis, by triangles
		tris = []
		panel_names = []
		for n in range(0, n_segments-1):
			l_seg = segments[n]
			r_seg = segments[n+1]
			for nl in range(len(l_seg)):
				next_nl = nl+1 if nl < (len(l_seg)-1) else 0
				l_one = l_seg[nl]
				l_two = l_seg[next_nl]
				r_one = r_seg[nl]
				r_two = r_seg[next_nl]
				name_1 = "triR_"+str(n)+"_"+str(nl)
				name_2 = "triL_"+str(n)+"_"+str(nl)
				p  = Surface._tab+"panel tri {} {} {} {}".format(l_one, r_one, r_two, name_1)
				p2 = Surface._tab+"panel tri {} {} {} {}".format(l_one, l_two, r_two, name_2)
				panel_names.append(name_1)
				panel_names.append(name_2)
				tris.append(p)
				tris.append(p2)
		
		# neighbour the triangles
		neighbours = []
		for i in range(1, len(panel_names)):
			prev_i = i-1
			next_i = i+1 if i < (len(panel_names)-1) else 0
			neighbour = self._tab+"neighbors {} {} {}".format(panel_names[prev_i], panel_names[i], panel_names[next_i])
			neighbours.append(neighbour)
		appender.extend(tris)
		appender.append("")
		appender.extend(neighbours)

	def __str_body__(self, appender):
		super(Polygon, self).__str_body__(appender)
		appender.append(Surface._tab+"# START GENERATED POLYGON("+str(self.n_corners)+")")
		self.__generate_polygon(appender)
		appender.append(Surface._tab+"# END GENERATED POLYGON")
		
if __name__ == "__main__":
	poly = Polygon("somename")
	print(poly)
	print("asdasd")