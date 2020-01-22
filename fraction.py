#!/usr/bin/env python3
import os
import csv
import argparse
import operator
import rrdtool
import pygraphviz
import networkx as nx

def main():
    parser = argparse.ArgumentParser(description='Aggregate experiment output')
    parser.add_argument('-c','--containers', dest='path', action='store',
            required=True, help='Path to containers directory')
    parser.add_argument('-m', '--csvpath', dest='mappingfile_path', action='store',
            required=True, help='Path to mapping file')
    parser.add_argument('-i', '--idpath', dest='idfile_path', action='store',
            required=True, help='Path to id file')
    parser.add_argument('-g','--graphpath', dest='graphfile_path', action='store',
            required=True, help='Path to graph file')
    parser.add_argument('-s', '--start', dest='start', action='store')
    parser.add_argument('-t', '--type', dest='type', action='store')
    args = parser.parse_args()
    switches = procescsv(args.idfile_path, args.mappingfile_path)

    apports = processrrd(args.path, switches)

    nodes = {}
    graph_path = os.path.join(args.graphfile_path, "graph.csv")
    graphfile = open(graph_path, "r")
    graph_csv = csv.reader(graphfile)
    for row in graph_csv:
        if ("Node" not in row[0]):
            i = 0
            while (i < len(row)):
                if (i == 0):
                    nodes[row[0]] = Node(row[0])
                    i = i+1
                else:
                    nodes[row[0]].add_remote(remotenode(row[i], row[i+1], row[i+2]))
                    i = i + 3
    # ## TODO: Using NetworkX to build this graaph
    # G = nx.DiGraph()
    # for node in nodes:
    #     for rnode in nodes[node].remote:
    #         if (G.has_edge(nodes[node].hostname,rnode.hostname)):
    #             G.add_edge(rnode.hostname, nodes[node].hostname)
    #
    #         else:
    #             label = '%s:%s' % (rnode.localinterface,rnode.remoteinterface)
    #             G.add_edge(nodes[node].hostname,rnode.hostname, label = label)

    target_hosts = ["casecloset-4507", "ho-4507", "colgate6807-vss"]
    results_id = []
    for local_node in nodes:
        for remote_node in nodes[local_node].remote:
            if remote_node.hostname in target_hosts:
                results_id.append(switches[nodes[local_node].hostname].getid(remote_node.localinterface))
    uplink = processuplink(args.path, results_id)

    end_str = os.path.basename(args.path).split('-')
    name_str = '_'.join(end_str[0:3]) + end_str[3]+":00"
    end_str = '/'.join(end_str[0:3]) + " " + end_str[3]+":00"
    datainfilepath = os.path.join(args.mappingfile_path, name_str+" datain.csv")
    dataoutfilepath = os.path.join(args.mappingfile_path, name_str+" dataout.csv")
    wirelessin = getwireless(apports, args.path, "in")
    wirelessout = getwireless(apports, args.path, "out")
    uplinkin = getwireless(uplink, args.path, "in")
    uplinkout = getwireless(uplink, args.path, "out")
    wirelessintotal, wirelessouttotal, uplinkintotal, uplinkouttotal, infraction, outfraction = calculate(wirelessin, wirelessout, uplinkin, uplinkout)
    datainfile = open(datainfilepath, 'w')
    writer = csv.writer(datainfile)
    writer.writerow(wirelessin)
    writer.writerow(uplinkin)
    writer.writerow(infraction)
    writer.writerow([wirelessintotal/uplinkintotal])
    datainfile.close()
    dataoutfile = open (dataoutfilepath, 'w')
    writer = csv.writer(dataoutfile)
    writer.writerow(wirelessout)
    writer.writerow(uplinkout)
    writer.writerow(outfraction)
    writer.writerow([wirelessouttotal/uplinkouttotal])
    dataoutfile.close()
    deviceup = {'caseeast1-0':'casecloset-4507', 'caseeast2-0':'casecloset-4507',
                'caseeast3-0':'colgate6807-vss', 'casewest1-0':'casecloset-4507',
                'casewest2-0':'casecloset-4507', 'casewest3-0':'casecloset-4507',
                'casewest4-0':'casecloset-4507', 'casewest5-0':'casecloset-4507',
                'ho-f0-0':'ho-4507', 'ho-f1-6':'ho-f1-5',
                'ho-f2-7':'ho-f2-6', 'ho-f2-8':'ho-f2-7',
                'ho-f3-2':'ho-f3-1', 'ho-f3-4':'ho-4507',
                'ho-f3-8':'ho-f3-5', 'ho-f4-0':'ho-4507',
                'ho-f4-2':'ho-f4-1', 'ho-f4-3':'ho-4507',
                'ho-f4-4':'ho-f4-3', 'ho-f4-5':'colgate6807-vss',
                'pinchin-0':'colgate6807-vss',
                'caseeast5-0a':'casecloset-4507'}
    perdevicebase(switches, deviceup, nodes, args.path)







    # masterfile = open(masterfilepath,'w')
    # writer = csv.writer(masterfile)
    # for s in switches:
    #     #print(switches[s].apports)
    #     for p in switches[s].ports:
    #         if (switches[s].ports.index(p) in switches[s].apports):
    #             #print(switches[s].ports.index(p), p.fulldir)
    #             apports.append(p)

    # first = True
    # sum = ['sum']
    # print(sorted(apports))


