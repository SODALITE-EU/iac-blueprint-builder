import json,os
topology_template = [] # header and template nodes
node_types = [] # type nodes
ansible_files = []

def innerdicts(data, tabs, l=[]):
    for key, value in data.items():
        if isinstance(value,list):
            if isinstance(value[0],dict):
                v = {}
                for i in value:
                    v.update(i)
                value = v
        if isinstance(value, dict):
            if 'isNodeTemplate' in value: # node template or node type
                if value['isNodeTemplate'] == False:
                    if not node_types: # node_types should be at same level as topology_template
                        tabs -= 1
                    l = node_types
                else:
                    l = topology_template
                del value['isNodeTemplate']
            if "https://" in str(key):
                key = str(key)[str(key).rfind('/')+1:]
            l. append('    '*(tabs)  + str(key) + ':  \n')
            innerdicts(value, tabs+1, l)
        else:
            if "Ansibles" in str(value):
                ansible_files.append(str(value))
                value = os.path.join(*value.split('/')[3:])
            l. append('    '*(tabs) + str(key) + ': ' + str(value) + ' \n')


def parse_data(name, data):
    #create an output file
    outfile = open(name+".yml", "w")
    # output file header generator
    outfile.write('tosca_definitions_version: tosca_simple_yaml_1_0 \n')
    header = ['    description: Template for deploying a single %s\n' %list(data)[0]]
    innerdicts(data[list(data)[0]],1, header)
    topology_template.append('topology_template: \n')
    topology_template.extend(header)
    topology_template.append('    node_templates: \n')
    del data[list(data)[0]]
    # output file content generator
    innerdicts(data, 2)
    #final clean_up
    s = ''.join(topology_template) + 'node types: \n' +''.join(node_types)
    s.replace('tosca_definitions_version: tosca_simple_yaml_1_0', '')
    outfile.write(s)
    print('TOSCA generated -------')
    return ansible_files


# with open("snowUC-testbed.json") as file:
#     body = json.load(file)
# a = parse_data("name",body)
# for l in a:
#     print (l)
