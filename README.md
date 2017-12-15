sdsapp
======
    
1. Download and unpack application
wget https://github.com/candle645/sdsapp/raw/master/sdsapp-0.1.tar.gz
tar -xvf sdsapp-0.1.tar.gz
cd sdsapp-0.1
 
2. Install Pyramid framework
apt install python-pyramid
 
3. Setup Python environment
export VENV=~/env
python3 -m venv $VENV
$VENV/bin/pip install --upgrade pip setuptools
 
4. Setup Pyramid framework 
$VENV/bin/pip install "pyramid==1.9.1"

5. Setup sample application 
cd ~/sdsapp-0.1
$VENV/bin/pip install -e ".[testing]"

6. Start sample application
$VENV/bin/pserve dockerenv.ini

7. Application runs as web server and accept connections at port 6543 
Configure container ports to make it available on host system, if necessary
Run web browser and open "http://<youors server name or IP>:6543/"
