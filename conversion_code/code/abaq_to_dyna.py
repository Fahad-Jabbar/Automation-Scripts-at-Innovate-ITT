types_of_elements = ['s4r', 's4', 's3', 's3r']
node_dictionary = {}
element = {}
shellsection = {}
node_sets = {}
pids ={}
mids = {}
density = {}
propertites = []
materials = []
section_count = 0
sid_count = 0
set_count = 0
ls_pid = 0
ls_mid = 0


def first_substring_index(list, substring):
    return next(i for i, string in enumerate(list) if substring in string)


def add_property(pid):
    if pid not in propertites:
        ls_pid += 1
        pids[pid] = str(ls_pid)
        propertites.append(pids)


def add_materials(mid):
    if mid not in materials:
        ls_mid += 1
        mids[mid] = str(ls_mid)
    materials.append(mid)
        
with open("/home/sces201/Saad/ABAQ_to_DYNA/archara_static_v2.inp", "r") as f:
    for line in f:
        if line.startswith("**"):
            continue
        elif line.startswith("*"):
            line_list = line.strip().strip('*').split(',')
            line_list = [word.casefold() for word in line_list]
            keyword = line_list[0].replace(' ','')
            if keyword == 'node':
                set_name = ''
                if any('nset' in word for word in line_list):
                    index = first_substring_index(line_list,'nset')
                    set_name = line_list[index].split('=')[1]
                    node_sets[set_name.upper()] = []
            if keyword == 'element':
                if any('elset' in word for word in line_list):
                    index = first_substring_index(line_list,'elset')
                    pid = line_list[index].split('=')[1]
                add_property(pid)
                for type in types_of_elements:
                    current_type = type
                    if any( type in word for word in line_list):
                        break#exit loop when it founds the element type                                                 
            if keyword == 'shellsection':
                if any('elset' in word for word in line_list):
                    index = first_substring_index(line_list,'elset')
                add_property(pid)
                mid = line_list[index].split('=')[1]
                add_materials(mid)
                section_count += 1
            if keyword == 'material':
                if any('material' in word for word in line_list):
                    index = first_substring_index(line_list,'material')
                mid = line_list[index].split('=')[1]
                add_materials(mid)
            if keyword == 'nset':
                if any('nset' in word for word in line_list):
                    index = first_substring_index(line_list,'nset')
                set_name = line_list[index].split('=')[1]
                node_sets[set_name.upper()] = []
        else: 
            keyword_data_list = [item.strip() for item in line.strip().split(',') if item]
            if keyword == 'node':
                node_dictionary[keyword_data_list[0]] = keyword_data_list[1:]
                if set_name != '':
                    node_sets[set_name.upper()].append(keyword_data_list[0])
            if keyword == 'element':
                keyword_data_list.append(pids[pid])
                # have to tell at this particular point how to store data in dictionary for tria and quad
                if current_type in ['s4r', 's4']:
                    element[keyword_data_list[0]] = keyword_data_list[1:]
                if current_type == ['s3r', 's3']:
                    keyword_data_list.append(keyword_data_list[3])
                    element[keyword_data_list[0]] = keyword_data_list[1:]
            if keyword == 'shellsection':
                keyword_data_list.append(pids[pid])
                keyword_data_list.append(mids[mid])
                shellsection[str(section_count)] = keyword_data_list
            if keyword == 'density':
                density[mid] = keyword_data_list
            if keyword == 'nset':
                node_sets[set_name.upper()] += keyword_data_list
                
with open("/home/sces201/Saad/ABAQ_to_DYNA/my_lsdyna_file.key", "w") as g:
    g.write('*KEYWORD\n')
    g.write(f'*NODE\n${"NID":>7}{"x":>16}{"y":>16}{"z":>16}{"TC":>8}{"RC":>8}\n${"_" * 75}\n')
    for nid , cord in node_dictionary.items():
        g.write(f'{nid:>8}{cord[0]:>16}{cord[1]:>16}{cord[2]:>16}{'0':>8}{"0":>8}\n')
    g.write(f'*ELEMENT_SHELL\n${"EID":>7}{"PID":>8}{"N1":>8}{"N2":>8}{"N3":>8}{"N4":>8}\n${"_" * 75}\n')
    for eid , nod in element.items():
        g.write(f'{eid:>8}{nod[4]:>8}{nod[0]:>8}{nod[1]:>8}{nod[2]:>8}{nod[3]:>8}\n')
    for sections, data in shellsection.items():
        sid_count += 1
        g.write(f'*PART\nELSET_MAT\n')
        #g.write(f'${'PID':>9}{'SID':>10}{'MID':>10}\n${"_" * 35}\n')
        g.write(f'{data[1]:>10}{sid_count:>10}{data[2]:>10}\n')
        g.write(f'*SECTION_SHELL_TITLE\nELSET_MAT\n')
        #g.write(f'${'SID':>9}\n${'T1':>9}{'T2':>10}{'T3':>10}{'T4':>10}\n${"_" * 42}\n')
        g.write(f'{sid_count:>10}\n{data[0]:>10}{data[0]:>10}{data[0]:>10}{data[0]:>10}\n')
    g.write('\n')
    for name, ns in node_sets.items():
        set_count += 1
        g.write(f'*SET_NODE_TITLE\n{name.upper()}\n{set_count:>10}\n')
        for i, n in enumerate(ns):
            g.write(f'{n:>10}')
            if (i + 1) % 8 == 0:
                g.write('\n')
        g.write('\n')

    g.write('*END')