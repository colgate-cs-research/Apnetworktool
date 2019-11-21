#!/usr/bin/env python3
import os
import csv
import argparse
import operator
import rrdtool

def main():
    parser = argparse.ArgumentParser(description='Aggregate experiment output')
    parser.add_argument('-c','--containers', dest='path', action='store',
            required=True, help='Path to containers directory')
    parser.add_argument('-m', '--csvpath', dest='mappingfile_path', action='store',
            required=True, help='Path to mapping file')
    parser.add_argument('-i', '--idpath', dest='idfile_path', action='store',
            required=True, help='Path to id file')
    parser.add_argument('-s', '--start', dest='start', action='store')
    parser.add_argument('-t', '--type', dest='type', action='store')
    args = parser.parse_args()
    switches = procescsv(args.idfile_path, args.mappingfile_path)

    apports = processrrd(args.path, switches)

    end_str = os.path.basename(args.path).split('-')
    name_str = '_'.join(end_str[0:3]) + end_str[3]+":00"
    end_str = '/'.join(end_str[0:3]) + " " + end_str[3]+":00"
    masterfilepath = os.path.join(args.mappingfile_path, name_str+".csv")
    masterfile = open(masterfilepath,'w')
    writer = csv.writer(masterfile)
    # for s in switches:
    #     #print(switches[s].apports)
    #     for p in switches[s].ports:
    #         if (switches[s].ports.index(p) in switches[s].apports):
    #             #print(switches[s].ports.index(p), p.fulldir)
    #             apports.append(p)

    first = True
    sum = ['sum']
    print(sorted(apports))
    for p in sorted(apports):
        # HACK: only consider
        # if not p.startswith("pinchin"):
        #     continue
        #
        # print(p)

        # Compute ending timestamp
        # end_str = os.path.basename(args.path).split('-')
        # end_str = '/'.join(end_str[0:3]) + " " + end_str[3]+":00"

        # Extract data
        rrddata = rrdtool.fetch(os.path.join(args.path, p), "AVERAGE",
                "--resolution", "60s",
                "--start", "end-10h",
                "--end", end_str)
        start, end, step = rrddata[0]
        datanames = rrddata[1]
        values = rrddata[2]
        if first:
            writer.writerow(rrddata[0])
        row = []
        row.append(p)
        index = 1
        for t in values:
            row.append(t[0])
            if not first:
                if t[0] != None:
                    sum[index] = sum[index]+t[0]
                else:
                    sum[index] = sum[index]+0
            else:
                if t[0]!=None:
                    sum.append(t[0])
                else:
                    sum.append(0)
            index = index + 1
        writer.writerow(row)
        first = False
        # print(datanames)
        # print(values)
    writer.writerow(sum)






class switch(object):
    """Swtich objects contains a list of ports"""

    def __init__(self,name):
        super(switch, self).__init__()
        self.name = name
        self.ports = []
        self.apportsinterface = []

    def add(self,port):
        self.ports.append(port)

    def addap(self,interface):
        self.apportsinterface.append(interface)

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
                                apports.append(name)
    else:
        print("please enter valid rrd directory")
    return apports

main()
