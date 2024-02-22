#Mencari rata rata dari input
import numpy as np

def ave(data, n_elec = 16):
    hasil = []

    for i in range(n_elec-3):
        mean = 0
        x = n_elec-3
        n,j = 0,i
        while (j < len(data)):
            n += 1
            if j >= x:
                j = j - (n_elec-3)
            x = x + (n_elec-3)
            
            mean = mean + data[j]

            if n in (1,n_elec-1):
                j += n_elec-3
            else:
                j += n_elec-2
            
        hasil.append(mean/n_elec)

    return reconstruc(n_elec=n_elec, data=hasil)     


def reconstruc(n_elec, data):
    Ndata = (n_elec-3)*n_elec
    reference = np.zeros(Ndata)


    for i in range(n_elec-3):
        x = n_elec-3
        n,j = 0,i           
        while (j < Ndata):
            n += 1
            if j >= x:
                j = j - (n_elec-3)
            x = x + (n_elec-3)
            
            reference[j] = data[i]

            if n in (1, n_elec-1):
                j += n_elec-3
            else:
                j += n_elec-2
                
    return reference


if __name__ == "__main__":
    data = np.loadtxt('2_VrmsSpidol20Knew3.csv', delimiter=',', dtype=float)
    
    """test = rata(208,[1,2,3,4,5,6,7,8,9,10,11,12,13,
    1,2,3,4,5,6,7,8,9,10,11,12,13,
    1,2,3,4,5,6,7,8,9,10,11,12,13], n_elec=3)
    print(test)"""

    test = ave(16, data)
    print(test)