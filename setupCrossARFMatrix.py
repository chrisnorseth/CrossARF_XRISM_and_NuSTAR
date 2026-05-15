import argparse

# argument handling
parser = argparse.ArgumentParser()
parser.add_argument("obs_file")
parser.add_argument("models_file")

args = parser.parse_args()
obs_file = args.obs_file
models_file = args.models_file


# load in the obs info
# obs_file = 'obs.dat'
obs_lines = []
with open(obs_file) as file:
    for line in file:
        obs_lines.append(line)

# load in the model info
# models_file = 'models.dat'
models_file_lines = []
with open(models_file) as file:
    for line in file:
        models_file_lines.append(line)


# function to get stuff with err messages
def getValue(type, search_string, equator, message):
    num_check = 0
    for line in obs_lines:
        if search_string in line and '#' not in line:
            num_check += 1
            try:
                value = type(line.split(equator)[1].strip())
            except Exception:
                raise RuntimeError(f"Issue with establishing {message}.")
    if num_check != 1:
        if num_check == 0:
            raise RuntimeError(f"Could not find {message}.")
        elif num_check > 1:
            raise RuntimeError(f"Found multiple instances of: {message}.")
    if type == str:
        value = value.replace('"', '')
    return value

# function to get array with err messages
def getArray(search_string, message):
    num_check = 0
    for idx,line in enumerate(obs_lines):
        if search_string in line and '#' not in line:
            num_check += 1
            start_idx = idx
    # make sure there aren't duplicates
    if num_check != 1:
        if num_check == 0:
            raise RuntimeError(f"Could not find {message}.")
        elif num_check > 1:
            raise RuntimeError(f"Found multiple instances of: {message}.")
    # find the end of the array
    for i in range(start_idx, len(obs_lines)):
        line = obs_lines[i]
        if ']' in line:
            end_idx = i
            break
    obsids = []
    for i in range(start_idx+1, end_idx):
        line = obs_lines[i]
        try:
            obsid = line.strip()
            # if quotes were used
            obsid = obsid.replace('"', '')
            obsids.append(obsid)
        except Exception:
            raise RuntimeError(f"Issue with establishing {message}.")
    return obsids

# function to get xrism dictionary with err messages
def getXRISM_Dic():
    
    xrism_data_in = {}
    xrism_data_final = {}

    # find what regions to include
    for idx,line in enumerate(obs_lines):
        if 'Region:' in line:
            try:
                num = int(line.split(':')[1].strip())
            except Exception:
                raise RuntimeError("Issue with how XRISM regions are defined.")
            xrism_data_in[num] = {'start_idx':idx}
            xrism_data_final[num] = {}
        
    # sort through the info
    for key in xrism_data_in:
        start = xrism_data_in[key]['start_idx']
        # get the directory
        for i in range(start, len(obs_lines)):
            line = obs_lines[i]
            if 'directory' in line:
                try:
                    dir = line.split('=')[1].strip()
                except Exception:
                    raise RuntimeError(f"Issue with XRISM 'Region {key}>' directory.")
                dir = dir.replace('"', '')
                xrism_data_final[key]['dir'] = dir
                xrism_data_final[key]['data'] = []
                break
        # get the num of obs
        for i in range(start, len(obs_lines)):
            line = obs_lines[i]
            if 'num_obs' in line:
                try:
                    num_obs = int(line.split('=')[1].strip())
                except Exception:
                    raise RuntimeError(f"Issue with XRISM 'Region {key}' num of obs definition.")
                xrism_data_in[key]['num_obs'] = num_obs
                # add a dic for each
                for _ in range(num_obs):
                    xrism_data_final[key]['data'].append({})
                break
        # get the spec
        found = 0
        for i in range(start, len(obs_lines)):
            line = obs_lines[i]
            if 'spectrum' in line:
                try:
                    spec = line.split('=')[1].strip()
                except Exception:
                    raise RuntimeError(f"Issue with XRISM 'Region {key}' spectrum definition.")
                spec = spec.replace('"', '')
                xrism_data_final[key]['data'][found]['spec'] = spec
                found += 1
                if found >= num_obs:
                    break
        # get the back
        found = 0
        for i in range(start, len(obs_lines)):
            line = obs_lines[i]
            if 'back' in line:
                try:
                    back = line.split('=')[1].strip()
                except Exception:
                    raise RuntimeError(f"Issue with XRISM 'Region {key}' back definition.")
                back = back.replace('"', '')
                xrism_data_final[key]['data'][found]['back'] = back
                found += 1
                if found >= num_obs:
                    break
        # get the rmf
        found = 0
        for i in range(start, len(obs_lines)):
            line = obs_lines[i]
            if 'rmf' in line:
                try:
                    rmf = line.split('=')[1].strip()
                except Exception:
                    raise RuntimeError(f"Issue with XRISM 'Region {key}' rmf definition.")
                rmf = rmf.replace('"', '')
                xrism_data_final[key]['data'][found]['rmf'] = rmf
                found += 1
                if found >= num_obs:
                    break
        ## get the arfs
        # add in the arf dics
        for n in range(num_obs):
            xrism_data_final[key]['data'][n]['arfs'] = {}
        # find the start
        found = 0
        arfs_start_idx = []
        for i in range(start, len(obs_lines)):
            line = obs_lines[i]
            if 'arfs' in line:
                arfs_start_idx.append(i)
                found += 1
                if found >= num_obs:
                    break
        # find the end
        found = 0
        arfs_end_idx = []
        for i in range(start, len(obs_lines)):
            line = obs_lines[i]
            if '}' in line:
                arfs_end_idx.append(i)
                found += 1
                if found >= num_obs:
                    break
        # grab the arfs
        for idx_arf,start_arf in enumerate(arfs_start_idx):
            for i in range(start_arf+1, arfs_end_idx[idx_arf]):
                line = obs_lines[i]
                arf_key = line.split(':')[0].strip()
                arf_key = arf_key.replace('"','')
                arf_file = line.split(':')[1].strip()
                arf_file = arf_file.replace('"','')
                xrism_data_final[key]['data'][idx_arf]['arfs'][arf_key] = arf_file
                
    return xrism_data_final


    


