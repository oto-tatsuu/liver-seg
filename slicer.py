layoutManager = slicer.app.layoutManager()
view = layoutManager.sliceWidget("Red").sliceView()
renderWindow = view.renderWindow()
renderers = renderWindow.GetRenderers()
renderer = renderers.GetItemAsObject(0)

p0 = [1.0, 0.0, 0.0]
p1 = [0.0, 1.0, 0.0]

lineSource = vtk.vtkLineSource()
lineSource.SetPoint1(p0)
lineSource.SetPoint2(p1)
# Visualize
colors = vtk.vtkNamedColors()
mapper = vtk.vtkPolyDataMapper()
mapper.SetInputConnection(lineSource.GetOutputPort())
actor = vtk.vtkActor()
actor.SetMapper(mapper)
actor.GetProperty().SetLineWidth(4)
actor.GetProperty().SetColor(colors.GetColor3d("Peacock"))
renderer.AddActor(actor)
