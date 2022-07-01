#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul  1 11:17:28 2022

@author: alecce
"""

import tkinter as tk
from tkinter import filedialog

root = tk.Tk()
root.withdraw()
file_path = filedialog.askopenfilename()

import scipy.io
mat = scipy.io.loadmat(file_path)

f0 = mat['param']['f0'][0][0][0][0]
