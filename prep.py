#!/usr/bin/python3
import os, json, glob, platform, re, sys

try:
    GNSFILE=sys.argv[1]
except :
    GNSFILE='testfeild.gns3'


f=open(GNSFILE)
raw=json.load(f)
f.close()
# # raw=f.read()
class Link:
    def __init__(self, name, id, term1, term2):
        self.name    = name
        self.id    = id
        self.term1    = term1
        self.term2    = term2

class Term:
    def __init__(self, Router_name, Router_id, inter):
        self.Router_name = Router_name
        self.Router_id = Router_id
        self.inter = inter




def surf(raw):
    Router_id = {}
    LINKS = {}
    for node in raw["topology"]["nodes"]:
        Router_id[node["node_id"]]=node["name"]
    count=1
    for link in raw["topology"]["links"]:
        LINKS[f'L{count}']=Link(f'L{count}',link["link_id"],Term(Router_id[link["nodes"][0]["node_id"]],link["nodes"][0]["node_id"],link["nodes"][0]['label']['text']),Term(Router_id[link["nodes"][1]["node_id"]],link["nodes"][1]["node_id"],link["nodes"][1]['label']['text']))
        count=count+1
    return LINKS, Router_id

# print(surf(raw))

class Router:
    def __init__(self, rid, name, intfs):
        self.id      = rid
        self.name    = name
        self.intfs   = intfs

    def add_ints(self,link,name,ip,mask):
        self.intfs[name]=Inter(link,name,ip,mask)


class Inter:
    def __init__(self, link, name, ip, mask):
        self.link    = link
        self.name    = name
        self.ip      = ip
        self.mask    = mask



# f=open('inpt.json')
# raw=json.load(f)
# f.close()
def DHCP(inp):
    NET_PREF="192.186."
    Ls,Rid=inp
    Rs={}
    for R in Rid:
        Rs[R]=Router(R,Rid[R],{})

    for router in Rs:
        l0=(Rs[router].name[1:]+'.')*4
        Rs[router].add_ints('L0',"loopback0",l0[:-1],32)
        # print(l0[:-1])


    for L in Ls:
        subnet = L[1:]
        c=1
        for term in [Ls[L].term1,Ls[L].term2]:
            ip=NET_PREF+subnet+'.'+str(c)
            Rs[term.Router_id].add_ints(L,term.inter,ip,24)
            c=c+1
            # print(term.inter)

    # print(Rs['eb4420b5-8862-44ba-a069-9b3b6d192a11'].intfs["f2/0"].ip)

    return Rs


Routing_Protocols={"CE":["BGP"],"PE":["BGP","OSPF","VPN"],"P":["OSPF"]}

def CEs():
    f=open("descriptor.json")
    d=json.load(f)
    f.close()
    CE=[]
    Cust=[j for j in [d[i] for i in d.keys() if i[:2]=="CE"]]
    for k in Cust:
        for l in k:
            CE.append(l)
    return CE
# print(CEs(d))

Rs=DHCP(surf(raw))


def cl(name):
    f=open("descriptor.json")
    d=json.load(f)
    f.close()
    if name in CEs():
        return "CE"
    elif name in d["PE"]:
        return "PE"
    elif name in d["P"]:
        return "P"

def vpn_ls():
    f=open("descriptor.json")
    d=json.load(f)
    f.close()
    vpn=[]#[{"VPN_id": i+1,"RD":f"{i+1}:{i+1}","RT":f"{i+1}:{i+1}"} for i in range(len(d["Clients"]))]
    for i,l in enumerate(d["Clients"]):
        v={}
        i=i+1
        v["VPN_id"]=i
        v["RD"]=f"{i}:{i}"
        v["RT"]=f"{i}:{i}"
        v["concerned_PEs"]=[]
        for c in d[l]:
            for link in surf(raw)[0].values():
                if c ==[link.term1.Router_name,link.term2.Router_name][0]:
                    v["concerned_PEs"].append(([link.term1.Router_name,link.term2.Router_name][1],link))
                if c ==[link.term1.Router_name,link.term2.Router_name][1]:
                    v["concerned_PEs"].append(([link.term1.Router_name,link.term2.Router_name][0],link))
        vpn.append(v)
    return vpn

