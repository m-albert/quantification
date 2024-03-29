__author__ = 'malbert'

from matplotlib import cm
import mayavi.mlab as mlab
from mayavi.filters.transform_data import TransformData
import moviing

import moviepy.editor as mpy

mlab.options.offscreen = False
duration= 10 # duration of the animation in seconds (it will loop)
fps = 30
dt = 1
# nt = len(bs[0].times)
nt = 1
rotPeriod = 10
ibrains=range(len(bs))
alreadyZoomed = False
# ibrains=[0]

# currentAzimuth = 0

spacing = n.array(bs[0].spacing).copy()
spacing[1] *= -1
spacing[2] *= -1

shape = bs[0].ms[0].shape[::-1]

fig_myv = mlab.figure(size=(2000,2000), bgcolor=(0,0,0))
sfs = []
x,y,z = n.mgrid[0:shape[0],0:shape[1],0:shape[2]]
previous_time = -1

engine = mlab.get_engine()
# -------------------------------------------
scene = engine.scenes[0]
scene.scene.z_minus_view()

def make_frame(t):

    global previous_time,alreadyZoomed

    # print t
    time = int((t/dt)%nt)
    # pdb.set_trace()
    print 't,time',t,time
    global sfs
    my_cm = n.append([[0,0,0,0]],cm.gist_rainbow(n.linspace(0,255,len(ibrains)).astype(n.uint16)),0)
    my_cm = my_cm[:,:3]

    # pdb.set_trace()

    if len(sfs) != len(ibrains) or time != previous_time:
        mlab.clf() # clear the figure (to reset the colors)
        for isample in range(len(ibrains)):
            print 'isample: %s' %isample
            # data = ((n.array(bs[ibrains[isample]].objects[time]['labels'])>0)*(isample+1)).astype(n.float)
            data = ((n.array(bs[ibrains[isample]].objects[time]['labels'])>0)).astype(n.float)
            data = imaging.sortAxes(data,[2,1,0])
            s = ndimage.gaussian_filter(data,1)
            if len(sfs) != len(ibrains):
                print 'first time!'
                sf = mlab.pipeline.scalar_field(x,y,z,s)
                sf.spacing = spacing
                sfs.append(sf)
            else:
                print 'only updating!'
                sfs[isample].set(scalar_data=s)
            del data,s
            contours = [0.5]
            mlab.pipeline.iso_surface(sfs[isample],contours=contours,figure=fig_myv,color=tuple(my_cm[isample+1]))
            calcIso = True


    if t:
        print 'rotating'
        scene.scene.camera.azimuth(360./rotPeriod/fps)
        scene.scene.render()
    if not alreadyZoomed:
        scene.scene.camera.zoom(1.25)
        scene.scene.camera.zoom(1.25)
        scene.scene.camera.zoom(1.25)
        scene.scene.render()
        alreadyZoomed = True

    previous_time = time
    # return
    return mlab.screenshot(antialiased=True)

# make_frame(0)
animation = mpy.VideoClip(make_frame, duration=duration)
animation.write_gif("%s/results/video_30fps_1nt_zoom.gif" %bs[0].dataDir, fps=fps) # export as GIF (slow)

# animation.write_videofile("%s/results/testvideo2.mp4" %bs[0].dataDir, fps=fps)