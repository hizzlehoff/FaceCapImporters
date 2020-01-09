# FaceCap Capture Importer v0.1

import maya.cmds as cmds
import os
import ntpath
import maya.mel

# Todo : Test with different framerates for audio syc.
# Todo : Set rotation order for transforms.
# Todo : Progress bar.

def CreateFaceCapCaptureRoot(name):
    #Todo : improve removal of non-maya compatible characters 
    name = name.replace("-","_")
    name = name.replace(" ","_") + "_TransformData"
    result = cmds.spaceLocator(n=name)
    cmds.addAttr(ln="Eye_L_X", attributeType='float', keyable=True)
    cmds.addAttr(ln="Eye_L_Y", attributeType='float', keyable=True)
    cmds.addAttr(ln="Eye_R_X", attributeType='float', keyable=True)
    cmds.addAttr(ln="Eye_R_Y", attributeType='float', keyable=True)
    cmds.xform(roo='zxy')
    return result

def CreateFaceCapCaptureBlendshapeRoot(parentObject, name):
    #Todo : improve removal of non-maya compatible characters 
    name = name.replace("-","_")
    name = name.replace(" ","_")+"_BlendshapeData"
    result = cmds.spaceLocator(n=name)
    cmds.parent("|"+result[0],parentObject)
    return result

def CreateFaceCapCaptureBlendshapeAttributes(parentObject, blendshapeObject, attributeNames):
    blendshapeAttributeNames = []

    cmds.select(parentObject+"|"+blendshapeObject)
    
    for blendshapeName in attributeNames[1:]:
        blendshapeAttributeNames.append(blendshapeName)
        cmds.addAttr(ln=blendshapeName, attributeType='float', keyable=True)

    return blendshapeAttributeNames

def CreateFaceCapCaptureKeyframes(data, scaleFactor, transformObj, blendshapeObj, blendshapeNames, framesPerSecond):
    frameTime = (float(data[1])/1000.0)*framesPerSecond
    cmds.currentTime(frameTime)
    
    CreateFaceCapTransformKeys(data, scaleFactor, transformObj)
    CreateFaceCapBlendShapeKeys(data, transformObj, blendshapeObj, blendshapeNames)

def CreateFaceCapTransformKeys(data, scaleFactor, transformObj):
    cmds.select(transformObj)
    cmds.setKeyframe(v=float(data[2])*scaleFactor, at='translateX')
    cmds.setKeyframe(v=float(data[3])*scaleFactor, at='translateY')
    cmds.setKeyframe(v=float(data[4])*scaleFactor, at='translateZ')

    cmds.setKeyframe(v=float(data[5]), at='rotateX')
    cmds.setKeyframe(v=float(data[6]), at='rotateY')
    cmds.setKeyframe(v=float(data[7]), at='rotateZ')

    cmds.setKeyframe(v=float(data[8]), at='Eye_L_X')
    cmds.setKeyframe(v=float(data[9]), at='Eye_L_Y')
    cmds.setKeyframe(v=float(data[10]), at='Eye_R_X')
    cmds.setKeyframe(v=float(data[11]), at='Eye_R_Y')

def CreateFaceCapBlendShapeKeys(data, transformObj, blendshapeObject, blendshapesAttributeNames):
    cmds.select(transformObj+"|"+blendshapeObject)
    index = 0
    for value in data[12:]:
        cmds.setKeyframe(v=float(value), at=blendshapesAttributeNames[index])
        index += 1

def FaceCapImportAudio(filePath):
    dirName, fileName = ntpath.split(filePath)
    name, extension = os.path.splitext(fileName)
    audioPath = ntpath.join(dirName, name+".wav")
    print("AudioPath:"+audioPath)
    
    if os.path.exists(audioPath):
        cmds.currentTime('0sec', edit=True)
        audioNode = cmds.sound(offset=0, file=audioPath)
        gPlayBackSlider = maya.mel.eval('$tmpVar=$gPlayBackSlider')
        cmds.timeControl(gPlayBackSlider, edit=True, sound=audioNode)
    else:
        print("Audio not found, load it manually.")

def FaceCapImport(*args):
    sceneScale = cmds.floatField("sceneScaleField", q=True, v=True)
    sceneFramesPerSecond = cmds.currentTime('1sec', edit=True)

    filePaths = cmds.fileDialog2(fileMode=1, caption="Select FaceCap Capture...")

    with open(filePaths[0], 'r') as file1:
        fileName = os.path.basename(filePaths[0])
        name, extension = os.path.splitext(fileName)

        print("Please wait...")

        captureRoot = CreateFaceCapCaptureRoot(name)
        blendshapeRoot = CreateFaceCapCaptureBlendshapeRoot(captureRoot[0], name)
        blendshapeNames = []
        
        for line in file1:
            line = line.strip()
            items = line.split(',')
            if 'bs' in items[0]:
                blendshapeNames = CreateFaceCapCaptureBlendshapeAttributes(captureRoot[0], blendshapeRoot[0], items)
            elif 'k' in items[0]:
                CreateFaceCapCaptureKeyframes(items, sceneScale, captureRoot[0], blendshapeRoot[0], blendshapeNames, sceneFramesPerSecond)

    cmds.playbackOptions(maxTime = cmds.currentTime(query = True))
    cmds.playbackOptions(animationEndTime = cmds.currentTime(query = True))

    FaceCapImportAudio(filePaths[0])

    print("All Done...")

def FaceCapImportWindow():

    if cmds.window("FaceCapWindow", exists = True):
        cmds.deleteUI("FaceCapWindow")
    
    window = cmds.window("FaceCapWindow", title="FaceCap Capture Import.", iconName='FaceCap', widthHeight=(300, 60), sizeable=False )
    cmds.window("FaceCapWindow", e=True, w=300, h=60)
    
    cmds.columnLayout( adjustableColumn=True)

    cmds.rowLayout( numberOfColumns=2, columnWidth2=(150,150), adjustableColumn=2)
    cmds.text('Scene Scale')
    cmds.floatField("sceneScaleField", value=1.0)
    cmds.setParent( '..' )

    cmds.rowLayout( numberOfColumns=1, adjustableColumn=1)
    cmds.button( label='Import', command=FaceCapImport)
    cmds.setParent( '..' )
    
    cmds.showWindow( window )

FaceCapImportWindow()
