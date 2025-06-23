import { fetchAPI } from './api';

export class AppState {
  constructor() {
    this.state = {
      promoCode: null,
      promoApplied: false,
      currentDate: new Date(),
      currentView: 'day',
      rates: {},
      tables: [],
      bookings: [],
      pricingPlan: null,
      equipment: [],
      isAdmin: false,
      isAuthenticated: false,
      currentUserId: null,
      siteSettings: {
        open_time: "09:00",
        close_time: "22:00",
        is_open: true
      }
    };
  }

  async init() {
    const user = await getCurrentUser();
    this.update({
      isAuthenticated: user !== null,
      currentUserId: user?.userId || null,
      isAdmin: user?.isAdmin || false
    });

    const data = await loadInitialData();
    this.update(data);
  }

  update(partialState) {
    this.state = { ...this.state, ...partialState };
    this.notifyListeners();
  }

  subscribe(callback) {
    this.listeners = this.listeners || [];
    this.listeners.push(callback);
    return () => {
      this.listeners = this.listeners.filter(l => l !== callback);
    };
  }

  notifyListeners() {
    if (this.listeners) {
      this.listeners.forEach(cb => cb(this.state));
    }
  }
}