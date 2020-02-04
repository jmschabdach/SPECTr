"""
Acquire a set of screenshots of the 3D view while rotating it.
Usage: copy-paste to the Python console in Slicer
Related work:
http://slicer-users.65878.n3.nabble.com/recording-movie-slicer-4-td4025866.html
https://gist.github.com/jcfr/5016384
"""

import os

TAKE_SCREENSHOT_DEFAULT_PATH = slicer.app.extensionsInstallPath+os.sep
TAKE_SCREENSHOT_DEFAULT_PATH = '/Users/Chase/Dropbox/Manuscripts/White_Matter_Networks_Manuscript/Network_Videos_WhiteBackground/Arcuate/'
TAKE_SCREENSHOT_DEFAULT_PREFIX = 'screenshot_'
PITCHROLLYAWINCREMENT = 1
YAWAMOUNT = 360

lm = slicer.app.layoutManager()
view = lm.threeDWidget(0).threeDView()
view.setPitchRollYawIncrement(PITCHROLLYAWINCREMENT)
view.yawDirection = view.YawLeft
screenshot_counter=0
for i in range(0,YAWAMOUNT,1):
  rw=view.renderWindow()
  wti=vtk.vtkWindowToImageFilter()
  wti.SetInput(rw)
  wti.Update()
  writer=vtk.vtkPNGWriter()
  filename = TAKE_SCREENSHOT_DEFAULT_PATH + TAKE_SCREENSHOT_DEFAULT_PREFIX + str(screenshot_counter).zfill(5) + '.png'
  screenshot_counter+=1
  print 'Written screenshot to: '+filename
  writer.SetFileName(filename)
  writer.SetInputConnection(wti.GetOutputPort())
  writer.Write()
  view.yaw()
  view.forceRender()
