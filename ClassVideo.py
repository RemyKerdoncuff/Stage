import numpy as np
import matplotlib.pyplot as plt
import sys
import scipy
import cv2 
import torch
import statistics
from statistics import mean
import json
import time
import ipywidgets
from ipywidgets import interact 
import seaborn
import glob
import subprocess
import string
import datetime
import os.path

class Video:

    def __init__(self, path):
        self.res=[]
        self.pic=[]
        self.bpm=0
        self.sec=0
        self.date=0
        self.data=[]
        self.tempsVideo=10
        self.fichierVideo=path
        fname = 'AnyTrack-HRM.db'
        print(self.fichierVideo)
        self.setRes()
        self.setFps()
        
        if("Ceinture" in path):
            self.d = str(os.path.getctime(path)*1000)
            self.createFile()
            self.data = self.load(fname)
        else:
            self.fichierText=self.fichierVideo.replace('.mp4','.txt')
            self.fichierTextEntre=self.fichierVideo.replace('.mp4','Entre.txt')
            self.setPic()
            self.setBPM()

    def hauteurn(self, index):
        a=int(len(self.res)/32)
        x=0
        for i in range (a):
            if((index-1-i)>0):
                if(self.res[index-1-i]>x):
                    x=self.res[index-1-i]
        return x;

    def hauteurp(self, index):
        a=int(len(self.res)/32)
        x=0
        for i in range (a):
            if((index+1+i)<len(self.res)):
                if(self.res[index+1+i]>x):
                    x=self.res[index+1+i]
        return x;
    
    def setRes(self):
        self.cap = cv2.VideoCapture(self.fichierVideo)
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        b=0
        while(self.cap.isOpened()):
            b=b+1
            ret, frame = self.cap.read()
            if (b>self.tempsVideo*self.fps): break
            self.res.append(frame[:,:,2].mean())
    
    def getRes(self):
        plt.plot(np.array(self.res)[20:30])
        plt.show()
    
    def setFps(self):
        self.cap = cv2.VideoCapture(self.fichierVideo)
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)

    def getFps(self):
        print(self.fps)
        
    def setPic(self):
        a=-20
        del self.pic[0 : len(self.pic)] 
        for i in range (len(self.res)):
            if(self.res[i]>self.hauteurn(i) and 
               self.res[i]>self.hauteurp(i) and 
               i-a>len(self.res)/32):
                a=i
                self.pic.append(i)
        print(self.pic)
                
    def getPic(self):
        print(self.pic)
        
    def setBPM(self):
        self.bpm=1/((np.mean(np.diff(self.pic))/self.fps))*60
        
    def getBPM(self):
        print(self.fps)
    
    def writeOutput(self):
        tab=self.putPicOnFrame()
        str1 = ''
        for i in range (len(tab)):
            if(i==len(tab)-1):
                str1=str1+str((int(tab[i])))
            else:
                str1=str1+str((int(tab[i])))+"\r"
        print(str1)
        f = open(self.fichierText,'w')
        f.write(str1) #"Battements sur 10 seconde:\r"+"bpm ="+str(bpm)
        
    def putPicOnFrame(self):
        tab = []
        j=0
        print(len(self.pic))
        for i in range(len(self.res)):
            if(int(self.pic[j])==i):
                tab.append(1)
                self.pic[j]
                if(len(self.pic)>j+1):
                    j=j+1
            else:
                tab.append(0)
                
        print(tab)
        return tab
    
    def Input(self):
        str2 = ''
        for i in range (len(self.res)):
            if(i==len(self.res)-1):
                str2=str2+(str)(self.res[i])
            else:
                str2=str2+(str)(self.res[i])+"\r"
        print(str2)
        f1 = open(self.fichierTextEntre,'w')
        f1.write(str2)
        
    def createFile(self):
        if ("1" in self.fichierVideo):
            print("Non")
        #else:
         #   a=self.fichierVideo.replace('.mp4', str(self.d)+'.mp4')
         #   os.rename(self.fichierVideo,str(a))
         #   self.fichierText=a
        self.fichierText=self.fichierVideo.replace('.mp4','.txt')
        self.fichierTextEntre=self.fichierVideo.replace('.mp4','Entre.txt')
    
    def battementCeinture(self, beg, end):
        moy = (beg+end)/2
        picCeinture=[]
        i=len(self.data)-1
        while i > 0:
            if(self.data[i,1]== ""):
                i=i-1
            elif("/" in self.data[i,1]):
                x=self.data[i,1].split("/")
                for j in range (len(x)):
                    moy=moy-int(x[j])
                    picCeinture.append(float(moy)-float(self.d))
                i=i-1
            else:
                moy = moy-float(self.data[i,1])
                picCeinture.append(float(moy)-float(self.d))
                i = i-1   
        picCeinture.reverse()
        taux=10000/(self.tempsVideo*self.fps)
        indice=0
        for j in range(10000):
            if(int(picCeinture[indice])<0):
                picCeinture.pop(indice)
            if(int(picCeinture[indice])==j):
                a=0
                a=picCeinture[indice]/taux
                self.pic.append(a)
                if(len(picCeinture)-1>indice):
                    indice=indice+1
     
    def calibrage(self):
        h=len(self.data)
        beg=self.data[0,0]
        end=self.data[1,0]
        for i in range (1,h-1):
            if(self.data[i,1]== ""):
                pass
            elif("/" in self.data[i,1]):
                x=self.data[i,1].split("/")
                for j in range (len(x)):
                    beg = max(int(self.data[i,0]), int(beg)+int(x[j]))
                    end = min(int(self.data[i+1,0]), int(end)+int(x[j]))
            else:
                beg = max(int(self.data[i,0]), int(beg)+int(self.data[i,1]))
                end = min(int(self.data[i+1,0]), int(end)+int(self.data[i,1]))     
        self.battementCeinture(beg, end)
    
    def load(self, fname):
        allValues = []
        false = False
        true = True
        def HRMSample(ts, bpm, status, hummm, has_hrm, intrarr):
            allValues.append([ts, intrarr])
        with open(fname, 'r') as f:
            for l in f.readlines():
                eval(l[:-1])    
        allValues = np.array(allValues)
        for i in range (len(allValues)):
            if(allValues[i,0]>self.d and len(self.data)<11):
                self.data.append(allValues[i])
        self.data=np.array(self.data)
        self.calibrage()
        
    def affichePlot(self):
        plt.plot(np.array(self.res))
        for i in range(len(self.pic)):
            print(int(self.pic[i]))
            print(self.res[int(self.pic[i])])
            plt.plot([int(self.pic[i])],[self.res[int(self.pic[i])]], 'go--', linewidth=2, markersize=12)
        plt.show()
    

    #def dateToTime(self):
    #    self.sec = datetime.datetime.strptime('20190502 11:30:00', '%Y%m%d %H:%M:%S')           
    #    self.sec.timestamp()
    #def findTime(self):
    #def timeToDate(self):
    #    d = os.path.getctime(self.fichierVideo)
    #    self.date = datetime.datetime.fromtimestamp(d)           
    #    self.date.timestamp()
    #    print(self.date)
        
#fichierVideo=glob.glob('BD\*.mp4')
#q=Video("BD\Annulaire3.mp4")
#q.writeOutput()
#q.Input()

fichierVideo=glob.glob('BD\*.mp4')
for i in range(len(fichierVideo)):
     q = Video(fichierVideo[i])
     q.writeOutput()
     q.Input()