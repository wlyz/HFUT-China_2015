import Image, ImageDraw, ImageFont
import os.path
import time
import datetime

from design.models import parts, chain

icon_width_small = 40
icon_height_small = 40
icon_width_large = 80
icon_height_large = 80
icon_text_space = 10
icon_space_small = 30
icon_space_large = 30

def createFolder(contentType):
    basePath = 'downloads/'
    year     = str(time.localtime().tm_year)
    month    = str(time.localtime().tm_mon)
    day      = str(time.localtime().tm_mday)
    if not os.path.exists(basePath + year + '/'):
        os.makedirs(basePath + year + '/')
    basePath += year + '/'
    if not os.path.exists(basePath + month + '/'):
        os.makedirs(basePath + month + '/')
    basePath += month + '/'
    if not os.path.exists(basePath + day + '/'):
        os.makedirs(basePath + month + '/')
    basePath += day + '/'
    if not os.path.exists(basePath + contentType + '/'):
        os.makedirs(basePath + contentType + '/')
    basePath += contentType + '/'
    return basePath

def geneFileName(name, surfix):
    now = datetime.datetime.now()
    fileNameFormat = '%(year)i-%(month)i-%(day)i-%(hour)i-%(minute)i-%(second)i-%(name)s.%(extension)s'
    fileNameValue = {
                     'year' : now.year,
                     'month' : now.month,
                     'day' : now.day,
                     'hour' : now.hour,
                     'minute' : now.minute,
                     'second' : now.second,
                     'name' : name,
                     'extension' : surfix
                     }
    return fileNameFormat % fileNameValue

def drawOnePart(name, position, drawer, isSmall, icon_im):
    #draw the line
    if isSmall:
        w = icon_width_small
        h = icon_height_small
        s = icon_space_small
    else:
        w = icon_width_large
        h = icon_height_large
        s = icon_space_large
    lineStartX = position[0]
    lineStartY = position[1] + h/2 + 2.5
    lineEndX = position[0] + w + s
    lineEndY = position[1] + h/2 + 2.5
    drawer.line([(lineStartX, lineStartY), (lineEndX, lineEndY)], fill='#800000', width=5)
    #draw the icon
    icon_data = icon_im.getdata()
    for x in range(0, icon_im.size[0]):
        for y in range(0, icon_im.size[1]):
            if icon_data[y*icon_im.size[0]+x][3] != 0:
                drawer.point((position[0] + x, position[1] + y), fill=icon_data[y*icon_im.size[0]+x])
    #draw text
    font = ImageFont.truetype('static/fonts/HelveticaNeueDeskInterface.ttc', 10)
    drawer.text((position[0], position[1] + h + icon_text_space), name, fill='black', font=font)

def drawCurve(drawer, cbox, isForward):
    if isForward:
        drawer.line([cbox[0], cbox[1], cbox[2], (cbox[1] + cbox[3])/2], fill=(128,0,0,255), width=5)
        drawer.line([cbox[2], (cbox[1] + cbox[3])/2, cbox[0], cbox[3]], fill=(128,0,0,255), width=5)
    else:
        drawer.line([cbox[2], cbox[1], cbox[0], (cbox[1] + cbox[3])/2], fill=(128,0,0,255), width=5)
        drawer.line([cbox[0], (cbox[1] + cbox[3])/2, cbox[2], cbox[3]], fill=(128,0,0,255), width=5)

def drawSequence(sequenceInfo, width, height, file_path):
    newImage = Image.new('RGBA', (width, height), (255,255,255,255))
    drawer = ImageDraw.Draw(newImage)
    initX = 10
    initY = 10
    isForward = True
    index = 0
    while index < len(sequenceInfo):
        item = sequenceInfo[index]
        if isForward:
            if initX + icon_width_small + icon_space_small > width - 10:
                drawCurve(drawer, [initX, initY+ icon_height_small/2 + 2.5, initX + 10, initY + icon_height_small/2 + 2.5 + icon_height_small*2], isForward)
                initY = initY + icon_height_small*2
                isForward = not isForward
                initX -= icon_width_small + icon_space_small
            else:
                icon_im = Image.open(item['icon_file_name'])
                drawOnePart(item['name'], (initX, initY), drawer, True, icon_im)
                initX += icon_width_small + icon_space_small
                index+=1
        else:
            if initX < 10:
                initX += icon_width_small + icon_space_small
                drawCurve(drawer, [initX-10, initY+ icon_height_small/2 + 2.5, initX, initY + icon_height_small/2 + 2.5 + icon_height_small*2], isForward)
                initY = initY + icon_height_small*2
                isForward = not isForward
                
            else:
                icon_im = Image.open(item['icon_file_name'])
                drawOnePart(item['name'], (initX, initY), drawer, True, icon_im)
                initX -= icon_width_small + icon_space_small
                index+=1
    newImage.save(file_path)

def getSequenceResultImage(sequence, width, height, name):
    if sequence.startswith('_'):
        sequence = sequence[1:]
    sequenceList = sequence.split('_')
    sequenceInfo = list()
    for partid in sequenceList:
        partObj = parts.objects.get(part_id=partid)
        infoDict = {
            'name': partObj.part_name,
            'icon_file_name' : 'static/img/%s.png' % partObj.part_type,
        }
        sequenceInfo.append(infoDict)
    filename = createFolder('image') + geneFileName(name, 'png')
    drawSequence(sequenceInfo, width, height, filename)
    return '/' + filename