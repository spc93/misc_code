#import sys, os
import os

#need to install handbrake (cli version): sudo apt-get install handbrake-cli
# Version 2: Python 3 version and JoinAndEncodeHDVFiles has long big file names with data stamp


class EncodeDVDFilesByChapter():
    #assume each set of video files for a tape is in a saparate folder directly under the specified folder
    def __init__(self, topfolder, outfolder, encode_command, maxchapters = 10, file_ext = 'mp4'):
        # encode_command is the command string string with input file string, output file string and
        #   chapter number (%s, %s, %i)
        # e.g. 'HandBrakeCLI -i %s -o %s -c %i -e x264 -q 20 --comb-detect --decomb --nlmeans=light'

        #get list of video folders
        _ff = os.popen('ls '+topfolder)
        self.video_folders = _ff.read().splitlines()

        for dvdname in self.video_folders:

            for chapter in range(1, maxchapters + 1):
                #input 'file' is a folder containing dvd files
                _infile = topfolder + '/' + dvdname
                _outfile = outfolder + '/' + dvdname + '_chapter_' + str(chapter) + '.' + file_ext
                print('... tyring to encode files in %s to %s ...' % (_infile, _outfile))
                print(encode_command % (_infile, _outfile, chapter))
                os.system(encode_command % (_infile, _outfile, chapter))

# used to make all dvd .mpeg4 files (handbrake bug causes extra chapter to be created that is the whole dvd - these need deleting)
#encode_command = 'HandBrakeCLI -i %s -o %s -c %i -e x264 -q 20 --comb-detect --decomb --nlmeans=light'
#laptop_pcloud = EncodeDVDFilesByChapter('/home/spc93/pCloudDrive/__tmp__/dvd', '/home/spc93/pCloudDrive/__media__/mpeg4', encode_command, maxchapters=36)


class JoinAndEncodeHDVFiles():
    #assume each set of video files for a tape is in a saparate folder directly under the specified folder
    #if encode command specified then big files re-encoded, otherwise just joined
    #if delete_after_encode is true then delete joined file and only keep compressed file (normal!)
    #sorry it's a mess - better to re-write with small __init__ and .process method
    def __init__(self, topfolder, outfolder, encode_command = None, delete_after_encode = False, file_extension = 'm2t'):
        #get list of video folders
        _ff = os.popen('ls '+topfolder)
        self.video_folders = _ff.read().splitlines()

        maxbytes=1900000000 #keep under 2Gb limit (mpeg2 file)
        maxmins=60 #If time difference > maxmins then start new file

        tmpfile='%s/tmp' % topfolder

        for tapename in self.video_folders:
            small_file_folder = '%s/%s' % (topfolder,tapename)
            print(small_file_folder)

            outfile_num=1
            newfile=True
            oldtime=99999
            olddate='olddate'
            bsize=0

            #ff=os.popen('ls '+small_file_folder+'/*.m2t')
            ff=os.popen('ls '+small_file_folder+'/*.' + file_extension)
            files=ff.read()
            filelist=files.splitlines()

            for file in filelist:
               
                fstat=os.stat(file); fsize=float(fstat[6])            #size in bytes
                
                try:
                    #for dvgrab files
                    yearstr = file.split('.')[0][-4:]
                    datestr=file.split('.')[1]+'_'+file.split('.')[2][0:2]
                    timestr=file.split('_')[-1].split('.')[0]
                    (h,m,s)=timestr.split('-')
                    print("=== Looks like a dvgrab file...")
                except:
                    #dvsplit files (older files)
                    #yearstr = '' # need to get year string if needed
                    datestr=file.split('-')[1]
                    timestr=file.split('-')[2][0:-4]
                    (h,m,s)=timestr.split('_')

                time_min=float(h)*24.+float(m)+float(s)/60.

                
                if not newfile:
                    #bstat=os.stat(file); bsize=float(fstat[6])            #size in bytes

                    if bsize+fsize>maxbytes or (time_min-oldtime)>maxmins or datestr!=olddate:            #too big (max 4GB?            
                        
                        #big file so start a new one and process old one
                        if encode_command != None:
                            #compress file
                            #print encode_command % (('%s.m2t' % bigfile), ('%s.mpeg4' % bigfile) )
                            print('=== Encode command', encode_command % ((('%s.' + file_extension) % bigfile), ('%s.mpeg4' % bigfile) ))
                            #os.system(encode_command % (('%s.m2t' % bigfile), ('%s.mpeg4' % bigfile) ))
                            os.system(encode_command % ((('%s.' + file_extension) % bigfile), ('%s.mpeg4' % bigfile) ))
                            if delete_after_encode:
                                #os.system('rm %s.m2t' % bigfile)
                                os.system(('rm %s.' + file_extension) % bigfile)

                        outfile_num+=1
                        #bigfile=outfolder+'/'+tapename+'_'+str(outfile_num)
                        bigfile=outfolder+'/'+tapename+'_'+ yearstr + '_' + datestr + '_' + timestr #long file names with data stamp
                        bsize=0
                        print("File: "+file+" "+str(fsize/1000000000.0) + "Gb joining to "+bigfile+" with new new file" )
                        #os.system('cat '+file+' > '+ bigfile+'.m2t')
                        os.system('cat '+file+' > '+ bigfile+'.' + file_extension)
                        bsize+=fsize
                        newfile=True
                    else:
                        print("File: "+file+" "+str(fsize/1000000000.0) + "Gb joining to "+bigfile )
                        #os.system('cat '+bigfile+'.m2t'+' '+file+' > '+tmpfile)
                        #os.system('mv -f '+tmpfile+' '+bigfile+'.m2t')
                        os.system('cat '+bigfile+'.' + file_extension +' '+file+' > '+tmpfile)
                        os.system('mv -f '+tmpfile+' '+bigfile+'.' + file_extension)
                        bsize+=fsize
                        
                else:
                    #bigfile=outfolder+'/'+tapename+'_'+str(outfile_num)
                    bigfile=outfolder+'/'+tapename+'_'+ yearstr + '_' + datestr + '_' + timestr #long file names with data stamp
                    print('=== bigfile:', bigfile)
                    print("File: "+file+"  joining to "+bigfile )
                    #os.system('cat '+file+' > '+ bigfile+'.m2t')
                    os.system('cat '+file+' > '+ bigfile+'.' + file_extension)
                    bsize+=fsize        

                oldtime=time_min
                olddate=datestr
                newfile=False
                #print time_min
                #print 'cat '+file+' to '+bigfile
                #raise('ValueError')


            os.system('rm '+tmpfile)

            #compress last file
            #print encode_command % (('%s.m2t' % bigfile), ('%s.mpeg4' % bigfile) )
            if encode_command != None:
                print(encode_command % ((('%s.' + file_extension) % bigfile), ('%s.mpeg4' % bigfile) ))
                #os.system(encode_command % (('%s.m2t' % bigfile), ('%s.mpeg4' % bigfile) ))
                os.system(encode_command % ((('%s.' + file_extension) % bigfile), ('%s.mpeg4' % bigfile) ))
            if delete_after_encode:
                #os.system('rm %s.m2t' % bigfile)
                os.system(('rm %s.' + file_extension) % bigfile)





