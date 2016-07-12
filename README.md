# What is RsyncHero ?
RsyncHero is a threaded backup solution, It works on speeding and optimizing the backup process of rsync by running parallel pool of workers for the backup process and excluding file paths of common tmp files and other extenisons to save diskspace and bandwidth. In addition to that an easy-to-use web console is here to manage the backup server and clients.


## ScreenShots
#### Home
![](https://raw.githubusercontent.com/RamyAllam/RsyncHero/master/rsynchero_web/screenshots/home.png)
#### Client Control
![](https://raw.githubusercontent.com/RamyAllam/RsyncHero/master/rsynchero_web/screenshots/servercontrol.png)
#### Client Add
![](https://raw.githubusercontent.com/RamyAllam/RsyncHero/master/rsynchero_web/screenshots/serveradd.png)
#### Client Edit
![](https://raw.githubusercontent.com/RamyAllam/RsyncHero/master/rsynchero_web/screenshots/serveredit.png)

## Requirements
- Python3 with SQLite enabled
- Django
- SSH-Keys between backup server and clients

## How-To
1. Setup SSH-Key between the backup server and the clients.
```
[root@BACKUPSERVER ~]# ssh-copy-id root@$CLIENTIP
```https://raw.githubusercontent.com/RamyAllam/RsyncHero/master/rsynchero_web/screenshots/serveradd.png
2. Clone this repo and modify `vary.py` file with your prefered paths to backup.
3. Go to rsynchero_web and initiate the database.
```
cd rsynchero_web
python3 manage.py makemigrations
python3 manage.py migrate
python3 manage.py createsuperuser
```
4. Run the django server from the same directory and define your prefered IP and Port to bind on. 
Ex. to bind on all networks and port 8000
```
python3 manage.py runserver 0.0.0.0:8000
```
And for local network
```
python3 manage.py runserver
```
4. Enter the backup server IP and port in the brower add the clients from the web console.
5. Execute `main.py` from the ROOT dir and enjoy!
6. Do not forget to play around with your cron.