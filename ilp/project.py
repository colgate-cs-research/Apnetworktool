#!/usr/bin/env python3
import json
import math
import random
from gurobipy import *
import randomgen as ran

class link(object):
    """docstring for ."""

    def __init__(self, n1, n2, capacity):
        super(link, self).__init__()
        self.n1 = n1
        self.n2 = n2
        self.capacity = capacity

class flow(object):
    """docstring for ."""

    def __init__(self, src, dst, demand, id):
        super(flow, self).__init__()
        self.src = src
        self.dst = dst
        self.demand = demand
        self.id = id

def find_id(flows,id):
    for flow in flows:
        if flow.id == id:
            return flow
    return None

def find_link(Links, r1, r2):
    for link in Links:
        if (link.n1 == r1 and link.n2 == r2) or (link.n2 == r1 and link.n1 == r2):
            return link
    return None

def generateflow(data, Flow, Wired_id, Wireless_id):
    id = 0
    for i in range(5):
        id += 1
        source      = data["Nodes"]["Router"][random.randint(0,len(data["Nodes"]["Router"])-1)]
        destination = data["Nodes"]["Router"][random.randint(0,len(data["Nodes"]["Router"])-1)]
        while (source == destination):
            source      = data["Nodes"]["Router"][random.randint(0,len(data["Nodes"]["Router"])-1)]
            destination = data["Nodes"]["Router"][random.randint(0,len(data["Nodes"]["Router"])-1)]
        demand = random.randint(0,10)
        temp_flow = flow(source, destination, demand,id)
        Flow.append(temp_flow)
        Wired_id.append(id)
    for i in range(5):
        id += 1
        source      = data["Nodes"]["Client"][random.randint(0,len(data["Nodes"]["Client"])-1)]
        destination = data["Nodes"]["Router"][random.randint(0,len(data["Nodes"]["Router"])-1)]
        demand = random.randint(0,10)
        temp_flow = flow(source, destination, demand, id)
        Flow.append(temp_flow)
        Wireless_id.append(id)

def generateclient(data):
    for i in range(10):
        x = random.randint(0, data["max_x"])
        y = random.randint(0, data["max_y"])
        name = "w"+str(i+1)
        data["Nodes"]["Client"].append(name)
        data["Location"][name] = [x,y]


