#!/usr/bin/env python3
import os
import csv

def main():
    masterfile = open("graph.csv",'w')
    writer = csv.writer(masterfile)
    writer.writerow(["Node", "Connected","Local","Remote"])
    row = []
    remote = False
    aruba = False
    for line in open("CDP-neighbors.txt","r"):
        #initialize every row of the csv
        if ("_" in line):
            if (len(row)!=0):
                writer.writerow(row)
                remote = False
                aruba = False
            row = []

        if ("aruba" in line):
        #check if it is aruba router
            row.append(line.split('-')[0].strip()+line.split('-')[1].strip())
            aruba = True

        if (aruba and ".colgate.edu" in line):
            row.append(line.split()[1])
            row.append(line.split()[0])
            row.append("none")

        if (".colgate.edu" in line and not remote and not aruba):
            row.append((line.split('.')[0]).strip())
            remote = True
        elif (".colgate.edu" in line and remote and not aruba):
            row.append((line.split('.')[0]).strip())

        if (("WS" in line or "XL" in line or "XM" in line) and not aruba):
            row.append(line.split()[0]+line.split()[1])
            row.append(line.split()[-2]+line.split()[-1])
main()