class switch(object):
    """Swtich objects contains a list of ports"""

    def __init__(self,name):
        super(switch, self).__init__()
        self.name = name
        self.ports = []
        self.apportsinterface = []
        self.apports = []
        self.upportid = []
        self.upport=[]

    def add(self,port):
        self.ports.append(port)

    def addap(self,interface):
        self.apportsinterface.append(interface)

    def addupid(self,upport):
        self.upportid.append(upport)

    def addup(self, upport):
        self.upport.append(upport)

    def addaport(self, apport):
        self.apports.append(apport)

    def checkid (self, id):
    #check if the given ID coreponding port is in this switch
        for p in self.ports:
            if p.portid == id:
                return True
        return False

    def getinterface(self, id):
    #return the interface name of the coreponding id port in this switche
        for p in self.ports:
            if p.portid == id:
                return p.interface
        return None

    def getid(self, interface):
    #return the portid of the coreponding interface in this switch
        for p in self.ports:
            if p.interface == interface:
                return p.portid
        return None


class port(object):
    """A port object has portid and full path to file name"""

    def __init__(self, portid, interface):
        super(port, self).__init__()
        self.portid = portid
        self.interface = interface

    def setid(self, id):
        self.id = id

    def setdir (self, fulldir):
        sefl.fulldir = fulldir

    @property
    def filename(self):
        return self.fulldir

    def __str__(self):
        return "Port <file=%s>" % (self.fulldir)

    def __lt__(self, other):
        return self.filename < other.filename

class Node(object):
    """docstring for Node."""

    def __init__(self, hostname):
        super(Node, self).__init__()
        self.hostname = hostname
        self.remote = []

    def add_remote(self, remote_node):
        self.remote.append(remote_node)

class remotenode(object):
    """docstring for remotenode."""

    def __init__(self, hostname, localinterface, remoteinterface):
        super(remotenode, self).__init__()
        self.hostname = hostname
        self.localinterface = localinterface
        self.remoteinterface = remoteinterface

def calculate(wirelessin, wirelessout, uplinkin, uplinkout):
    wirelessintotal = 0
    wirelessouttotal = 0
    uplinkintotal = 0
    uplinkouttotal = 0
    for data in wirelessin:
        wirelessintotal = wirelessintotal + data
    for data in wirelessout:
        wirelessouttotal = wirelessouttotal + data
    for data in uplinkin:
        uplinkintotal = uplinkintotal + data
    for data in uplinkout:
        uplinkouttotal = uplinkouttotal + data
    infraction = []
    outfraction = []
    for i in range (len(wirelessin)):
        if uplinkin[i] == 0:
            infraction.append("None")
        else:
            infraction.append(wirelessin[i]/uplinkin[i])
        if uplinkout[i] == 0:
            outfraction.append("None")
        else:
            outfraction.append(wirelessout[i]/uplinkout[i])
    return wirelessintotal, wirelessouttotal, uplinkintotal, uplinkouttotal, infraction, outfraction

