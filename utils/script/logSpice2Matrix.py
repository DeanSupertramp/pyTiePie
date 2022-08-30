#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 13 14:48:08 2022

@author: alecce
"""
import pandas as pd

# path = "/home/alecce/Scrivania/Test_TiePie/repo/pyTiePie/utils/Spice_Circuit/RC_Difference_LTSpice.log"
# path = "C:/Users/andry/Desktop/Alecce/repo/pyTiePie/utils/Spice_Circuit/RC_Difference_LTSpice.log"
path = "C:/Users/andry/Desktop/pyTiePie/utils/Spice_Circuit/RC_Difference_LTSpice.log"
lunghezza = 100

def getMatrix():
    try:
        with open(path) as file:
            lines = file.readlines()
           # lines = [line.rstrip() for line in lines]
        for l in range(len(lines)):
            if lines[l].find("vdiff") != -1:
                index = l
        df_list = []
        for l in range(index+2,index+102):
            df = pd.DataFrame([lines[l].split('\t')])
            df_list.append(df)
        final_df = pd.concat(df_list)
        new=final_df[1].values.reshape(10,10).T
        file.close()
        return new
    except:
        print("errore apertura log Spice")

if __name__ == '__main__':
    matrice = getMatrix()
    
