pip install . --break-system-packages
sudo apt install instaloader
instaloader --load-cookies firefox

docker build -t my-neo4j .
#docker run -d --name neo4j -p 7474:7474 -p 7687:7687 -v $HOME/neo4j/data:/data my-neo4j