def solve():
    try:
        with open("random.json") as f:
          data = json.load(f)
        AP_Capacity = data["AP_Capacity"]
        x_max = data["max_x"]
        y_max = data["max_y"]
        Router = data["Nodes"]["Router"]
        Ap = data["Nodes"]["Ap"]
        Client = data["Nodes"]["Client"]
        if len(Client) == 0:
            generateclient(data)
            Client = data["Nodes"]["Client"]
        Connect = data["Connect"]
        Controller = data["Controller"]
        Coverage = int(data["AP_Coverage"])
        Links = []
        tuple_links=[]
        Flows = []
        Wired_id = []
        Wireless_id = []
        for i in range(len(data["Link"]["node1"])):
            temp_link = link(data["Link"]["node1"][i],data["Link"]["node2"][i],data["Link"]["capacity"][i])
            Links.append(temp_link)
            tuple_links.append((data["Link"]["node1"][i],data["Link"]["node2"][i]))
            tuple_links.append((data["Link"]["node2"][i],data["Link"]["node1"][i]))
        for ap in data["Connect"]:
            temp_link = link(ap, data["Connect"][ap], AP_Capacity)
            Links.append(temp_link)
            if ((ap, data["Connect"][ap]) not in tuple_links):
                tuple_links.append((ap, data["Connect"][ap]))
                tuple_links.append((data["Connect"][ap], ap))
        id = 0
        if (not len(data["Flow"]["source"])==0):
            for i in range(len(data["Flow"]["source"])):
                temp_flow = flow(data["Flow"]["source"][i],data["Flow"]["destination"][i],data["Flow"]["demand"][i],id)
                Flows.append(temp_flow)
                if (data["Flow"]["source"][i] in Router):
                    Wired_id.append(id)
                else:
                    Wireless_id.append(id)
                id += 1
        else:
            generateflow(data, Flows, Wired_id, Wireless_id)

        Location_tuple = []
        Range = {}
        for ap in Ap:
            x_max = int(data["Location"][ap][0])+Coverage
            x_min = int(data["Location"][ap][0])-Coverage
            y_max = int(data["Location"][ap][1])+Coverage
            y_min = int(data["Location"][ap][1])-Coverage
            for client in Client:
                # if  (int(data["Location"][client][0])<int(data["Location"][ap][0])+int(data["AP_Coverage"]) or int(data["Location"][client][0])>int(data["Location"][ap][0])-int(data["AP_Coverage"])) and (int(data["Location"][client][1])<int(data["Location"][ap][1])+int(data["AP_Coverage"]) or int(data["Location"][client][1])>int(data["Location"][ap][1])-int(data["AP_Coverage"])):
                x = int(data["Location"][client][0])
                y = int(data["Location"][client][1])
                if (x<x_max and x>x_min) and (y>y_min and y<y_max):
                    Range[(ap, client)] = 1
                    Location_tuple.append((client,ap))
                else:
                    Range[(ap,client)] = 0
        # for ap in data["range"]:
        #     for client in data["range"][ap]:
        #         Range[(ap, client)] = 1
        #         Location_tuple.append((client,ap))

        # for ap in Ap:
        #     for client in Client:
        #         if (ap, client) not in Range:
        #             Range[(ap,client)] = 0
        m = Model("mip1")

        Links_set = gurobipy.tuplelist(tuple_links)
        Location_set = gurobipy.tuplelist(Location_tuple)

        H = m.addVars(Location_set, vtype= gurobipy.GRB.BINARY, name="Assign")
        O = m.addVars(Ap, vtype=gurobipy.GRB.BINARY, name="AP on")
        flow_d = m.addVars(Wired_id, Links_set, vtype=gurobipy.GRB.INTEGER, name="wired flow on")
        flow_1d = m.addVars(Wireless_id, Links_set, vtype=gurobipy.GRB.INTEGER, name="wireless flow to controller on")
        flow_2d = m.addVars(Wireless_id, Links_set, vtype=gurobipy.GRB.INTEGER, name="wireless flow to destination on")
        L = m.addVars(Links_set, vtype=gurobipy.GRB.BINARY, name="Link is on or off")
        m.update()

        m.setObjectiveN(gurobipy.quicksum(O[i] for i in Ap), index=0, weight = 5)
        # m.setObjectiveN(gurobipy.quicksum(flow_d[wired,r1,r2] for wired in Wired_id for r1,r2 in Links_set)+
        #                 gurobipy.quicksum(flow_1d[wireless,r1,r2]+flow_2d[wireless,r1,r2] for wireless in Wireless_id for r1,r2 in Links_set)
        #                 , index =1, weight = 2)
        m.setObjectiveN(gurobipy.quicksum(L[r1,r2]*find_link(Links,r1,r2).capacity for r1,r2 in Links_set), index = 1, weight =1)

        for wireless in Wireless_id:
            src = find_id(Flows,wireless).src
            dst = find_id(Flows,wireless).dst
            demand = find_id(Flows,wireless).demand
            m.addConstr(gurobipy.quicksum(H[src,i] for i in Ap if (src, i) in Location_set) == 1)
            m.addConstr(gurobipy.quicksum(H[src,i]*O[i] for i in Ap if (src, i) in Location_set) == 1)
            m.addConstr(gurobipy.quicksum(H[src,i]*flow_1d[wireless,i,Connect[i]] for i in Ap if (i,Connect[i]) in Links_set and (src,i) in Location_set) == demand)
            m.addConstr(gurobipy.quicksum(H[src,i]*flow_1d[wireless,Connect[i],r1] for i in Ap for r1 in    Router if (src, i) in Location_set and (Connect[i],r1) in Links_set) == demand)
            m.addConstr(gurobipy.quicksum(flow_1d[wireless,r1,Controller] for r1 in Router if (r1, Controller) in Links_set) == demand)
            m.addConstr(gurobipy.quicksum(flow_2d[wireless,Controller,r1] for r1 in Router if (Controller, r1) in Links_set) == demand)
            m.addConstr(gurobipy.quicksum(flow_2d[wireless,r1,dst] for r1 in Router if (r1, dst) in Links_set) == demand)
            for r1 in Router:
               m.addConstr(gurobipy.quicksum(flow_1d[wireless, r1, r2] for r2 in Router if (r1,r2) in Links_set and not (r1 == Controller))==
                            gurobipy.quicksum(flow_1d[wireless, r2, r1] for r2 in (Router+Ap) if (r2,r1) in Links_set and not (r1 == Controller)))
               m.addConstr(gurobipy.quicksum(flow_2d[wireless, r1, r2] for r2 in Router if (r1,r2) in Links_set and not (r1 == Controller or r1 == dst))==
                            gurobipy.quicksum(flow_2d[wireless, r2, r1] for r2 in Router if (r2,r1) in Links_set and not (r1 == Controller or r1 == dst)))
            #m.addConstr(gurobipy.quicksum(flow_1d[wireless,r1,r2]-flow_1d[wireless,r2,r1] for r1,r2 in Router if (r1,r2) in Links_set and not r2 == Controller)==0)
            #m.addConstr(gurobipy.quicksum(flow_2d[wireless,r1,r2]-flow_2d[wireless,r2,r1] for r1,r2 in Router if (r1,r2) in Links_set and not(r1== Controller or r1== dst) and not(r2== Controller or r2== dst))==0)
        for client in Client:
            m.addConstr(gurobipy.quicksum(Range[i,client]*O[i] for i in Ap)>=1)
        for ap in Ap:
            m.addConstr(gurobipy.quicksum(O[ap]*H[find_id(Flows,f).src,ap]*find_id(Flows,f).demand for f in Wireless_id if (find_id(Flows,f).src,ap) in Location_set)<= AP_Capacity)
        for ap in Connect:
            m.addConstr(gurobipy.quicksum(O[ap]*H[find_id(Flows,f).src,ap]*find_id(Flows,f).demand for f in Wireless_id if (find_id(Flows,f).src,ap) in Location_set)<= find_link(Links,ap,Connect[ap]).capacity)
        for wired in Wired_id:
            src = find_id(Flows,wired).src
            dst = find_id(Flows,wired).dst
            demand = find_id(Flows,wired).demand
            m.addConstr(gurobipy.quicksum(flow_d[wired, src, r2] for r2 in Router if (src, r2) in Links_set) == demand)
            m.addConstr(gurobipy.quicksum(flow_d[wired, r1, dst] for r1 in Router if (r1, dst) in Links_set) == demand)
            for r1 in Router:
                m.addConstr(gurobipy.quicksum(flow_d[wired, r1, r2] for r2 in Router if (r1,r2) in Links_set and not (r1 == src or r1 == dst))==
                            gurobipy.quicksum(flow_d[wired, r2, r1] for r2 in Router if (r2,r1) in Links_set and not (r1 == src or r1 == dst)))

        for r1 in (Ap+Router):
            for r2 in (Ap+Router):
                if (r1,r2) in (Links_set):
                    m.addConstr(gurobipy.quicksum(flow_d[num, r1, r2]+flow_d[num, r2, r1] for num in Wired_id if (r1,r2) in Links_set)+
                                gurobipy.quicksum(flow_1d[num, r1, r2] + flow_1d[num, r2,r1] + flow_2d[num, r1, r2] + flow_2d[num, r2,r1] for num in Wireless_id if (r1,r2) in Links_set) <= L[r1,r2]*find_link(Links, r1, r2).capacity)
                    # print(r1,r2,gurobipy.quicksum(flow_d[num, r1, r2]+flow_d[num, r2, r1] for num in Wired_id)+
                    #             gurobipy.quicksum(flow_1d[num, r1, r2] + flow_1d[num, r2,r1] + flow_2d[num, r1, r2] + flow_2d[num, r2,r1]))
        m.Params.TimeLimit = 2000
        m.optimize()

        with open("result.txt","a") as outfile:
            for v in m.getVars():
                line = v.varName +str(v.x)+"\n"
                outfile.write(line)
        print('Obj:', m.objVal)
        with open("result.txt","a") as outfile:
            outfile.write('Obj'+str(m.objVal)+"\n")
        with open("time.txt", "a") as outfile:
            outfile.write("Running time: "+ str(m.Runtime)+"\n")
        return True

    except (AttributeError, GurobiError, Exception):
        return False

