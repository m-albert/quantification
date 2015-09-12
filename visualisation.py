from dependencies import *


def contour(brains,attributes=["ms"],startAttr=0,spacing=None,contours=[1]):

    from traits.api import HasTraits, Range, Instance, \
            on_trait_change
    from traitsui.api import View, Item, Group

    from mayavi.core.api import PipelineBase
    from mayavi.core.ui.api import MayaviScene, SceneEditor, \
                    MlabSceneModel

    if spacing is None:
        spacing = brains[0].spacing
    else:
        spacing = spacing

    def getData(ibrain,itime,iattr):
        im = n.array(brains[ibrain].__getattribute__(attributes[iattr])[itime][:,600:1400])
        return im


    class MyModel(HasTraits):
        #n_track    = Range(0, len(tracks)-1, 0, )#mode='spinner')
        n_time  = Range(0, len(brains[0].__getattribute__(attributes[0])), 0, )#mode='spinner')
        n_attribute = Range(0,len(attributes)-1,startAttr)
        n_brain = Range(0,len(brains)-1,0)

        scene = Instance(MlabSceneModel, ())

        plot = Instance(PipelineBase)


        # When the scene is activated, or when the parameters are changed, we
        # update the plot.
        @on_trait_change('n_brain,n_time,n_attribute,scene.activated')
        def update_plot(self):
            # im = getData = getData(self.n_brain, self.n_time, self.n_attribute)
            im = getData(self.n_brain, self.n_time, self.n_attribute)
            # pdb.set_trace()
            if self.plot is None:
                # self.plot = self.scene.mlab.contour3d(im,contours=contours)
                sf = self.scene.mlab.pipeline.scalar_field(im)
                sf.spacing = spacing
                self.plot = self.scene.mlab.pipeline.iso_surface(sf,contours=contours)
            else:
                # pdb.set_trace()
                self.scene.mlab.clf()
                sf = self.scene.mlab.pipeline.scalar_field(im)
                sf.spacing = spacing
                # self.plot = self.scene.mlab.contour3d(im,contours=contours)
                self.plot = self.scene.mlab.pipeline.iso_surface(sf,contours=contours)

        # The layout of the dialog created
        view = View(Item('scene', editor=SceneEditor(scene_class=MayaviScene),
                         height=500, width=500, show_label=False),
                    Group(
                            '_', 'n_brain','n_time','n_attribute'
                         ),
                    resizable=True,
                    )

    my_model = MyModel()
    my_model.configure_traits()