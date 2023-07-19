# My Cattle Project

My Cattle Project is a web application designed to help farmers manage their cattle and track important information about each animal. The application allows users to record cattle details such as acquisition method, birth date, weight, and more. It also provides various reports and statistics to help farmers make informed decisions about their cattle.

## Features

- **Cattle Management**: Add, edit, and delete cattle information, including acquisition method, birth date, weight, and other details.

- **Livestock Movement Tracking**: Keep track of cattle movements, including acquisition, loss, and transfers between groups.

- **Group Management**: Organize cattle into groups for better organization and management.

- **Weight Estimation**: Estimate cattle weight based on their entry date or end date using historical weight data.

- **Reports and Statistics**: Generate reports and statistics to analyze cattle data, track weight changes, and monitor acquisition and loss over time.

- **Herd Management**: Organize cattle into herds, allowing users to create herds and track information about each herd. Users can easily assign individual cattle to herds based on their characteristics or purpose. The application allows users to record herd details such as field,start date, herd leader, is active.

- **Field Management**: Record information about fields where cattle are kept. Users can add details such as field size, location, and any specific conditions relevant to the field.

- **Livestock Movement Between Herds**: It allows  manage cattle movements between different herds for rotation or moving them for grazing purposes. This feature helps users optimize herd utilization and manage grazing effectively.

- **User Authentication**: Secure access to the application with user authentication and permissions.

## Installation

1. Clone the repository: `git clone https://github.com/JeskevicRasa/my_cattle.git
2. Install dependencies: `pip install -r requirements.txt`
3. Set up the database: `python manage.py migrate`
4. Create a superuser: `python manage.py createsuperuser`
5. Start the development server: `python manage.py runserver`

## Usage

1. Access the application in your web browser at `http://localhost:8000`.
2. Log in using your superuser account or create a new account with appropriate permissions.
3. Add cattle information using the provided forms and interfaces.
4. Manage cattle movements, group assignments, and other details from the user-friendly dashboard.
5. Generate reports and statistics to analyze cattle data and make informed decisions.

## Contributing

Contributions to My Cattle Project are welcome! If you find any bugs, have feature requests, or want to contribute code, please follow these steps:

1. Fork the repository on GitHub.
2. Create a new branch from the `main` branch.
3. Make your changes and commit them with descriptive commit messages.
4. Push your changes to your forked repository.
5. Create a pull request to the `main` branch of the original repository.

## License

My Cattle Project is open-source learning project, and it is not licensed yet.

## Support

If you encounter any issues or have questions about the project, please open an issue on GitHub
or contact us at krivojyte.r@gmail.com or Beata.

Happy cattle management! 🐮
