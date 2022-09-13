# -*- coding: utf-8 -*-
"""
Created on Thu Aug 18 16:25:32 2022

@author: mzy
"""

'''
https://blog.csdn.net/weixin_38442390/article/details/121804647

每一类武器有多个的情况，如每类武器的数量为2

'''

import pandas as pd
import numpy as np
from gurobipy import *
import copy

#原始数据
data=pd.read_table('data/5_3.txt',header=None)
m=int(data.iloc[0,0])
weapon_num=[2 for i in range(m)]
n=int(data.iloc[1,0])
v=[float(item) for item in data.iloc[2,0].split('   ')]
p=[[float(item[j]) for j in range(len(item))] for item in [item.split(' ') for item in data.iloc[3:,0].values]]

#中间数据
bits=[]
def next_bit(bit):
    for i in range(m):
        if bit[i]==weapon_num[i]:
            continue
        bit[i]+=1
        for j in range(i):
            bit[j]=0
        break
    return bit

def get_destroy(j,bit):
    survive=1
    for i in range(len(bit)):
        survive*=pow(1-p[i][j],bit[i])
    return v[j]*(1-survive)

S=np.prod([i+1 for i in weapon_num])
bit=[0 for i in range(m)]
bits=[bit]
while bit!=next_bit(copy.deepcopy(bit)):
    bit=next_bit(copy.deepcopy(bit))
    bits.append(bit)

#模型
model=Model('WTA')

#变量
y=model.addVars([(j,s) for j in range(n) for s in range(S)],\
                obj=[get_destroy(j,bits[s]) for j in range(n) for s in range(S)],vtype='B',name='y')

#目标
model.setAttr(GRB.Attr.ModelSense,-1)

#约束
#(1)对每个目标j，只有一个状态
model.addConstrs((quicksum(y[j,s] for s in range(S))==1 for j in range(n)),name='state constraint')
#(2)对每个武器i，只能分配给一个目标
model.addConstrs((quicksum(quicksum(y[j,s]*bits[s][i] for j in range(n))\
                          for s in range(S))<=weapon_num[i] for i in range(m)),name='assign constraint')
#求解
model.setParam(GRB.Param.OutputFlag,0)
model.optimize()

#输出
print('毁伤值为{}'.format(model.objVal))
for j in range(n):
    for s in range(S):
        if y[j,s].x:
            weapon=[]
            for i in range(len(bits[s])):
                if bits[s][i]:
                    print('武器{}分配给目标{}的数量为{}'.format(i+1,j+1,bits[s][i]))