Notes about the Code Challenge submitted by Giovanni Chajon:

I have included in the gioCodeCurve zip file 3 files:

1. processInv.python:

the file that will parse the CSV and will present the summary, it supports multiparallelism

2. extract.py

This program has a function that determines the compression of an origin file, places the content on the destination and creates any intermediary paths. 

The program can run from the command line to process a single log file

When using from command line please provide full paths when specifying the file 

e.g. usage:

python extract.py ./errors.log.gz ./gio.txt 


3.  I have provided a Dockerfile so you may test on an Ubuntu distro:

you may open the Dockerfile and see that it installs python3.7 and curl (to download the files), it will get them from google using the hashIds, unzip them and finally, it runs a bash shell. 

a. build the container with the following command:

docker build --tag=giochallenge .

b. run the container 

docker run -it --rm giochallenge

c. the container will be up to the point to run the program, do it with the following command

python3.7 processInv.py 


Feel free to contact me with any inquiries. I hope this code fulfills all your requirements.