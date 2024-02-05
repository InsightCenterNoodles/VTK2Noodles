
"""
Simple stand alone script for writing out each frame of a paraview animation. 
Run this script in the paraview GUI, change frame number to number of time steps you need
"""
from paraview.simple import *
frames = 0
while frames < 150:
    WriteTimeSteps = 0
    print("hello")

    contour1 = FindSource('Contour1')

    SetActiveSource(contour1)

    SaveData('path to folder' + str(frames) + '.ply', proxy=contour1, Filenamesuffix='_%.3d',EnableColoring=1)

    animationScene1 = GetAnimationScene()
    animationScene1.GoToNext()
    frames += 1
