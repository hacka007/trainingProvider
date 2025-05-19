<template>
  <div class="booking-form">
    <v-btn class="mb-4" prepend-icon="mdi-arrow-left" @click="goBack">
      Back
    </v-btn>

    <v-row v-if="loading">
      <v-col cols="12" class="text-center">
        <v-progress-circular indeterminate color="primary"></v-progress-circular>
      </v-col>
    </v-row>

    <v-row v-else-if="error">
      <v-col cols="12">
        <v-alert type="error">{{ error }}</v-alert>
      </v-col>
    </v-row>

    <template v-else-if="trainingDate && training">
      <v-row>
        <v-col cols="12">
          <v-card>
            <v-card-title class="text-h4">Book Training</v-card-title>
            <v-card-subtitle class="text-subtitle-1">
              {{ training.name }} - {{ formatDate(trainingDate.start_date) }}
            </v-card-subtitle>
            <v-card-text>
              <p class="mb-4">
                <strong>Location:</strong> {{ trainingDate.location }}<br>
                <strong>Date:</strong> {{ formatDateRange(trainingDate.start_date, trainingDate.end_date) }}<br>
                <strong>Time:</strong> {{ formatTime(trainingDate.start_date) }} - {{ formatTime(trainingDate.end_date) }}<br>
                <strong>Price:</strong> {{ training.price }}<br>
                <strong>Available Slots:</strong> {{ trainingDate.available_slots }}
              </p>

              <v-form ref="form" v-model="valid" @submit.prevent="submitBooking">
                <v-text-field
                  v-model="booking.customer_name"
                  label="Full Name"
                  required
                  :rules="[v => !!v || 'Name is required']"
                ></v-text-field>
                <v-text-field
                  v-model="booking.customer_email"
                  label="Email"
                  type="email"
                  required
                  :readonly="hasUserEmail"
                  :rules="[
                    v => !!v || 'Email is required',
                    v => /.+@.+\..+/.test(v) || 'Email must be valid'
                  ]"
                ></v-text-field>

                <v-text-field
                  v-model="booking.customer_phone"
                  label="Phone Number"
                  hint="Optional"
                ></v-text-field>

                <v-textarea
                  v-model="booking.notes"
                  label="Special Requirements or Notes"
                  hint="Optional"
                  rows="3"
                ></v-textarea>

                <v-alert
                  v-if="bookingSuccess"
                  type="success"
                  class="mt-4"
                >
                  Booking successful! Your booking has been confirmed.
                </v-alert>

                <v-alert
                  v-if="bookingError"
                  type="error"
                  class="mt-4"
                >
                  {{ bookingError }}
                </v-alert>

                <v-card-actions class="mt-4">
                  <v-spacer></v-spacer>
                  <v-btn
                    color="primary"
                    type="submit"
                    :loading="submitting"
                    :disabled="!valid || submitting || bookingSuccess"
                  >
                    Book Now
                  </v-btn>
                </v-card-actions>
              </v-form>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
    </template>
  </div>
</template>

<script>
import api from '@/services/api';

export default {
  name: 'BookingFormView',
  props: {
    trainingDateId: {
      type: String,
      required: true
    }
  },
  data() {
    return {
      trainingDate: null,
      training: null,
      loading: true,
      error: null,
      valid: false,
      submitting: false,
      bookingSuccess: false,
      bookingError: null,
      hasUserEmail: false,
      booking: {
        training_date_id: '',
        customer_name: '',
        customer_email: '',
        customer_phone: '',
        notes: ''
      }
    }
  },
  methods: {
    formatDate(dateString) {
      const date = new Date(dateString);
      return date.toLocaleDateString();
    },
    formatTime(dateString) {
      const date = new Date(dateString);
      return date.toLocaleTimeString();
    },
    formatDateRange(startDateString, endDateString) {
      const startDate = new Date(startDateString);
      const endDate = new Date(endDateString);

      // If same day
      if (startDate.toDateString() === endDate.toDateString()) {
        return `${startDate.toLocaleDateString()}`;
      }

      // Different days
      return `${startDate.toLocaleDateString()} - ${endDate.toLocaleDateString()}`;
    },
    goBack() {
      if (this.training) {
        this.$router.push(`/trainings/${this.training.id}`);
      } else {
        this.$router.push('/trainings');
      }
    },
    async fetchTrainingDate() {
      this.loading = true;
      this.error = null;

      try {
        const response = await api.getTrainingDateById(this.trainingDateId);
        if (response.data.data && response.data.data.length > 0) {
          this.trainingDate = response.data.data[0];
          this.booking.training_date_id = this.trainingDateId;

          // Fetch the associated training
          await this.fetchTraining(this.trainingDate.training_id);
        } else {
          this.error = 'Training date not found';
        }
      } catch (err) {
        this.error = 'Failed to load training date details. Please try again later.';
        console.error(err);
      } finally {
        this.loading = false;
      }
    },
    async fetchTraining(trainingId) {
      try {
        const response = await api.getTrainingById(trainingId);
        if (response.data.data && response.data.data.length > 0) {
          this.training = response.data.data[0];
        } else {
          this.error = 'Training not found';
        }
      } catch (err) {
        this.error = 'Failed to load training details. Please try again later.';
        console.error(err);
      }
    },
    async submitBooking() {
      if (!this.$refs.form.validate()) return;

      this.submitting = true;
      this.bookingError = null;

      try {
        await api.createBooking(this.booking);
        this.bookingSuccess = true;

        // Reset form after successful booking
        setTimeout(() => {
          this.$router.push('/trainings');
        }, 3000);
      } catch (err) {
        this.bookingError = err.response?.data?.detail || 'Failed to create booking. Please try again.';
        console.error(err);
      } finally {
        this.submitting = false;
      }
    }
  },
  async created() {
    // Set customer email from localStorage if available
    const userEmail = localStorage.getItem('userEmail');
    if (userEmail) {
      this.booking.customer_email = userEmail;
      this.hasUserEmail = true;
    }

    await this.fetchTrainingDate();
  }
}
</script>
