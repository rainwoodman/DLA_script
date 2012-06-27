# vim: set fileencoding=utf-8
"""
This is a module for making plots like those in Tescari & Viel, based on the data gathered in the Halohi module
Figures implemented:
    5,6,9,10-13
Possible but not implemented:
    14
        """

import halohi
import numpy as np
import scipy
import os.path as path
import math
import matplotlib.pyplot as plt

acol="blue"
gcol="red"
acol2="cyan"
gcol2="magenta"
rcol="black"
astyle="-"
gstyle="--"

#These are parameters for the analytic fits for the DLA abundances.
#Format: a,b,ra,rb
#breakpoint is at 10^10.5
arepo_halo_p = { 90 : [2.4, 4.29, -0.17, 0.78],
                91 : [2.24, 4.29, -0.17, 0.78],

                124 : [2.03, 4.22, -0.14, 0.78],
                141 : [1.88, 4.1, -0.1, 0.78],
                191 : [1.49, 3.8, -0.06, 0.78],
                314 : [1.06, 3.0, 0.03, 0.71]}

gadget_halo_p = { 90 : [1.96,4.44,-0.11,0.78],
                    91 : [1.96,4.44,-0.11,0.78],
                  124 : [1.57,4.28,-0.13,0.79],
                  141 : [1.43,4.16,-0.1, 0.77],
                  191 : [1.13, 3.84, -0.07, 0.76],
                  314 : [0.97, 2.91, 0.0, 0.7] }

class PrettyHalo(halohi.HaloHI):
    """
    Derived class with extra methods for plotting a pretty (high-resolution) picture of the grid around a halo.
    """

    def plot_pretty_something(self,num,grid,bar_label):
        """
        Plots a pretty (high-resolution) picture of the grid around a halo.
        Helper for the other functions.
        """
        #Plot a figure
        vmax=np.max([np.max(grid),25.5])
        maxdist = self.sub_radii[num]
        plt.imshow(grid,origin='lower',extent=(-maxdist,maxdist,-maxdist,maxdist),vmin=0,vmax=vmax)
        bar=plt.colorbar(use_gridspec=True)
        bar.set_label(bar_label)
        if (maxdist > 150) * (maxdist < 200):
            plt.xticks((-150,-75,0,75,150))
            plt.yticks((-150,-75,0,75,150))
        if maxdist > 300:
            plt.xticks((-300,-150,0,150,300))
            plt.yticks((-300,-150,0,150,300))
        plt.xlabel(r"x (kpc h$^{-1}$)")
        plt.ylabel(r"y (kpc h$^{-1}$)")
        plt.tight_layout()
        plt.show()

    def plot_pretty_halo(self,num=0):
        """
        Plots a pretty (high-resolution) picture of the grid around a halo.
        """
        self.plot_pretty_something(num,self.sub_nHI_grid[num],"log$_{10}$ N$_{HI}$ (cm$^{-2}$)")

    def plot_pretty_cut_halo(self,num=0,cut_LLS=17,cut_DLA=20.3):
        """
        Plots a pretty (high-resolution) picture of the grid around a halo.
        """
        cut_grid=np.array(self.sub_nHI_grid[num])
        ind=np.where(cut_grid < cut_LLS)
        cut_grid[ind]=10
        ind2=np.where((cut_grid < cut_DLA)*(cut_grid > cut_LLS))
        cut_grid[ind2]=17.
        ind3=np.where(cut_grid > cut_DLA)
        cut_grid[ind3]=20.3
        maxdist = self.sub_radii[num]
        plt.imshow(cut_grid,origin='lower',extent=(-maxdist,maxdist,-maxdist,maxdist),vmin=10,vmax=20.3)
        if (maxdist > 150) * (maxdist < 200):
            plt.xticks((-150,-75,0,75,150))
            plt.yticks((-150,-75,0,75,150))
        if maxdist > 300:
            plt.xticks((-300,-150,0,150,300))
            plt.yticks((-300,-150,0,150,300))
        plt.xlabel(r"x (kpc h$^{-1}$)")
        plt.ylabel(r"y (kpc h$^{-1}$)")
        plt.tight_layout()
        plt.show()

    def plot_pretty_cut_gas_halo(self,num=0,cut_LLS=17,cut_DLA=20.3):
        """
        Plots a pretty (high-resolution) picture of the grid around a halo.
        """
        cut_grid=np.array(self.sub_gas_grid[num])
        ind=np.where(cut_grid < cut_LLS)
        cut_grid[ind]=10
        ind2=np.where((cut_grid < cut_DLA)*(cut_grid > cut_LLS))
        cut_grid[ind2]=17.
        ind3=np.where(cut_grid > cut_DLA)
        cut_grid[ind3]=20.3
        maxdist = self.sub_radii[num]
        plt.imshow(cut_grid,origin='lower',extent=(-maxdist,maxdist,-maxdist,maxdist),vmin=10,vmax=20.3)
        plt.xlabel(r"x (kpc h$^{-1}$)")
        plt.xlabel(r"y (kpc h$^{-1}$)")
        plt.tight_layout()
        plt.show()

    def plot_pretty_gas_halo(self,num=0):
        """
        Plots a pretty (high-resolution) picture of the grid around a halo.
        """
        self.plot_pretty_something(num,self.sub_gas_grid[num],"log$_{10}$ N$_{H}$ (cm$^{-2}$)")

    def plot_radial_profile(self,minM=3e11,maxM=1e12,minR=0,maxR=20.):
        """Plots the radial density of neutral hydrogen (and possibly gas) for a given halo,
        stacking several halo profiles together."""
        Rbins=np.linspace(minR,maxR,20)
        try:
            aRprof=[self.get_stacked_radial_profile(minM,maxM,Rbins[i],Rbins[i+1]) for i in xrange(0,np.size(Rbins)-1)]
            plt.plot(Rbins[0:-1],aRprof,color=acol, ls=astyle,label="HI")
            #If we didn't load the HI grid this time
        except AttributeError:
            pass
        #Gas profiles
        try:
            agRprof=[self.get_stacked_radial_profile(minM,maxM,Rbins[i],Rbins[i+1],True) for i in xrange(0,np.size(Rbins)-1)]
            plt.plot(Rbins[0:-1],agRprof,color="brown", ls=astyle,label="Gas")
        except AttributeError:
            pass
        plt.xlabel(r"R (kpc h$^{-1}$)")
        plt.ylabel(r"Density $N_{HI}$ (kpc$^{-1}$)")
        plt.legend(loc=1)
        plt.tight_layout()
        plt.show()


