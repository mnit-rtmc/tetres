The following softwares are required to run the Tetres system.
1. python3
2. pip3
3. default-jre (not default-jre-headless)
4. python3-tkinter (can be installed by using sudo yum install python3-tkinter)
5. postgresql server

<br/><br/>
<h4>Instruction for running Tetres on linux systems </h4><br/>
update the postgresql server details in server/bin/dbinfo.py<br/>
Note: Use the format preserving tools to update the dbinfo.py like vi,nano,vim...
<br/>
<br/>

run the package_installer.sh to install the required libraries for python3. It will create a virtual environment, download and installs the required packages. You need to run only once.
<br/>
<br/>

To run the server, execute the start_server.sh<br/>
To run the User client, execute the start_user_client.sh<br/>
To run the admin client, execute the start_admin_client.sh<br/>
<br/>
<br/>


When the Client or Server was executed for the first time, it will ask for PyTICAS Server URL, PyTICAS Server Port, Data Directory Path, Log Level, and Maps provider.

PyTICAS server URL - the system URL or IP on which PyTICAS server is running.<br>
PyTICAS Port - default is 5000. The port on which PyTICAS server is running.<br>
Data Directory Path - The directory containing the containing the configuration files (like filters, maps, ...) and temp data.<br>
Maps Provider - Choose OSM. <br><br>

![alt text](config.png)

Data directory for user client is located in the 'user/data' of the repository. Data directory for admin client is located in the 'admin/data' of the repository. Use the 'Browse' button instead of typing. 

Configured details are stored at user/ticas.prefs for user clients and admin/ticas.prefs for admin. Our system uses the relative path to find the configuration file. It should be in the parent directory of executable jar. It can not read configurations from any other path.

It is suggested to not edit the configuration files manually. Later, you change the configuration by going to <b>Tools -> options</b> in the program.

<br/>
<br/>

Tested on Ubuntu 16.04 and Fedora 28.

