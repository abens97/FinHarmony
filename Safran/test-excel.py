# -*- coding: utf-8 -*-
"""
Created on Fri May  7 14:33:31 2021

@author: Rapha
"""
import pandas as pd


df =pd.read_html("gleif-annual-report-2018-viewer.xhtml")
print (df)