class PrettyBox(halohi.BoxHI,PrettyHalo):
    """
    As above but for the whole box grid
    """
    def __init__(self,snap_dir,snapnum,reload_file=False,skip_grid=None,savefile=None):
        halohi.BoxHI.__init__(self,snap_dir,snapnum,reload_file=False,skip_grid=None,savefile=None)


class PrettyTotalHI(halohi.TotalHaloHI):
    """Derived class for plotting total nHI frac and total nHI mass
    against halo mass"""
    def plot_totalHI(self,color="black",label=""):
        """Make the plot of total neutral hydrogen density in a halo:
            Figure 9 of Tescari & Viel 2009"""
        #Plot.
        plt.loglog(self.mass,self.nHI,'o',color=color,label=label)
        #Axes
        plt.xlabel(r"Mass ($M_\odot$ h$^{-1}$)")
        plt.ylabel("HI frac")
        plt.xlim(1e9,5e12)

    def plot_MHI(self,color="black",label=""):
        """Total M_HI vs M_halo"""
        #Plot.
        plt.loglog(self.mass,self.MHI,'o',color=color)
        #Make a best-fit curve.
        ind=np.where(self.MHI > 0.)
        logmass=np.log10(self.mass[ind])-12
        loggas=np.log10(self.MHI[ind])
        ind2=np.where(logmass > -2)
        (alpha,beta)=scipy.polyfit(logmass[ind2],loggas[ind2],1)
        mass_bins=np.logspace(np.log10(np.min(self.mass)),np.log10(np.max(self.mass)),num=100)
        fit= 10**(alpha*(np.log10(mass_bins)-12)+beta)
        plt.loglog(mass_bins,fit, color=color,label=label+r"$\alpha$="+str(np.round(alpha,2))+r" $\beta$ = "+str(np.round(beta,2)))
        #Axes
        plt.xlabel(r"Mass ($M_\odot$ h$^{-1}$)")
        plt.ylabel(r"Mass$_{HI}$ ($M_\odot$ h$^{-1}$)")
        plt.xlim(1e9,5e12)

    def plot_gas(self,color="black",label=""):
        """Total M_gas vs M_halo"""
        #Plot.
        plt.loglog(self.mass,self.Mgas,'o',color=color)
        #Make a best-fit curve.
        ind=np.where(self.Mgas > 0.)
        logmass=np.log10(self.mass[ind])-12
        loggas=np.log10(self.Mgas[ind])
        ind2=np.where(logmass > -2)
        (alpha,beta)=scipy.polyfit(logmass[ind2],loggas[ind2],1)
        mass_bins=np.logspace(np.log10(np.min(self.mass)),np.log10(np.max(self.mass)),num=100)
        fit= 10**(alpha*(np.log10(mass_bins)-12)+beta)
        plt.loglog(mass_bins,fit, color=color,label=label+r"$\alpha$="+str(np.round(alpha,2))+r" $\beta$ = "+str(np.round(beta,2)))
        #Axes
        plt.xlabel(r"Mass ($M_\odot$ h$^{-1}$)")
        plt.ylabel(r"Mass$_{gas}$ ($M_\odot$ h$^{-1}$)")
        plt.xlim(1e9,5e12)


