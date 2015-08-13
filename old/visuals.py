from dependencies import *


def visual(tracks,attributes=["skeletonCoords","coordinates","skeletonNodes"]):

    from traits.api import HasTraits, Range, Instance, \
            on_trait_change
    from traitsui.api import View, Item, Group

    from mayavi.core.api import PipelineBase
    from mayavi.core.ui.api import MayaviScene, SceneEditor, \
                    MlabSceneModel


    def getData(itrack,itime,iattr):

        print 'getting data...'
        track_start = tracks[itrack][0].time
        track_end = tracks[itrack][-1].time

        if itime > track_end or itime < track_start:
            x,y,z,t = [0],[0],[0],[0]
        else:
            tmpTime = itime-track_start
            tmp = tracks[itrack][tmpTime].__getattribute__(attributes[iattr])
            if tmp is None: raise(Exception('attribute "%s" not computed yet' %attributes[iattr]))

            spacing = tracks[itrack][tmpTime].brain.spacing
            #pdb.set_trace()
            x,y,z = tmp[0]*spacing[0],tmp[1]*spacing[1],tmp[2]*spacing[2]

            if attributes[iattr] == 'skeletonCoords':
                t = tracks[itrack][tmpTime].nodeValues
                # t = n.ones((len(x),3))
                # t[tracks[itrack][tmpTime].nodeValues == 2] = n.ones(3)
                # t[tracks[itrack][tmpTime].nodeValues == 1] = n.array([0,1,0.])
                # t[tracks[itrack][tmpTime].nodeValues >2] = n.array([1,0,0.])
            else:
                t = n.ones(len(x))

        print x,y,z,t
        return x, y, z, t


    class MyModel(HasTraits):
        n_track    = Range(0, len(tracks)-1, 0, )#mode='spinner')
        n_time  = Range(0, n.max([tracks[i][-1].time for i in range(len(tracks))]), 0, )#mode='spinner')
        n_attribute = Range(0,len(attributes)-1,0)

        scene = Instance(MlabSceneModel, ())

        plot = Instance(PipelineBase)


        # When the scene is activated, or when the parameters are changed, we
        # update the plot.
        @on_trait_change('n_track,n_time,n_attribute,scene.activated')
        def update_plot(self):
            x, y, z, t = getData(self.n_track, self.n_time, self.n_attribute)
            if self.plot is None:
                #pdb.set_trace()
                self.plot = self.scene.mlab.points3d(x, y, z, t,
                                    scale_factor=1.,
                                    scale_mode='none',
                                    colormap='Spectral',
                                    vmin=0,vmax=5
                                    )
            else:
                self.scene.mlab.clf()
                self.plot = self.scene.mlab.points3d(x, y, z, t,
                                    scale_factor=1.,
                                    scale_mode='none',
                                    colormap='Spectral',
                                    vmin=0,vmax=5
                                    )
                # self.plot.mlab_source.set(x=x, y=y, z=z, scalars=t)
                # self.plot.mlab_source.x = x
                # self.plot.mlab_source.y = y
                # self.plot.mlab_source.z = z
                # self.plot.mlab_source.scalars = t

        # The layout of the dialog created
        view = View(Item('scene', editor=SceneEditor(scene_class=MayaviScene),
                         height=250, width=300, show_label=False),
                    Group(
                            '_', 'n_track', 'n_time','n_attribute'
                         ),
                    resizable=True,
                    )

    my_model = MyModel()
    my_model.configure_traits()


def visualBrain(tracks,startAttr=0,attributes=["skeletonCoords","segmentation","skeletonNodes"]):

    from traits.api import HasTraits, Range, Instance, \
            on_trait_change
    from traitsui.api import View, Item, Group

    from mayavi.core.api import PipelineBase
    from mayavi.core.ui.api import MayaviScene, SceneEditor, \
                    MlabSceneModel


    def getData(itime,iattr):

        spacing = tracks[0][0].brain.spacing

        if iattr == 1:
            s = tracks[0][0].brain.segmentation[0][itime]
            x,y,z = n.mgrid[0:tracks[0][0].brain.segmentation[0][itime].shape[0]*spacing[0]:spacing[0],
                            0:tracks[0][0].brain.segmentation[0][itime].shape[1]*spacing[1]:spacing[1],
                            0:tracks[0][0].brain.segmentation[0][itime].shape[2]*spacing[2]:spacing[2]]
            return x,y,z,s

        print 'getting data...'
        objs = []
        for itrack in range(len(tracks)):
            for iobj in range(len(tracks[itrack])):
                if tracks[itrack][iobj].time == itime: objs.append(tracks[itrack][iobj])

        #pdb.set_trace()
        if len(objs) == 0: x,y,z,t = [0],[0],[0],[0]
        else:
            x,y,z,t = [n.array([])]*4
            for iobj in range(len(objs)):
                tmp = objs[iobj].__getattribute__(attributes[iattr])
                tmp = tmp + n.array([objs[iobj].bbox[idim].start for idim in range(3)]).reshape((3,1))
                x = n.append(x,tmp[0]*spacing[0],0)
                y = n.append(y,tmp[1]*spacing[1],0)
                z = n.append(z,tmp[2]*spacing[2],0)

                if attributes[iattr] == 'skeletonCoords':
                    t = n.append(t,objs[iobj].nodeValues,0)
                else:
                    t = n.append(t,n.ones(len(tmp[0])),0)


        #print x,y,z,t
        return x, y, z, t


    class MyModel(HasTraits):
        #n_track    = Range(0, len(tracks)-1, 0, )#mode='spinner')
        n_time  = Range(0, n.max([tracks[i][-1].time for i in range(len(tracks))]), 0, )#mode='spinner')
        n_attribute = Range(0,len(attributes)-1,startAttr)

        scene = Instance(MlabSceneModel, ())

        plot = Instance(PipelineBase)


        # When the scene is activated, or when the parameters are changed, we
        # update the plot.
        @on_trait_change('n_time,n_attribute,scene.activated')
        def update_plot(self):
            x, y, z, t = getData( self.n_time, self.n_attribute)
            if self.plot is None:
                if len(x.shape)>1:
                    self.plot = self.scene.mlab.contour3d(x,y,z,t,contours=[0.5])
                else:
                    self.plot = self.scene.mlab.points3d(x, y, z, t,
                                        scale_factor=1.,
                                        scale_mode='none',
                                        colormap='Spectral',
                                        vmin=0,vmax=5
                                        )
            else:
                #pdb.set_trace()
                self.scene.mlab.clf()
                if len(x.shape)>1:
                    self.plot = self.scene.mlab.contour3d(x,y,z,t,contours=[0.5])
                    #self.plot.mlab_source.set(x=x,y=y,z=z,scalars=t)
                else:
                    self.plot = self.scene.mlab.points3d(x, y, z, t,
                                        scale_factor=1.,
                                        scale_mode='none',
                                        colormap='Spectral',
                                        vmin=0,vmax=5
                                        )
                # self.plot.mlab_source.set(x=x, y=y, z=z, scalars=t)
                # self.plot.mlab_source.x = x
                # self.plot.mlab_source.y = y
                # self.plot.mlab_source.z = z
                # self.plot.mlab_source.scalars = t

        # The layout of the dialog created
        view = View(Item('scene', editor=SceneEditor(scene_class=MayaviScene),
                         height=250, width=300, show_label=False),
                    Group(
                            '_', 'n_time','n_attribute'
                         ),
                    resizable=True,
                    )

    my_model = MyModel()
    my_model.configure_traits()