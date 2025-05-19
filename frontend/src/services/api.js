import axios from 'axios';

const apiClient = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  },
  timeout: 10000
});

// Request interceptor for adding the auth token
apiClient.interceptors.request.use(
  config => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  error => {
    return Promise.reject(error);
  }
);

// Response interceptor for handling common errors
apiClient.interceptors.response.use(
  response => response,
  error => {
    if (error.response && error.response.status === 401) {
      // Unauthorized, clear token and redirect to login
      localStorage.removeItem('token');
      // window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default {
  // Auth
  login(credentials) {
    const formData = new URLSearchParams();
    formData.append('username', credentials.email);
    formData.append('password', credentials.password);

    return apiClient.post('/v1/auth/login/', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      }
    });
  },

  // Trainings
  getTrainings() {
    return apiClient.get('/v1/trainings/');
  },

  getTrainingById(id) {
    return apiClient.get(`/v1/trainings/?id=${id}`);
  },

  getTrainingsByTimePeriod(startDate, endDate) {
    return apiClient.get(`/v1/trainings/time-period/?start_date=${startDate}&end_date=${endDate}`);
  },

  // Training Dates
  getTrainingDates(trainingId = null) {
    const params = trainingId ? `?training_id=${trainingId}` : '';
    return apiClient.get(`/v1/training-dates/${params}`);
  },

  getTrainingDateById(id) {
    return apiClient.get(`/v1/training-dates/?id=${id}`);
  },

  // Bookings
  getBookings(customerEmail = null) {
    const params = customerEmail ? `?customer_email=${customerEmail}` : '';
    return apiClient.get(`/v1/bookings/${params}`);
  },

  createBooking(bookingData) {
    return apiClient.post('/v1/bookings/', bookingData);
  },

  updateBooking(bookingData) {
    return apiClient.put('/v1/bookings/', bookingData);
  },

  cancelBooking(id) {
    return apiClient.delete(`/v1/bookings/${id}`);
  }
};
