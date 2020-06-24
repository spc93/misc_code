#
# changes required
#
# move scan_fields and scan_header up to subentry
# remove fields that are not required by modified defintion (confluece)
# new field in subentry:
# numerical_scale(optional) [n] int # no. of decimal places - to format numerical strings (if required)
# or (better) an optional @scale (int) attribute for each field

# Issues: have to save to new file before modifying (else original read-only)
# Can't move entire entry to a subentry - have entry and subentry for tests
# using link for measurement breaks title
# use sample name only to avoid all the transformations, beam etc
# don't include instrument
# add optional scan_header
# remove non_scan data

# tests: test pdnx with new definition
#test with manual parameters for entry and data
# if entry is the field containing data then update help string


import nexusformat.nexus as nx

inpath = '/dls/i16/data/2020/mm23580-2/'
outpath = '/dls/science/users/spc93/misc_nexus_data/modified/'
filenum = 815893


def getScanOutputNamesFromDatFile(file):
    # Extract information from .dat file that is not yet in the NeXus file
    # cols: list of scannable output names involved in the scan
    # header: list of strings to add to .dat file header
    # cmd: scan command (not currently formatted corrected in nexus files)
    # decs: decimal places for each field, based on first row
    header, cmd, linestr = [], '', ''
    with open(file, "r") as f:
        for i in range(5): # assume 5 lines for conventional SRS header
            header += [f.readline().replace("\n","")]
        
        while not '&END' in linestr:
            linestr = f.readline()
            if 'cmd' in linestr:
                cmd = (linestr.replace("cmd='","")).replace("'\n","")
        cols = f.readline().replace('\n','').split('\t')
        value_strings = f.readline().replace('\n','').split('\t')
        decs = []
        for i in range(len(value_strings)):
            int_dec = value_strings[i].split('.')
            if len(int_dec) == 1:
                decs += [0]     #must be integer
            else:
                decs += [len(int_dec[1])]  # number of decimal places
                

    return (cols, header, cmd, decs)


(cols, srs_header, cmd, decs) = getScanOutputNamesFromDatFile('%s%i.dat' %  (inpath, filenum))

n = nx.nxload('%s%i.nxs' %  (inpath, filenum))

n.save('%s%i.nxs' %  (outpath, filenum),'w') # seems to be required in order to change read/write mode

with n.nxfile:
   n['/entry1'].attrs['default'] ='scan'
   n['entry1/scan'] = nx.NXsubentry(definition = 'NXclassic_scan')
   n['/entry1/scan'].attrs['default'] = 'measurement'
   n['entry1/scan/title'] = cmd #get command string from .dat file
   n['entry1/scan/start_time'] = nx.NXlink(n['/entry1/start_time'])
   n['entry1/scan/end_time'] = nx.NXlink(n['/entry1/end_time'])
   n['entry1/scan/scan_command'] = nx.NXlink(n['/entry1/scan_command'])
   n['entry1/scan/measurement'] = n['/entry1/measurement']
   n['entry1/scan/scan_header'] = srs_header
   n['entry1/scan/scan_fields'] = cols
   n['entry1/scan/called_by'] = 'Not yet implemented in GDA'
   n['entry1/scan/positioners'] = nx.NXlink(n['/entry1/before_scan'])

   ind_str = '%s_indices' % str(n['/entry1/scan/measurement']._attrs['axes'])
   n['/entry1/scan/measurement']._attrs[ind_str] = 0
   for i in range(len(cols)):
       print(cols[i], decs[i])
       n['entry1/scan/measurement'][cols[i]].attrs['decimals'] = decs[i]


#del n['/entry1/measurement'] # delete else @default doesn't work

# test new file
new = nx.nxload('%s%i.nxs' %  (outpath, filenum))
#print(new.entry1.scan.tree)
#new.entry1.scan.plot()
new.plot()

new['entry1/scan/measurement/eta'].attrs



