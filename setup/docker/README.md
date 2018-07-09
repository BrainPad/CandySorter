# Ansible/Docker setup

This folder contains the required files to run the application under Docker, using Ansible to setup the machine. 

# Container
The docker images for the application is contained in the folder *container*. There are four images

* Base
* OpenCV
* Robot
* Webapp

The *base* image installs python, supervisor, nginx and other basic requirements to a base Ubuntu 18.04 image. The *OpenCV* image builds OpenCV 3.4.1 from source and installs it into the image. 

The dependencies of the images are as follows:
* Base -> OpenCV -> Webapp
* Base -> Robot


## Usage
The images can be built manually, or using the helper script *build.sh* that takes the name of the container as the argument, and automatically tags the image with the current time and *latest* tag. 


# Host

The host folder contains Ansible configuration files for setting up the system to use Docker. The roles folder contains configuration for installing docker, chrome and creating and moving script files and required files. The setup.sh can be used to execute the ansible script. 

NB! The script is currently only uable for local deployment. Some minor changes to the parameters passed to ansible in the script must be made to enable remote configuration. 
