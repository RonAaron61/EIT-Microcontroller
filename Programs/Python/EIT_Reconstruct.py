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


        """ 3. Input Data """
        if self.use_ref == 1:     #Use existing reference data
            referenceData = np.array(self.reference)
            

        elif self.use_ref == 0:   #Create reference data from data
            referenceData = average.ave(data=self.data, n_elec=self.n_el)

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
        fig, axes = plt.subplots(1, 1, constrained_layout=True, figsize=(6, 6))

        # reconstructed
        ax1 = axes
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

        #plt.show()  #Jangan lupa di Full screen dulu baru di close kalo mau disave image nya fullscreen
        return plt.show()
        #fig.savefig('ReferensiRATARATA.png', dpi=96, bbox_inches='tight')

if __name__ == '__main__':
    reference = [1.809055, 0.8100247, 0.3967621, 0.3232599, 0.2467575, 0.2371947, 0.2000686, 0.2242568, 0.2328821, 0.3315101, 0.4357633, 0.7938993, 1.722053, 1.916683, 0.6648952, 0.4732644, 0.3185722, 0.2756334, 0.212444, 0.2175066, 0.2066313, 0.2668206, 0.3076969, 0.4689518, 0.7428976, 1.928871, 1.819368, 1.271664, 0.8216501, 0.4655767, 0.3549483, 0.2473201, 0.2311945, 0.2015687, 0.2370072, 0.2471325, 0.3339477, 0.4466386, 0.8539011, 0.8171499, 1.900558, 2.138315, 0.8734017, 0.5514544, 0.3390104, 0.2850087, 0.2266944, 0.2435699, 0.2310071, 0.2806961, 0.3288851, 0.5193909, 0.4051999, 0.688896, 1.580673, 1.295852, 0.769336, 0.3965746, 0.294009, 0.211694, 0.2085064, 0.1811305, 0.2011936, 0.2133815, 0.2990716, 0.3318851, 0.4730769, 0.8295254, 2.169629, 1.773054, 0.7462728, 0.4708269, 0.3041343, 0.2718833, 0.2169441, 0.2220068, 0.2158191, 0.2731958, 0.2561328, 0.3174472, 0.4730769, 0.8786518, 1.375729, 1.538297, 0.7736486, 0.4232004, 0.3345102, 0.2411324, 0.2248194, 0.2002561, 0.230632, 0.24432, 0.2711333, 0.3583234, 0.5512669, 0.7338974, 1.912933, 1.978748, 0.8057121, 0.5321412, 0.3388228, 0.2850087, 0.230632, 0.2415074, 0.2079438, 0.2092564, 0.2516327, 0.3401354, 0.3984497, 0.7468353, 1.493483, 1.641237, 0.8077746, 0.4305131, 0.3193222, 0.2336321, 0.2233193, 0.2321321, 0.2137565, 0.2362572, 0.2857587, 0.2956965, 0.4717644, 0.7749611, 1.87562, 2.026749, 0.7914617, 0.49239, 0.3202598, 0.2746959, 0.2401948, 0.2023187, 0.2055063, 0.2268819, 0.2130065, 0.3043218, 0.4239504, 0.8077746, 1.619112, 1.618737, 0.7552731, 0.4143877, 0.3142596, 0.3399479, 0.262508, 0.2418824, 0.2437574, 0.2090689, 0.2718833, 0.3339477, 0.5328912, 0.8070247, 2.026374, 1.926621, 0.7925867, 0.5057029, 0.4449511, 0.3046968, 0.2531327, 0.2323196, 0.1828181, 0.2178817, 0.2420699, 0.3412604, 0.4338882, 0.7959618, 1.6253, 1.672739, 0.7908991, 0.8036495, 0.4650142, 0.3399479, 0.2816336, 0.2026937, 0.2220068, 0.2251944, 0.2861337, 0.3208223, 0.4937026, 0.7562106, 1.932246, 1.930184, 1.738178, 0.7425227, 0.4558264, 0.3326352, 0.2169441, 0.2180691, 0.2023187, 0.2347572, 0.2375698, 0.3234473, 0.4194503, 0.7980244, 1.677989, 1.921371, 0.8632764, 0.5225784, 0.3015092, 0.2743209, 0.2311945, 0.24432, 0.2242568, 0.2748834, 0.3150096, 0.5040154, 0.7858365, 1.918184]
    data = [1.650988, 0.8212751, 0.4367009, 0.3624485, 0.2718833, 0.2516327, 0.2049438, 0.2233193, 0.2266944, 0.3198848, 0.4170127, 0.7592107, 1.647988, 1.835681, 0.7020214, 0.5184533, 0.3573859, 0.3067594, 0.2317571, 0.2311945, 0.213194, 0.2696332, 0.3037593, 0.4539514, 0.7102716, 1.850307, 1.05847, 1.29829, 0.8381506, 0.5012028, 0.3935745, 0.2782585, 0.2600704, 0.2238818, 0.2602579, 0.2653206, 0.3483856, 0.4513263, 0.8377756, 0.8058996, 1.835681, 2.054313, 0.8574636, 0.5610171, 0.3566359, 0.3082594, 0.2493826, 0.2726333, 0.2596954, 0.3136971, 0.3622611, 0.5542669, 0.4455136, 0.7121467, 1.542047, 1.114347, 0.7393351, 0.3871993, 0.2938215, 0.2161941, 0.2197567, 0.1955685, 0.2227568, 0.2405699, 0.3380728, 0.3718238, 0.5175158, 0.8456508, 2.063875, 1.767804, 0.7123342, 0.4505763, 0.2930715, 0.2679457, 0.2184442, 0.229882, 0.2311945, 0.3028218, 0.2818211, 0.3566359, 0.508328, 0.8645888, 1.38773, 1.591736, 0.7404601, 0.4027623, 0.3206348, 0.2332571, 0.2216318, 0.2028812, 0.24432, 0.2595079, 0.3028218, 0.3967621, 0.5617671, 0.73746, 1.841681, 1.914246, 0.770836, 0.5092655, 0.3228848, 0.2731958, 0.2253819, 0.24507, 0.2126315, 0.2285695, 0.2823836, 0.3583234, 0.3892619, 0.7145843, 1.266039, 1.583486, 0.7762737, 0.4110126, 0.3046968, 0.2242568, 0.2191942, 0.2315696, 0.2278195, 0.2645706, 0.3090094, 0.2956965, 0.4526388, 0.7419601, 1.858182, 1.96656, 0.7607107, 0.4710144, 0.3048843, 0.2647581, 0.2341946, 0.2094439, 0.227632, 0.2499451, 0.2178817, 0.2945715, 0.4040748, 0.7751487, 1.589111, 1.56361, 0.7233971, 0.3946996, 0.2998216, 0.3279475, 0.2655081, 0.2641956, 0.2726333, 0.2205067, 0.2683207, 0.3204473, 0.5102031, 0.7768362, 1.96806, 1.872995, 0.7618358, 0.4839523, 0.4262005, 0.3007592, 0.2705708, 0.2608205, 0.197256, 0.2199442, 0.2341946, 0.3260725, 0.4140126, 0.7653984, 1.57111, 1.620799, 0.7597732, 0.7710236, 0.4509513, 0.3538233, 0.3148221, 0.2242568, 0.2308196, 0.2221943, 0.2754459, 0.3065719, 0.4732644, 0.7263971, 1.876932, 1.872245, 1.022281, 0.7102716, 0.4588265, 0.3643236, 0.2433824, 0.2334446, 0.2051313, 0.2293195, 0.2278195, 0.3086344, 0.3988247, 0.7668984, 1.624549, 1.849931, 0.8473384, 0.555767, 0.3403229, 0.3039468, 0.2452575, 0.2476951, 0.2208817, 0.2662581, 0.3009467, 0.4833898, 0.7558356, 1.863807]   
    reconstruct = EIT_reconstruct(data=data, reference=reference, use_ref=1, n_el=16)

    reconstruct.Reconstruct()