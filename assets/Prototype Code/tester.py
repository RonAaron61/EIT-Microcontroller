from __future__ import absolute_import, division, print_function

import matplotlib.pyplot as plt
from matplotlib import colors
import numpy as np
import pyeit.eit.bp as bp
import pyeit.eit.protocol as protocol
import pyeit.mesh as mesh
from pyeit.eit.fem import EITForward
from pyeit.mesh import shape, distmesh, plot_distmesh
from pyeit.mesh.wrapper import PyEITAnomaly_Circle

import average  #Untuk merata-rata satu data aja

class EIT_reconstruct:
    def __init__ (self, data, reference = None, use_ref = 0, n_el = 16, use_shape = 3):
        self.n_el = n_el  # nb of electrodes
        self.use_shape = use_shape
        self.data = data
        self.reference = reference
        self.use_ref = use_ref
    
    def Reconstruct(self):

        """ 0. build mesh """
        if self.use_shape == 1:
            # Mesh shape is specified with fd parameter in the instantiation, e.g : fd=thorax
            # mesh_obj = mesh.create(n_el, h0=0.1, fd=thorax)
            mesh_obj = mesh.layer_circle(self.n_el, n_fan=15, n_layer=20)
            # n_fan dan n_layer diutak-atik buat jumlah mesh
        elif self.use_shape == 2:
            """Bulat biasa"""
            mesh_obj = mesh.create(self.n_el, h0=0.04)
            #h0 -> menentukan jumlah mesh
        elif self.use_shape == 3 :
            """unit circle mesh - Bulat dengan distmesh kyk eidors"""
            """ #Note: Buat make ini awal2 harus ngutak-ngatik di plot_mesh.py dulu, dan __init__.py nya"""
            def _fd(pts):
                """shape function"""
                return shape.circle(pts, pc=[0, 0], r=1.0)

            def _fh(pts):
                """distance function"""
                r2 = np.sum(pts**2, axis=1)
                return 0.2 * (2.0 - r2)

            # build fix points, may be used as the position for electrodes
            p_fix = shape.fix_points_circle(ppl=self.n_el)
            # firs num nodes are the positions for electrodes
            el_pos = np.arange(self.n_el)

            # build triangle
            #p, t = distmesh.build(_fd, _fh, pfix=p_fix, h0=0.05)
            mesh_obj = mesh.create(fd=_fd, fh=_fh, p_fix=p_fix, h0=0.024)
            #plot_distmesh(p, t, el_pos)

        el_pos = mesh_obj.el_pos


        """ 1. FEM forward simulations """
        # setup EIT scan conditions
        # adjacent stimulation (dist_exc=1), adjacent measures (step_meas=1)
        protocol_obj = protocol.create(self.n_el, dist_exc=1, step_meas=1, parser_meas="std")
        print("Mesh done...")


        """ 2. naive inverse solver using back-projection """
        eit = bp.BP(mesh_obj, protocol_obj)
        eit.setup(weight="simple")  #Lebih bagus pake ini
        #eit.setup(weight="None")


        """ 3. Input Data """
        if self.use_ref == 1:     #Use existing reference data
            referenceData = np.array(self.reference)

        elif self.use_ref == 0:   #Create reference data from data
            referenceData = average.ave(data=self.data, n_elec=self.n_el)

        #data = np.loadtxt('2_VrmsSpidolLogam20Knew3.csv', delimiter=',', dtype=float)   
        print("Input Data Done...")


        """ 4. Inverse Problem """
        node_ds = 192.0 * eit.solve(self.data, referenceData, normalize=True)

        # extract node, element, alpha
        pts = mesh_obj.node
        tri = mesh_obj.element

        """ Plot Hasil """
        print("Plotting result...")
        #Draw the number of electrode
        def dot_num(x, y, axn, n):
            elect = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16]
            for i in range(len(n)):
                el2 = el_pos[i]
                el = elect[i]
                xi = x[el2, 0]
                yi = y[el2, 1]
                offset = 0.06
                if round(xi,3) > 0:
                    xt = xi+offset-0.04       
                elif round(xi,3) < 0:
                    xt = xi-offset
                else:
                    xt = xi
                
                if round(yi,3) > 0:
                    yt = yi+offset-0.04
                elif round(yi,3) < 0:
                    yt = yi-offset
                else:
                    yt = yi

                axn.annotate(el, xy=(xt,yt))
        # draw
        fig, axes = plt.subplots(1, 2, constrained_layout=True, figsize=(6, 9))


        # Mesh - plot the mesh
        ax2 = axes[0]
        ax2.triplot(pts[:, 0], pts[:, 1], tri, linewidth=1) #pts[:, 1], pts[:, 0] -> kebalik urutan elekt nya
        ax2.plot(pts[el_pos, 0], pts[el_pos, 1], "ro")
        #dot_num(pts, pts, ax2, pts[el_pos, 1])
        ax2.axis("equal")
        ax2.axis([-1.2, 1.2, -1.2, 1.2])
        title_src = (
            "number of triangles = "
            + str(np.size(tri, 0))
            + ", "
            + "number of nodes = "
            + str(np.size(pts, 0))
        )
        ax2.set_title(title_src)

        # reconstructed
        ax1 = axes[1]
        ax1.set_title(r"Reconstituted $\Delta$ Conductivities")
        ax1.axis("equal")
        ax1.plot(pts[el_pos, 0], pts[el_pos, 1],"ro")
        im = ax1.tripcolor(
            pts[:, 0],
            pts[:, 1],
            tri,
            np.real(node_ds),
            #edgecolor="k", #Buat nampilin bentuk mesh
            shading="flat",
            alpha=1,
            cmap=plt.cm.twilight_shifted,    #For colormap -> https://matplotlib.org/stable/gallery/color/colormap_reference.html
            norm = colors.CenteredNorm() #Biar colormap nya gk geser2
            
            #Kalo mau warnanya di kontrasin ->
            #norm = colors.BoundaryNorm(boundaries=np.linspace(-13, 13, 6), ncolors=256, extend='both'),
            #cmap = 'RdBu_r'
        )
        #dot_num(pts, pts, ax1, pts[el_pos, 1])
        x, y = pts[:, 0], pts[:, 1]
        for i, e in enumerate(mesh_obj.el_pos):
            ax1.annotate(str(i + 1), xy=(x[e], y[e]), color="b")

        # 'tricontour' interpolates values on nodes, for example
        # ax.tricontour(pts[:, 0], pts[:, 1], tri, np.real(node_ds),
        # shading='flat', alpha=1.0, linewidths=1,
        # cmap=plt.cm.RdBu)
        fig.colorbar(im)
        #fig.colorbar(im, ax=axes.ravel().tolist())
        #mng = plt.get_current_fig_manager()
        #mng.full_screen_toggle()

        plt.show()  #Jangan lupa di Full screen dulu baru di close kalo mau disave image nya fullscreen
        #fig.savefig('ReferensiRATARATA.png', dpi=96, bbox_inches='tight')

