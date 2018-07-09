# Model setup, training, and testing.



### The following tools are used
- Tensorflow (In Windows tensorflow is not compatible with a Python version prior to 3.5)
- NumPy
- Inception v3



## Install

- Install python 3.6 (make sure to set environment variable)
- Install PyCharm or Anaconda (Python 3.6)

#### Windows:
- pip
        
        Enter C://python in Command Prompt and get pip, 'python get-pip.py', for further installations 
            pip install tensorflow==1.8.0
            pip install numpy
    Or install using PyCharm Project interpreter
- Inception v3 downlaod the file 'classify_image_graph_def.pb' and add to the trainer directory


#### macOS or OS X
- pip
       
        $ sudo easy_install pip
        $ pip3 install tensorflow==1.8.0
        $ pip install numpy
- Inception v3
 
        $ wget http://download.tensorflow.org/models/image/imagenet/inception-2015-12-05.tgz
        $ tar xvzf inception-2015-12-05.tgz
    Copy the .pb file to _installationfiles/models


## Run


### Preperation
##### Set up image directory for test and training data.
    You will need two separat directories separating test and training data, naming each folder inside the two directories after the label. 
    It is important to not have any duplicates.



##### Set features and labels
    After adding train and test data, run feature_extractor.py to write features and labels to json files.
 
  
   
     
         
### Start training
Once features and labels are extracted, set the following values appropriately to the amount of data used, in train.py.

- __Epochs__ - Number of iterations the training is run
- __Batch size__ - The number of training examples (images) utilised in one iteration, the higher batch size the more general. A batch size equal to one will update the gradient and the neural network parameters after each samlpe.
- __Number of hidden__ layers'- Given the data not being linearly separable, the model will require at least one hidden layer. 
- __Learning rate__ - A parameter that controls the weight adjustment. The lower the value, the slower it will adjust.
    
        Alternatively use the default values: 'epochs=50, batch_size=16, hidden layer size=3, learning rate = 1e-3'
    **Run _train.py_** for training


Train builds a transfer network (model developed for a task is reused as the starting point on a second task). For each epoch training is run on shuffled samples and loss minimized.
After running train.py, the model should be trained and stored in the train directory.