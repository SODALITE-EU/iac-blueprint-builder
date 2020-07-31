import os
import re

artifact_types = ['\nartifact_types: \n\n']
capability_types = ['\ncapability_types: \n\n']
data_types = ['\ndata_types: \n \n']
entity_types = ['\nentity_types: \n\n']
group_types = ['\ngroup_types: \n\n']
interface_types = ['\ninterface_types: \n\n']
policy_types = ['\npolicy_types: \n\n']
relationship_types = ['\nrelationship_types: \n\n']
topology_template = ['  ', 'node_templates: \n']  # header and template nodes
node_types = ['\nnode_types: \n \n']  # type nodes

participants = []
ansible_files = []
ansible_paths = []
dependency_files = []
dependency_paths = []
inputs = ['\ntopology_template:\n\n']

types = ['https://www.sodalite.eu/ontologies/tosca/tosca.artifacts',
         'https://www.sodalite.eu/ontologies/tosca/tosca.capabilities',
         'https://www.sodalite.eu/ontologies/tosca/tosca.datatypes',
         'https://www.sodalite.eu/ontologies/tosca/tosca.entity',
         'https://www.sodalite.eu/ontologies/tosca/tosca.groups',
         'https://www.sodalite.eu/ontologies/tosca/tosca.interfaces',
         'https://www.sodalite.eu/ontologies/tosca/tosca.policies',
         'https://www.sodalite.eu/ontologies/tosca/tosca.relationships']

l_of_l = [artifact_types, capability_types, data_types, entity_types, group_types, interface_types, policy_types,
          relationship_types, node_types, inputs, topology_template]


