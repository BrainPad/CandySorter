### Feature extraction
There are two feature extractors in this folder, feature_extractor and paralell_extractor. The feature 
extractor is used by the application in learn mode when training a model using the interface. This way of training only supports four 
categories and is not efficient. The paralell extractor does the same as the featue extractor, only it does so by spawning multiple 
processes. This allows it to extract features from a greater datasat in a much smaller amout of time, especially if run on 
a more powerfull machine, such as a powerfull GCP Compute Engine instance. 

#### Note
While most of the functionality of the paralell extractor, such as applying rotation to the images, are exposed through variables, 
the application of several rounds of random gamma adjustments are hard-coded and must be changed though modification of the code.
The relevant code can be found on line 269. 
```
for gamma_min, gamma_max in [(0.9, 1), (0.5, 0.9), (1, 1.3)]:
```
Where the three tuples define (min, max) values for the random gamma correction, and the numer of tuples defines how many different 
gamma adjusted features will be created per input file. 


### Training
The training script can be packaged and uploaded to GCP Cloud engine. To start a job manually, use the following command, replacing the required values. On unix, use \ instead of ^. Please the the Google Cloud ML documentation.
```
gcloud ml-engine jobs submit training {job_name} ^
--module-name=trainer.train ^
--scale-tier=basic ^
--packages=gs://path/to/trainer-0.0.0.tar.gz ^
--python-version=3.5 ^
--region=us-central1 ^
--runtime-version=1.8 ^
--project={project-name} ^
-- ^
--data_dir=gs://path/to/output ^
--test_dir=gs://path/to/output ^
--log_dir=gs://path/to/{job_name}/logs ^
--train_dir=gs://path/to/{job_name}/train ^
--plot_dir=gs://path/to/{job_name}/plots ^
--active_test_mode ^
--epochs={value} ^
--keep_prob={value} ^
--hidden_size={value} ^
--batch_size={value} 
```

The training script can also be run locally, in which case only the arguments following -- are applicable


### Plotter
The training script, if set to test mode, will produce a file called plot_data.sjon, which contains the required data to plot accuracy and loss using training, both overall and per label. This file can be plotted using the plotter.py. It is used by passing it the path to the plot file. 
```
> python plotter.py /path/to/plot_data.json
```
