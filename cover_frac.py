# vim: set fileencoding=utf-8
"""
Module for computing covering fractions, similar to how they are defined in Rudie et al. 2012 (e.g. see their Figure 15)
"""

import halohi
import numpy as np
import os.path as path
import math
import matplotlib.pyplot as plt
import matplotlib.colors

def tight_layout_wrapper():
    try:
        plt.tight_layout()
    except AttributeError:
        pass

class CoverFrac(halohi.HaloHI):

    def kpc_to_grid(self, kpc_dist, halo_num):
        fac = self.ngrid[halo_num]/(2.*self.sub_radii[halo_num])
        grid_dist = kpc_dist * fac
        return grid_dist

    def halo_covering_frac(self, halo_num, N0_cutoffs, r_min_array, delta_r_kpc,return_LLA_DLA_totalfrac=False,return_percents=False):
        halo_grid=np.array(self.sub_nHI_grid[halo_num])
        halo_radius = self.sub_radii[halo_num]
        #print "halo_radius ",halo_radius
        #print "np.size(halo_grid,axis=0)", np.size(halo_grid,axis=0)
        #print "np.size(halo_grid,axis=1)", np.size(halo_grid,axis=1)
        N13_percent = np.float(np.sum(halo_grid > 13.))/(np.size(halo_grid,axis=0)**2)
        LLS_percent = np.float(np.sum(np.logical_and(halo_grid > 17.2,halo_grid < 20.3)))/(np.size(halo_grid,axis=0)**2)
        DLA_percent = np.float(np.sum(halo_grid > 20.3))/(np.size(halo_grid,axis=0)**2)

        tot_n_cells = np.float(np.size(halo_grid,axis=0)**2)
        percents_N0_cutoffs = np.arange(13,25)
        percents = np.ones(np.size(percents_N0_cutoffs)-1)
        for i in np.arange(np.size(percents_N0_cutoffs)-1):
            percents[i] = np.float(np.sum(np.logical_and(halo_grid > percents_N0_cutoffs[i],halo_grid < percents_N0_cutoffs[i+1])))/tot_n_cells
        #print "N13_percent ",N13_percent
        #print "n_covered ",n_covered
        #plt.hist(np.ravel(halo_grid),normed=False)
        #plt.show()


        halo_ngrid = self.ngrid[halo_num]
        #print "self.ngrid", self.ngrid
        #print "self.ngrid[halo_num] ", self.ngrid[halo_num]

        [gridx,gridy] = np.meshgrid(np.arange(halo_ngrid),np.arange(halo_ngrid))
        grid_cent = (halo_ngrid-1)/2. #assume square grid: grid_centx = grid_centy = grid_cent

        delta_r_grid = self.kpc_to_grid(delta_r_kpc,halo_num)
        r_grid = np.sqrt((gridx-grid_cent)**2+(gridy-grid_cent)**2)


        N_r_ticks = np.size(r_min_array)
        N_N0_ticks = np.size(N0_cutoffs)
        cover_frac = np.zeros([N_r_ticks,N_N0_ticks])
        
        for r_ind in np.arange(N_r_ticks):
            rmin = self.kpc_to_grid(r_min_array[r_ind],halo_num)
            rmax = rmin + delta_r_grid

            rmin_cond = (r_grid >= rmin)
            rmax_cond = (r_grid < rmax)

            ind = np.where(np.logical_and(rmin_cond,rmax_cond))

            nHI_annulus = halo_grid[ind]
            #print "nHI_annulus ",nHI_annulus
            #print "np.shape(nHI_annulus)",np.shape(nHI_annulus)
            n_tot = np.float(np.size(nHI_annulus))
            #print "n_tot ",n_tot


            for N0_ind in np.arange(N_N0_ticks):
                if n_tot > 0:
                    N0 = N0_cutoffs[N0_ind]
                    n_covered = np.float(np.sum(nHI_annulus > N0))
                    cover_frac[r_ind,N0_ind] = n_covered/n_tot
                elif n_tot == 0:
                    cover_frac[r_ind,N0_ind] = -1.

        if return_LLA_DLA_totalfrac:
            return [cover_frac,LLS_percent,DLA_percent]
        elif return_percents:
            return [cover_frac, percents, percents_N0_cutoffs]
        else:
            return cover_frac



    def aggregate_covering_fracs(self):
        #m_min_array = np.array([10.**10.,10.**10.5,10.**11.0,10.**11.5,10.**12.0])
        m_min_array = np.array([10.**11.25,10.**11.75])
        m_max_array = m_min_array*(10.**0.5)
        n_mbins = np.size(m_min_array)

        fig = plt.figure()
        fig_percent=plt.figure(10)

        for m_ind in np.arange(n_mbins):
            topmass = m_max_array[m_ind]
            botmass = m_min_array[m_ind]
            #print "self.sub_mass ",self.sub_mass

            mass_ind = np.where(np.logical_and(self.sub_mass > botmass, self.sub_mass < topmass))[0]
            n_halo = np.size(mass_ind)

            print "n_halo", n_halo

            delta_r_kpc = 10. #100.
            #r_min_array = np.arange(0.,2900.,delta_r_kpc)
            r_min_array = np.arange(0.,190.,delta_r_kpc)
            N_r_ticks = np.size(r_min_array)

            N0_cutoffs = [13.0, 13.5, 14.0, 14.5, 15.0, 16.0]
            N_N0_ticks = np.size(N0_cutoffs)

            all_cover_dat = np.zeros([N_r_ticks,N_N0_ticks,n_halo])

            # Aggregate all covering fraction data for halos of interest
            LLS_percent = np.zeros(n_halo)
            DLA_percent = np.zeros(n_halo)
            percents_N0_cutoffs = np.arange(13,25)
            percents_dat = np.zeros([n_halo,np.size(percents_N0_cutoffs)-1])
            for i in np.arange(n_halo):
                #[cover_frac, percents_dat[i,:], percents_N0_cutoffs] = self.halo_covering_frac(mass_ind[i],N0_cutoffs,r_min_array,delta_r_kpc,return_percents=True)
                [cover_frac, LLS_percent[i],DLA_percent[i]] = self.halo_covering_frac(mass_ind[i],N0_cutoffs,r_min_array,delta_r_kpc,return_LLA_DLA_totalfrac=True)
                all_cover_dat[:,:,i] = cover_frac

            print "For M >",botmass," and < ",topmass,", we find that within 1 Rvir: "
            print "LLS percent", np.mean(LLS_percent)
            print "DLA_percent", np.mean(DLA_percent)
            #percents_avg = np.ones(np.size(percents_N0_cutoffs)-1)
            #percents_std = np.ones(np.size(percents_N0_cutoffs)-1)
            #for i in np.arange(np.size(percents_N0_cutoffs)-1):
            #    percents_avg[i] = np.mean(percents_dat[:,i])
            #    print "Between ",percents_N0_cutoffs[i]," and ",percents_N0_cutoffs[i+1], ", we find ",np.mean(percents_dat[:,i])

            #plt.semilogy(percents_N0_cutoffs[:-1],percents_avg)
            #plt.title("")
            #plt.ylim(10.**-5.,0.1)
            #plt.ylabel("Fc(< 1 rvir)")
            #plt.xlabel("N_HI")
            #plt.show()

            for N0_ind in np.arange(N_N0_ticks):
                ax = fig.add_subplot(2,3,N0_ind+1)

                Q1 = np.zeros(N_r_ticks)
                median = np.zeros(N_r_ticks)
                Q3 = np.zeros(N_r_ticks)

                for r_ind in np.arange(N_r_ticks):
                    data_on_grid = np.where(all_cover_dat[r_ind,N0_ind,:] >= 0.)[0]
                    #print "data_on_grid ",data_on_grid
                    # wherever the cover_frac is -1, this means that the grid did not extend far enough to calculate the covering fraction
                    #print "all_cover_dat[r_ind,N0_ind,data_on_grid]", all_cover_dat[r_ind,N0_ind,data_on_grid]

                    Q3[r_ind] = np.percentile(all_cover_dat[r_ind,N0_ind,data_on_grid],75)
                    median[r_ind] = np.median(all_cover_dat[r_ind,N0_ind,data_on_grid])
                    Q1[r_ind] = np.percentile(all_cover_dat[r_ind,N0_ind,data_on_grid],25)

                    #print "Q3[r_ind]", Q3[r_ind]
                    #print "median[r_ind]", median[r_ind]
                    #print "Q1[r_ind]", Q1[r_ind]

                #plt.title("N_HI > "+str(N0_cutoffs[N0_ind]))
                if m_ind == 0: 
                    facecolor='blue'
                elif m_ind == 1: 
                    facecolor='green'
                elif m_ind == 2:
                    facecolor='red'

                comoving_to_physical = 1./(1+self.redshift)
                #print "self.redshift ",self.redshift

                #plt.plot(comoving_to_physical*r_min_array,median)
                #plt.semilogy(r_min_array,median) #drawstyle='steps-pre'
                #plt.fill_between(comoving_to_physical*r_min_array, Q3, Q1, facecolor=facecolor,alpha=0.25)  #, facecolor='blue'
                #plt.ylim(0.,1.)
                #plt.ylabel("f_C")
                #plt.xlabel(r"r (kpc h$^{-1}$)")

        tight_layout_wrapper()
        plt.show()





    def sum_NHI_statistic(self):
        """ Use sum(NHI) statistic to compare with observations """
        m_min_array = np.array([10.**11.25,10.**11.75])
        m_max_array = m_min_array*(10.**0.5)
        n_mbins = np.size(m_min_array)

        for m_ind in np.arange(n_mbins):
            topmass = m_max_array[m_ind]
            botmass = m_min_array[m_ind]

            mass_ind = np.where(np.logical_and(self.sub_mass > botmass, self.sub_mass < topmass))[0]
            n_halo = np.size(mass_ind)

            print "n_halo", n_halo











    def alternate_covering_frac(self):
        """ This is a failed attempt at calculating the cover fraction.  Here what I do is treat an "absorber" as any individual pixel with column
        density greater than the threshold, and try to find the fraction of galaxies that have such an "absorber" within any given radius bin. """

        fig = plt.figure()

        topmass = 10.**12.25
        botmass = 10.**11.75

        mass_ind = np.where(np.logical_and(self.sub_mass > botmass, self.sub_mass < topmass))[0]
        n_halo = np.size(mass_ind)


        print "n_halo", n_halo

        delta_r_kpc = 10. #100.
        #r_min_array = np.arange(0.,2900.,delta_r_kpc)
        r_min_array = np.arange(0.,190.,delta_r_kpc)
        N_r_ticks = np.size(r_min_array)

        N0_cutoffs = [13.0, 13.5, 14.0, 14.5, 15.0, 16.0]
        N_N0_ticks = np.size(N0_cutoffs)

        all_inclus_dat = np.zeros([N_r_ticks,N_N0_ticks,n_halo])

        # Aggregate all covering fraction data for halos of interest
        for i in np.arange(n_halo):
            inclus_frac = self.halo_inclusion_frac(mass_ind[i],N0_cutoffs,r_min_array,delta_r_kpc)
            all_inclus_dat[:,:,i] = inclus_frac


        all_cover_frac = np.zeros([N_r_ticks,N_N0_ticks])

        for N0_ind in np.arange(N_N0_ticks):
            ax = fig.add_subplot(2,3,N0_ind+1)

            for r_ind in np.arange(N_r_ticks):
                n_covered = 0.
                n_tot = 0.
                for halo_ind in np.arange(n_halo):
                    if all_inclus_dat[r_ind,N0_ind,halo_ind] == -1:
                        pass
                    elif all_inclus_dat[r_ind,N0_ind,halo_ind] == 0:
                        n_tot = n_tot + 1.
                    elif all_inclus_dat[r_ind,N0_ind,halo_ind] == 1:
                        n_covered = n_covered + 1.
                        n_tot = n_tot + 1.

                if n_tot == 0.:
                    raise KeyError("Too far")
                cover_frac = n_covered/n_tot
                all_cover_frac[r_ind,N0_ind] = cover_frac

            plt.title("N_HI > "+str(N0_cutoffs[N0_ind]))

            comoving_to_physical = 1./(1+self.redshift)

            plt.plot(comoving_to_physical*r_min_array,all_cover_frac[:,N0_ind],drawstyle='steps-pre')
            plt.ylim(0.,1.1)
            plt.ylabel("f_C")
            plt.xlabel(r"r (kpc h$^{-1}$)")

        tight_layout_wrapper()
        plt.show()



    def halo_inclusion_frac(self, halo_num, N0_cutoffs, r_min_array, delta_r_kpc):
        halo_grid=np.array(self.sub_nHI_grid[halo_num])
        halo_radius = self.sub_radii[halo_num]

        comoving_to_physical = 1./(1+self.redshift)
        physical_radius = halo_radius * comoving_to_physical
        print "physical radius",physical_radius

        halo_ngrid = self.ngrid[halo_num]

        [gridx,gridy] = np.meshgrid(np.arange(halo_ngrid),np.arange(halo_ngrid))
        grid_cent = halo_ngrid/2. #assume square grid: grid_centx = grid_centy = grid_cent

        delta_r_grid = self.kpc_to_grid(delta_r_kpc,halo_num)
        r_grid = np.sqrt((gridx-grid_cent)**2+(gridy-grid_cent)**2)


        N_r_ticks = np.size(r_min_array)
        N_N0_ticks = np.size(N0_cutoffs)
        inclusion_frac = np.zeros([N_r_ticks,N_N0_ticks])
        
        for r_ind in np.arange(N_r_ticks):
            rmin = self.kpc_to_grid(r_min_array[r_ind],halo_num)
            rmax = rmin + delta_r_grid

            rmin_cond = (r_grid >= rmin)
            rmax_cond = (r_grid < rmax)

            ind = np.where(np.logical_and(rmin_cond,rmax_cond))

            nHI_annulus = halo_grid[ind]
            n_tot = np.float(np.size(nHI_annulus))

            for N0_ind in np.arange(N_N0_ticks):
                if n_tot > 0:
                    N0 = N0_cutoffs[N0_ind]
                    n_covered = np.float(np.sum(nHI_annulus > N0))
                    print "For N0 ",N0, "with Rmin=",rmin,"we find n_covered ",n_covered
                    if n_covered >= 1:
                        inclusion_frac[r_ind,N0_ind] = 1.
                    elif n_covered == 0:
                        inclusion_frac[r_ind,N0_ind] = 0.
                elif n_tot == 0:
                    inclusion_frac[r_ind,N0_ind] = -1.

        return inclusion_frac























