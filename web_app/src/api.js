/* eslint-disable prefer-destructuring */
/* eslint-disable no-console */
/* eslint-disable no-param-reassign */
/* eslint-disable no-unused-vars */
/* eslint-disable no-undef */
/* eslint-disable consistent-return */
import axios from 'axios'
import env from './env'

const registrationServiceURL = env.REGISTRATION_URL
const authServiceURL = env.AUTH_URL
const transactionServiceURL = env.TRANSACTION_URL

// request interceptor to add the auth token header to requests
axios.interceptors.request.use(
  config => {
    const accessToken = localStorage.getItem('access_token')
    if (accessToken) {
      config.headers.Authorization = `Bearer ${accessToken}`
    }
    console.log(config)
    return config
  },
  error => {
    Promise.reject(error)
  },
)

// response interceptor to refresh token on receiving token expired error
axios.interceptors.response.use(
  response => response,
  error => {
    const originalRequest = error.config
    const refreshToken = localStorage.getItem('refresh_token')
    if (
      refreshToken &&
      error.response.status === 401 &&
      !originalRequest.retry
    ) {
      originalRequest.retry = true
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      window.location =  '/login';
    }
    return Promise.reject(error)
  },
)

// functions to make api calls
const api = {
  register: body => axios.post(`${registrationServiceURL}/registration`, body),
  login: body => axios.post(`${authServiceURL}/login`, body),
  handle_transaction: body => axios.post(`${transactionServiceURL}/handle_transaction`, body),
  get_balance: card_id => axios.get(`${transactionServiceURL}/get_balance?card_id=${card_id}`),
  get_transactions: (card_id, idx) => axios.get(`${transactionServiceURL}/get_transactions?card_id=${card_id}&start_idx=${idx}`),
  get_notifications: last_transaction_id => axios.get(`${transactionServiceURL}/get_notifications?last_transaction_id=${last_transaction_id}`),
}

// eslint-disable-next-line import/no-anonymous-default-export
export default api