## Read in all Info
# get num_regs
num_regs = getValue(int, 'Regions:', ':', 'number of regions')

# get parent dir
parent_dir = getValue(str, 'main_directory', '=', 'main directory')

# get output file name
output_file = parent_dir + '/' + getValue(str, 'output_script', '=', 'output script')


## NuSTAR
# get nustar data container
data_container_nu = getValue(str, 'nu_directory', '=', 'nustar directory')

# get nustar reg base
reg_base = getValue(str, 'nu_reg_base', '=', 'nustar reg base')

# get nustar obsids
obsids = getArray('nu_obsids', 'nustar obsids')


## XRISM
# get xrism data container
data_container_xrism = getValue(str, 'xrism_directory', '=', 'xrism directory')

# get xrism bg data container
bg_container_xrism = getValue(str, 'xrism_bg_directory', '=', 'xrism bg directory')

# get all the xrism info
try:
    regs_xrism = getXRISM_Dic()
except Exception:
    raise RuntimeError(f"Issue with reading in XRISM arfs. Contact Christian.")


## Models
models = {}
for idx,line in enumerate(models_file_lines):
    # find the model
    if 'model' in line and '#' not in line:
        # model line
        mod_line = line.strip()

        # get the model num
        mod_num = int(line.split('model')[1].split(':')[0].strip())

        models[mod_num] = {'lines':[mod_line]}

        # find the end (and also add things along the way) (and also count up number of pars)
        num_pars = 0
        for i in range(idx+1,len(models_file_lines)):
            search_line = models_file_lines[i]
            if search_line == '\n':
                break
            else:
                line_to_add = search_line.strip()
                models[mod_num]['lines'].append(line_to_add)
                num_pars += 1
        models[mod_num]['num_pars'] = num_pars
   


matrix = {}

### setup data/back lines
'''
each spec is loaded in diagonally, starting with each A reg,
followed by each B reg, then repeating for each obs
'''

# nustar
spec_num = 1
# each obsid
for obsid in obsids:
    for det in ['A', 'B']:
        # each reg
        for r in range(1,num_regs+1):
            entry = {'reg':r,
                     'path':f'{data_container_nu}/{obsid}',
                     'bg_path':f'{data_container_nu}/{obsid}',
                     'spec':f'{reg_base}{det}{r}.pha',
                     'back':f'bgd{reg_base}{det}{r}.pha',
                     'rmf':f'{reg_base}{det}{r}.rmf'
                    }
            arfs = {}
            for source in range(1, num_regs+1):
                arfs[f'{source}_{r}'] = f'{reg_base}{det}{source}_{r}.arf'
            entry['arfs'] = arfs
            matrix[spec_num] = entry 
            spec_num += 1

