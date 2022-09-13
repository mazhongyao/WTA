# -*- coding: utf-8 -*-
"""
Created on Thu Aug 18 11:52:59 2022

@author: mzy
"""

'''
https://blog.csdn.net/weixin_38442390/article/details/121804647

每一类武器有单个的情况

'''
import pandas as pd
from gurobipy import *
import random
import copy

# 数据处理
data=pd.read_table('data/5_3.txt',header=None)
m=int(data.iloc[0,0])
n=int(data.iloc[1,0])
v=[float(item) for item in data.iloc[2,0].split('   ')]
p=[[float(item[j]) for j in range(len(item))] for item in [item.split(' ') for item in data.iloc[3:,0].values]]

# 生成所有可能的分配状态
def enumeration(m,n,b,bits):
    if len(b)==m:
        bits.append(copy.deepcopy(b))
        return
    for i in range(2):
        b.append(i)
        enumeration(m,n,b,bits)
        b.pop()
def get_bit(m,n):
    b=[]
    bits=[]
    enumeration(m,n,b,bits)
    return bits

def get_destroy(j,bit):
    survive=v[j]
    for i in range(len(bit)):
        if bit[i]==0:continue
        survive*=(1-p[i][j])
    return v[j]-survive
    
bits=get_bit(m,n)

# 模型
model=Model('WTA')

# 变量
y=model.addVars([(j,s) for j in range(n) for s in range(2**m)],name='y')

#目标函数
model.setObjective(quicksum(quicksum(get_destroy(j,bits[s])*y[j,s] for s in range(2**m))\
                            for j in range(n)),GRB.MAXIMIZE)

#约束
#(1)对每个目标j，只有一个状态
model.addConstrs(((quicksum(y[j,s] for s in range(2**m))==1) for j in range(n)),name='state constraint')
#(2)对每个武器i，只能分配给一个目标
model.addConstrs(((quicksum(quicksum(y[j,s]*bits[s][i] for j in range(n)) for s in range(2**m))<=1)\
                  for i in range(m)),name='assign constraint')

#求解
model.params.OutputFlag=0
model.optimize()

#输出
print('Obj={}'.format(model.objVal))
for j in range(n):
    for s in range(2**m):
        if y[j,s].x:
            weapon=[]
            for i in range(len(bits[s])):
                if bits[s][i]:
                    weapon.append(i+1)
            print('weapon {} assigned to target [{}]'.format(weapon,j+1))