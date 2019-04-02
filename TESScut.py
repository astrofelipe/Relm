from lightkurve.search import search_tesscut
from matplotlib import animation
from astroquery.mast import Catalogs
from astropy.coordinates import SkyCoord
from astropy.stats import SigmaClip
from photutils import MMMBackground
import numpy as np
import matplotlib.pyplot as plt
import argparse

parser = argparse.ArgumentParser(description='Extract Lightcurves from FFIs')
parser.add_argument('TIC', type=int, help='TIC ID or RA DEC')
parser.add_argument('Sector', type=int, help='Sector')
parser.add_argument('--size', type=int, default=21)


args = parser.parse_args()


target = Catalogs.query_object('TIC %d' % args.TIC, radius=0.05, catalog='TIC')
ra     = float(target[0]['ra'])
dec    = float(target[0]['dec'])
coord  = SkyCoord(ra, dec, unit='deg')



ahdu = search_tesscut(coord, sector=args.Sector).download(cutout_size=args.size, download_dir='.')
#w    = WCS(allhdus.hdu[2].header)
hdu  = ahdu.hdu

flux = hdu[1].data['FLUX']
bkgs = np.zeros(len(flux))

#Background
for i,f in enumerate(flux):
    sigma_clip = SigmaClip(sigma=3)
    bkg        = MMMBackground(sigma_clip=sigma_clip)
    bkgs[i]    = bkg.calc_background(f)


#flux = np.log10(np.abs(np.nanmin(flux)) + flux + 1)
time = hdu[1].data['TIME'] + hdu[1].header['BJDREFI']

def animate(i, fig, ax, flux, time, start=0):
    #ax.text(0.98, 0.98, time[i], transform=ax.transAxes, color='white', ha='right', va='top')
    #im = ax.matshow(flux[i+start], cmap=plt.cm.YlGnBu_r)
    im.set_array(flux[i+start])
    te.set_text('%.4f' % time[i+start])
    return im, te

fig, ax = plt.subplots(figsize=[2,2])
ax.set_xticks([])
ax.set_yticks([])
ax.axis('off')
fig.subplots_adjust(left=0.0, right=1.0, top=1.0, bottom=0.0)

im = ax.matshow(flux[0] - bkgs[0], cmap=plt.cm.YlGnBu_r, origin='lower')
te = ax.text(0.98, 0.98, '%.4f' % time[0], transform=ax.transAxes, color='white', ha='right', va='top', family="monospace")
#fig.tight_layout()


Writer = animation.writers['ffmpeg']
writer = Writer(fps=27, metadata=dict(artist='Me'), bitrate=3600)

ani = animation.FuncAnimation(fig, animate, fargs=(fig, ax, flux-bkgs[:,None,None], time), frames=len(flux),
                              interval=1, repeat_delay=0)

ani.save('%d.mp4' % args.TIC, writer=writer)
