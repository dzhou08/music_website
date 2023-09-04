# Setup
1. Open the "iTerm" or "Terminal" application
1. In the selected application, enter `mkdir dev_music_website` - makes a new folder named `dev_music_website` (if there already exists a folder with the same name, choose a different name (but use the different name from now on))).
1. Enter `cd dev_music_website`
1. Install docker if necessary with the instructions below:
    1. Go to this [Docker website](https://www.docker.com/get-started/), and choose the right version to download.
# Build Website with Docker
1. Enter `docker build -t fastapi:latest .`
1. Enter `docker run -p 8000:8000 fastapi:latest`
# Visit Website
1. Now you can access `http://localhost:8000/`

# Push Docker Image to AWS ECR
# More details can be found in this web page:

1. `docker tag fastapi:latest 907893623888.dkr.ecr.us-east-2.amazonaws.com/skyline-music`

1. `echo $(aws ecr get-login-password --region us-east-2) | docker login -u AWS --password-stdin 907893623888.dkr.ecr.us-east-2.amazonaws.com`

1. `docker push 907893623888.dkr.ecr.us-east-2.amazonaws.com/skyline-music`

1. `ssh -i ../dev_music_website_pem/skyline-music.pem ec2-user@ec2-3-141-100-44.us-east-2.compute.amazonaws.com`

1. `docker pull 907893623888.dkr.ecr.us-east-2.amazonaws.com/skyline-music:latest`

1. `sudo service docker restart`

1. `exit`

1. `ssh -i ../dev_music_website_pem/skyline-music.pem ec2-user@ec2-3-141-100-44.us-east-2.compute.amazonaws.com`

1. `docker run -p 8000:8000 907893623888.dkr.ecr.us-east-2.amazonaws.com/skyline-music`