class TotalHIPlots:
    """Class for plotting functions from PrettyHaloHI"""
    def __init__(self,base,snapnum,minpart=400):
        #Get paths
        gdir=path.join(base,"Gadget")
        adir=path.join(base,"Arepo_ENERGY")
        #Load data
        self.atHI=PrettyTotalHI(adir,snapnum,minpart)
        self.atHI.save_file()
        self.gtHI=PrettyTotalHI(gdir,snapnum,minpart)
        self.gtHI.save_file()

    def plot_totalHI(self):
        """Make the plot of total neutral hydrogen density in a halo:
            Figure 9 of Tescari & Viel 2009"""
        #Plot.
        self.gtHI.plot_totalHI(color=gcol,label="Gadget")
        self.atHI.plot_totalHI(color=acol,label="Arepo")
        #Axes
        plt.legend(loc=4)
        plt.tight_layout()
        plt.show()

    def plot_MHI(self):
        """Make the plot of total neutral hydrogen mass in a halo:
            Figure 9 of Tescari & Viel 2009"""
        #Plot.
        self.gtHI.plot_MHI(color=gcol,label="Gadget")
        self.atHI.plot_MHI(color=acol,label="Arepo")
        #Axes
        plt.legend(loc=0)
        plt.tight_layout()
        plt.show()

    def plot_gas(self):
        """Plot total gas mass in a halo"""
        #Plot.
        self.gtHI.plot_gas(color=gcol,label="Gadget")
        self.atHI.plot_gas(color=acol,label="Arepo")
        #Axes
        plt.legend(loc=0)
        plt.tight_layout()
        plt.show()



class HaloHIPlots:
    """
    This class contains functions for plotting all the plots in
    Tescari and Viel which are derived from the grid of HI density around the halos.
    These are figs 10-13
    """
    def __init__(self,base,snapnum,minpart=400,minplot=1e9, maxplot=5e12,reload_file=False,skip_grid=None):
        #Get paths
        self.gdir=path.join(base,"Gadget")
        self.adir=path.join(base,"Arepo_ENERGY")
        #Get data
        self.ahalo=PrettyHalo(self.adir,snapnum,minpart,reload_file=reload_file,skip_grid=skip_grid)
#         self.ahalo.save_file()
        self.ghalo=PrettyHalo(self.gdir,snapnum,minpart,reload_file=reload_file,skip_grid=skip_grid)
#         self.ghalo.save_file()
        self.minplot=minplot
        self.maxplot=maxplot

    def pr_num(self,num):
        """Return a string rep of a number"""
        return str(np.round(num,2))

    def plot_sigma_DLA(self, DLA_cut=20.3,DLA_upper_cut=42.):
        """Plot sigma_DLA against mass."""
        mass=np.logspace(np.log10(np.min(self.ahalo.sub_mass)),np.log10(np.max(self.ahalo.sub_mass)),num=100)
        gsigDLA=self.ghalo.get_sigma_DLA(DLA_cut,DLA_upper_cut)
        asigDLA=self.ahalo.get_sigma_DLA(DLA_cut,DLA_upper_cut)
        #Generate mean halo mass
        g_mean_halo_mass = np.sum(self.ghalo.sub_mass*gsigDLA)/np.sum(gsigDLA)
        a_mean_halo_mass = np.sum(self.ahalo.sub_mass*asigDLA)/np.sum(asigDLA)
        print "Mean halo mass, Arepo: ",a_mean_halo_mass/1e10,"Gadget: ",g_mean_halo_mass/1e10,"Cut=",DLA_cut
        #Plot sigma DLA
        #as scatter
#         plt.loglog(self.ghalo.sub_mass,gsigDLA,'s',color=gcol)
#         plt.loglog(self.ahalo.sub_mass,asigDLA,'^',color=acol)
        #As contour
        ind = np.where(gsigDLA > 0)
        (hist,xedges, yedges)=np.histogram2d(np.log10(self.ghalo.sub_mass[ind]),np.log10(gsigDLA[ind]),bins=(30,30))
        xbins=np.array([(xedges[i+1]+xedges[i])/2 for i in xrange(0,np.size(xedges)-1)])
        ybins=np.array([(yedges[i+1]+yedges[i])/2 for i in xrange(0,np.size(yedges)-1)])
        plt.contourf(10**xbins,10**ybins,hist.T,[1,1000],colors=(gcol,gcol2),alpha=0.7)
        ind = np.where(asigDLA > 0)
        (hist,xedges, yedges)=np.histogram2d(np.log10(self.ahalo.sub_mass[ind]),np.log10(asigDLA[ind]),bins=(30,30))
        xbins=np.array([(xedges[i+1]+xedges[i])/2 for i in xrange(0,np.size(xedges)-1)])
        ybins=np.array([(yedges[i+1]+yedges[i])/2 for i in xrange(0,np.size(yedges)-1)])
        plt.contourf(10**xbins,10**ybins,hist.T,[1,1000],colors=(acol,acol2),alpha=0.7)
        #Plot Analytic Fit
        asfit=self.ahalo.sDLA_analytic(mass,arepo_halo_p[self.ahalo.snapnum],DLA_cut)-self.ahalo.sDLA_analytic(mass,arepo_halo_p[self.ahalo.snapnum],DLA_upper_cut)
        gsfit=self.ghalo.sDLA_analytic(mass,gadget_halo_p[self.ghalo.snapnum],DLA_cut)-self.ghalo.sDLA_analytic(mass,arepo_halo_p[self.ahalo.snapnum],DLA_upper_cut)
        plt.loglog(mass,asfit,color=acol,ls=astyle)
        plt.loglog(mass,gsfit,color=gcol,ls=gstyle)
        #Plot Axes stuff
        plt.xlabel(r"Mass ($M_\odot$ h$^{-1}$)")
        plt.ylabel(r"$\sigma_{DLA}$ (kpc$^2$ h$^{-2}$)")
        plt.xlim(self.minplot,self.maxplot)
