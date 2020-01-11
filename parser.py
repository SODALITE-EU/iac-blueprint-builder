import json
node_templates = [] # header and template nodes
node_types = [] # type nodes
def innerdicts(data,tabs, l=[]):
    for key, value in data.items():
        if isinstance(value,list):
            if isinstance(value[0],dict):
                v = {}
                for i in value:
                    v.update(i)
                value = v
        if isinstance(value,dict):
            if 'isNodeTemplate' in value:
                if value['isNodeTemplate'] == False:
                    l = node_types
                else:
                    l = node_templates
                del value['isNodeTemplate']
            if "https://" in str(key):
                key = str(key)[str(key).rfind('/')+1:]
            l. append('    '*(tabs)  + str(key) + ':  \n')
            innerdicts(value,tabs+1, l)
        else:
            l. append('    '*(tabs) + str(key) + ': ' + str(value) + ' \n')



def parse_file(filename):
    # read the json file
    with open(filename) as file:
        data = json.load(file)
    #create an output file
    outfile = open(filename.replace(".json",".yml"), "w")
    # output file header generator
    outfile.write('tosca_definitions_version: tosca_simple_yaml_1_0 \ndescription: Template for deploying a single %s\n' %list(data)[0])
    header = []
    innerdicts(data[list(data)[0]],1, header)
    node_templates.append('topology_template:')
    node_templates.append('\n    node_templates: \n')
    del data[list(data)[0]]
    # output file content generator
    innerdicts(data,2)
    #final clean_up
    s = ''.join(header) + ''.join(node_templates) + '\nnode types: \n' +''.join(node_types)
    s.replace('tosca_definitions_version: tosca_simple_yaml_1_0', '')
    outfile.write(s)



data = parse_file("snowUC-testbed.json")
