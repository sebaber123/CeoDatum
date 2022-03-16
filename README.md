# Set up

## Clone the repository
    
## Install and set up PostgreSQL

Install PostgreSQL in Linux using the command,

    sudo apt-get install postgresql postgresql-contrib

Now create a superuser for PostgreSQL

    sudo -u postgres createuser --superuser name_of_user
    
Login into the psql:    

    sudo -u postgres psql
    
Create the database user

    CREATE ROLE sebaber12 WITH LOGIN SUPERUSER PASSWORD 'sebas';
    
## Install pgAdmin4 and set up the database

First, import the repository signing GPG key and add the pgAdmin4 PPA to your system using the following commands.

    curl https://www.pgadmin.org/static/packages_pgadmin_org.pub | sudo apt-key add -
    sudo sh -c 'echo "deb https://ftp.postgresql.org/pub/pgadmin/pgadmin4/apt/focal pgadmin4 main" > /etc/apt/sources.list.d/pgadmin4.list' 

After adding the PPA, update the Apt cache and install pgAdmin4 package on your system.

    sudo apt update
    sudo apt install pgadmin4 

run the below command to configure it. This will add a login screen to pgAdmin4 web dashboard.

    sudo /usr/pgadmin4/bin/setup-web.sh 

Access pgAdmin4 Dashboard
    
    localhost/pgadmin4/browser/
    
To add a new server, click on “Add New Server” button.


![Screenshot from 2022-03-16 16-14-05](https://user-images.githubusercontent.com/37642068/158669075-38a22b76-452d-4670-8430-b6ad80a283f7.png)

Set up the server
  
![Screenshot from 2022-03-16 16-31-54](https://user-images.githubusercontent.com/37642068/158675101-fa5be6a3-1204-4eed-a270-14569b40a016.png)


![Screenshot from 2022-03-16 16-32-28](https://user-images.githubusercontent.com/37642068/158675112-5d217115-7c06-4340-bc43-bc5a03f0f765.png)

    * the password is 'sebas'

Then open the CeoDatum server and press the right click on 'Databases' and press the option 'Create > Database'
  
Create the database with the name 'CeoDatum'

![Screenshot from 2022-03-16 16-41-59](https://user-images.githubusercontent.com/37642068/158676615-6eaee186-83a9-43c1-93bb-88326f4a5de0.png)

press right click on the database 'CeoDatum' and select the option 'Query Tool'

In the 'query tool' menu copy the text of the file 'CeoDatum/database' and paste it on the 'Query Editor' then press the 'execute' button

## Install VirtualEnv

    pip install virtualenv
    
Go to the folder where you clone the repository (you have to be inside of the folder CeoDatum) and activate the virtual environment 

    source CeoDatumEnv/bin/activate
    
install the requirements of Ceodatum

    pip install -r requirements.txt

run the application

    cd CeoDatumEnv
    
    export FLASK_APP=index.py

    export FLASK_ENV=development
    
    flask run
    
# Enter to the URL:  http://127.0.0.1:5000/loginForm    

