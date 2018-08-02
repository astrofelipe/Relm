import matplotlib
matplotlib.use('Agg')

import glob
import matplotlib.pyplot as plt
import numpy as np
import argparse
import os
import subprocess
import shlex
from astropy.io import fits
from joblib import Parallel, delayed

parser = argparse.ArgumentParser(description='FITS Animator')
parser.add_argument('Target', help='Folder or FITS file (activate Kepler mode for 2nd)')
parser.add_argument('Output', default='output.gif', help='Output filename')
parser.add_argument('--kepler', action='store_true', help='Takes images from a FITS file instead of individual ones')
parser.add_argument('--nomag', action='store_true', help='Uses flux instead magnitude')
parser.add_argument('--cmap', type=str, default='bone', help='Colormap to use (check Matplotlib documentation)')
parser.add_argument('--xlim', type=float, nargs=2, default=None, help='Limits on x axis')
parser.add_argument('--ylim', type=float, nargs=2, default=None, help='Limits on y axis')
parser.add_argument('--showframe', action='store_true', help='Show frame number on corner')
parser.add_argument('--noaxis', action='store_true', help='Hides axes from plots')
parser.add_argument('--ncpu', type=int, default=8, help='Number of CPUs to use')

args = parser.parse_args()

def make_image(i,f):
    img, hdr = fits.getdata(f, header=True)
    img[img<1] = np.nan

    if not args.nomag:
        img = np.log10(img)

    fig, ax = plt.subplots()
    ms = ax.matshow(img, cmap=args.cmap)

    #fig = plt.figure()
    #ax  = plt.Axes(fig, [0,0,1,1])

    if args.noaxis:
        fig.subplots_adjust(0,0,1,1)
        #ax.set_axis_off()
        plt.axis('off')
        ms.axes.get_xaxis().set_visible(False)
        ms.axes.get_yaxis().set_visible(False)
        #plt.imsave('itmp/%05d.png' % i, img, dpi=200)#, bbox_inches='tight')#, pad_inches=0)
    #fig.add_axes(ax)

    if args.xlim is not None:
        ax.set_xlim(args.xlim[0], args.xlim[1])

    if args.ylim is not None:
        ax.set_ylim(args.ylim[0], args.ylim[1])

    if args.showframe:
        ax.text(0.96, 0.98, '%d/%d' % (i,len(files)), color='lime', fontsize=8, transform=ax.transAxes, ha='right', va='top')

    fig.savefig('itmp/%05d.png' % i,dpi=72, bbox_inches='tight', pad_inches=0)

    plt.close()

    return 1

if args.kepler:
    print 'eeee'

else:
    files = np.sort(glob.glob(args.Target + '/*.fit*'))
    print '%d files found!' % len(files)

    if not os.path.isdir('itmp'):
        os.makedirs('itmp')

    res = Parallel(n_jobs=args.ncpu, verbose=10)([delayed(make_image)(i,f) for i,f in enumerate(files)])

    cmd     = shlex.split('ffmpeg -y -r 20 -i itmp/%%05d.png %s' % args.Output)
    subprocess.call(cmd)
    #process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
    #for line in process.stdout:
    #    print line
