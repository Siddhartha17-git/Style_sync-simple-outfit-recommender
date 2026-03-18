# Outfit Recommender App

A web-based outfit recommendation system that uses machine learning to suggest personalized clothing combinations based on user preferences, weather conditions, and occasions.

Built with Flask, MongoDB, and scikit-learn.

---

## Features

- User authentication (signup/login with password hashing)
- Machine learning–based outfit recommendations
- User history tracking
- Responsive web interface
- MongoDB integration for data storage

---

## Tech Stack

- Backend: Flask (Python)
- Frontend: HTML, CSS, JavaScript
- Database: MongoDB (Atlas or Local)
- Machine Learning: scikit-learn, joblib
- Other: bcrypt, pymongo

---

## Installation

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/outfit-recommender.git
cd outfit-recommender
```

### 2. Create Virtual Environment
```bash
python -m venv venv
```

Activate environment:

**Windows**
```bash
venv\Scripts\activate
```

**Mac/Linux**
```bash
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

---

## Database Setup

### Local MongoDB
```bash
mongod
```

Create `.env` file:
```env
MONGODB_URI=mongodb://localhost:27017/
```

### MongoDB Atlas
```env
MONGODB_URI=mongodb+srv://<username>:<password>@cluster.mongodb.net/?retryWrites=true&w=majority
```

---

## Model Setup

```bash
python prepare_dataset.py
```

---

## Run the Application

```bash
python app.py
```

Open in browser:  
http://localhost:5000

---

## Project Structure

```
├── app.py
├── db_config.py
├── outfit_recommender.py
├── dataset.py
├── prepare_dataset.py
├── retrain_model.py
├── outfit_dataset.csv
├── outfit_recommender_model.joblib
├── outfit_images/
├── templates/
├── static/
├── .env
└── requirements.txt
```

---

## API Endpoints

| Method | Endpoint | Description |
|--------|---------|------------|
| GET    | `/` | Home |
| POST   | `/signup` | Register |
| POST   | `/login` | Login |
| GET    | `/logout` | Logout |
| GET    | `/profile/<user_id>` | Profile |
| PUT    | `/profile/update/<user_id>` | Update Profile |
| POST   | `/recommend` | Get Recommendations |

---

## Troubleshooting

- MongoDB not connecting → Check if MongoDB is running or verify URI  
- Model missing → Run `python prepare_dataset.py`  
- Port already in use → Change port in `app.py`  

---

## Future Improvements

- Image-based recommendations  
- Improved model accuracy  
- Deployment support  
- User feedback system  

---

---

## Acknowledgments

- Dataset inspired by outfit recommendation research  
- Developed as an academic project
