# Training Provider Application

This application allows a training provider to offer their services online. It consists of a FastAPI backend and a Vue.js frontend. Potential customers can browse available trainings, view training dates, and book training sessions.

## Application Overview

The application is built using:
- **Backend**: FastAPI with MongoDB for data storage
- **Frontend**: Vue 3 with Vite and Vuetify 3 for UI components

It provides the following functionalities:

1. **Trainings Management**
   - Overview of all offered trainings (name, description, price, instructor, duration and max participants)
   - Display of all trainings in a specific time period
   - Creating, updating, and deleting trainings

2. **Training Dates Management**
   - Display of all dates for a specific training
   - Creating, updating, and deleting training dates

3. **Bookings Management**
   - Booking a training on a specific date
   - Viewing, updating, and cancelling bookings

## Backend API Endpoints

### Trainings

- `GET /api/v1/trainings` - Get a list of all trainings
- `GET /api/v1/trainings/time-period` - Get trainings available in a specific time period
- `POST /api/v1/trainings` - Create a new training
- `PUT /api/v1/trainings` - Update an existing training
- `DELETE /api/v1/trainings/{id}` - Delete a training

### Training Dates

- `GET /api/v1/training-dates` - Get a list of all training dates
- `GET /api/v1/training-dates?training_id={id}` - Get all dates for a specific training
- `POST /api/v1/training-dates` - Create a new training date
- `PUT /api/v1/training-dates` - Update an existing training date
- `DELETE /api/v1/training-dates/{id}` - Delete a training date

### Bookings

- `GET /api/v1/bookings` - Get a list of all bookings (admin only)
- `GET /api/v1/bookings?customer_email={email}` - Get bookings for a specific customer
- `POST /api/v1/bookings` - Create a new booking (public endpoint)
- `PUT /api/v1/bookings` - Update an existing booking
- `DELETE /api/v1/bookings/{id}` - Delete a booking

## Frontend Pages

- **Home**: Landing page with featured trainings
- **Trainings**: List of all trainings with filtering options
- **Training Details**: Detailed information about a training and its available dates
- **Booking Form**: Form to book a training on a specific date
- **My Bookings**: List of user's bookings with management options
- **Login**: Authentication page for users

## Authentication and Authorization

Most endpoints require authentication using JWT tokens. The following roles are available:

- **Admin**: Can manage all trainings, training dates, and bookings
- **User**: Can view trainings and training dates, and manage their own bookings

## Data Models

### Training

```json
{
  "name": "Python Programming",
  "description": "Learn Python programming from scratch",
  "price": 299.99,
  "instructor": "John Doe",
  "duration_hours": 16,
  "max_participants": 10
}
```

### Training Date

```json
{
  "training_id": "60d21b4667d0d8992e610c85",
  "start_date": "2023-06-15T09:00:00Z",
  "end_date": "2023-06-16T17:00:00Z",
  "location": "Online",
  "available_slots": 10
}
```

### Booking

```json
{
  "training_date_id": "60d21b4667d0d8992e610c86",
  "customer_name": "Jane Smith",
  "customer_email": "jane@example.com",
  "customer_phone": "+1234567890",
  "notes": "Special dietary requirements"
}
```

## Getting Started

### Running with Docker Compose (Recommended)

The easiest way to run the application is using Docker Compose:

```bash
docker-compose up --build
```

This will start:
- The backend API at http://localhost:8000
- The frontend application at http://localhost:3000
- MongoDB database
- Redis cache

### Running Locally

#### Backend

1. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set up environment variables (see `.env.example`)

3. Run the FastAPI application:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000
   ```

4. Access the API documentation at http://localhost:8000/api/docs

#### Frontend

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install Node.js dependencies:
   ```bash
   npm install
   ```

3. Run the development server:
   ```bash
   npm run dev
   ```

4. Access the frontend application at http://localhost:3000