#         plt.ylim(1,4*self.ghalo.sub_radii[0]**2)
        if (DLA_cut < 19):
            plt.ylim(10,np.max(np.concatenate([gsigDLA,asigDLA]))*4)
        else:
            plt.ylim(1,np.max(np.concatenate([gsigDLA,asigDLA]))*4)
        #Fits
        plt.tight_layout()
        plt.show()

    def plot_sigma_DLA_nHI(self, DLA_cut=20.3):
        """Plot sigma_DLA against HI mass."""
        #Get MHI
#         athi=PrettyTotalHI(self.adir,self.ahalo.snapnum,self.ahalo.minpart)
#         gthi=PrettyTotalHI(self.gdir,self.ahalo.snapnum,self.ahalo.minpart)
        anHI_mass=10.**np.array([self.ahalo.get_halo_central_density(h) for h in xrange(0,self.ahalo.nhalo)])
        gnHI_mass=10.**np.array([self.ghalo.get_halo_central_density(h) for h in xrange(0,self.ghalo.nhalo)])
#         anHI_mass = np.array([athi.get_hi_mass(mass) for mass in self.ahalo.sub_mass])
#         gnHI_mass = np.array([gthi.get_hi_mass(mass) for mass in self.ghalo.sub_mass])
        mass=np.logspace(np.log10(np.min(anHI_mass)),np.log10(np.max(anHI_mass)),num=100)
        asfit=self.ahalo.sigma_DLA_fit(mass,DLA_cut,anHI_mass)
        gsfit=self.ghalo.sigma_DLA_fit(mass,DLA_cut,gnHI_mass)
        alabel = r"$\alpha=$"+self.pr_num(self.ahalo.alpha)+" $\\beta=$"+self.pr_num(self.ahalo.beta)+" $\\gamma=$"+self.pr_num(self.ahalo.gamma)+" b = "+self.pr_num(self.ahalo.pow_break)
        glabel = r"$\alpha=$"+self.pr_num(self.ghalo.alpha)+" $\\beta=$"+self.pr_num(self.ghalo.beta)+" $\\gamma=$"+self.pr_num(self.ghalo.gamma)+" b = "+self.pr_num(self.ghalo.pow_break)
        plt.loglog(mass,asfit,color=acol,label=alabel,ls=astyle)
        plt.loglog(mass,gsfit,color=gcol,label=glabel,ls=gstyle)
        #Axes
        plt.xlabel(r"Mass HI ($M_\odot$ h$^{-1}$)")
        plt.ylabel(r"$\sigma_{DLA}$ (kpc$^2$ h$^{-2}$) DLA is N > "+str(DLA_cut))
        plt.legend(loc=0)
        plt.loglog(gnHI_mass,self.ghalo.get_sigma_DLA(DLA_cut),'s',color=gcol)
        plt.loglog(anHI_mass,self.ahalo.get_sigma_DLA(DLA_cut),'^',color=acol)
        plt.loglog(mass,asfit,color=acol,label=alabel,ls=astyle)
        plt.loglog(mass,gsfit,color=gcol,label=glabel,ls=gstyle)