#encode_command = 'HandBrakeCLI -i %s -o %s -e x264 -q 22'
#test = JoinAndEncodeHDVFiles('/media/spc93/Data/hd_tapes', '/media/spc93/Data/mpeg4', encode_command = encode_command, delete_after_encode = True )
#part = JoinAndEncodeHDVFiles('/media/spc93/Data/hd_part/', '/media/spc93/Data/mpeg4', encode_command = encode_command, delete_after_encode = True )

#Recommended settings for x264 and x265 encoders:
#RF 18-22 for 480p/576p Standard Definition1
#RF 19-23 for 720p High Definition2
#RF 20-24 for 1080p Full High Definition3
#RF 22-28 for 2160p 4K Ultra High Definition4


########################### march 2020 #############
#################### new parameter string: file extension (.m2t or .dv etc)

#encode_command = 'HandBrakeCLI -i %s -o %s -c %i -e x264 -q 20 --comb-detect --decomb --nlmeans=light' # deinterlace for dvd/dv files

#encode_command = 'HandBrakeCLI -i %s -o %s -e x264 -q 20 --comb-detect --decomb --nlmeans=light'
#dad_dv_tapes = JoinAndEncodeHDVFiles('/media/spc93/MyBook/dad_dv_video_dvgrab/', '/media/spc93/MyBook/dad_dv_video_dvgrab_mpeg4', #encode_command = encode_command, delete_after_encode = True, file_extension = 'dv')

#no encode - join only dont delete
#dad_dv_tapes = JoinAndEncodeHDVFiles('/media/spc93/MyBook/dad_dv_video_dvgrab/', '/media/spc93/MyBook/dad_dv_video_dvgrab_mpeg4', #encode_command = None, delete_after_encode = False, file_extension = 'dv')

encode_command = 'HandBrakeCLI -i %s -o %s -e x264 -q 22'
#first folder is the one that contains individual folders e.g. tape63
#newhdv = JoinAndEncodeHDVFiles('/media/spc93/ToshibaUSB/video', '/media/spc93/ToshibaUSB/out', encode_command = encode_command, delete_after_encode = True )
newhdv = JoinAndEncodeHDVFiles('/home/spc93/Videos', '/home/spc93/Videos', encode_command = encode_command, delete_after_encode = True )