# xrism
for key in regs_xrism:
    obs = regs_xrism[key]
    dir = obs['dir']
    data = obs['data']

    for each_obs in data:
        spec = each_obs['spec']
        back = each_obs['back']
        rmf = each_obs['rmf']
        arfs = each_obs['arfs']

        entry = {'reg':key,
                     'path':f'{data_container_xrism}/{dir}',
                     'bg_path':f'{bg_container_xrism}',
                     'spec':spec,
                     'back':back,
                     'rmf':rmf,
                     'arfs':arfs
                    }
        matrix[spec_num] = entry 
        spec_num += 1


        
        
# setup the script
script_lines = []

# loading data
for col in matrix:
    spec = matrix[col]['spec']
    back = matrix[col]['back']
    path = matrix[col]['path']
    bg_path = matrix[col]['bg_path']

    data_line = f'data {col}:{col} {path}/{spec}\n'
    back_line = f'back {col} {bg_path}/{back}\n'
    
    script_lines.append(data_line)
    script_lines.append(back_line)

# loading responses
for col in matrix:
    rmf = matrix[col]['rmf']
    path = matrix[col]['path']
    arfs = matrix[col]['arfs']
    reg = matrix[col]['reg']
    for row in range(1,num_regs+1):
        arf_idx = f'{row}_{reg}'
        try:
            arf = arfs[arf_idx]
            arf_line = f'arf {row}:{col} {path}/{arf}\n'
            rmf_line = f'resp {row}:{col} {path}/{rmf}\n'

            script_lines.append(rmf_line)
            script_lines.append(arf_line)
        except:
            None


### setup models
# establish models
model_lines = ['\n# setup models\n']

for model_key in models:
    model = models[model_key]['lines']
    for line in model:
        model_lines.append(f'{line}\n')


### tie consts (potentially split acros obsids, but tied for now)
## keep in mind its all As by default and we just tie As across models to each other
## the order of nustar data is all A regs, all B regs, for each obsid
## the main const par is stored in the first model

# get the first model par num
first_mod_par_num = models[1]['num_pars']
const_par = (num_regs+1)*first_mod_par_num

# for 1 Bs for first obs
model_lines.append('\n# tie s1 Bs for 1st obs\n')
for reg in range(1,num_regs):
    one_B_line = f'newpar s1:{(num_regs+1+reg)*first_mod_par_num}=s1:{const_par}\n'
    model_lines.append(one_B_line)

# 1 Bs for other obs (sequence is A,B,A,B)
model_lines.append('\n# tie s1 Bs for other obs\n')
for obs in range(len(obsids)-1):
    for reg in range(num_regs):
        '''
        first B (num_regs+1)*num_par (e.g. (5+1)*5=30)
        and then the following Bs are the above plus num_par for each reg
        -> (num_regs+1)*num_par + num_par*reg = (num_regs+1+reg)*num_par
        then for the rest of the Bs for s1, you then have to skip the next set
        of A regs, so +(num_regs+1)*num_par
        -> (num_regs+1+(reg->(num_regs-1)))*num_par + (num_regs+1)*num_par
        = (num_regs+1+num_regs-1)*num_par + (num_regs+1)*num_par
        = (2*num_regs)*num_par + (num_regs+1)*num_par
        = (2*num_regs + num_regs+1)*num_par
        = (3*num_regs+1)*num_par
        then plus num_par for the rest of the regs
        -> (3*num_regs+1)*num_par + num_par*reg
        then repeat for each obsid, where you again skip over all the As +(num_regs+1)*num_par
        so for the next one start at
        -> (3*num_regs+1)*num_par + num_par*(reg->num_regs-1) +(num_regs+1)*num_par
        = (3*num_regs+1)*num_par + num_par*(num_regs-1) +(num_regs+1)*num_par
        = (3*num_regs+1+num_regs-1+num_regs+1)*num_par
        = (5*num_regs+1)*num_par
        then again add num_par for the rest of the regs
        -> (5*num_regs+1)*num_par + num_par*reg
        so from this pattern
        => ((3+2*obs)*num_regs+1)*num_par + num_par*reg
        '''
        
        par = ((3+2*obs)*num_regs+1)*first_mod_par_num + first_mod_par_num*reg
        line = f'newpar s1:{par}=s1:{const_par}\n'
        model_lines.append(line)



