import os
import re
import sys
import glob
import shutil
import numpy as np
import nibabel as nb


def preproc(dataLoc, subject):
    subjectLoc = os.path.join(dataLoc, subject)
    apLoc = glob.glob(subjectLoc + '/*DTI_MB_AP_2*')[0]

    # order image files as stated in the bvals and bvecs files
    bvalues = ['b0_', 'b0995_', 'b1000', 'b1005']
    orderedList = []
    for bvalue in bvalues:
        imgFiles = [x for x in os.listdir(apLoc) if bvalue in x]
        imgFiles = sorted(imgFiles)
        orderedList += imgFiles

    # merge nii files
    mergedNiiLoc = os.path.join(apLoc, 'data.nii.gz')
    command = 'fslmerge -a {outputLoc} {imgList}'.format(
        outputLoc = mergedNiiLoc,
        imgList = ' '.join([os.path.join(apLoc, x) for x in orderedList]))

    if not os.path.isfile(mergedNiiLoc):
        print(command)
        os.popen(command).read()

    # bval and bvec copy
    for i in 'bval', 'bvec':
        raw_file = glob.glob(apLoc + '/*{0}*'.format(i))[0]
        shutil.copy(raw_file, os.path.join(apLoc, i+'s'))

    # eddy_corrent
    eddyOut = os.path.join(apLoc, 'data_eddy.nii.gz')
    command = 'eddy_correct {0} {1} 0'.format(mergedNiiLoc, eddyOut)

    if not os.path.isfile(eddyOut):
        print(command)
        os.popen(command).read()

    # bet
    betOut = os.path.join(apLoc, 'nodif_brain.nii.gz')
    command = 'bet {0} {1} -m -c 63 67 21 -f 0.25'.format(
        os.path.join(apLoc, orderedList[0]), betOut)

    if not os.path.isfile(betOut):
        print(command)
        os.popen(command).read()

    # dtifit
    faOut = os.path.join(apLoc, 'DTI')
    command = 'dtifit -k {merged} -o {basename} \
        -m {mask} -r {bvecs} -b {bvals}'.format(
            merged = mergedNiiLoc,
            basename = faOut,
            mask = os.path.join(apLoc, 'nodif_brain_mask.nii.gz'),
            bvecs = os.path.join(apLoc, 'bvecs'),
            bvals = os.path.join(apLoc, 'bvals'))
    print(command)
    os.popen(command).read()

if __name__=='__main__':
    dataLoc = '/home/kangik/CRC/allData/Data_with_skull'
    preproc(dataLoc, sys.argv[1])
