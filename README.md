# My Cattle - Cattle Management Web Application

My Cattle is a web application designed to assist cattle farmers in managing their cattle, herds, and fields. The application offers a centralized platform for recording and accessing essential information about livestock and fields, as well as generating livestock movement reports.

This README provides an overview of the application's features, including its installation process and usage guideline. 

## Features

- **Cattle Management**: The application allows users to record detailed information about each individual cattle, including acquisition method, birth date, weight, and other essential data. This centralized data storage enables easy access to cattle records at any time.

- **Group Management**: Organize cattle into age groups for better organization and management.

- **Herd Management**: Organize cattle into herds, allowing users to create herds and track information about each herd. Users can easily assign individual cattle to herds and allows recording herd details such as field,start date, herd leader, and status.

- **Field Management**: Record information about fields where herds are located. Users can add details such as field size, location, coordinates, and any other specific conditions relevant to the field. Additionally, farmers can assign herds to specific fields for better organization and management.

- **Dashboard**: Get a clear overview of active cattle by age group, herds, and fields.

- **Efficient Search**: Quick access to information about cattle, herds, and fields through efficient search functionality. Farmers can easily find specific data they need, helping to manage their cattle farm effectively.

- **Livestock Movement Report**: Generate detailed reports to track changes in their livestock over different age groups, monitor weight fluctuations, and observe acquisition and loss events within selected time periods. 

- **User Authentication**: Secure access to the application with user authentication.

## Installation

1. Clone original project repository without deployment settings for local development and testing: `https://github.comJeskevicRasa/my_cattle'
2. Install dependencies: pip install -r requirements.txt
3. Set up the database - note that this is running on SQLite by default, you will have to download and install it: python manage.py migrate
4. Create a superuser: python manage.py createsuperuser
5. Start the development server: python manage.py runserver`

## Usage

1. Access the Application: Open your web browser and navigate to http://localhost:8000.
2. Login or Create an Account: Log in using your superuser account or create a new account.
3. Manage Data: Use the navigation panel to access the interfaces for managing fields, herds, and cattle. Input relevant data for each section.
4. Explore Cattle Information: After inputting data, go to the main dashboard and access cattle details by age group, active herds, and fields.
5. Generate Reports: Create livestock movement reports to monitor changes in livestock across different age groups during selected time periods.


Happy cattle management! 🐮
