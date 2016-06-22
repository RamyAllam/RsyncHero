# Intoduction
RsyncHero is an ennhanced backup solution for Linux machines, It works on developing, speeding and optimizing the backup process using Rsync.

# Requirements
- Python3
- Password-Less authentication between Backup server and Clients.

# How-To
1. Setup SSH-Key between the backup server and the clients.
2. Clone this repo and modify `vary.py` file with your prefered paths to backup.
3. Adjust the **number of threads** based on backup server hardware and network capacity.
3. Create `servers_ip.txt` file on the same path which includes the client IPs.
4. Execute `main.py` using python3 and enjoy!
