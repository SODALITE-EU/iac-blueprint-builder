import json

def Convert(lst):
    res_dct = {lst[i]: lst[i + 1] for i in range(0, len(lst), 2)}
    return res_dct

def innerdicts(data,tabs, outfile):
    for key, value in data.items():
        if tabs == 0: outfile.write('\n')
        if isinstance(value,list):
            value = value[0]
        if isinstance(value,dict):
            outfile.write('    '*(tabs)  + str(key) + ':  \n')
            innerdicts(value,tabs+1,outfile)
        else:
            outfile.write('    '*(tabs) + str(key) + ': ' + str(value) + ' \n')


def parse_file(filename):
    with open(filename) as file:
        data = json.load(file)
    outfile = open(filename.replace(".json",".yml"), "w")
    innerdicts(data,0, outfile)



data = parse_file("snowUC-testbed.json")
