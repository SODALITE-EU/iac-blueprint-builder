import json

def innerdicts(data,tabs, outfile):
    for key, value in data.items():
        if isinstance(value,list):
            if isinstance(value[0],dict):
                v = {}
                for i in value:
                    v.update(i)
                value = v
            # else:
            #     value = [a[a.rfind('/')+1:] for a in value if "https://" in a]
        if isinstance(value,dict):
            if "https://" in str(key):
                key = str(key)[str(key).rfind('/')+1:]
            outfile.write('    '*(tabs)  + str(key) + ':  \n')
            innerdicts(value,tabs+1,outfile)
        else:
            outfile.write('    '*(tabs) + str(key) + ': ' + str(value) + ' \n')

def parse_file(filename):
    with open(filename) as file:
        data = json.load(file)
    outfile = open(filename.replace(".json",".yml"), "w")
    outfile.write('tosca_definitions_version: tosca_simple_yaml_1_0 \ndescription: Template for deploying a single %s' %list(data)[0])
    innerdicts(data[list(data)[0]],1, outfile)
    outfile.write('\ntopology_template: \n')
    del data[list(data)[0]]
    innerdicts(data,1, outfile)


data = parse_file("snowUC-testbed.json")