def getwireless(apports, path, check):
    if check == "in":
        num = 0
    elif check == "out":
        num = 1
    end_str = os.path.basename(path).split('-')
    name_str = '_'.join(end_str[0:3]) + end_str[3]+":00"
    end_str = '/'.join(end_str[0:3]) + " " + end_str[3]+":00"
    first = True
    wirelessin = []
    for p in sorted(apports):
        rrddata = rrdtool.fetch(os.path.join(path, p), "AVERAGE",
                "--resolution", "60s",
                "--start", "end-10h",
                "--end", end_str)
        start, end, step = rrddata[0]
        datanames = rrddata[1]
        values = rrddata[2]
        index = 0
        for t in values:
            if not first:
                if t[num] != None:
                    wirelessin[index] = wirelessin[index]+t[num]
                else:
                    wirelessin[index] = wirelessin[index]+0
            else:
                if t[num]!=None:
                    wirelessin.append(t[num])
                else:
                    wirelessin.append(0)
            index = index + 1
        first = False
    return wirelessin


def procescsv(id_path, mappingfile_path):
    ports={}
    #read in id.csv to create Swtich and port objects
    id_path = os.path.join(id_path, "id.csv")
    try:
        idfile = open(id_path, "r")
    except IOError:
        print("Can't find id file")
    id_csv = csv.reader(idfile)
    for row in id_csv:
        portname = row[0].split(" - ")
        ##create new Swtich object if not exist
        if portname[0] not in ports:
            ports[portname[0]] = switch(portname[0])
        ports[portname[0]].add(port(row[1],portname[-1]))
    # read in mapping.csv to add apportsinterface name in swtich object
    mappingfile_path = os.path.join(mappingfile_path, "mapping.csv")
    try:
        mappingfile = open(mappingfile_path, "r")
    except IOError:
        print("Can't find mapping file")
    mapping_csv = csv.reader(mappingfile)
    for row in mapping_csv:
        if row[0] not in ports:
            ports[row[0]] = switch(row[0])
        ports[row[0]].addap(row[1])
    return ports

def processrrd(base_dir, allports):
    apports=[]
    if os.path.isdir(base_dir):
        for root,dirs,files in os.walk(base_dir):
            for name in files:
                name_list = name.split('_')
                if name_list[1] == "traffic":
                    if name_list[0] in allports:
                        if allports[name_list[0]].checkid(name_list[-1][:-4]):
                            if allports[name_list[0]].getinterface(name_list[-1][:-4]) in allports[name_list[0]].apportsinterface:
                                allports[name_list[0]].addaport(name)
                                apports.append(name)
    else:
        print("please enter valid rrd directory")
    return apports

def processuplink(base_dir, idlist):
    results = []
    if os.path.isdir(base_dir):
        for root,dirs,files in os.walk(base_dir):
            for name in files:
                name_list = name.split('_')
                if name_list[-1][:-4] in idlist:
                    results.append(name)
    return results

def processdeviceup(base_dir, switches):
    if os.path.isdir(base_dir):
        for root,dirs,files in os.walk(base_dir):
            for name in files:
                name_list = name.split('_')
                for device in switches:
                    if name_list[-1][:-4] in switches[device].upportid:
                        switches[device].addup(name)
# TODO: Complete perdevicebase function that return every apports of a device
def perdevicebase(switches, updevice, nodes, path):
    for device in switches:
        if not len(switches[device].apportsinterface) == 0:
            for rnode in nodes[device].remote:
                if rnode.hostname == updevice[device]:
                    switches[device].addupid(switches[device].getid(rnode.localinterface))

    processdeviceup(path, switches)

    for device in switches:
        if not len(switches[device].apportsinterface) == 0:
            wirelessin = getwireless(switches[device].apports, path, 'in')
            uplinkin = getwireless(switches[device].upport, path, 'in')
            wirelessout = getwireless(switches[device].apports, path, 'out')
            uplinkout = getwireless(switches[device].upport, path, 'out')
            print(device)
            wirelessintotal, wirelessouttotal, uplinkintotal, uplinkouttotal, infraction, outfraction = calculate(wirelessin, wirelessout, uplinkin, uplinkout)
            print('total in fraction : %f' %(wirelessintotal/uplinkintotal))
            print('total out fraction :%f' %(wirelessouttotal/uplinkouttotal))




main()
