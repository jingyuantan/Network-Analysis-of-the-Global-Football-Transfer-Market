Developer: Jing Yuan Tan
Supervisor: Derek Greene
Project Title: Network Analysis of the Global Football Transfer Market

File structure (Description of major files and folders only):
FT_Analysis\
  -----------
  app\
    static\
	css\ (Contains Cascading Style Sheet Documents used) 
	img\ (Contains Image files used)
	js\  (Contains JavaScript files used)
    templates\ (Contains HTML files of this project)
    __init__.py (To create the application object as an instance of class Flask and run)
    routes.py (Main file that manages the flow of the web application, like a controller in MVC concept) 
    models.py (Contains all the classes that define the database structure for this application)
  -----------
  app.py (The file that defines the Flask application instance)
  config.py (Consists of configuration settings of the application)
  delete.py (Execute this file to clear all the data in the database)
  populateDB.py (Execute this file to populate the database with latest data [variable name has to be change in the code to the file name containing the latest raw data from Transfermarkt].)
  app.db (The database of this project)


The code explanation is available as comments in routes.py.


To run this application, change current directory to /FT_Analysis/app and execute the following code:
$ python3 __init__.py

To run it at the background without disconnecting it when the terminal is closed, run this command:
$ nohup python3 __init__.py &