def bgp():
    f=open("descriptor.json")
    d=json.load(f)
    f.close()
    links=surf(raw)[0].values()
    Rs=DHCP(surf(raw))
    b={"PE":{"BGP_AS":1,"neighbor":[]},"CE":{},"CEp":{}}
    c=2
    for rout in Rs.values():
        if rout.name in d["PE"]:
            b["PE"]["neighbor"].append(([rout.intfs["loopback0"].ip,1],rout.name))
        # print(CEs())
        if rout.name in CEs():
            b["CE"][rout.name]={"BGP_AS":c,"neighbor":[]}
            b["CEp"][rout.name]={"BGP_AS":c,"neighbor":[]}
            for l in links:
                if rout.name==l.term1.Router_name:
                    b["CE"][rout.name]["neighbor"].append(([rout.intfs[l.term1.inter].ip,c],l.term2.Router_name))
                    b["CEp"][rout.name]["neighbor"].append(([Rs[l.term2.Router_id].intfs[l.term2.inter].ip,c],l.term2.Router_name))
                if rout.name==l.term2.Router_name:
                    b["CE"][rout.name]["neighbor"].append(([rout.intfs[l.term2.inter].ip,c],l.term1.Router_name))
                    b["CEp"][rout.name]["neighbor"].append(([Rs[l.term1.Router_id].intfs[l.term1.inter].ip,c],l.term1.Router_name))
            c=c+1
    # print(b)
    return b

# print(bgp())
bgp()

# print(vpn_ls())
# print(cl("R15"))

# for i in Rs:
#     print(Rs[i].name,':')
#     for x in Rs[i].intfs:
#         print("\t",x,':')
#         print("\t"*2,Rs[i].intfs[x].ip,'/',Rs[i].intfs[x].mask)
def generate():
    input={}
    input["Links"],input["Routers"]={},{}
    # print(dir(surf(raw)[0]["L1"]))
    infos = surf(raw)
    input["Links"]["L0"]={}
    for j in infos[1]:
        input["Links"]["L0"][infos[1][j]]="loopback0"
    for i in infos[0]:
        input["Links"][i]={}
        # print(dir(infos[0][i].term1))
        input["Links"][i][infos[0][i].term1.Router_name]=infos[0][i].term1.inter
        input["Links"][i][infos[0][i].term2.Router_name]=infos[0][i].term2.inter
    for r in Rs.values():
        input["Routers"][r.name]={}
        input["Routers"][r.name]["name"]=r.name
        input["Routers"][r.name]["class"]=cl(r.name)
        input["Routers"][r.name]["RP"]=Routing_Protocols[cl(r.name)]
        if "VPN" in Routing_Protocols[cl(r.name)]:
            input["Routers"][r.name]["VPN"]=[]
            for v in vpn_ls():
                if r.name in [i[0] for i in v["concerned_PEs"]] :
                    smth={}
                    smth["VPN_id"]=v["VPN_id"]
                    smth["RD"]=v["RD"]
                    smth["RT"]=v["RT"]
                    smth["neighbor"]=[]
                    for k in bgp()["CE"].values():
                        if k["neighbor"][0][1]==r.name:
                            smth["neighbor"].append(k["neighbor"][0][0])  #[["ip?","remote_as(int)"]]
                            # print(k["neighbor"][0][0])
                    input["Routers"][r.name]["VPN"].append(smth)
        if "BGP" in Routing_Protocols[cl(r.name)]:
            input["Routers"][r.name]["BGP"]={}
            if cl(r.name)=="PE":
                input["Routers"][r.name]["BGP"]["BGP_AS"]=bgp()["PE"]["BGP_AS"]
                input["Routers"][r.name]["BGP"]["neighbor"]=[]
                for n in bgp()["PE"]["neighbor"]:
                    if r.name != n[1]:
                        input["Routers"][r.name]["BGP"]["neighbor"].append(n[0])
            if cl(r.name)=="CE":
                input["Routers"][r.name]["BGP"]["BGP_AS"]=bgp()["CEp"][r.name]["BGP_AS"]
                input["Routers"][r.name]["BGP"]["neighbor"]=[]
                # print(bgp()["CEp"][r.name]["neighbor"][0][0])
                input["Routers"][r.name]["BGP"]["neighbor"]=bgp()["CEp"][r.name]["neighbor"][0][0]
        if "OSPF" in Routing_Protocols[cl(r.name)]:
                f=open("descriptor.json")
                d=json.load(f)
                f.close()
                input["Routers"][r.name]["OSPF"]=d["OSPF"]



        input["Routers"][r.name]["ints"]=[]
        for intf in r.intfs.values():
            i={}
            i["link"]=intf.link
            i["IP"]=intf.ip
            i["mask_l"]=intf.mask
            if cl(r.name) == "PE":
                for v in vpn_ls():
                    a=list(zip([i[1].term1.inter for i in v["concerned_PEs"]],[i[1].term1.Router_name for i in v["concerned_PEs"]]))
                    b=list(zip([i[1].term2.inter for i in v["concerned_PEs"]],[i[1].term2.Router_name for i in v["concerned_PEs"]]))
                    # print((intf.name,r.name),a)
                    if (intf.name,r.name) in a or (intf.name,r.name) in b:
                        i["VRF"]=v["VPN_id"]
            input["Routers"][r.name]["ints"].append(i)




    json_object = json.dumps(input, indent = 4)
    # print(type(json_object))
    f=open("inpt.json","w")
    f.write(json_object)
    f.close()



generate()