def main():
   with open("result.txt", "w") as outfile:
       outfile.write("Begin \n")
   with open("time.txt", "w") as outfile:
       outfile.write("Begin \n")
   for i in range(3,5):s
       num_ap = i*i
       for j in range(1,3):
           num_client = j*5
           size = 100
           for k in range(1,3):
               num_nodes = k*5
               for m in range(1,3):
                   num_wflow = m*5
                   num_flow = m*5
                   ran.generate(num_ap, num_client, size, num_nodes, num_wflow, num_flow, 100, 100, 25)
                   line = " ".join([str(num_ap), str(num_client), str(size), str(num_nodes), str(num_wflow), str(num_flow), "100", "100", "25"])+"\n"
                   with open("result.txt", "a") as outfile:
                       outfile.write(line)
#                    print(solve())
                   while (not solve()):
                       ran.generate(num_ap, num_client, size, num_nodes, num_wflow, num_flow, 100, 100, 25)
                       print("regenerate")
   print("AP")
   for i in range(3,21):
       num_ap = i*i
       for n in range (10):
           with open("time.txt" ,"a") as outfile:
               outfile.write("Ap "+ str(num_ap)+", 30, 100, 20, 50, 50, 1000, 100, 25 \n")
           ran.generate(num_ap, 30, 100, 20, 50, 50, 1000, 100, 25)
           while (not solve()):
               ran.generate(num_ap, 30, 100, 20, 50, 50, 1000, 100, 25)
   print("Num_client")
   for i in range (1,11):
       num_client = i* 10
       for n in range(10):
           with open("time.txt" ,"a") as outfile:
               outfile.write("Client 16, "+ str(num_client)+", 100, 20, 50, 50, 1000, 100, 25 \n")
           ran.generate(16, num_client, 100, 20, 50, 50, 1000, 100, 25)
           while (not solve()):
               ran.generate(16, num_client, 100, 10, 50, 50, 1000, 100, 25)
    print("Num_nodes")
    for i in range(1,7):
        num_nodes = i*5
        for n in range(10):
            with open("time.txt", "a") as outfile:
                outfile.write("Nodes 16, 30, 100, "+ str(num_nodes)+ ", 50, 50, 1000, 100, 25\n")
            ran.generate(16,30, 100, num_nodes, 50,50,1000,100,25)
            while (not solve()):
                ran.generate(16,30, 100, num_nodes, 50,50,1000,100,25)
    print("Flow")
    for i in range(1,21):
        num_flow = i*10
        for n in range(10):
            with open("time.txt", "a") as outfile:
                outfile.write("Demand 16, 30, 100, 10, "+ str(num_flow)+", "+ str(num_flow)+", 1000, 100, 25\n")
            ran.generate(16,30,100,10,num_flow, num_flow , 1000, 100, 25)
            while (not (solve())):
                ran.generate(16,30,100,10,num_flow, num_flow , 1000, 100, 25)
    print("finish")


main()