#         plt.xlim(np.min(gnHI_mass)/2.,self.maxplot/100)
        plt.ylim((2.*np.max(self.ahalo.sub_radii/self.ahalo.ngrid))**2/10.,asfit[-1]*2)
        #Fits
        plt.tight_layout()
        plt.show()

    def plot_sigma_DLA_gas(self, DLA_cut=20.3):
        """Plot sigma_DLA against HI mass."""
        #Get MHI
        athi=PrettyTotalHI(self.adir,self.ahalo.snapnum,self.ahalo.minpart)
        gthi=PrettyTotalHI(self.gdir,self.ahalo.snapnum,self.ahalo.minpart)
        anHI_mass = np.array([athi.get_gas_mass(mass) for mass in self.ahalo.sub_mass])
        gnHI_mass = np.array([gthi.get_gas_mass(mass) for mass in self.ghalo.sub_mass])
        mass=np.logspace(np.log10(np.min(anHI_mass)),np.log10(np.max(anHI_mass)),num=100)
        asfit=self.ahalo.sigma_DLA_fit(mass,DLA_cut,anHI_mass)
        gsfit=self.ghalo.sigma_DLA_fit(mass,DLA_cut,gnHI_mass)
        alabel = r"$\alpha=$"+self.pr_num(self.ahalo.alpha)+" $\\beta=$"+self.pr_num(self.ahalo.beta)+" $\\gamma=$"+self.pr_num(self.ahalo.gamma)+" b = "+self.pr_num(self.ahalo.pow_break)
        glabel = r"$\alpha=$"+self.pr_num(self.ghalo.alpha)+" $\\beta=$"+self.pr_num(self.ghalo.beta)+" $\\gamma=$"+self.pr_num(self.ghalo.gamma)+" b = "+self.pr_num(self.ghalo.pow_break)
        plt.loglog(mass,asfit,color=acol,label=alabel,ls=astyle)
        plt.loglog(mass,gsfit,color=gcol,label=glabel,ls=gstyle)
        #Axes
        plt.xlabel(r"Halo Gas Mass ($M_\odot$ h$^{-1}$)")
        plt.ylabel(r"$\sigma_{DLA}$ (kpc$^2$ h$^{-2}$) DLA is N > "+str(DLA_cut))
        plt.legend(loc=0)
        plt.loglog(gnHI_mass,self.ghalo.get_sigma_DLA(DLA_cut),'s',color=gcol)
        plt.loglog(anHI_mass,self.ahalo.get_sigma_DLA(DLA_cut),'^',color=acol)
        plt.loglog(mass,asfit,color=acol,label=alabel,ls=astyle)
        plt.loglog(mass,gsfit,color=gcol,label=glabel,ls=gstyle)
        plt.xlim(np.min(gnHI_mass)/2.,self.maxplot/100)
        plt.ylim((2.*np.max(self.ahalo.sub_radii/self.ahalo.ngrid))**2/10.,asfit[-1]*2)
        #Fits
        plt.tight_layout()
        plt.show()

    def get_rel_sigma_DLA(self,DLA_cut=20.3, DLA_upper_cut=42.,min_sigma=15.):
        """
        Get the change in sigma_DLA for a particular halo.
        and the mass of each halo averaged across arepo and gadget.
        DLA_cut is the column density above which to consider a DLA
        min_sigma is the minimal sigma_DLA to look at (in grid cell units)
        """
        aDLA=self.ahalo.get_sigma_DLA(DLA_cut,DLA_upper_cut)
        gDLA=self.ghalo.get_sigma_DLA(DLA_cut,DLA_upper_cut)
        rDLA=np.empty(np.size(aDLA))
        rmass=np.empty(np.size(aDLA))
        cell_area=(2*self.ahalo.sub_radii[0]/self.ahalo.ngrid[0])**2
        for ii in xrange(0,np.size(aDLA)):
            gg=self.ghalo.identify_eq_halo(self.ahalo.sub_mass[ii],self.ahalo.sub_cofm[ii])
            if np.size(gg) > 0 and aDLA[ii]+gDLA[gg] > min_sigma*cell_area:
                rDLA[ii] = aDLA[ii]-gDLA[gg]
                rmass[ii]=0.5*(self.ahalo.sub_mass[ii]+self.ghalo.sub_mass[gg])
            else:
                rDLA[ii]=np.NaN
                rmass[ii]=np.NaN
        return (rmass,rDLA)


    def plot_rel_sigma_DLA(self):
        """Plot sigma_DLA against mass. Figure 10."""
