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

// request interceptor to add the auth token header to requests
axios.interceptors.request.use(
  config => {
    const accessToken = localStorage.getItem('access_token')
    if (accessToken) {
      config.headers.Authorization = `Bearer ${accessToken}`
      config.headers.ACCESS_TOKEN = HARAPI_ACCESS_TOKEN
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
    const refreshToken = localStorage.getItem('refresh')
    if (
      refreshToken &&
      error.response.status === 401 &&
      !originalRequest.retry
    ) {
      originalRequest.retry = true
      return axios
        .post(`${baseUrlAuth}/refresh`, { refreshToken })
        .then(res => {
          if (res.status === 200) {
            localStorage.setItem('access_token', res.data.accessToken)
            console.log('Access token refreshed!')
            return axios(originalRequest)
          }
        })
    }
    return Promise.reject(error)
  },
)

// functions to make api calls
const api = {
  register: body => axios.post(`${registrationServiceURL}/registration`, body),
  login: body => axios.post(`${authServiceURL}/login`, body),
}

export default api
