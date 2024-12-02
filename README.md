# **Library Management System**

## **Overview**

This is a web application designed to manage library operations, including tracking books, members, and transactions. 
It was developed as part of the [Developer Hiring Test for Frappe](https://frappe.io/dev-hiring-test).  
**Technology stack:** Flask, Jinja, and MySQL.

## **Steps to Get Started**

1. **Install Dependencies**  
   Use the following command to install all required packages:  
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure MySQL**  
   Update the `host`, `user`, and `password` variables in `setupDB.py`, `app.py`, and `test.py` with your MySQL credentials.  

3. **Database Initialization**  
   Create the database and tables by executing the `setupDB.py` script:  
   ```bash
   cd utils; python setupDB.py; cd ..```

4. **Launch the Application**  
   Start the Flask app using the command below:  
   ```bash
   python app.py
   ```  

