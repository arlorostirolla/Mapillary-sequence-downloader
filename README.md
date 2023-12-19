# Mapillary-sequence-downloader
Mapillary sequence downloader

To download all mapillary sequences within a bounding box above a certain quality cutoff
  1. Set the quality cutoff (from 0.0 to 1.0)
  2. Go into google maps, select the point furthest north and east of the bounding box you want to capture, fill out this information in the get_bbox function
  3. Do the same thing with the point furthest south/west
  4.  run the script. it will first find/download all the images within 
      the bounding box, and then organize them into seperate folders for       every sequence
  5. if there are errors in the first phase, try running again with   first time = False
