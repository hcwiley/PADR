import requests
import os
import time
import glob
import re

query = "landscape"
IMG_DIR = os.path.join(os.path.abspath('./'), "../MET")
MAX_OBJECTS = 2000

print("Downloading {} images from MET to {}".format(MAX_OBJECTS, IMG_DIR))

# get all the objects matching this query
response = requests.get(
    "https://collectionapi.metmuseum.org/public/collection/v1/search?hasImages=true&q={}".format(query))
objectIDs = response.json()['objectIDs']

imageInfos = []

# check which images we've got downloaded already
downloadedImgs = []
for imgPath in glob.iglob(IMG_DIR + "/*.jpg"):
  downloadedImgs.append(re.sub(r'\.jpg', '', os.path.basename(imgPath)))

for uid in objectIDs:

  imageInfo = {}
  imageInfo['uid'] = str(uid)

  # get the object details
  # NOTE: there's a lot of additional metadata here we'll probably want for labels at some point
  response = requests.get(
      "https://collectionapi.metmuseum.org/public/collection/v1/objects/{}".format(uid))

  objectDetails = response.json()
  # check if the response failed
  if not 'primaryImage' in objectDetails:
    continue

  primaryImage = objectDetails['primaryImage']

  # we can't use the image if it's not public domain or there's primaryImage
  if not objectDetails['isPublicDomain'] or not primaryImage:
    continue

  imgPath = os.path.join(IMG_DIR, '{}.jpg'.format(uid))

  # don't re-download images
  if uid in downloadedImgs:
    # already have it!
    # we are passing rather than continuing the loop so that we can update the imageInfos json with the data here every time.
    pass
  else:
    # save the image to the dir with the uid as the name
    imgData = requests.get(primaryImage).content
    with open(imgPath, 'wb') as handler:
      handler.write(imgData)

  # update the imageInfo json
  imageInfo['primaryImage'] = primaryImage
  imageInfo['imgPath'] = imgPath
  imageInfos.append(imageInfo)

  # sleep for 2 seconds
  time.sleep(2)

  # if we've reached the max number of objects, stop
  if len(imageInfos) == MAX_OBJECTS:
    break

  print("Downloaded {} ({}/{})".format(uid, len(imageInfos), MAX_OBJECTS))


# save the imageInfos to json file
imageInfosPath = os.path.join(IMG_DIR, 'imageInfos.json')
with open(imageInfosPath, 'w') as handler:
  handler.write(str(imageInfos))

print("Stored image info to {}".format(imageInfosPath))