if __name__ == '__main__':
    #data = np.loadtxt('2_VrmsSpidolLogam20Knew3.csv', delimiter=',', dtype=float)
    data = [1.604861, 0.6898336, 0.3483856, 0.2765709, 0.2214443, 0.2026937, 0.1610674, 0.1723178, 0.1711927, 0.261008, 0.3480106, 0.6476448, 1.472107, 1.655488, 0.6140813, 0.4127001, 0.2872587, 0.2471325, 0.1828181, 0.178693, 0.1605049, 0.2158191, 0.2491951, 0.3836367, 0.6506448, 1.625862, 1.549735, 1.356979, 0.6978963, 0.4059499, 0.311447, 0.2182567, 0.1923809, 0.1560048, 0.1850681, 0.1899433, 0.2583829, 0.3695738, 0.6872085, 0.6613327, 1.560235, 1.816743, 0.7483353, 0.4832023, 0.3045093, 0.2521952, 0.1822556, 0.1951935, 0.1777554, 0.2107564, 0.2668206, 0.4040748, 0.3155721, 0.5332663, 1.353416, 1.461045, 0.6879585, 0.3783865, 0.2816336, 0.1871307, 0.1800055, 0.1558173, 0.1612549, 0.1755054, 0.2272569, 0.2505076, 0.3530733, 0.6950837, 1.71174, 1.6328, 0.6911461, 0.4595766, 0.2876338, 0.2535077, 0.1890058, 0.1777554, 0.1845056, 0.2094439, 0.2071938, 0.2491951, 0.4147627, 0.7177719, 1.424481, 1.467982, 0.7466478, 0.4179502, 0.3358228, 0.2336321, 0.2043813, 0.1901308, 0.1963185, 0.2038187, 0.2165691, 0.3316977, 0.4623891, 0.6712705, 1.576736, 1.680426, 0.7145843, 0.4937026, 0.3172597, 0.2576329, 0.2244443, 0.2145066, 0.1711927, 0.16538, 0.24432, 0.3033843, 0.3811991, 0.6761456, 1.425793, 1.454669, 0.722272, 0.3856993, 0.2786335, 0.2186317, 0.1944434, 0.1788805, 0.1612549, 0.2165691, 0.2420699, 0.2825711, 0.4440135, 0.7117717, 1.591736, 1.812243, 0.6898336, 0.4151377, 0.2827586, 0.2266944, 0.1818806, 0.1597549, 0.1803805, 0.179068, 0.1942559, 0.2833211, 0.3999497, 0.6680829, 1.372729, 1.438544, 0.6587076, 0.3697613, 0.261383, 0.2677582, 0.1884433, 0.2109439, 0.1875057, 0.1841306, 0.2448825, 0.3127595, 0.443076, 0.6527074, 1.679301, 1.709865, 0.7119593, 0.4288256, 0.3630111, 0.2325071, 0.2178817, 0.1764429, 0.1571298, 0.1882558, 0.2227568, 0.2868838, 0.3463231, 0.6482072, 1.368792, 1.501921, 0.6830833, 0.6860834, 0.3793241, 0.2953215, 0.2203192, 0.1700677, 0.1893808, 0.2060688, 0.2431949, 0.2555703, 0.3958246, 0.621019, 1.649488, 1.677239, 1.522359, 0.6416446, 0.4083875, 0.2696332, 0.1873182, 0.1863807, 0.1831931, 0.1978185, 0.1846931, 0.2523827, 0.3288851, 0.6632078, 1.418856, 1.645175, 0.7449602, 0.4235754, 0.2583829, 0.2300695, 0.2043813, 0.2040062, 0.1730678, 0.2098189, 0.2349447, 0.4003247, 0.637707, 1.582361]


    reference = [1.6283, 0.7035215, 0.3577609, 0.2808836, 0.2090689, 0.178318, 0.1599424, 0.1708177, 0.1777554, 0.2716958, 0.3585109, 0.6624577, 1.497608, 1.686051, 0.6322693, 0.4228254, 0.2814461, 0.2208817, 0.1625675, 0.1719428, 0.162755, 0.2233193, 0.2578204, 0.393762, 0.6643328, 1.656801, 1.575236, 1.387542, 0.7138343, 0.4046374, 0.2848212, 0.1899433, 0.1811305, 0.1552547, 0.1903183, 0.1963185, 0.2666332, 0.3798866, 0.705209, 0.6858959, 1.589861, 1.81693, 0.7622108, 0.4532013, 0.2681332, 0.2272569, 0.1753179, 0.196131, 0.1815055, 0.2165691, 0.2756334, 0.4173877, 0.3275725, 0.5518293, 1.378355, 1.502108, 0.6693954, 0.3373228, 0.2486326, 0.1726928, 0.1740053, 0.1614424, 0.1563798, 0.179443, 0.2390698, 0.2583829, 0.3633861, 0.7153344, 1.754116, 1.6508, 0.6412696, 0.4087625, 0.2542578, 0.2326946, 0.1781304, 0.1719428, 0.1824431, 0.2126315, 0.197631, 0.2420699, 0.4168252, 0.7299598, 1.464982, 1.473232, 0.7010839, 0.3727614, 0.2988841, 0.2075688, 0.180943, 0.181318, 0.1890058, 0.1927559, 0.1882558, 0.3039468, 0.4333257, 0.6564575, 1.598299, 1.703677, 0.6993964, 0.4635141, 0.2883838, 0.2281945, 0.1983811, 0.1893808, 0.1590049, 0.1603174, 0.2171316, 0.2658831, 0.3420105, 0.6328318, 1.435731, 1.491983, 0.7331474, 0.3843867, 0.2716958, 0.2083189, 0.1826306, 0.1755054, 0.1548797, 0.2045687, 0.2190067, 0.2506951, 0.3943245, 0.6682704, 1.620612, 1.809618, 0.7083966, 0.4237629, 0.2913839, 0.228382, 0.1863807, 0.1565673, 0.178318, 0.1725053, 0.178693, 0.2510702, 0.3605735, 0.6553325, 1.409105, 1.464045, 0.6744581, 0.3825117, 0.2705708, 0.2771335, 0.195006, 0.214694, 0.1873182, 0.1766304, 0.2223818, 0.2761959, 0.4192628, 0.6647078, 1.718678, 1.73574, 0.7329598, 0.4436386, 0.3729489, 0.2413199, 0.2233193, 0.1807555, 0.1563798, 0.1764429, 0.196506, 0.262133, 0.3463231, 0.6662078, 1.39823, 1.522922, 0.7016464, 0.6993964, 0.3913244, 0.3045093, 0.227632, 0.1719428, 0.1826306, 0.1837556, 0.2165691, 0.2493826, 0.4057624, 0.6393945, 1.678551, 1.710615, 1.547485, 0.656645, 0.4183252, 0.2793835, 0.1914433, 0.1835681, 0.1672551, 0.1741928, 0.1747553, 0.2578204, 0.3420105, 0.6785832, 1.442107, 1.671051, 0.7633358, 0.4363258, 0.2641956, 0.2315696, 0.1893808, 0.1796305, 0.1597549, 0.2111314, 0.2437574, 0.4125126, 0.6521449, 1.605611]
  
    reconstruct = EIT_reconstruct(data=data, reference=reference, use_ref=1, n_el=16)
    reconstruct.Reconstruct()