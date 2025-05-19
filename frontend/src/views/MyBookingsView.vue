<template>
  <div class="my-bookings">
    <h1 class="text-h3 mb-4">My Bookings</h1>

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

    <v-row v-else-if="bookings.length === 0">
      <v-col cols="12">
        <v-alert type="info">
          You don't have any bookings yet. 
          <v-btn color="primary" to="/trainings" class="ml-2">Browse Trainings</v-btn>
        </v-alert>
      </v-col>
    </v-row>

    <template v-else>
      <v-row>
        <v-col cols="12">
          <v-card>
            <v-card-title>
              <v-text-field
                v-model="search"
                append-icon="mdi-magnify"
                label="Search"
                single-line
                hide-details
              ></v-text-field>
            </v-card-title>
            <v-data-table
              :headers="headers"
              :items="bookings"
              :search="search"
              :loading="loading"
              class="elevation-1"
            >
              <template v-slot:item.training_name="{ item }">
                {{ getTrainingName(item.training_date_id) }}
              </template>

              <template v-slot:item.date="{ item }">
                {{ formatDate(getTrainingDate(item.training_date_id)?.start_date) }}
              </template>

              <template v-slot:item.time="{ item }">
                {{ formatTime(getTrainingDate(item.training_date_id)?.start_date) }} - 
                {{ formatTime(getTrainingDate(item.training_date_id)?.end_date) }}
              </template>

              <template v-slot:item.location="{ item }">
                {{ getTrainingDate(item.training_date_id)?.location }}
              </template>

              <template v-slot:item.status="{ item }">
                <v-chip
                  :color="getStatusColor(item.status)"
                  text-color="white"
                >
                  {{ item.status }}
                </v-chip>
              </template>

              <template v-slot:item.actions="{ item }">
                <v-btn
                  icon
                  small
                  color="error"
                  @click="confirmCancelBooking(item)"
                  :disabled="item.status === 'cancelled'"
                >
                  <v-icon>mdi-delete</v-icon>
                </v-btn>
              </template>
            </v-data-table>
          </v-card>
        </v-col>
      </v-row>
    </template>

    <!-- Confirmation Dialog -->
    <v-dialog v-model="dialog" max-width="500px">
      <v-card>
        <v-card-title class="text-h5">Cancel Booking</v-card-title>
        <v-card-text>
          Are you sure you want to cancel this booking? This action cannot be undone.
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="blue-darken-1" variant="text" @click="dialog = false">Cancel</v-btn>
          <v-btn color="error" @click="cancelBooking" :loading="cancelling">Confirm</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
import api from '@/services/api';

export default {
  name: 'MyBookingsView',
  data() {
    return {
      bookings: [],
      trainingDates: {},
      trainings: {},
      loading: true,
      error: null,
      search: '',
      dialog: false,
      selectedBooking: null,
      cancelling: false,
      headers: [
        { title: 'Training', key: 'training_name', sortable: true },
        { title: 'Date', key: 'date', sortable: true },
        { title: 'Time', key: 'time', sortable: false },
        { title: 'Location', key: 'location', sortable: true },
        { title: 'Status', key: 'status', sortable: true },
        { title: 'Actions', key: 'actions', sortable: false }
      ]
    }
  },
  methods: {
    formatDate(dateString) {
      if (!dateString) return '';
      const date = new Date(dateString);
      return date.toLocaleDateString();
    },
    formatTime(dateString) {
      if (!dateString) return '';
      const date = new Date(dateString);
      return date.toLocaleTimeString();
    },
    getStatusColor(status) {
      switch (status) {
        case 'confirmed': return 'success';
        case 'cancelled': return 'error';
        case 'completed': return 'info';
        default: return 'primary';
      }
    },
    getTrainingDate(trainingDateId) {
      return this.trainingDates[trainingDateId];
    },
    getTrainingName(trainingDateId) {
      const trainingDate = this.trainingDates[trainingDateId];
      if (!trainingDate) return 'Unknown Training';

      const training = this.trainings[trainingDate.training_id];
      return training ? training.name : 'Unknown Training';
    },
    confirmCancelBooking(booking) {
      this.selectedBooking = booking;
      this.dialog = true;
    },
    async cancelBooking() {
      if (!this.selectedBooking) return;

      this.cancelling = true;

      try {
        await api.cancelBooking(this.selectedBooking.id);

        // Update the booking status in the local list
        const index = this.bookings.findIndex(b => b.id === this.selectedBooking.id);
        if (index !== -1) {
          this.bookings[index].status = 'cancelled';
        }

        this.dialog = false;
        this.selectedBooking = null;
      } catch (err) {
        this.error = err.response?.data?.detail || 'Failed to cancel booking. Please try again.';
        console.error(err);
      } finally {
        this.cancelling = false;
      }
    },
    async fetchBookings() {
      this.loading = true;
      this.error = null;

      try {
        // Get the user's email from localStorage or other state management
        const userEmail = localStorage.getItem('userEmail');

        if (!userEmail) {
          this.error = 'User email not found. Please log in again.';
          this.loading = false;
          return;
        }

        const response = await api.getBookings(userEmail);
        this.bookings = response.data.data;

        // Fetch training dates for all bookings
        await this.fetchTrainingDates();
      } catch (err) {
        this.error = 'Failed to load bookings. Please try again later.';
        console.error(err);
      } finally {
        this.loading = false;
      }
    },
    async fetchTrainingDates() {
      const trainingDateIds = [...new Set(this.bookings.map(b => b.training_date_id))];

      for (const id of trainingDateIds) {
        try {
          const response = await api.getTrainingDateById(id);
          if (response.data.data && response.data.data.length > 0) {
            const trainingDate = response.data.data[0];
            this.trainingDates[id] = trainingDate;

            // Fetch training details if not already fetched
            if (!this.trainings[trainingDate.training_id]) {
              await this.fetchTraining(trainingDate.training_id);
            }
          }
        } catch (err) {
          console.error(`Failed to fetch training date ${id}:`, err);
        }
      }
    },
    async fetchTraining(trainingId) {
      try {
        const response = await api.getTrainingById(trainingId);
        if (response.data.data && response.data.data.length > 0) {
          this.trainings[trainingId] = response.data.data[0];
        }
      } catch (err) {
        console.error(`Failed to fetch training ${trainingId}:`, err);
      }
    }
  },
  async created() {
    await this.fetchBookings();
  }
}
</script>