#         (rmass,rDLA)=self.get_rel_sigma_DLA(17,25)
#         ind=np.where(np.isnan(rDLA) != True)
#         plt.semilogx(rmass[ind],rDLA[ind],'o',color="green",label="N_HI> 17")
        (rmass,rDLA)=self.get_rel_sigma_DLA(20.3,30.)
        ind=np.where(np.isnan(rDLA) != True)
        plt.semilogx(rmass[ind],rDLA[ind],'o',color="blue",label="N_HI> 20.3")
        #Axes
        plt.xlim(self.minplot,self.maxplot)
        plt.xlabel(r"Mass ($M_\odot$ h$^{-1}$)")
        plt.ylabel(r"$\sigma_\mathrm{DLA}$ (Arepo) - $\sigma_\mathrm{DLA}$ (Gadget) (kpc$^2$ h$^{-2}$)")
        plt.legend(loc=0)
        plt.tight_layout()
        plt.show()

    def plot_dN_dla(self,Mmin=1e9,Mmax=1e13):
        """Plots dN_DLA/dz for the halos. Figure 11"""
        mass=np.logspace(np.log10(Mmin),np.log10(Mmax),num=100)
        aDLA_dz_tab = np.empty(np.size(mass))
        gDLA_dz_tab = np.empty(np.size(mass))
        for (i,m) in enumerate(mass):
            aDLA_dz_tab[i] = self.ahalo.get_N_DLA_dz(arepo_halo_p[self.ahalo.snapnum],m)
            gDLA_dz_tab[i] = self.ghalo.get_N_DLA_dz(gadget_halo_p[self.ghalo.snapnum],m)
        plt.loglog(mass,aDLA_dz_tab,color=acol,label="Arepo",ls=astyle)
        plt.loglog(mass,gDLA_dz_tab,color=gcol,label="Gadget",ls=gstyle)
        ax=plt.gca()
        ax.fill_between(mass, 10**(-0.7), 10**(-0.5),color='yellow')
        plt.xlabel(r"Mass ($M_\odot$ h$^{-1}$)")
        plt.ylabel(r"$\mathrm{dN}_\mathrm{DLA} / \mathrm{dz} (> M_\mathrm{tot})$")
        plt.legend(loc=3)
        plt.xlim(Mmin,Mmax)
        plt.ylim(10**(-5),1)
        plt.tight_layout()
        plt.show()

    def plot_column_density(self,minN=17,maxN=23.):
        """Plots the column density distribution function. Figures 12 and 13"""
        (aNHI,af_N)=self.ahalo.column_density_function(0.4,minN-1,maxN+1)
        (gNHI,gf_N)=self.ghalo.column_density_function(0.4,minN-1,maxN+1)
        plt.loglog(aNHI,af_N,color=acol, ls=astyle,label="Arepo")
        plt.loglog(gNHI,gf_N,color=gcol, ls=gstyle,label="Gadget")
        #Make the ticks be less-dense
        #ax=plt.gca()
        #ax.xaxis.set_ticks(np.power(10.,np.arange(int(minN),int(maxN),2)))
        #ax.yaxis.set_ticks(np.power(10.,np.arange(int(np.log10(af_N[-1])),int(np.log10(af_N[0])),2)))
        plt.xlabel(r"$N_\mathrm{HI} (\mathrm{cm}^{-2})$")
        plt.ylabel(r"$f(N) (\mathrm{cm}^2)$")
        plt.xlim(10**minN, 10**maxN)
        plt.ylim(ymin=1e-26)
#         plt.legend(loc=0)
        plt.tight_layout()
        plt.show()

    def plot_column_density_breakdown(self,minN=17,maxN=23.):
        """Plots the column density distribution function, broken down into halos. """
        (aNHI,af_N)=self.ahalo.column_density_function(0.4,minN-1,maxN+1,minM=11)
        (gNHI,gf_N)=self.ghalo.column_density_function(0.4,minN-1,maxN+1,minM=11)
        plt.loglog(aNHI,af_N,color=acol, ls="-",label="Arepo")
        plt.loglog(gNHI,gf_N,color=gcol, ls="-",label="Gadget")
        (aNHI,af_N)=self.ahalo.column_density_function(0.4,minN-1,maxN+1,minM=10,maxM=11)
        (gNHI,gf_N)=self.ghalo.column_density_function(0.4,minN-1,maxN+1,minM=10,maxM=11)
        plt.loglog(aNHI,af_N,color=acol, ls="--",label="Arepo")
        plt.loglog(gNHI,gf_N,color=gcol, ls="--",label="Gadget")
        (aNHI,af_N)=self.ahalo.column_density_function(0.4,minN-1,maxN+1,minM=9,maxM=10)
        (gNHI,gf_N)=self.ghalo.column_density_function(0.4,minN-1,maxN+1,minM=9,maxM=10)
        plt.loglog(aNHI,af_N,color=acol, ls=":",label="Arepo")
        plt.loglog(gNHI,gf_N,color=gcol, ls=":",label="Gadget")
        #Make the ticks be less-dense
        #ax=plt.gca()
        #ax.xaxis.set_ticks(np.power(10.,np.arange(int(minN),int(maxN),2)))
        #ax.yaxis.set_ticks(np.power(10.,np.arange(int(np.log10(af_N[-1])),int(np.log10(af_N[0])),2)))
        plt.xlabel(r"$N_\mathrm{HI} (\mathrm{cm}^{-2})$")
        plt.ylabel(r"$f(N) (\mathrm{cm}^2)$")
        plt.xlim(10**minN, 10**maxN)