## for the As in other models
# tie the first const of other models to the first model's
model_lines.append('\n# tie As for other srcs to src 1 A\n')
for reg in range(2,num_regs+1):
    num_pars_mod = models[reg]['num_pars']
    a_line = f'newpar s{reg}:{num_pars_mod}=s1:{first_mod_par_num}\n'
    model_lines.append(a_line)

## untie the B const
model_lines.append('\n# untie B const in src 1\n')
model_lines.append(f'untie s1:{const_par}\n')

## tie the Bs from other models to the first model (for the first obsid)
'''
first tie the first B in the other model to the first model
then tie the rest of the Bs in that model to the first B in the model
'''
model_lines.append('\n# for first obs: tie Bs in src N to src 1 and then src N Bs to each other\n')
for reg in range(2, num_regs+1):
    # number of paramters in specific model
    num_pars_mod = models[reg]['num_pars']
    for n in range(1,num_regs+1):
        # par number in specific model, steps of model pars
        par_to_set = (num_regs+1*n)*num_pars_mod
        # first B par in this model
        par_setting_to = (num_regs+1)*num_pars_mod
        newpar_line = f'newpar s{reg}:{par_to_set}=s{1 if n==1 else reg}:{const_par if n==1 else par_setting_to}\n'
        model_lines.append(newpar_line)

## tie Bs for other obs
# follows same logic as above for the 1st Bs, except now based on each specific model num of pars
model_lines.append('\n# for other obs: tie Bs in src N to src 1 and then src N Bs to each other\n')
for reg in range(2,num_regs+1):
    # number of paramters in specific model
    num_pars_mod = models[reg]['num_pars']
    # first B par in this model
    par_setting_to = (num_regs+1)*num_pars_mod

    for obs in range(len(obsids)-1):
        for r in range(num_regs):
            par = ((3+2*obs)*num_regs+1)*num_pars_mod + num_pars_mod*r

            line = f'newpar s{reg}:{par}=s{reg}:{par_setting_to}\n'
            model_lines.append(line)


##### XRISM CONSTANTS #####
# identify number of xrism obs
num_xrism_obs = 0
for key in regs_xrism:
    num_obs_this = len(regs_xrism[key]['data'])
    for _ in range(num_obs_this):
        num_xrism_obs += 1

# untie each xrism const in s1 (since they are all seperate obs)
'''
logic from above:
obs is 0-(len(obsids)-1) because it was designed for obs beyond the first (-1)
r is 0-num_regs
-> ((3+2*obs)*num_regs+1)*num_par + num_par*r
-> maximize: ((3+2*(obs->len(obsids)-2))*num_regs+1)*num_par + num_par*(r->num_regs-1)
-> maximize: ((3+2*(len(obsids)-2))*num_regs+1)*num_par + num_par*(num_regs-1)
'''
model_lines.append('\n# untie XRISM constants in s1 (all seperate for now)\n')
xrism_consts = []
# for just s1
num_par = models[1]['num_pars']
last_nu = ((3+2*(len(obsids)-2))*num_regs+1)*num_par + num_par*(num_regs-1)
first_xrism = last_nu + num_par
for next_xrism in range(num_xrism_obs):
    par = first_xrism + next_xrism*num_par
    xrism_consts.append(par)
    new_line = f'untie s1:{par}\n'
    model_lines.append(new_line)

# tie across the models to s1
model_lines.append('\n# tie XRISM constants to s1 constants\n')
for mod in range(2,num_regs+1):
    num_par = models[mod]['num_pars']
    last_nu = ((3+2*(len(obsids)-2))*num_regs+1)*num_par + num_par*(num_regs-1)
    first_xrism = last_nu + num_par
    for next_xrism in range(num_xrism_obs):
        par = first_xrism + next_xrism*num_par
        new_line = f'newpar s{mod}=s1:{xrism_consts[next_xrism]}\n'
        model_lines.append(new_line)


# add the model lines to the script
script_lines.extend(model_lines)


# the additional things
script_lines.extend([
    '\n# set statistic\n',
    'statistic cstat\n',
    '\n# set abundance\n',
    'abund lpgs\n',
    '\n# set query\n',
    'query yes\n\n',
    'cpd /xs\n'
    'setpl e\n',
    'ignore **:**-3.,16.-**\n',
    'setpl reb 10 30\n',
    'pl ld\n'
    '\n# thaw constant\n',
    f'thaw s1:{const_par}\n'
])


## write the script
with open(output_file, 'w') as file:
    file.writelines(script_lines)