# Image handeling
Directory for handeling images.


#### Getting Started 
To tune the camera run camera_tune.py. 
All QR codes must be in the picture in order to proceed. The camera needs to be focused and have a high exposure. 
To set the detection for twist candy, set candy_type in from candysorter.config to 0, 1 for box candy.

#### Capture images for training data
Run capture_images_for_training.py. Make sure that the candy is well displayed for the camera, that they are fully within the black frame, and that the red edge boxes only cover one piece of candy each. To collect data, click on the space bar. Make sure to move the candy between each capture to get a variation in the pictures. Restart capture_images_for_training when starting on a new label.


#### Configure and detect candy
Capture_images_for_training.py and camera_tune.py uses cv2.VideoCapture() to take snapshots and show live feed camera, the snapshot taken of all candies is fed to detect.py. Variables for edge detection, margin, size etc. in detect.py are set in config.py. In order to get good images for training data or live demo, changes might have to be done to suite the given candy objects. 

The following variables dominates the success of the image detection: 

- __CANDY_DETECTOR_HISTGRAM_BAND:__ The span from black to white. Determines which  
- __CANDY_DETECTOR_HISTGRAM_THRES:__ The threshold for the histogram of an image. 
- __CANDY_DETECTOR_BIN_THRES:__ Partition an image using a determined threshold.
- __CANDY_DETECTOR_CLOSING_ITER:__ Number of iterations closing small holes inside the foreground objects, or small black points on the object. 
- __CANDY_DETECTOR_OPENING_ITER:__ Number of iterations closing small holes in the background of the foreground objects, or small black points. 
- __CANDY_DETECTOR_ERODE_ITER:__ Useful for removing small white noises or detach two connected objects etc. 
- __CANDY_DETECTOR_DILATE_ITER:__   Normally, in cases like noise removal, erosion is followed by dilation. Because, erosion removes white noises, but it also shrinks our object. So we dilate it. Since noise is gone, they won’t come back, but our object area increases. It is also useful in joining broken parts of an object.
- __CANDY_DETECTOR_BOX_DIM_THRES:__ The lowest dimension on a detected item. Tested on the Twist candy, 125 will exclude marsipan, while 100 will include it. A box dimension on 50 will split the Twist candy into 2 or 3 pieces.    
- __IMAGE_CAPTURE_DEVICE:__ 0 for internal camera, 1 for external


####### Image detection in detect.py
The image is converted to binary based on the image’s histogram. A histogram will show a graph of pixel grayscale color values between 0 and 255. 
The Laplacian of an image highlights regions of rapid intensity change and is used to detect edges. An image with high variance might need 3x3 while slightly less variance will need a 5x5 gradient mask edge detector. With 5x5, the gradient will be less sensitive to local noise.
In order to remove noise, closed and opening is used to remove small white holes in the background and foreground. Erode is then used to remove shade etc. around the object and then dilate widens the obejct to restore its size.