#         plt.legend(loc=0)
        plt.tight_layout()
        plt.show()

    def plot_radial_profile(self,minM=4e11,maxM=1e12,minR=0,maxR=40.):
        """Plots the radial density of neutral hydrogen for all halos stacked in the mass bin.
        """
        #Use sufficiently large bins
        scale = 10**43
        space=2.*self.ahalo.sub_radii[0]/self.ahalo.ngrid[0]
        if maxR/30. > space:
            Rbins=np.linspace(minR,maxR,20)
        else:
            Rbins=np.concatenate((np.array([minR,]),np.linspace(minR+np.ceil(2.5*space),maxR+space,maxR/np.ceil(space))))
        Rbinc = [(Rbins[i+1]+Rbins[i])/2 for i in xrange(0,np.size(Rbins)-1)]
        Rbinc=[minR,]+Rbinc
        try:
            aRprof=[self.ahalo.get_stacked_radial_profile(minM,maxM,Rbins[i],Rbins[i+1])/scale for i in xrange(0,np.size(Rbins)-1)]
            gRprof=[self.ghalo.get_stacked_radial_profile(minM,maxM,Rbins[i],Rbins[i+1])/scale for i in xrange(0,np.size(Rbins)-1)]
            plt.plot(Rbinc,[aRprof[0],]+aRprof,color=acol, ls=astyle,label="Arepo HI")
            plt.plot(Rbinc,[gRprof[0],]+gRprof,color=gcol, ls=gstyle,label="Gadget HI")
            plt.plot(Rbins,2*math.pi*Rbins*self.ahalo.UnitLength_in_cm*10**20.3/scale,color="black", ls="-.",label="DLA density")
            maxx=np.max((aRprof[0],gRprof[0]))
            #If we didn't load the HI grid this time
        except AttributeError:
            pass
#         #Gas profiles
#         try:
#             agRprof=[self.ahalo.get_stacked_radial_profile(minM,maxM,Rbins[i],Rbins[i+1],True) for i in xrange(0,np.size(Rbins)-1)]
#             ggRprof=[self.ghalo.get_stacked_radial_profile(minM,maxM,Rbins[i],Rbins[i+1],True) for i in xrange(0,np.size(Rbins)-1)]
#             plt.plot(Rbinc,[agRprof[0],]+agRprof,color="brown", ls=astyle,label="Arepo Gas")
#             plt.plot(Rbinc,[ggRprof[0],]+ggRprof,color="orange", ls=gstyle,label="Gadget Gas")
#             maxx=np.max((agRprof[0],ggRprof[0]))
#         except AttributeError:
#             pass
        #Make the ticks be less-dense
        #ax=plt.gca()
        #ax.xaxis.set_ticks(np.power(10.,np.arange(int(minN),int(maxN),2)))
        #ax.yaxis.set_ticks(np.power(10.,np.arange(int(np.log10(af_N[-1])),int(np.log10(af_N[0])),2)))
        plt.xlabel(r"R (kpc h$^{-1}$)")
        plt.ylabel(r"Radial Density ($10^{43}$ cm$^{-1}$)")
        #Crop the frame so we see the DLA cross-over point
        DLAdens=2*math.pi*Rbins[-1]*self.ahalo.UnitLength_in_cm*10**20.3
        if maxx > 20*DLAdens:
            plt.ylim(0,20*DLAdens)
        plt.xlim(minR,maxR)
        plt.legend(loc=1)
        plt.tight_layout()
        plt.show()

    import brokenpowerfit as br

    def plot_halo_fits(self):
        """Plots the central HI densities for a list of halos"""
        (aMbins, aM0, ar0)=self.ahalo.get_halo_fit_parameters()
        (gMbins, gM0, gr0)=self.ghalo.get_halo_fit_parameters()
        scale=1e42
        #Get a fit to the central density
        ap=self.br.powerfit(np.log10(aMbins[:-1]),np.log10(aM0[:-1]/scale),breakpoint=10.5)
        #No room for thieves, mercenaries, etc...
        gp=self.br.powerfit(np.log10(gMbins[:-1]),np.log10(gM0[:-1]/scale),breakpoint=10.5)
        alabel=r"$"+self.pr_num(ap[1])+"+(\mathrm{log M}-"+self.pr_num(ap[0])+")"+self.pr_num(ap[2])+"$"
        glabel=r"$"+self.pr_num(gp[1])+"+(\mathrm{log M}-"+self.pr_num(gp[0])+")"+self.pr_num(gp[2])+"$"
        plt.loglog(aMbins, aM0/scale,ls=astyle,label=alabel)
        plt.loglog(gMbins, gM0/scale,ls=gstyle,label=glabel)
        plt.loglog(aMbins, 10**(ap[2]*(np.log10(aMbins)-ap[0])+ap[1]),ls=astyle)
        plt.loglog(gMbins, 10**(gp[2]*(np.log10(gMbins)-gp[0])+gp[1]),ls=gstyle)
        #Get a fit to the central density
        ap=self.br.powerfit(np.log10(aMbins[:-1]),np.log10(ar0[:-1]),breakpoint=10.5)
        gp=self.br.powerfit(np.log10(gMbins[:-1]),np.log10(gr0[:-1]),breakpoint=10.5)
        alabel=r"$"+self.pr_num(ap[1])+"+(\mathrm{log M}-"+self.pr_num(ap[0])+")"+self.pr_num(ap[2])+"$"
        glabel=r"$"+self.pr_num(gp[1])+"+(\mathrm{log M}-"+self.pr_num(gp[0])+")"+self.pr_num(gp[2])+"$"
        plt.loglog(aMbins, ar0,ls=astyle,label=alabel)
        plt.loglog(gMbins, gr0, ls=gstyle,label=glabel)
        plt.ylim(1e-6,1e9)
        plt.legend(loc=0)

    def plot_central_density(self):
        """Plots the central HI densities for a list of halos"""
        aN0=np.array([self.ahalo.get_halo_central_density(h) for h in xrange(0,self.ahalo.nhalo)])
        gN0=np.array([self.ghalo.get_halo_central_density(h) for h in xrange(0,self.ghalo.nhalo)])
        aM = self.ahalo.sub_mass
        gM = self.ghalo.sub_mass
        aind = np.where(aN0 > 20)
        gind = np.where(gN0 > 20)
        afit=self.br.powerfit(np.log10(aM[aind]),aN0[aind],breakpoint=11)
        gfit=self.br.powerfit(np.log10(gM[gind]),gN0[gind],breakpoint=11)
        alabel=r"$"+self.pr_num(afit[1])+"+(\mathrm{log M}-11)"+self.pr_num(afit[2])+"$"
        glabel=r"$"+self.pr_num(gfit[1])+"+(\mathrm{log M}-11)"+self.pr_num(gfit[2])+"$"
        plt.semilogx(gM,(np.log10(gM)-gfit[0])*gfit[2]+gfit[1],ls=gstyle,color=gcol,label=glabel)
        plt.semilogx(aM,(np.log10(aM)-afit[0])*afit[2]+afit[1],ls=astyle,color=acol,label=alabel)
        plt.legend(loc=0)
        plt.semilogx(gM[gind],gN0[gind],'s',color=gcol)
        plt.semilogx(aM[aind],aN0[aind],'^',color=acol)
        plt.semilogx(gM,(np.log10(gM)-gfit[0])*gfit[2]+gfit[1],ls=gstyle,color=gcol,label=glabel)
        plt.semilogx(aM,(np.log10(aM)-afit[0])*afit[2]+afit[1],ls=astyle,color=acol,label=alabel)
        plt.ylabel(r"$ \mathrm{log} N_{HI} (\mathrm{cm}^{-2})$")
        plt.xlabel(r"Mass ($M_\odot$ h$^{-1}$)")
        plt.tight_layout()
        plt.show()

    def plot_rel_column_density(self,minN=17,maxN=23.):
        """Plots the column density distribution function. Figures 12 and 13"""
        (aNHI,af_N)=self.ahalo.column_density_function(0.4,minN-1,maxN+1)
        (gNHI,gf_N)=self.ghalo.column_density_function(0.4,minN-1,maxN+1)
        plt.semilogx(aNHI,af_N/gf_N,label="Arepo / Gadget",color=rcol)
        #Make the ticks be less-dense
