components = {}
def read_att_pro_req_cap_int(s):
    pass


with open("snowUC-testbed.json") as file:
    lines = file.readlines()
    name = ""
    for l in lines:
        if l.startswith("    \"https://www.sodalite.eu/"):
            name = l[l.rfind('/')+1 : l.rfind('": {')]
            components[name] = {}
        elif '": "' in l:
            a = l.split('": "')[0].replace("\"","").replace("}","").replace("{","").replace(" ","").replace(',',"").replace('\n',"")
            b = l.split('": "')[1].replace("\"","").replace("}","").replace("{","").replace(" ","").replace(',',"").replace('\n',"")
            p = {a:b}
            components[name].update(p)
        elif '": [' in l:
            a = l.split('": [')[0].replace("\"","").replace("}","").replace("{","").replace(" ","").replace(',',"").replace('\n',"")
            b = read_att_pro_req_cap_int(l.split('": [')[1])
            p = {a:b}
            components[name].update(p)


print(components)
