#!/usr/bin/env python3
import json
import math
import random

def generatenodes(data,num_nodes,num_ap):
    for i in range(num_nodes):
        name = "r"+str(i+1)
        data["Nodes"]["Router"].append(name)

    chunk = int(math.sqrt(num_ap))
    # print(data["max_x"]//chunk)
    check = {}
    for i in range(chunk):
        for j in range(chunk):
            check[(i,j)] = 0

    for i in range(num_ap):
        name = "a"+str(i+1)
        x = random.randint(0, data["max_x"]-1)
        y = random.randint(0, data["max_y"]-1)
        if (x == data["max_x"]-1):
            i = (x-1)//(data["max_x"]//chunk)
        else:
            i = x//(data["max_x"]//chunk)
        if (y == data["max_y"]-1):
            j = (y-1)//(data["max_y"]//chunk)
        else:
            j = y//(data["max_y"]//chunk)
        if i == chunk:
            i = i-1
        if j == chunk:
            j = j-1
        while (check[(i,j)]!=0):
            x = random.randint(0, data["max_x"]-1)
            y = random.randint(0, data["max_y"]-1)
            if (x == data["max_x"]-1):
                i = (x-1)//(data["max_x"]//chunk)
            else:
                i = x//(data["max_x"]//chunk)
            if (y == data["max_y"]-1):
                j = (y-1)//(data["max_y"]//chunk)
            else:
                j = y//(data["max_y"]//chunk)
            if i == chunk:
                i = i-1
            if j == chunk:
                j = j-1
        data["Nodes"]["Ap"].append(name)
        data["Location"][name]=[x,y]
        check[(i,j)] = name
    return check

def generateclient(data, num_client):
    for i in range(num_client):
        x = random.randint(0, data["max_x"]-1)
        y = random.randint(0, data["max_y"]-1)
        name = "w"+str(i+1)
        data["Nodes"]["Client"].append(name)
        data["Location"][name] = [x,y]

def generateflow(data, num_flow, num_wflow):
    id = 0
    for i in range(num_flow):
        source      = data["Nodes"]["Router"][random.randint(0,len(data["Nodes"]["Router"])-1)]
        destination = data["Nodes"]["Router"][random.randint(0,len(data["Nodes"]["Router"])-1)]
        while (source == destination):
            source      = data["Nodes"]["Router"][random.randint(0,len(data["Nodes"]["Router"])-1)]
            destination = data["Nodes"]["Router"][random.randint(0,len(data["Nodes"]["Router"])-1)]
        demand = random.randint(0,10)+1
        data["Flow"]["source"].append(source)
        data["Flow"]["destination"].append(destination)
        data["Flow"]["demand"].append(demand)
    for i in range(num_wflow):
        id += 1
        source      = data["Nodes"]["Client"][random.randint(0,len(data["Nodes"]["Client"])-1)]
        destination = data["Nodes"]["Router"][random.randint(0,len(data["Nodes"]["Router"])-1)]
        demand = random.randint(0,10)
        data["Flow"]["source"].append(source)
        data["Flow"]["destination"].append(destination)
        data["Flow"]["demand"].append(demand)

def generatetopology(data,link_cap, check):
    for i in range(5):
        node1 = data["Nodes"]["Router"][random.randint(0,len(data["Nodes"]["Router"])-1)]
        node2 = data["Nodes"]["Router"][random.randint(0,len(data["Nodes"]["Router"])-1)]
        while (node1 == node2 or (node1,node2) in check):
            node1 = data["Nodes"]["Router"][random.randint(0,len(data["Nodes"]["Router"])-1)]
            node2 = data["Nodes"]["Router"][random.randint(0,len(data["Nodes"]["Router"])-1)]
        data["Link"]["node1"].append(node1)
        data["Link"]["node2"].append(node2)
        data["Link"]["capacity"].append(link_cap)
        check.append((node1,node2))
        check.append((node2,node1))

def dfs(visited, graph, node):
    if node not in visited:
        visited.append(node)
        for neighbor in graph[node]:
            dfs(visited, graph, neighbor)

def checktopology(data):
    graph={}
    visited=[]
    for i in range(len(data["Link"]["node1"])):
        node1 = data["Link"]["node1"][i]
        node2 = data["Link"]["node2"][i]
        if node1 not in graph:
            graph[node1] = [node2]
        else:
            graph[node1].append(node2)
        if node2 not in graph:
            graph[node2]=[node1]
        else:
            graph[node2].append(node1)
    dfs(visited, graph, data["Link"]["node1"][0])
    return (len(visited) == len(data["Nodes"]["Router"]))

def generateconnect(data,check,num_ap):
    chunk = math.sqrt(num_ap)
    # if chunk % 2 == 0:
    #     left = check[(int((chunk-1)//2),int((chunk-1)//2))]
    #     right = check[(int((chunk-1)//2)+1,int((chunk-1)//2)+1)]
    # else:
    #     left = check[(int((chunk-1)//2)-1, int((chunk-1)//2))]
    #     right = check[(int((chunk+1)//2), int((chunk-1)//2))]
    # print(left, right)
    for i in range(num_ap):
        name = "a"+str(i+1)
        if data["Location"][name][0] < int(data["max_x"]//2):
            data["Connect"][name] = "r2"
        else:
            data["Connect"][name] = "r3"

def generate(num_ap, num_client, size, num_nodes, num_wflow, num_flow, link_cap, ap_cap, ap_cov):
#    num_ap=num_ap
#    num_client=num_client
#    size=size
#    num_nodes=num_nodes
#    num_wflow=num_wflow
#    num_flow=num_flow
#    link_cap = link_cap
#    ap_cap = ap_cap
#    ap_cov = ap_cov

    data={}
    data["max_x"] = size
    data["max_y"] = size
    data["AP_Capacity"] = ap_cap
    data["AP_Coverage"] = ap_cov
    data["Nodes"] = {}
    data["Nodes"]["Router"]=[]
    data["Nodes"]["Ap"]=[]
    data["Nodes"]["Client"]=[]
    data["Controller"]="r1"
    data["Link"]={}
    data["Link"]["node1"]=[]
    data["Link"]["node2"]=[]
    data["Link"]["capacity"]=[]
    data["Connect"]={}
    data["Location"]={}
    data["Flow"]={}
    data["Flow"]["source"]=[]
    data["Flow"]["destination"]=[]
    data["Flow"]["demand"]=[]

    check = generatenodes(data, num_nodes, num_ap)
    generateclient(data,num_client)
    generateflow(data,num_flow,num_wflow)
    check = []
    generatetopology(data,link_cap,check)
    while (not checktopology(data)):
        generatetopology(data,link_cap,check)
    generateconnect(data, check, num_ap)
    with open('random.json', 'w') as outfile:
        json.dump(data, outfile)
