# ! /usr/bin/env python
# _*_ coding: UTF-8 _*_


# import modules
import time, sys, datetime, signal, os, csv, numpy
sys.path.append('/home/amigos/NASCORX_System/device/')
import L218
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

class monitor(object):
    '''
    DESCRIPTION
    ================
    This class controls Lake Shore Model 218.

    ARGUMENT
    ================
    1. IP: IP address
        Type: string
    2. GPIB: GPIB port number
        Number: 0 -- 30
        Type: int 
    3. logpath: directry path of the monitoring data.
        Type: string
    '''

    def __init__(self, IP='192.168.101.178', GPIB=1, logpath='/home/amigos/data/'):
        self.IP = IP
        self.GPIB = GPIB
        signal.signal(signal.SIGINT, signal.SIG_DFL)
        self.ls = L218.l218(IP=self.IP, GPIB=self.GPIB)
        utc = datetime.datetime.utcnow()
        self.ts = utc.strftime('%Y%m%d')
        self.logpath = logpath

    def logging(self, interval=5.0):
        '''
        DESCRIPTION
        ================
        This function monitors cryo temperature sensed by Lake Shore Model 218.

        ARGUMENT
        ================
        1. interval: interval time [sec]
            Type: float

        RETURN
        ================
        Nothing.
        '''
        while 1:
            tcheck = datetime.datetime.utcnow()
            check = tcheck.strftime('%Y%m%d')
            if self.ts != check:
                self.ts = check
            if os.path.isfile(self.logpath+'4Kmonitor%s.csv'%(self.ts)) == 0:
                f = open(self.logpath+'4Kmonitor%s.csv'%(self.ts), 'w')
                writecsv = csv.writer(f)
                writecsv.writerow(['#UTC', 'dewar_temp[K]'])
                f.close()
            else:
                temp = []
                for i in [1, 2, 3, 4, 5, 6, 7, 8]:
                    ret = self.ls.measure(ch=i)
                    temp.append(ret)
                dt = datetime.datetime.utcnow()
                ddt = dt.strftime('%Y-%m-%d-%H-%M-%S')
                f = open(self.logpath+'4Kmonitor%s.csv'%(self.ts), 'a')
                writecsv = csv.writer(f)
                writecsv.writerow([ddt, temp[0], temp[1], temp[2], temp[3], temp[4], temp[5], temp[6], temp[7]])
                f.close()
                time.sleep(float(interval))

    def realtime_plot(self, ymin=0, ymax=300, interval=5):
        '''
        DESCRIPTION
        ================
        This function plots cryo temperature in real time.

        ARGUMENT
        ================
        1. ymin: minimum value of the y range.
            Type: float
        2. ymax: maximum value of the y range.
            Type: float
        3. interval: interval time [sec]
            Type: float

        RETURN
        ================
        Nothing.
        '''
        plt.ion()
        fig = plt.figure()
        while 1:
            tcheck = datetime.datetime.utcnow()
            check = tcheck.strftime('%Y%m%d')
            if self.ts != check:
                self.ts = check
            data = numpy.genfromtxt(self.logpath+'4Kmonitor%s.csv'%(self.ts), dtype=None, comments="#", delimiter=",")
            x = []
            y_1 = []
            y_2 = []
            y_3 = []
            y_4 = []
            y_5 = []
            y_6 = []
            y_7 = []
            y_8 = []
            for i in range(len(data)):
                tdatetime = datetime.datetime.strptime(data[i][0], '%Y-%m-%d-%H-%M-%S')
                x.append(tdatetime)
                y_1.append(data[i][1])
                y_2.append(data[i][2])
                y_3.append(data[i][3])
                y_4.append(data[i][4])
                y_5.append(data[i][5])
                y_6.append(data[i][6])
                y_7.append(data[i][7])
                y_8.append(data[i][8])
            ax = fig.add_subplot(1,1,1)
            hours = mdates.AutoDateLocator()
            hoursFmt = mdates.DateFormatter('%H:%M')
            ax.xaxis.set_major_locator(hours)
            ax.xaxis.set_major_formatter(hoursFmt)
            ax.set_title("4K Stage Monitor")
            ax.set_ylim(ymin,ymax)
            ax.set_xlabel('UT')
            ax.set_ylabel('4K stage Temp [K]')
#            ax.grid()
            ax.plot(x,y_1, color='red', marker='.', label='ch1')
            ax.plot(x,y_2, color='orange', marker='.', label='ch2')
            ax.plot(x,y_3, color='yellowgreen', marker='.', label='ch3')
            ax.plot(x,y_4, color='green', marker='.', label='ch4')
            ax.plot(x,y_5, color='cyan', marker='.', label='ch5')
            ax.plot(x,y_6, color='blue', marker='.', label='ch6')
            ax.plot(x,y_7, color='magenta', marker='.', label='ch7')
            ax.plot(x,y_8, color='purple', marker='.', label='ch8')
            ax.legend(loc="upper right")
            plt.draw()
            plt.clf()
            time.sleep(interval)

if __name__ == '__main__':
    import threading
    cl = monitor()
    itv = 10.0
    th_log = threading.Thread(target=cl.logging, args=(itv,))
#    th_log.daemon = True
    th_log.start()
    time.sleep(itv*5)
    cl.realtime_plot(ymin=0, ymax=300, interval=itv*2)

# written by K.Urushihara
## Chaneged by K.Sakasai @20170502 [IP_adress]
