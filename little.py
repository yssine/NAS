import os, json, glob, platform, re, jinja2, sys

print(sys.argv[1])


f=open("descriptor.json")
d=json.load(f)
def CEs(d):
    CE=[]
    Cust=[j for j in [d[i] for i in d.keys() if i[:2]=="CE"]]
    for k in Cust:
        for l in k:
            CE.append(l)
    return CE
# print(CEs(d))
a=[1,2,3]
b=["a","b","c"]
i=list(zip(a,b))
# print((i))
for j in i:
    if 1 in j:
        pass
        # print("yay")
# x = re.search("^The.*Spain$", d.keys())
# d["sec*"]