def innerdicts(data, tabs, l=[], inList=False):
    for key, value in data.items():
        isList = False
        if key == "participants": participants = value
        if key == 'valid_source_types' and str(value) == '{}':
            value = []  # convert badly parsed empty lists to lists
        if value and isinstance(value, list):
            if key == 'requirements':
                value = [{('- ' + k.split('/')[-1]): (v) for (k, v) in c.items()} for c in value if isinstance(c, dict)]
                isList = True
            elif "occurrences" in key:
                constraint_value = ""
                first_el = True
                for element in value:
                    if first_el:
                        constraint_value += str(element)
                        first_el = False
                    else:
                        constraint_value += (", " + str(element))
                value = '[ {} ]'.format(constraint_value)
            if isinstance(value[0], dict):
                v = {}
                for i in value:
                    v.update(i)
                value = v
        if isinstance(value, dict):
            if 'topology_template_inputs' in key:
                l = inputs
                tabs = 1
            elif 'isNodeTemplate' in value:  # node template or node type
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
            if "https://" in str(key): key = str(key)[str(key).rfind('/') + 1:]
            if "Standard" in key:
                l.append('  ' * (tabs) + "Standard: " + "\n")
                if 'specification' in value:
                    l.append('  ' * (tabs + 1) + "type: tosca.interfaces.node.lifecycle.Standard " + "\n")
                    l.append('  ' * (tabs + 1) + "operations: " + "\n")
                    operations = ['create', 'delete']
                    for operation in operations:
                        # implementations don't need to implement all steps anymore
                        if operation in value['specification']['operations'].keys():
                            l.append('  ' * (tabs + 2) + operation + ": \n")
                            innerdicts(value['specification']['operations'][operation], tabs + 3, l, isList)
            # convert constraints maps to lists
            elif "constraints" in key:
                l.append('  ' * (tabs) + "constraints: \n")
                for constraint in value.keys():
                    l.append('  ' * (tabs + 1) + '- {}: {}'.format(constraint, value[constraint]) + "\n")
            # concat implementation urls
            elif "implementation" in key:
                l.append("{}implementation: \n".format('  ' * tabs))
                if "primary" in value:
                    ansible_files.append(value['primary']['url'])
                    temp_path = os.path.join(*value['primary']['url'].split('/')[4:]) + "_" + \
                                value['primary']['path'].split('/')[-1]
                    ansible_paths.append(temp_path)
                    l.append("{}primary: {} \n".format('  ' * (tabs + 1), temp_path))
                if "dependencies" in value:
                    if "file" in value["dependencies"]:
                        dep = value['dependencies']['file']
                        dependency_files.append(dep['url'])
                        temp_path = dep['path'].split('/')[-1]
                        dependency_paths.append(temp_path)
                        l.append("{}dependencies: \n".format('  ' * (tabs + 1)))
                        l.append("{}- file: {} \n".format('  ' * (tabs + 2), temp_path))
                        l.append("{}type: {} \n".format('  ' * (tabs + 3), "tosca.artifacts.File"))
            # convert variable accessors to shorthand variants to improve clarity
            elif "default" in value and isinstance(value["default"], dict) and (
                    "get_property" in value["default"].keys() or "get_attribute" in value["default"].keys()):
                get_prop_or_att = next(iter(value["default"]))
                prop_or_att = get_prop_or_att.split("_")[-1]
                default_properties = value["default"][get_prop_or_att]
                if "req_cap" in default_properties.keys():
                    l.append(
                        "{}{:20} {{ default: {{ {}: [ {}, {}, {} ] }} }} \n".format('  ' * tabs,
                                                                                    key + ":",
                                                                                    get_prop_or_att,
                                                                                    default_properties['entity'],
                                                                                    default_properties['req_cap'],
                                                                                    default_properties[prop_or_att]))
                else:
                    l.append(
                        "{}{:20} {{ default: {{ {}: [ {}, {} ] }} }} \n".format('  ' * tabs,
                                                                                key + ":",
                                                                                get_prop_or_att,
                                                                                default_properties['entity'],
                                                                                default_properties[prop_or_att]))
            elif "command" in key and "value" in value.keys():
                l.append('  ' * (tabs) + "command: \n")
                if isinstance(value["value"], list):
                    for command_value in value["value"]:
                        l.append('  ' * (tabs + 1) + '- "{}"'.format(command_value) + "\n")
                else:
                    l.append('  ' * (tabs + 1) + '- "{}"'.format(value["value"]) + "\n")
            elif key != 'specification' and key != 'topology_template_inputs':
                l.append('  ' * (tabs) + str(key) + ':  \n')
                if inList:
                    innerdicts(value, tabs + 2, l, isList)
                else:
                    innerdicts(value, tabs + 1, l, isList)
            else:
                innerdicts(value, tabs, l, isList)
        else:
            # legacy implementation parser
            if "Ansibles" in str(value):
                ansible_files.append(str(value))
                value = os.path.join(*value.split('/')[4:]) + "_" + data['path'].split('/')[-1]
                ansible_paths.append(value)
                l.append('  ' * (tabs) + 'file: ' + str(value) + ' \n')
                l.append('  ' * (tabs) + 'type: tosca.artifacts.Implementation \n')
            else:
                if key == 'type' and '/tosca/tosca.' in value:
                    key = 'derived_from'
                if "https://" in str(value):
                    value = str(value)[str(value).rfind('/') + 1:]
                elif ": " in str(value) and "description" == str(key):
                    value = str(value).replace(':', ' ')
                l.append('  ' * (tabs) + str(key) + ': ' + str(value) + ' \n')


def remove_extra_hierarchies(s):
    s = re.sub("(\s*)(.*?:)(\s+)(.*?):(\s+)(label:)(\s+)(.*?)(\s+)", r'\1\2 \4\9', s, flags=re.M)
    s = re.sub("(\s*)(.*?:)(\s+)(value:)(.*?)(\s+)(label:)(\s+)(.*?)(\s+)", r'\1\2 \5\10', s, flags=re.M)
    return s


def parse(data):
    innerdicts(data, 1)
    return ansible_files, ansible_paths, dependency_files, dependency_paths


def parse_data(name, data):
    # create an output file
    outfile = open(name + ".yml", "w")
    # output file header generator
    outfile.write('tosca_definitions_version: tosca_simple_yaml_1_3  \n\n')
    parse(data)
    s = []
    # print(data_types)
    for l in l_of_l:
        if len(l) > 1:
            s.append(''.join(l) + '\n\n')
    # s.append(''.join(data_types) + '\n\n' + ''.join(node_types) + '\n\n' + ''.join(topology_template) + '\n\n')

    outfile.write(remove_extra_hierarchies(''.join(s)))
    print('TOSCA generated -------')
    return ansible_files, ansible_paths, dependency_files, dependency_paths
