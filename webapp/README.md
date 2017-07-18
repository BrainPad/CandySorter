Copyright 2017 BrainPad Inc. All Rights Reserved.
webapp
===

## Note
This software is designed to work with Python2.7 under following condtions:
- This software depends on the following libraries:
  - OpenCV 3.2 (need to be compiled from source)
    - Refer to [installation instructions](../setup/linux_box.md), under _OpenCV3.2 installation_ for installation.
  - Software you install with pip
  ```
  $ pip install -r requirements.txt
  # ex)
  #  - TensorFlow
  #  - Flask
  #  - uWSGI
  #  - google-cloud
  #  - scipy
  #  - gemsim
  #  ...
  ```


### Environment variables
```
export FLASK_ENV='prd'   # choices are 'prd', 'stg' or 'dev'
export GOOGLE_APPLICATION_CREDENTIALS="path_to_your_own_credential_file"
export PYTHONPATH=/usr/local/lib/python2.7/dist-packages
```

### word2vec
- download word2vec model for English from https://github.com/mmihaltz/word2vec-GoogleNews-vectors
  - (* you need to follow the link below to get from the [MIRROR](https://drive.google.com/file/d/0B7XkCwpI5KDYNlNUTTlSS21pQmM/edit?usp=sharing). Be careful you cannot downlod it from git.)
- copy it to the 'models' directory
```
$ mkdir -p ~/FindYourCandy/webapp/candysorter/resources/models
```
- download japanese language model of word2vec from http://qiita.com/Hironsan/items/513b9f93752ecee9e670 .
And copy it to the same directory.

(* If you don't need Japanese model, just comment out the item of 'ja' within the declaration of WORD2VEC_MODEL_FILES list in [config.py](./candysorter/config.py). )

### inception-V3
- download [inception-v3 model](http://download.tensorflow.org/models/image/imagenet/inception-2015-12-05.tgz)
- copy it to the 'models' directory
```
$ mkdir -p ~/FindYourCandy/webapp/candysorter/resources/models
$ cd ~/FindYourCandy/webapp/candysorter/resources/models
$ wget http://download.tensorflow.org/models/image/imagenet/inception-2015-12-05.tgz
$ tar xvzf inception-2015-12-05.tgz
```

### CloudML
#### create your own bucket for CloudML
- [create your own bucket](https://cloud.google.com/storage/docs/creating-buckets) in your project
- replace some environments in `webapp/candysorter/config.py`

```
# replace "YOUR-OWN-BUCKET-NAME" to your own bucket name
CLOUD_ML_BUCKET        = 'gs://{YOUR-OWN-BUCKET-NAME}'
CLOUD_ML_PACKAGE_URIS  = ['gs://{YOUR-OWN-BUCKET-NAME}/package/trainer-0.0.0.tar.gz']
CLOUD_ML_PYTHON_MODULE = 'trainer.train'
CLOUD_ML_TRAIN_DIR     = 'gs://{YOUR-OWN-BUCKET-NAME}/{job_id}/checkpoints'
CLOUD_ML_LOG_DIR       = 'gs://{YOUR-OWN-BUCKET-NAME}/logs/{job_id}'
CLOUD_ML_DATA_DIR      = 'gs://{YOUR-OWN-BUCKET-NAME}/{job_id}/features'
```
( https://github.com/BrainPad/FindYourCandy/blob/master/webapp/candysorter/config.py#L60-L65 )

#### build and upload package to GCS
- execute shell for build and upload package
- reopen your terminal

```
# replace {YOUR-OWN-BUCKET-NAME} to your own bukcet name
$ cd ~/FindYourCandy/train
$ bash build_package.sh gs://{YOUR-OWN-BUCKET-NAME}/package/
# make sure you have a trailing slash at the end of the command above
```

### Configuration files
- `candysorter/config.py`
  - WORD2VEC_MODEL_FILE="path_to_GoogleNews-vectors-negative300.bin.gz"
     default path:
       candysorter/resources/models/GoogleNews-vectors-negative300.bin.gz

### Network
- TCP port 18000 need to be exposed to browser.

## Run app
After tuning the camera, you can start webapp.
```
$ sudo systemctl start uwsgi-webapp.service
```
In this setup senario, the next command is not used. We use nginx+uWSGI instead.
```
# Run app. This requres environment variables.
$ python2 run.py  # Be sure to use python2.7
```

## UI
- Acceess http://{LINUX_BOX_IP}:18000/predict by chrome browser after app launched
- We provide "Full Screen Mode". Please setup following instruction.

#### setup for Full Screen Mode
- open setup menu and tap "Add to Home screen"
![](../setup/image/tablet_ui/1.png)

- name to icon on Home screen
![](../setup/image/tablet_ui/2.png)

- tap icon
![](../setup/image/tablet_ui/3.png)
![](../setup/image/tablet_ui/4.png)
![](../setup/image/tablet_ui/5.png)



## API example
##### Morphological Analysis
```sh
$ curl -i -H "Content-type: application/json" -X POST http://{LINUX_BOX_IP}:18000/api/morphs \
    -d '{"text": "I like chewy chocolate candy", "id": "test"}'
```

##### Similarities

```sh
$ curl -i -H "Content-type: application/json" -X POST http://{LINUX_BOX_IP}:18000/api/similarities \
    -d '{"text": "I like chewy chocolate candy", "id": "testid"}'
```

##### Reset the model for the relation of labels and candies
If you keep teaching labels to the system, at some point you want to clear all them out.
```sh
$ curl -i -H "Content-type: application/json" -X POST http://{LINUX_BOX_IP}:18000/api/_reset \
    -d '{"id": "testid"}'
```
