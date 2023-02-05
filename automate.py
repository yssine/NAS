#!/usr/bin/python3
import os, json, glob, platform, re, jinja2


GNSFILE='testfeild.gns3'
router_path={}
hosts=[]

f=open(GNSFILE)
raw=json.load(f)
# raw=f.read()
# print(raw.keys())
for node in raw['topology']['nodes']:
    path=r'project-files/dynamips/'+node['node_id']+r'/configs/'
    conf_file=glob.glob(path+'/*startup*',recursive=True)[0]
    if platform.uname().system=='Windows':
        conf_file=conf_file.split('\\')
    else:
        conf_file=conf_file.split('/')
    conf_file=conf_file[-1]
    # print(conf_file)
    hosts.append(node['name'])
    router_path[node['name']]= path+conf_file
f.close()
# print(router_path)


class Router:
    def __init__(self, name, input):
        self.name       = name
        if self.name in router_path.keys():
            self.path   = router_path[self.name]
        self.input      = input
        self.cl      = self.input["Routers"][self.name]["class"]
        self.RP         = self.input["Routers"][self.name]["RP"]
        if "BGP" in self.RP:
            self.BGP   = self.input["Routers"][self.name]["BGP"]
        if "VPN" in self.RP:
            self.VPN   = self.input["Routers"][self.name]["VPN"]
        if "OSPF" in self.RP:
            self.OSPF   = self.input["Routers"][self.name]["OSPF"]
        self.itfs = self.fill_ints()

    def fill_ints(self):
        ints = []
        for interface in self.input["Routers"][self.name]["ints"]:
            # print(interface)
            n = self.input["Links"][interface["link"]][self.name]
            if not "VRF" in interface.keys():
                interface["VRF"]=False
            ints.append(Interface(interface["link"],n,interface["IP"],interface["mask_l"],interface["VRF"]))
        return ints


class Interface:
    def __init__(self, link, name, ip, mask_l,VRF):
        self.link       = link
        self.name       = name
        self.ip         = ip
        self.mask_l     = mask_l
        self.mask       = self.mask(self.mask_l)
        self.VRF        = VRF

    def mask(self,l):
            s = '1'*l
            s = s.ljust(32,'0')
            my_mask = ""
            for i in range(4):
                my_mask = my_mask + str(int(s[i*8:(i+1)*8],2)) + '.'
            return my_mask[:-1]


jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader('template'))


def auto(RX):
    f=open('inpt.json')
    raw=json.load(f)
    Rx=Router(RX,raw)
    jinja_var = {
        'R'         : Rx
    }

    template = jinja_env.get_template('genconf.txt')
    conf=template.render(jinja_var)
    print(conf)
    # print(Rx.RP)

    # print(Rx.name)

    # s=open(router_path[Rx.name],"w")
    # s.write(conf)


auto("R4")
