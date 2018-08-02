import glob
import matplotlib.pyplot as plt
import numpy as np
import argparse
import os
import subprocess
import shlex
from astropy.io import fits
from tqdm import tqdm

parser = argparse.ArgumentParser(description='FITS Animator')
parser.add_argument('Target', help='Folder or FITS file (activate Kepler mode for 2nd)')
parser.add_argument('Output', default='output.gif', help='Output filename')
parser.add_argument('--kepler', action='store_true', help='Takes images from a FITS file instead of individual ones')
parser.add_argument('--nomag', action='store_true', help='Uses flux instead magnitude')
parser.add_argument('--cmap', type=str, default='bone', help='Colormap to use (check Matplotlib documentation)')

args = parser.parse_args()

if args.kepler:
    print 'eeee'

else:
    files = np.sort(glob.glob(args.Target + '/*.fit*'))

    if not os.path.isdir('itmp'):
        os.makedirs('itmp')

    #for i,f in enumerate(files):
    for i,f in enumerate(tqdm(files)):
        img, hdr = fits.getdata(f, header=True)
        if not args.nomag:
            img = np.log10(img)

        fig, ax = plt.subplots()
        ax.matshow(img, cmap=args.cmap)

        fig.savefig('itmp/%05d.png' % i, dpi=200, bbox_inches='tight')
        plt.close()

    cmd     = shlex.split('ffmpeg -y -r 10 -i itmp/%%05d.png %s' % args.Output)
    subprocess.call(cmd)
    #process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
    #for line in process.stdout:
    #    print line
