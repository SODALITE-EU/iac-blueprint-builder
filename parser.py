import re
import json,os
artifact_types = ['\n  artifact_types: \n\n']
capability_types = ['\n  capability_types: \n\n']
data_types = ['\n data_types: \n \n']
entity_types = ['\n  entity_types: \n\n']
group_types = ['\n  group_types: \n\n']
interface_types = ['\n  interface_types: \n\n']
policy_types = ['\n  policy_types: \n\n']
relationship_types = ['\n  relationship_types: \n\n']
topology_template = ['  node_templates: \n'] # header and template nodes
node_types = ['\n node_types: \n \n' ] # type nodes

participants = []
ansible_files = []
inputs = ['\n topology_template:\n\n']


def innerdicts(data, tabs, l=[]):
    for key, value in data.items():
        if key == "participants": participants = value
        if isinstance(value,list):
            if isinstance(value[0],dict):
                v = {}
                for i in value:
                    v.update(i)
                value = v
        if isinstance(value, dict):
            if 'topology_template_inputs' in key:
                l = inputs
            elif 'isNodeTemplate' in value: # node template or node type
                if value['isNodeTemplate'] == False:
                    if not node_types: # node_types should be at same level as topology_template
                        tabs -= 1
                    if 'ontologies/tosca/tosca' in key:
                        l = []
                    elif 'https://www.sodalite.eu/ontologies/tosca/tosca.datatypes' in value['type']:
                        l = data_types
                    elif 'https://www.sodalite.eu/ontologies/tosca/tosca.capabilities' in value['type']:
                        l = capability_types
                    elif 'https://www.sodalite.eu/ontologies/tosca/tosca.artifacts' in value['type']:
                        l = artifact_types
                    elif 'https://www.sodalite.eu/ontologies/tosca/tosca.entity' in value['type']:
                        l = entity_types
                    elif 'https://www.sodalite.eu/ontologies/tosca/tosca.groups' in value['type']:
                        l = group_types
                    elif 'https://www.sodalite.eu/ontologies/tosca/tosca.interfaces' in value['type']:
                        l = interface_types
                    elif 'https://www.sodalite.eu/ontologies/tosca/tosca.policies' in value['type']:
                        l = policy_types
                    elif 'https://www.sodalite.eu/ontologies/tosca/tosca.relationships' in value['type']:
                        l = relationship_types

                    else:
                        l = node_types
                else:
                    l = topology_template
                l.append('\n')
                del value['isNodeTemplate']
            if "https://" in str(key): key = str(key)[str(key).rfind('/')+1:]
            l. append('  '*(tabs)  + str(key) + ':  \n')
            innerdicts(value, tabs+1, l)
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
    innerdicts(data, 2)
    s = []
    for l in [artifact_types ,    capability_types,    data_types ,    entity_types ,    group_types, interface_types, policy_types, relationship_types, node_types, inputs, topology_template ]:
        if len(l) > 1:
                s.append(''.join(l) + '\n\n')

    outfile.write(remove_extra_hierarchies(''.join(s)))
    print('TOSCA generated -------')
    return ansible_files
