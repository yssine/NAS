#!/usr/bin/python3
import os, json, glob, platform, re


GNSFILE='testfeild.gns3'
f=open(GNSFILE)
raw=json.load(f)
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



Rs=DHCP(surf(raw))

# for i in Rs:
#     print(Rs[i].name,':')
#     for x in Rs[i].intfs:
#         print("\t",x,':')
#         print("\t"*2,Rs[i].intfs[x].ip,'/',Rs[i].intfs[x].mask)

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
    input["Routers"][r.name]["class"]="CE/PE/P?"
    input["Routers"][r.name]["RP"]=["BGP?","OSPF?","VPN?"]
    input["Routers"][r.name]["VPN"]={}
    input["Routers"][r.name]["VPN"]["VPN_id"]="?"
    input["Routers"][r.name]["VPN"]["RD"]="?"
    input["Routers"][r.name]["VPN"]["RT"]="?"
    input["Routers"][r.name]["VPN"]["neighbor"]=[["ip?","remote_as(int)"]]
    input["Routers"][r.name]["BGP"]={}
    input["Routers"][r.name]["BGP"]["BGP_AS"]="as(int)"
    input["Routers"][r.name]["BGP"]["neighbor"]=[["ip?","remote_as(int)"]]
    input["Routers"][r.name]["ints"]=[]
    for intf in r.intfs.values():
        i={}
        i["link"]=intf.link
        i["IP"]=intf.ip
        i["mask_l"]=intf.mask
        i["VRF"]="vrf_id? (int)"
        i["OSPF"]={"PID":"process_id (int)","area":"area_ (int)"}

        input["Routers"][r.name]["ints"].append(i)





json_object = json.dumps(input, indent = 4)
# print(type(json_object))
f=open("inpt.json","w")
f.write(json_object)
f.close()






