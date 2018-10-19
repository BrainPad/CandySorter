# Step 1: Hardware setup
1. Print out [the marker sheet](./setup/image/marker_paper.pdf) in A3 paper and stick it on the center
(This sheet will be used during both setup and demo.)
2. Build the robot arm by following manuals.
3. Place the robot arm to attach the A3 paper on A-D side.
4. Plugin the power supply unit of the robot arm to AC outlet.
5. Place the camera(CDVU-06IP) as shown below. In this case, camera should built with joint extender, CDVU-04IP-A1.
Note: Due to unavailability of 'CDVU-04IP-A1' in some regions including japan, a small box of 27-32cm in height can be used instead.

# Step 2: Setup of pc

## Basic setup

* Ubuntu 18.01

### Update your installation
```
$ sudo apt-get update && sudo apt-get upgrade -y && sudo reboot
```

### Install Git, Python and curl
```
$ sudo apt install git python2.7 python-pip curl ansible
```

### Clone this repository
```
$ cd ~
$ git clone {repo_url}
```

### Create the installation files folder
```
$ mkdir -p _installationfiles/models
```

###  Setting up the Google Cloud Platform access


#### Install gsutil
To install gsutil (python application for managing google could storage) it is easier to just install the google cloud SKD

```
$ cd ~
$ curl https://sdk.cloud.google.com | bash
```

Close and reopen the shell for the changes to take effect.

#### Setup account and APIs
#### Install gsutil
To install gsutil (python application for managing google could storage) it is easier to just install the google cloud SKD

```
$ cd ~
$ curl https://sdk.cloud.google.com | bash
```

Close and reopen the shell for the changes to take effect.

#### Setup account and APIs
This demo requires API credential for Google Cloud Platform(GCP). If this is your first project to use GCP, you can get an account from [cloud.google.com](https://cloud.google.com/).

1. Create a new GCP project

2. Enable the following APIs and services on [API Manager](https://support.google.com/cloud/answer/6158841)
  - Google Cloud Storage and Google Cloud Storage JSON API
  - Vision API
  - Speech API
  - Natural Language API
  - Cloud ML API

3. Create a Storage Bucket - For all future steps, the name of this will be your bucket id.

4. Create a service account key file

    See [this doc](https://cloud.google.com/vision/docs/common/auth#set_up_a_service_account) to create a service account key
    - Service account: Compute Engine default service account
    - Key type: JSON
      - Save the JSON as /home/{user}/FindYourCandy/credentials.json and a copy in /home as well
      - (* Saving to different path or filename may require editing webapp.ini later)



5. Give the service account previously created access to the storage bucket. The required permissions are: 
    - Storage Object Admin (only this might suffice) 
    - Storage Object Creator
    - Storage Object Viewer

6. Set env variable
  - Add the following line (replace the path_to_your_own_credential_file with the actual JSON file path) to the last of `~/.bashrc` file.  

  ```
  export GOOGLE_APPLICATION_CREDENTIALS="path_to_your_own_credential_file"
  ```

7. Reopen the shell so that it takes effect


### Models

### English word vector
1. Download https://drive.google.com/file/d/0B7XkCwpI5KDYNlNUTTlSS21pQmM 
2. Copy the file to _installationfiles/models

### Inception v3
```
$ wget http://download.tensorflow.org/models/image/imagenet/inception-2015-12-05.tgz
$ tar xvzf inception-2015-12-05.tgz
```
Copy the .pb file to _installationfiles/models



## Using Ansible to install requrements and move scripts

### Copy hosts file
```
$ cd setup/docker/host
$ cp hosts.example hosts.file
```

### Edit the hosts.file and replace the required values
```
$ nano hosts.file

some_user={the current users username}
fyc_home={root directory of Find your candy}
cloud_ml_bucket={the name of the Cloud Storage Bucket you created previously}
```

```
$ ./setup.sh hosts.file
```


### Execute the ansible script
```
$ ./setup.sh hosts.file
```

This script will install Chrome, create required folders and move requried scripts. It will also build the docker images from source. 



### Upload ML model to Google Cloud storage 
```
$ cd /train
$ gcloud auth activate-service-account --key-file=../_installationfiles/credentials.json
$ ./build_package.sh gs://{bucket-id}/package/
```
Feel free to log on to [GCP Console](https://cloud.google.com), navigate to the storage bucket and ensure that the model has been uploaded. 


## Success

### Calibrate

#### Calibrate camera
```
$ bin/tune_camera.sh
```

#### Calibrate robot arm
```
$ bin/tune_robot.sh
```

### Run
```
$ bin/start_all.sh
```
Note that even though the command returns immediately, the webapp will take some time to start the first time.
To see the log output of the services, use the command
```
$ bin/tail_logs.sh
```

Go to settings and ensure that the correct microphone/input is selected, as this is often an issue it seems. 
