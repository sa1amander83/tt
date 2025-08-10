import { get } from './index.js';

export const AuthAPI = {
  current: () => get('/accounts/current_user/').catch(() => null)
};