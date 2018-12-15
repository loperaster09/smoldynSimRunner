from SmoldynManipulator import *
import matplotlib.pyplot as plt
import math as m
import numpy as np
import os, Tkinter, tkFileDialog

class Sim(object):
	"""
	Program to automatically perform N simulations
	per parameter variation, either with 2D scaffold structure
	or no scaffold structure where enzymes diffuse freely, based on 
	Joaquin's Manipulator.
	"""
	def __init__(self,N=1,simType="Free"):
		self.simType = simType									#defines type of sim
		self.N = N												#defines number of simulations per parameter variation
		self.man = []											#defines all manipulated config files
		self.dirs = []											#defines all used directories
		self.man = []											#stores the manipulated files
		self.simResults = []									#will store results
	
	def setupSim(self,IED=range(10,91,10)):
		"""
		Creates folders and saves corresponding config files in them, 
		dependent on type of simulation and IED chosen.
		It now only inserts IED in files!
		"""
		#choosing correct template, constants and variables and inserting them in config file
		THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
		if self.simType=="Scaffold" or self.simType=="Free":
			self.template = "templateControl.txt"
			man=Manipulator.from_file(os.path.join(THIS_FOLDER, self.template))
			if self.simType=="Scaffold":
				for I in IED:
					dir="sims_{}_IED={}/".format(self.simType,I)
					fullPath=os.path.join(THIS_FOLDER,dir[:-1])
					if not os.path.exists(fullPath):
						os.mkdir(os.path.join(fullPath))
					man.insert('ied',I)
					man.set_output_filename(os.path.join(fullPath,"sim_IED={}.txt".format(I)))
					self.dirs.append(os.path.join(fullPath,"sim_IED={}.txt".format(I)))
					man.save(dir)
			elif self.simType=="Free":
				dir="sims_{}/".format(self.simType)
				fullPath=os.path.join(THIS_FOLDER,dir[:-1])
				if not os.path.exists(fullPath):
					os.mkdir(os.path.join(THIS_FOLDER,dir[:-1]))
				man.insert('makeScaffold', 'placeholder')
				man.set_output_filename(os.path.join(fullPath,"sim_Free.txt"))
				self.dirs.append(os.path.join(fullPath,"sim_Free.txt"))
				man.save(dir)
		elif self.simType=="Hexagon":
			self.template = "templateHexagon.txt"
			#hexagon simulation can be added here. 
		else:
			print "Unknown simulation type :("	
		return self

	def runSim(self,gui=False,a=1,b=5):
		"""
		Runs simulation #a until #b in the directories made in setupSim()
		or from arbitrary template file, if gui is set to True.
		"""
		if not gui:
			path=self.dirs
			b=self.N
		else:
			root=Tkinter.Tk()
			root.withdraw()
			path=[str(tkFileDialog.askopenfilename())]
		for dir in path:
			for i in range(a,b+1):
				man=Manipulator.from_file(dir)
				man.insert('i',i)
				man.set_output_filename("sim_#"+str(i)+".txt")
				print "Running simulation #"+str(i)+"."
				folder=os.path.dirname(dir)
				man.save(folder)
				man.output_filename=os.path.join(folder,man.output_filename)
				man.run()

			
	def getResults(self, gui=False,a=0, b=100):
		"""
		For every simulation output, calculate d[P]/dt and - d[S]/dt and extract molecule counts in the index domain [a,b].
		derivs stores dicts for every simulation containing dPdt and dSdt values
		One element of simResults stores time, mean_countS, mean_countP, mean_actS, mean_actP
		In case an arbitrary folder needs to be selected for results: 
		Set gui to True and navigate to the simulation output file of choice. 
		Note: all output files in this folder will be used to calculate mean results!
		"""
		if not gui:
			path=self.dirs
		else:
			root=Tkinter.Tk()
			root.withdraw()
			path=[str(tkFileDialog.askopenfilename())]
		for dir in path:
			folder=os.path.dirname(dir)
			listOfFile=os.listdir(folder)
			#these will be our primary output
			mean_actP=[]
			mean_actS=[]
			mean_countS=[]
			mean_countP=[]
			#for intermediate calculation, these are necessary
			Scounts=[]
			Pcounts=[]
			derivs=[]
			for entry in listOfFile:	#open every simOut_xxx.txt file
				if "Out" in entry:
					fullPath=os.path.join(os.path.join(folder, entry))
					inf=open(fullPath)
					lines=inf.readlines()
					inf.close()
					mols=lines[0].rstrip().split()
					S_index=mols.index("Gluc")
					I_index=mols.index("Perox")
					P_index=mols.index("ABTS-")
					time=[]
					Scount=[]
					Pcount=[]
					for line in lines[1:-1]:
						line=line.split()
						time.append(float(line[0]))
						Scount.append(float(line[S_index]))
						Pcount.append(float(line[P_index]))
					Scounts.append(Scount)
					Pcounts.append(Pcount)
					#calculating d[S]/dt and d[P]/dt
					dt=np.diff(time[a:b])
					dS=np.diff(Scount[a:b])
					dP=np.diff(Pcount[a:b])
					dSdt=dS/dt
					dPdt=dP/dt					#has length len(time[a:b])-1!
					derivs.append({'dPdt':dPdt,'dSdt':dSdt})
					
			for m in range(len(time[a:b])):			#m'th count of P or S in a simulation
				sum_P=0
				sum_S=0
				for n in range(len(Scounts)):		#n'th simulation = n'th list in Scounts
					sum_P+=Pcounts[n][m]
					sum_S+=Scounts[n][m]
				mean_countS.append(sum_S/len(Scounts))
				mean_countP.append(sum_P/len(Pcounts))
				
			for i in range(len(derivs[0]['dPdt'])):	#i'th derivative of P or S in a simulation	
				sum_dP=0
				sum_dS=0
				for j in range(len(derivs)):		#j'th simulation = j'th dict in derivs
					sum_dP+=derivs[j]['dPdt'][i]
					sum_dS+=derivs[j]['dSdt'][i]
				mean_actP.append(sum_dP/len(derivs))
				mean_actS.append(sum_dS/len(derivs))

			mean_actS = [i * -1 for i in mean_actS] #convert d[S]/dt to positives numbers
			self.simResults.append([time, mean_countS, mean_countP, mean_actS, mean_actP])
		return self

	def makePlots(self,countPlot=True,actPlot=True):
		for i in range(len(self.simResults)):
			fig=plt.figure()
			t=self.simResults[i]
			if countPlot:
				y=[self.simResults[i][1],self.simResults[i][2]]
				fit=np.polyfit(t[0],y[0],2)
				fit_fn=np.poly1d(fit)
				plt.plot(t[0], y[0], 'ro', label='N_Glucose')
				plt.plot(t[0],fit_fn(t[0]),'--k')
				plt.plot(t[0], y[1], 'bo', label='N_ABTS-')
				plt.ylabel('Number of molecules (-)')
				
			if actPlot:
				y=[self.simResults[i][3],self.simResults[i][4]]
				fit=np.polyfit(t[0][:-1],y[0],1)
				fit_fn=np.poly1d(fit)
				plt.plot(t[0][:-1], y[0], 'g*', label='- d[Glucose]/dt')
				plt.plot(t[0],fit_fn(t[0]),'--k')
				plt.plot(t[0][:-1], y[1], 'y*', label='d[ABTS-]/dt')
				plt.ylabel('Molecule conversion rate (s^-1)')
			if self.simType=="Scaffold":
				plt.title("2D "+self.simType+" Simulation")
			else:
				plt.title(self.simType+" Diffusion Simulation")
			plt.xlabel('time (s)')
			plt.legend(loc='best')
			
			#calculate R-squared of the fitted function
			yhat=fit_fn(t[0])
			ybar=np.sum(y[0])/len(y[0])
			ssreg=np.sum((yhat-ybar)**2)
			sstot=np.sum((y[0]-ybar)**2)
			R_sq=ssreg/sstot
			print "Fit has an R_squared of "+str(R_sq)
			plt.text(33,100,"R^2 = "+str(round(R_sq,3)))
			plt.show()
		
	def clearDirs(self,dir):										#clears the contents of directory dir
		for the_file in os.listdir(dir):
			file_path = os.path.join(dir, the_file)
			try:
				if os.path.isfile(file_path):
					os.unlink(file_path)
			except Exception as e:
				print(e)
				
if __name__ == "__main__":
	sim=Sim(N=5,simType="Scaffold")
	sim.setupSim(IED=range(10,31,10))
	sim.runSim()
	#sim.getResults(gui=True).makePlots(countPlot=True,actPlot=False)
	