#         ax=plt.gca()
#         ax.xaxis.set_ticks(np.power(10.,np.arange(int(minN),int(maxN),3)))
        #ax.yaxis.set_ticks(np.power(10.,np.arange(int(np.log10(af_N[-1])),int(np.log10(af_N[0])),2)))
        plt.xlabel(r"$N_\mathrm{HI} (\mathrm{cm}^{-2})$")
        plt.ylabel(r"$ \delta f(N)$")
        plt.xlim(10**minN, 10**maxN)
#         plt.legend(loc=0)
        plt.tight_layout()
        plt.show()

    def plot_halo_mass_func(self):
        """Plots the halo mass function as well as Sheth-Torman. Figure 5."""
        mass=np.logspace(np.log10(self.minplot),np.log10(self.maxplot),51)
        shdndm=[self.ahalo.halo_mass.dndm(mm) for mm in mass]
        adndm=np.empty(50)
        gdndm=np.empty(50)
        for ii in range(0,50):
            adndm[ii]=self.ahalo.get_dndm(mass[ii],mass[ii+1])
            gdndm[ii]=self.ghalo.get_dndm(mass[ii],mass[ii+1])
        plt.loglog(mass,shdndm,color="black",ls='--',label="Sheth-Tormen")
        plt.loglog(mass[0:-1],adndm,color=acol,ls=astyle,label="Arepo")
        plt.loglog(mass[0:-1],gdndm,color=gcol,ls=gstyle,label="Gadget")
        #Make the ticks be less-dense
        ax=plt.gca()
        ax.yaxis.set_ticks(np.power(10.,np.arange(int(np.log10(shdndm[-1])),int(np.log10(shdndm[0])),2)))

        plt.ylabel(r"dn/dM (h$^4$ $M^{-1}_\odot$ Mpc$^{-3}$)")
        plt.xlabel(r"Mass ($M_\odot$ h$^{-1}$)")
        plt.legend(loc=0)
        plt.xlim(self.minplot,self.maxplot)
        plt.tight_layout()
        plt.show()

