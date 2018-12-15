#!/usr/bin/python
# -*- coding: utf-8 -*-
import re
from subprocess import Popen, PIPE
import os
import errno

class Manipulator(object):
	"""
		Maakt de manipulatie van smoldyn automatiseerbaar dmv van tags:
			#TAG: identifier
			of:	
			#color both 0 #TAG:green #TAG:blue 1 	-> silenced: commment op het begin wordt weggehaald als een vervangende waarde bekend is
													   dit geeft de mogelijkheid het bron-script ook runbaar te maken
			color both 0 #TAG:green #TAG:blue 1		-> non-silent
		Joaquin van den Bemt: 25-11-2018
	"""
	__tag = re.compile(r"#[\sa-zA-Z0-9-]*TAG:\s*", re.IGNORECASE)

	def __init__(self, data):
		self.__data = []
		self.mods = {}
		for line in data:
			line = line.rstrip()
			line = line.replace("\t", "   ")
			if self.__tag.search(line):
				indices, id = Manipulator.__get_tag(line)
				print("Found id: "+ '\"'+id+'\"')
				self.mods[id] = None
			self.__data.append(line)
			self.output_filename = "output.txt"
	
	@classmethod
	def from_file(cls, filename, strip_comments = False, strip_empty_lines = False):
		inf = open(filename)
		data = []
		for line in inf:                    			# Loop alle regels in de file af
			hashtag = line.find("#")
			if strip_comments and hashtag is not -1:
				if Manipulator.__tag.search(line):		# don't strip tags, 
					indices, id = Manipulator.__get_tag(line)
					_, _, index_end = indices
					hashtag = line[index_end:].find("#") + index_end
					if hashtag is not -1:				# do skip comments after tags
						line = line[0:hashtag]
				else:
					line = line[0:hashtag]
					if not line.strip():		# always skip empty lines coming from a stripped comment
						continue
			line = line.rstrip()
			if strip_empty_lines and not line:	# skip empty lines
				continue
			data.append(line)
		inf.close()
		return cls(data)

	@staticmethod
	def __get_tag(line):
		"""
			return:
				tuple [0] : indices tuple
						[0] : start index of the tag "#"
						[1] : start index of the id
						[2] : end index of the tag " "
				id : identifier of tag
		"""
		match_objs = [m for m in Manipulator.__tag.finditer(line)]
		tag_start = match_objs[0].start(0)
		tag_end   = match_objs[0].end(0)
		id = line[tag_end:].split(" ")[0]
		return ((tag_start, tag_end, tag_end+len(id)), id)
	
	def replace(self, id, replacement):
		self.mod[id] = replacement
		
	def set_output_filename(self, value):
		self.output_filename = value
		return self
		
	def replace_tag(self, line):
		"""
			replace 
		"""
		indices, id = Manipulator.__get_tag(line)
		replacement = self.mods[id]

		if replacement is None:
			print("{:<20} has no replacement".format(id))
			return line
		else:
			index_tag_start, index_id, index_tag_end = indices
			header = line[0:index_tag_start]
			silenced = False
			if "#" in header:
				silenced = True
				print("{:<20} is no longer silenced".format(id))
				index_silencer = header.find("#")
				header = header[0:index_silencer] + header[index_silencer+1:]
				
			empty_header = True if not header.strip() else False
			footer = line[index_tag_end:]
			empty_footer = True if not footer.strip() else False
			if empty_header:
				#replace mode - vervang hele lijn
				whitespace = header
				print(("{:<20} > replaced by value "+str(type(replacement))).format(id))
				var = self.write_var_to_string(replacement, whitespace)
				if not empty_footer:
					var = whitespace+footer.lstrip() +"\n"+var
				return var
			else:
				#insert mode - plaats string in een lijn bijv. #color both #TAG:color 0.1
				print(("{:<20} > inserted value "+str(type(replacement))).format(id))
				return header + self.write_var_to_string(replacement) + footer
	
	def get_data(self):
		return self.__data
	
	def get_manipulated_data(self):
		data = []
		for line in self.__data:
			if self.__tag.search(line):
				data.append(self.replace_tag(line))
			else:
				data.append(line)
		return data
				
	def save(self,folder=os.path.dirname(os.path.abspath(__file__))):
		"""
			save the manipulated config to a file
		"""
		THIS_FOLDER = folder
		my_file = os.path.join(THIS_FOLDER, self.output_filename)
		print my_file
		if not os.path.exists(os.path.dirname(self.output_filename)):
			try:
				os.makedirs(os.path.dirname(my_file))
			except OSError as exc: 	# Guard against race condition
				if exc.errno != errno.EEXIST:
					raise
					
		f = open(my_file,"w+")
		f.write("\n".join(self.get_manipulated_data()))
		f.close()
		
	def write_var_to_string(self, var, prefix = ""):
		"""
			write variable to string
			params:
				var:		variable
				prefix:		prefix
			return:
				string
		"""
		if type(var) is list:
			return "\n".join([prefix + self.write_var_to_string(line, prefix) for line in var])
		elif type(var) is tuple:
			return ' '.join(map(str, var))
		else:
			str_repr = str(var)
			if prefix and str_repr.count("\n") > 1:
				# with string_representation of custom object each line should be prefixed
				# used for formatting
				unprefixed = str_repr.split("\n")
				prefixed = []
				for l in unprefixed:
					prefixed.append(prefix+l)
				return "\n".join(prefixed)
			else:
				return prefix + str_repr
			
	def dim(self):
		"""
			return:
				the value of the dim property
		"""
		return (self.get_static_property("dim")[0][0])	

	def get_property(self, property_name, data_set = "static"):
		"""
			retrieve all occurences of this property
			params:
				data_set:
					"static": the non-manipulated data_set is used
					"manipulated": the manipulated data_set is used
					other: custom data set can be passed as an argument
			return:
				list of tuples with the values of the property
		"""
		data = None
		if data_set is "static":
			data = self.__data
		elif data_set is "manipulated":
			data = self.get_manipulated_data()
		else:
			data = data_set
			
		prop_list = []
		for l in data:
			l = l.lstrip()
			if l.startswith(property_name):
				if "static" and "TAG:" in l:
					raise ValueError('property is not static as it contains a TAG:') 
				params = l.split(" ")[1:]
				parsed_params = []
				for p in params:
					if "." in p:
						try:
							p = float(p)
						except:
							pass
					else:
						try:
							p = int(p)
						except:
							pass
					parsed_params.append(p)
				prop_list.append(tuple(parsed_params))
		return prop_list
	
	def center(self):
		bnds = self.get_property("boundaries", "static")
		xyz = []
		axis_names = {"x" : 0, "y" : 1, "z" : 2}
		for b in bnds:
			index = None
			if b[0] in axis_names.keys():
				index = axis_names[b[0]]
			else:
				index = int(b[0])
			mid = (b[1]+ b[2])/2.0
			xyz.insert(index, mid)
		return tuple(xyz)
		
	def insert(self, id, var):
		self.mods[id] = var
		
	def run(self,output=True):
		#self.save()
		handle = Popen(['smoldyn', self.output_filename, '-w'], stdin=PIPE, stderr=PIPE,
			stdout=PIPE, shell=True)
		out=handle.stdout.readlines()
		if output:
			for line in out:
				print line
		print("".join(["_"]*100)+"\n")