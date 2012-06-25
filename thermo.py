"""Script for making thermodynamic comparison plots for the Lyman-alpha forest
between Arepo and Gadget"""

import matplotlib
matplotlib.use('PDF')

import numpy as np
import matplotlib.pyplot as plt
import plot_flux_power as pflux
plt.figure(1)
ddir="/home/spb/scratch/ComparisonProject/"
gad=np.loadtxt(ddir+"Gadget/thermo.txt")
ar=np.loadtxt(ddir+"Arepo/thermo.txt")
#ar_m=np.loadtxt(ddir+"Arepo/thermo_m.txt")
#are=np.loadtxt(ddir+"Arepo_ENTROPY/thermo.txt")
ar2=np.loadtxt(ddir+"Arepo_256/thermo_m.txt")
# ar2=np.loadtxt(ddir+"Arepo_256/thermo.txt")
gad2=np.loadtxt(ddir+"Gadget_256/thermo.txt")
plt.plot(ar[:,0],ar[:,1]/1e3,label="Arepo",color="blue")
#plt.plot(ar_m[:,0],ar_m[:,1],label="Arepo Mass")
#plt.plot(are[:,0],are[:,1],label="Arepo_ENTROPY")
#plt.plot(ar2[:,0],ar2[:,1],label="Arepo 256")
plt.plot(ar2[:,0],ar2[:,1]/1e3,label="Arepo 256",ls="-.",color="black")
plt.plot(gad[:,0],gad[:,1]/1e3, label="Gadget",ls = '--',color="red")
#plt.plot(gad2[:,0],gad2[:,1]/1e3,label="Gadget 256",ls = '-.',color="magenta")
plt.ylabel("$T_0$ ($10^3$ K)")
plt.xlabel("Redshift")
plt.xlim(0,8)
plt.ylim(6,12)
# plt.legend(loc=3,ncol=2)
plt.tight_layout()
plt.savefig(ddir+"temp.pdf")
plt.figure(4)
plt.plot(gad[:,0],gad[:,2], label="Gadget")
plt.plot(ar[:,0],ar[:,2],label="Arepo")
plt.plot(ar2[:,0],ar2[:,2],label="Arepo 256")
plt.plot(gad2[:,0],gad2[:,2],label="Gadget 256",ls = '--')
plt.ylabel("Temp-density relation")
plt.xlabel("Redshift")
plt.xlim(0,10)
plt.legend(loc=0)
plt.tight_layout()
plt.savefig(ddir+"gamma.pdf")
plt.figure(2)
pflux.pdfplots(139)
pflux.pdfplots(159,color="green")
pflux.pdfplots(189,color="red")
# plt.legend(loc=0)
plt.tight_layout()
plt.savefig(ddir+"flux_pdf.pdf")
plt.figure(3)
pflux.pfplots(119)
#pflux.pfplots(139)
pflux.pfplots(159)
pflux.pfplots(189)
plt.xlim(4.2e-3,0.03)
plt.ylim(0,4000)
plt.legend(loc=0)
plt.tight_layout()
plt.savefig(ddir+"flux_pow.pdf")
plt.figure(5)
gad=np.loadtxt(ddir+"Gadget/high-den-thermo.txt")
ar=np.loadtxt(ddir+"Arepo/high-den-thermo.txt")
plt.plot(gad[:,0],gad[:,1], label="Gadget")
plt.plot(ar[:,0],ar[:,1],label="Arepo")
plt.ylabel("Temp at mean density")
plt.xlabel("Redshift")
plt.legend(loc=0)
plt.savefig(ddir+"hdtemp.pdf")
plt.figure(6)
plt.plot(gad[:,0],gad[:,2], label="Gadget")
plt.plot(ar[:,0],ar[:,2],label="Arepo")
plt.ylabel("Temp-density relation")
plt.xlabel("Redshift")
plt.legend(loc=0)
plt.tight_layout()
plt.savefig(ddir+"hdgamma.pdf")

#Histogram
import re
def load_multi_txt(snap_file):
    """Load data from a text file split into multiple pieces"""
    data=np.loadtxt(snap_file)
    for i in np.arange(1,500):
        file2=re.sub("_0_","_"+str(i)+"_",snap_file)
        if snap_file == file2:
            break
        try:
            data=np.append(data,np.loadtxt(file2))
        except IOError:
            break
    return np.array(data)
plt.clf()
temp_ar=load_multi_txt(ddir+"/Arepo/124_tempdata.txt")
temp_gad=load_multi_txt(ddir+"/Gadget/124_tempdata.txt")
temp_ar_256=load_multi_txt(ddir+"/Arepo_256/124_0_tempdata.txt")
temp_gad_256=load_multi_txt(ddir+"/Gadget_256/124_0_tempdata.txt")
# temp_ar_128=load_multi_txt(ddir+"/Arepo_128/124_0_tempdata.txt")
# temp_gad_128=load_multi_txt(ddir+"/Gadget_128/124_0_tempdata.txt")
plt.hist(temp_ar_256,bins=40,log=True,histtype='stepfilled',label="Arepo 256")
plt.hist(temp_gad_256,bins=40,log=True,histtype='stepfilled',label="Gadget 256")
# plt.hist(temp_ar_128,bins=40,log=True,histtype='step',label="Arepo 128")
# plt.hist(temp_gad_128,bins=40,log=True,histtype='step',label="Gadget 128")
plt.hist(temp_ar,bins=40,log=True,histtype='step',label="Arepo 512")
plt.hist(temp_gad,bins=40,log=True,histtype='step',label="Gadget 512")
plt.legend(loc=0)

plt.tight_layout()
plt.savefig(ddir+"temp_hist.pdf")
#Positional plot
#plt.clf()
#pos_ar_256=load_multi_txt(ddir+"/Arepo_256/124_0_posdata.txt")
#pos_ar_256=np.reshape(pos_ar_256,[-1,3])/1000
#pos_gad_256=load_multi_txt(ddir+"/Gadget_256/124_0_posdata.txt")
#pos_gad_256=np.reshape(pos_gad_256,[-1,3])/1000
#ind=np.where(pos_ar_256[:,2]> 19.9)
#plt.scatter(pos_ar_256[ind,0],pos_ar_256[ind,1],c=temp_ar_256[ind],vmin=3.5,vmax=5)
#plt.xlim(0,20)
#plt.ylim(0,20)
#plt.xlabel("x (Mpc)")
#plt.ylabel("y (Mpc)")
#plt.title("Arepo Positions at 19.9 < z < 20 Mpc.")
#cb=plt.colorbar()
#cb.set_label("log T_0")
#plt.tight_layout()
#plt.savefig(ddir+"arepo_pos.pdf")
#plt.figure(7)
#ind2=np.where(pos_gad_256[:,2]> 19.9)
#plt.scatter(pos_gad_256[ind2,0],pos_gad_256[ind2,1],c=temp_gad_256[ind2],vmin=3.5,vmax=5)
#plt.xlim(0,20)
#plt.ylim(0,20)
#plt.xlabel("x (Mpc)")
#plt.ylabel("y (Mpc)")
#plt.title("Gadget Positions at 19.9 < z < 20 Mpc.")
#cb=plt.colorbar()
#cb.set_label("log T_0")
#plt.tight_layout()
#plt.savefig(ddir+"gadget_pos.pdf")
