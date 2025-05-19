<template>
  <div class="training-details">
    <v-btn class="mb-4" prepend-icon="mdi-arrow-left" to="/trainings">
      Back to Trainings
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

    <template v-else-if="training">
      <!-- Training Details -->
      <v-row>
        <v-col cols="12">
          <v-card>
            <v-card-title class="text-h4">{{ training.name }}</v-card-title>
            <v-card-subtitle class="text-subtitle-1">
              <v-icon>mdi-account</v-icon> Instructor: {{ training.instructor }}
            </v-card-subtitle>
            <v-card-text>
              <p class="text-body-1 mb-4">{{ training.description }}</p>

              <v-row>
                <v-col cols="12" md="4">
                  <v-list>
                    <v-list-item>
                      <template v-slot:prepend>
                        <v-icon>mdi-currency-usd</v-icon>
                      </template>
                      <v-list-item-title>Price</v-list-item-title>
                      <v-list-item-subtitle>{{ training.price }}</v-list-item-subtitle>
                    </v-list-item>
                  </v-list>
                </v-col>
                <v-col cols="12" md="4">
                  <v-list>
                    <v-list-item>
                      <template v-slot:prepend>
                        <v-icon>mdi-clock-outline</v-icon>
                      </template>
                      <v-list-item-title>Duration</v-list-item-title>
                      <v-list-item-subtitle>{{ training.duration_hours }} hours</v-list-item-subtitle>
                    </v-list-item>
                  </v-list>
                </v-col>
                <v-col cols="12" md="4">
                  <v-list>
                    <v-list-item>
                      <template v-slot:prepend>
                        <v-icon>mdi-account-group</v-icon>
                      </template>
                      <v-list-item-title>Max Participants</v-list-item-title>
                      <v-list-item-subtitle>{{ training.max_participants }}</v-list-item-subtitle>
                    </v-list-item>
                  </v-list>
                </v-col>
              </v-row>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>

      <!-- Training Dates -->
      <v-row class="mt-6">
        <v-col cols="12">
          <h2 class="text-h4 mb-4">Available Dates</h2>

          <v-row v-if="loadingDates">
            <v-col cols="12" class="text-center">
              <v-progress-circular indeterminate color="primary"></v-progress-circular>
            </v-col>
          </v-row>

          <v-row v-else-if="datesError">
            <v-col cols="12">
              <v-alert type="error">{{ datesError }}</v-alert>
            </v-col>
          </v-row>

          <v-row v-else-if="trainingDates.length === 0">
            <v-col cols="12">
              <v-alert type="info">No dates available for this training at the moment.</v-alert>
            </v-col>
          </v-row>

          <v-row v-else>
            <v-col v-for="date in trainingDates" :key="date.id" cols="12" md="6" lg="4">
              <v-card>
                <v-card-title>{{ formatDate(date.start_date) }}</v-card-title>
                <v-card-subtitle>
                  {{ formatTime(date.start_date) }} - {{ formatTime(date.end_date) }}
                </v-card-subtitle>
                <v-card-text>
                  <p><v-icon small>mdi-map-marker</v-icon> {{ date.location }}</p>
                  <p><v-icon small>mdi-calendar-range</v-icon> {{ formatDateRange(date.start_date, date.end_date) }}</p>
                  <p><v-icon small>mdi-seat</v-icon> Available slots: {{ date.available_slots }}</p>
                </v-card-text>
                <v-card-actions>
                  <v-btn 
                    color="primary" 
                    :to="`/book/${date.id}`"
                    :disabled="date.available_slots <= 0"
                  >
                    {{ date.available_slots > 0 ? 'Book Now' : 'Fully Booked' }}
                  </v-btn>
                </v-card-actions>
              </v-card>
            </v-col>
          </v-row>
        </v-col>
      </v-row>
    </template>
  </div>
</template>

<script>
import api from '@/services/api';

export default {
  name: 'TrainingDetailsView',
  props: {
    id: {
      type: String,
      required: true
    }
  },
  data() {
    return {
      training: null,
      trainingDates: [],
      loading: true,
      loadingDates: true,
      error: null,
      datesError: null
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
    async fetchTraining() {
      this.loading = true;
      this.error = null;

      try {
        const response = await api.getTrainingById(this.id);
        if (response.data.data && response.data.data.length > 0) {
          this.training = response.data.data[0];
        } else {
          this.error = 'Training not found';
        }
      } catch (err) {
        this.error = 'Failed to load training details. Please try again later.';
        console.error(err);
      } finally {
        this.loading = false;
      }
    },
    async fetchTrainingDates() {
      this.loadingDates = true;
      this.datesError = null;

      try {
        const response = await api.getTrainingDates(this.id);
        this.trainingDates = response.data.data;
      } catch (err) {
        this.datesError = 'Failed to load training dates. Please try again later.';
        console.error(err);
      } finally {
        this.loadingDates = false;
      }
    }
  },
  async created() {
    await this.fetchTraining();
    if (this.training) {
      await this.fetchTrainingDates();
    }
  }
}
</script>
