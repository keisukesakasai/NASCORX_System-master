#! /usr/bin/env python
# _*_ coding: UTF-8 _*_


#import modules
import sys, time, datetime, os, csv, numpy
sys.path.append('/home/amigos/NASCORX_System/base/')
import Cryo, Lo
sys.path.append('/home/amigos/NASCORX_System/device/')
import ML2437A, CPZ7204

class ymap(object):
    '''
    DESCRIPTION
    ================
    This class makes the Y-factor maps of the SIS mixer.

    ARGUMENTS
    ================
    Nothing.
    '''

    def __init__(self):
        self.mix = Cryo.mixer()
        self.sg = Lo.firstlo(multiplier=6)
        self.pm = ML2437A.ml2437a(IP='192.168.100.113', GPIB=13)
        self.load = CPZ7204.cpz7204()

    def makemap(self, LOrange=[90, 120], LOres=5, Vrange=[6, 8], Vres=0.1, Irange=[10, 30], Ires=10, logpath='/home/amigos/data/SIS/'):
        '''
        DESCRIPTION
        ================
        This function measures SIS mixer noise.

        ARGUMENTS
        ================
        1. LOrange: searching area of the LO frequency [GHz]
            Number: 1st SG * multiplier [mV]
            Type: list[float, float]
            Default: [90, 120]
        2. LOres: searching resolutin of the LO frequency [GHz]
            Number: LOres > 1 [Hz]
            Type: float
            Default: 5
        3. Vrange: searching area of the mixer voltage [mV]
            Number: 0 -- 30 [mV]
            Type: list[float, float]
            Default: [6, 8]
        4. Vres: searching resolutin of the mixer voltage [uV]
            Number: 0.04 < Vres <= 30 [mV]
            Type: float
            Default: 0.1
        5. Irange: searching area of the LO attenuator [mA]
            Number: 0 -- 100 [mA]
            Type: list[float, float]
            Default: [10, 100]
        6. Ires: searching resolutin of LO attenuator [mA]
            Number: 0 < Ires <= 100 [mA]
            Type: float
            Default: 10
        7. logpath: directory path of the log file
            Type: string
            Default: '/home/amigos/data/SIS/'

        RETURNS
        ================
        Nothing.
        '''
        DAch = 0
        VADch = 0
        IADch = 1
        LOatt = 0
        print('====START MEASUREMENT====')
        utc = datetime.datetime.utcnow()
        ts = utc.strftime('%Y%m%d%H%M%S')
        self.mix.set_loatt(att=90, ch=0)
        self.sg.start_osci(freq=LOrange[0], power=19.0)
        self.load.set_home() # define HOT position
        print('Current position is defined as the HOT position.')
        if os.path.isfile(logpath+'mixerYmap%s.csv'%(ts)) == 0:
            f = open(logpath+'mixerYmap%s.csv'%(ts), 'w')
            writecsv = csv.writer(f)
            writecsv.writerow(['#UTC', 'LO[GHz]', 'Vmix[mV]', 'Imix[uA]', 'HOT[dB]', 'COLD[dBm]'])
            f.close()
        else:
            pass
        cnt = 1
        Lo_list = numpy.arange(LOrange[0], LOrange[1], LOres)
        for lo in Lo_list:
            self.sg.change_freq(freq=lo)
            lf = self.sg.query_status
            V_list = numpy.arange(Vrange[0], Vrange[1], Vres)
            for v in V_list:
                self.mix.set_sisv(Vmix=v, ch=DAch)
                time.sleep(1.0)
                Vmon = self.mix.monitor_sis()
                Vmon = Vmon[VADch]*1e+1
                I_list = numpy.arange(Irange[0], Irange[1], Ires)
                for i in I_list:
                    self.mix.set_loatt(att=i, ch=LOatt)
                    time.sleep(1.0)
                    Imon = self.mix.monitor_sis()
                    Imon = Imon[IADch]*1e+3
                    t = datetime.datetime.utcnow()
                    dt = t.strftime('%Y-%m-%d-%H-%M-%S')
                    Phot = self.pm.measure(ch=1, resolution=3)
                    self.load.rot_angle(speed=3000, angle=-90) # COLD
                    time.sleep(0.5)
                    Pcold = self.pm.measure(ch=1, resolution=3)
                    self.load.go_home(speed=3000) # HOT
                    print('********************')
                    print('LO freq = '+str(lf[0])+' GHz')
                    print('Mixer bias = '+str(v)+' mV')
                    print('LO att = '+str(i)+' %')
                    print(str(int(cnt))+'/'+str(int(len(Lo_list)*len(V_list)*len(I_list))))
                    print('********************')
                    f = open(logpath+'mixerYmap%s.csv'%(ts), 'a')
                    writecsv = csv.writer(f)
                    writecsv.writerow([dt, lf[0], Vmon, Imon, Phot, Pcold])
                    f.close()
                    cnt = cnt + 1
        self.mix.set_loatt(att=90, ch=0)
        self.sg.end_osci()
        print('====END MEASUREMENT====')
        return


#written by K.Urushihara
