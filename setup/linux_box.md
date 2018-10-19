Linux Setup
===

## OS installation
- Ubuntu 16.04.4 LTS Server or Desktop
- Choose “standard system utilities” and “OpenSSH server” as software selection

## Basic setup

- Update packages
```
$ sudo apt-get update && sudo apt-get upgrade -y && sudo reboot
$ sudo apt-get install ubuntu-desktop # if you have installed server edition
```

- Install Docker, git
```
$ sudo apt-get install git
$ sudo apt-get install docker
```

- Install Google Chrome (needed for web app)
```
$ wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | sudo apt-key add - 
$ sudo sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'
$ sudo apt-get update && sudo apt-get install google-chrome-stable
```

- Check Python version:
```
$ python -V
Python 2.7.12
```

- Install python-pip
```
sudo apt-get install python-pip
```

- Install ansible (must be version 2.3.0.0)
```
sudo pip install ansible==2.3.0.0
```

- Make sure that ~/.ansible is own by the user that will be running everything (i.e., not root)
- Check that everything is set up correctly
```
ansible -i hosts.file servers -m ping -vvv
```

- Create an SSH key, if necessary, save to default location (stting password to the key is not necessary):
```
ssh-keygen -t rsa
ssh-add
```

- Copy SSH key to the machine:
```
ssh-copy-id -i ~/.ssh/id_rsa.pub <user>@<ip>/addq
sudo ./setup.sh hosts.file ~/.ssh/id_rsa
```

- Create docker group and add current user to the group
```
sudo groupadd docker
sudo gpasswd -a $USER docker
```


## Setup for FindYourCandy
- Copy hosts file from `hosts.example` to `hosts.file`:
```
cd setup/docker/host
cp hosts.example hosts.file
```

- Update `hosts.file` with IP to the machine that will be running the slution. If it is the same machine as the one you are running the commands from, use ```ifconfig```. To update the IP, make sure that you put the right IP under `[servers]`

- Create `_installationfiles` folder:
```
$ mkdir -p ~/FindYourCandy/_installationfiles/models
```

- Copy credentials.json to `_installationfiles`
- Copy `GoogleNews-vectors-negative300.bin.gz` to `_installationfiles/models`
- Copy inception model to `_installationfiles/models`
```
$ cd ~/FindYourCandy/_installationfiles/models
$ wget http://download.tensorflow.org/models/image/imagenet/inception-2015-12-05.tgz
$ tar xvzf inception-2015-12-05.tgz
```

```
$ cd ~/FindYourCandy/setup/docker/container
$ ./build.sh base
$ ./build.sh opencv
$ ./build.sh robot
$ ./build.sh webapp
```
- Tune the camera and the robot arm
```
~/FindYourCandy/bin$ ./tune_camera.sh
~/FindYourCandy/bin$ ./tune_robot.sh
```
