# FitTrack �️‍♂️💪

A fitness tracking web application developed for CITS5505, focusing on personal goal setting, progress tracking, and social fitness engagement.

<p align="center">
  <img src="https://raw.githubusercontent.com/username/CITS5505/master/static/images/logo.png" alt="FitTrack Logo" width="250" height="auto">
</p>

## Contributors

| Name<sup>1</sup>       | Student Number<sup>2</sup> | GitHub Name<sup>3</sup>       |
|------------------------|----------------------------|-------------------------------|
| Zihan Wu<sup>4</sup>    | 24372276<sup>5</sup>       | Warrenwu123<sup>6</sup>       |
| Jiajun Yang<sup>7</sup>  | 24242577<sup>8</sup>       | Atalantayang; 杨佳君<sup>9</sup> |
| Yosuke Inoue<sup>9</sup> | 24513446<sup>9</sup>       | yosuke0905<sup>9</sup>        |
| Young Wei<sup>9</sup>    | 23857911<sup>9</sup>       | SayHiToYoung<sup>9</sup>      |

## 📋 Table of Contents
- [Overview](#-overview)
- [Features](#-features)
- [Installation](#-installation)
- [Usage](#-usage)
- [Testing](#-testing)
- [Project Structure](#-project-structure)
- [Contributing](#-contributing)
- [License](#-license)

## 🔍 Overview
FitTrack is a Flask-based web application that empowers users to set fitness goals, track their progress, visualize achievements, and compete on leaderboards. Users can also share their fitness data with others based on customizable permissions. The application uses SQLite for database management and includes comprehensive unit tests.

## ✨ Features

### 🏠 Home Page
- Welcome screen with intuitive navigation
- Quick access to all app features
- Authentication options for new visitors

### 🔐 Authentication
- **Register**: Create your personal FitTrack account
- **Login**: Secure access to your fitness data
- **Logout**: End your session safely

### 🎯 Goal Setting & Tracking
- Create personalized fitness goals with targets and deadlines
- Track daily progress toward your goals
- Log workout sessions and activities
- Monitor metrics like duration, intensity, and calories burned

### 📊 Dashboard
- Visualize progress and achievements over time
- View personalized statistics and trends
- Interactive charts showing performance metrics
- Achievement badges and milestone recognition

### 🏆 Leaderboards
- View rankings of most active users
- See users with the most achievements
- Compare your performance with other users
- Weekly and all-time leaderboards

### 🔄 Data Sharing
- Set permissions for sharing your fitness data
- Control which users can access your dashboard information
- Customize privacy settings for different metrics
- Request access to view other users' progress

### 👤 User Profile
- Update personal information
- Change password
- View activity summary
- Manage data sharing permissions

## 🔧 Installation

### Prerequisites
- Python 3.7+
- pip (Python package manager)
- Git

### Step 1: Clone the Repository
```bash
git clone https://github.com/warrenwu123/CITS5505.git
cd CITS5505
```
### Step 2: Create a Virtual Environment
For Windows:
```
bash
python -m venv venv
```
For macOS/Linux:
```
bash
python3 -m venv venv
```
### Step 3: Activate the Virtual Environment
For Windows:
```
bash
venv\Scripts\activate
```
For macOS/Linux:
```
bash
source venv/bin/activate
```
### Step 4: Install Dependencies
```
bash
pip install -r requirements.txt
```
## 🚀 Usage
### Running the Application

Ensure your virtual environment is activated
Start the application:

```
bash
flask run
```
Open your browser and navigate to http://127.0.0.1:5000/

### features

Create a new account or login with existing credentials
Set up your first fitness goal on the dashboard
Begin tracking your activities and progress
Explore the leaderboards to see how you compare to others

## 🧪 Testing
FitTrack uses pytest for comprehensive unit testing. To run the tests:

Ensure your virtual environment is activated
Run the test suite:
```
bash
pytest
```
For more detailed test output, including coverage information:
```
bash
pytest --cov=app
```
To run specific test files:
```
bash
pytest tests/test_auth.py
```
## 📁 Project Structure
CITS5505/
├── app            # Main application folder
  ├── main.py              # Main application file
  ├── models.py           # Database models
  ├── routes/             # Blueprint routes for different features
  │   ├── auth.py         # Authentication routes
  │   ├── dashboard.py    # Dashboard visualization routes
  ├── templates/          # HTML templates
  ├── static/             # Static assets (CSS, JS, images)
  ├── tests/              # Unit tests
  └── utils/              # Helper functions and utilities
├── config.py              # configration file
├── main.py               # the main entrance
├── seed_data.py          # initialized data for tables


## 👥 Contributing
Contributions are welcome! Please feel free to submit a Pull Request.
## 📄 License
This project is licensed under the MIT License - see the LICENSE file for details.

<p align="center">
  Developed with ❤️ for CITS5505
</p>
