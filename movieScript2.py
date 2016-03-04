__author__ = 'malbert'

from matplotlib import cm
import mayavi.mlab as mlab
from mayavi.filters.transform_data import TransformData
import moviing

import moviepy.editor as mpy

mlab.options.offscreen = True
duration= 10 # duration of the animation in seconds (it will loop)
fps = 20
dt = 1
nt = len(bs[0].times)
rotPeriod = 10
ibrains=range(len(bs))

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

my_cm = n.append([[0,0,0,0]],cm.gist_rainbow(n.linspace(0,255,len(ibrains)).astype(n.uint16)),0)
my_cm = my_cm[:,:3]

surfacesDict = dict()
for itime in range(nt):
    for isample in ibrains:
        print itime,isample
        data = (n.array(bs[ibrains[isample]].objects[itime]['labels'])>0).astype(n.float)
        data = imaging.sortAxes(data,[2,1,0])
        s = sitk.gafi(sitk.SmoothingRecursiveGaussian(sitk.gifa(data),1.))
        isurf = mlab.pipeline.iso_surface(s,contours=0.5,figure=fig_myv,color=tuple(my_cm[isample+1]))
        # points = array(isurf.mapper.input.points)
        # mesh = tvtk.PolyData(points=points, polys=triangles)
        # mesh.point_data.scalars = temperature
        # mesh.point_data.scalars.name = 'Temperature'

def make_frame(t):

    global previous_time#,currentAzimuth

    # print t
    time = int((t/dt)%nt)
    # pdb.set_trace()
    print 't,time',t,time
    global sfs

    # pdb.set_trace()

    if len(sfs) != len(ibrains) or time != previous_time:
        mlab.clf() # clear the figure (to reset the colors)
        for isample in range(len(ibrains)):
            data = ((n.array(bs[ibrains[isample]].objects[time]['labels'])>0)*(isample+1)).astype(n.float)
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
            contours = [(isample+1)/2.]
            mlab.pipeline.iso_surface(sfs[isample],contours=contours,figure=fig_myv,color=tuple(my_cm[isample+1]))
            calcIso = True


    if t:
        print 'rotating'
        scene.scene.camera.azimuth(360./rotPeriod/fps)
        scene.scene.render()

    previous_time = time
    # return
    return mlab.screenshot(antialiased=True)

# make_frame(0)
animation = mpy.VideoClip(make_frame, duration=duration)
animation.write_gif("%s/results/video.gif" %bs[0].dataDir, fps=fps) # export as GIF (slow)
# animation.write_videofile("%s/results/testvideo2.mp4" %bs[0].dataDir, fps=fps)