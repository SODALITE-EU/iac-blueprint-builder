import re
import json,os
artifact_types = ['\nartifact_types: \n\n']
capability_types = ['\ncapability_types: \n\n']
data_types = ['\ndata_types: \n \n']
entity_types = ['\nentity_types: \n\n']
group_types = ['\ngroup_types: \n\n']
interface_types = ['\ninterface_types: \n\n']
policy_types = ['\npolicy_types: \n\n']
relationship_types = ['\nrelationship_types: \n\n']
topology_template = ['  ', 'node_templates: \n'] # header and template nodes
node_types = ['\nnode_types: \n \n' ] # type nodes

participants = []
ansible_files = []
inputs = ['\ntopology_template:\n\n']


types = ['https://www.sodalite.eu/ontologies/tosca/tosca.artifacts', 'https://www.sodalite.eu/ontologies/tosca/tosca.capabilities',
'https://www.sodalite.eu/ontologies/tosca/tosca.datatypes', 'https://www.sodalite.eu/ontologies/tosca/tosca.entity',
'https://www.sodalite.eu/ontologies/tosca/tosca.groups', 'https://www.sodalite.eu/ontologies/tosca/tosca.interfaces',
'https://www.sodalite.eu/ontologies/tosca/tosca.policies', 'https://www.sodalite.eu/ontologies/tosca/tosca.relationships']

l_of_l = [artifact_types, capability_types, data_types, entity_types, group_types, interface_types, policy_types, relationship_types, node_types, inputs, topology_template]

def innerdicts(data, tabs, l=[], inList=False):
    for key, value in data.items():
        isList = False
        if key == "participants": participants = value
        if value and isinstance(value, list):
            if key == 'requirements':
                value = [{ ('- '+k.split('/')[-1]) : (v)  for (k, v) in c.items()} for c in value if isinstance(c, dict)]
                isList = True
            if isinstance(value[0],dict):
                v = {}
                for i in value:
                    v.update(i)
                value = v
        if isinstance(value, dict):
            if 'topology_template_inputs' in key:
                l = inputs
                tabs = 1
            elif 'isNodeTemplate' in value: # node template or node type
                if value['isNodeTemplate'] == False:
                    l = node_types
                    tabs = 1
                    for i in range(7):
                        if types[i] in value['type']:
                            l = l_of_l[i]
                    if 'ontologies/tosca/tosca' in key:
                        l = []
                else:
                    l = topology_template
                    tabs = 2
                l.append('\n')
                del value['isNodeTemplate']
            if "https://" in str(key): key = str(key)[str(key).rfind('/')+1:]
            if  key != 'specification' and  key  != 'topology_template_inputs':
                l. append('  '*(tabs)  + str(key) + ':  \n')
                if inList:
                    innerdicts(value, tabs+2, l, isList)
                else:
                    innerdicts(value, tabs+1, l, isList)
            else:
                innerdicts(value, tabs, l, isList)
        else:
            if key == 'type' and '/tosca/tosca.' in value:
                key = 'derived_from'
            if "Ansibles" in str(value):
                ansible_files.append(str(value))
                value = os.path.join(*value.split('/')[4:])
            if "https://" in str(value):
                value = str(value)[str(value).rfind('/')+1:]
            elif ": " in str(value) and "description" == str(key):
                value = str(value).replace(':', ' ')
            l. append('  '*(tabs) + str(key) + ': ' + str(value) + ' \n')


def remove_extra_hierarchies(s):
    s=re.sub("(\s*)(.*?:)(\s+)(.*?):(\s+)(label:)(\s+)(.*?)(\s+)", r'\1\2 \4\9',  s, flags=re.M)
    s=re.sub("(\s*)(.*?:)(\s+)(value:)(.*?)(\s+)(label:)(\s+)(.*?)(\s+)", r'\1\2 \5\10',  s, flags=re.M)
    return s

def parse_data(name, data):
    #create an output file
    outfile = open(name+".yml", "w")
    # output file header generator
    outfile.write('tosca_definitions_version: tosca_simple_yaml_1_0 \n\n')
    innerdicts(data, 1)
    s = []
    # print(data_types)
    for l in l_of_l:
        if len(l) > 1:
                s.append(''.join(l) + '\n\n')
    # s.append(''.join(data_types) + '\n\n' + ''.join(node_types) + '\n\n' + ''.join(topology_template) + '\n\n')

    outfile.write(remove_extra_hierarchies(''.join(s)))
    print('TOSCA generated -------')
    return ansible_files
