/* eslint-disable no-console */
/* eslint-disable no-undef */
import TextField from '@material-ui/core/TextField'
import React, { useState, useEffect } from 'react'
import { useHistory } from 'react-router-dom'
import api from '../../../api'
import styles from './styles.module.scss'
import { makeStyles } from "@material-ui/core/styles";

const useStyles = makeStyles({
  root: {
    "& .MuiOutlinedInput-root.Mui-focused .MuiOutlinedInput-notchedOutline": {
      borderColor: "#6D3ADC"
    },
    "& .MuiInputLabel-outlined.Mui-focused": {
      color: "#6D3ADC"
    }
  }
});

const LoginForm = () => {
  const history = useHistory()
  const classes = useStyles();

  const [formState, setFormState] = useState({
    email: 'lopushanskyy@gmail.co',
    password: '12345',
    error: '',
  })

  useEffect(() => {
    const accessToken = localStorage.getItem('access_token')
    const refreshToken = localStorage.getItem('refresh_token')
    console.log('tokens', accessToken, refreshToken)
    if (accessToken) {
      try {
        history.push('/profile')
      } catch (error) {
        console.error(error)
        setFormState({ ...formState, error })
      }
    }
  }, [formState, history])

  const handleChange = e => {
    setFormState({ ...formState, [e.target.name]: e.target.value })
  }

  const handleSubmit = async e => {
    e.preventDefault()
    const { email, password } = formState
    const formData = new FormData()
    formData.append('username', email)
    formData.append('password', password)
    
    await api
      .login(formData)
      .then(apiResponse => {
        console.log('apiResponse', apiResponse.data)
        const accessToken = apiResponse.data.access_token
        const refreshToken = apiResponse.data.refresh_token
        console.log('accessToken, refreshToken', accessToken, refreshToken)

        localStorage.setItem('access_token', accessToken)
        localStorage.setItem('refresh_token', refreshToken)
        localStorage.setItem('email', apiResponse.data.email)
        localStorage.setItem('user_name', apiResponse.data.user_name)
        localStorage.setItem('card_id', apiResponse.data.card_id)
        localStorage.setItem('user_id', apiResponse.data.user_id)
        history.go('/profile')
      })
      .catch(error => {
        console.log('error', error)
        setFormState({ ...formState, error: 'Сталася помилка: ' + error })
      })
  }

  return (
    <section id="right-section">
      <form noValidate>
        <h3>Вхід в особистий кабінет</h3>
        <p className={styles.message}>{formState.error}</p>
        <TextField
          fullWidth
          label="E-mail"
          name="email"
          variant="outlined"
          className={styles.nomoInput + " " + classes.root}
          value={formState.email}
          onChange={e => handleChange(e)}
        />
        <TextField
          fullWidth
          label="Password"
          name="password"
          type="password"
          variant="outlined"
          className={styles.nomoInput + " " + classes.root}
          value={formState.password}
          onChange={e => handleChange(e)}
        />
        <button 
          className="bank-btn black login-btn"
          onClick={e => handleSubmit(e)}
        >
          <span>Продовжити</span>
        </button>
        <p className={styles.additionalText}>
          Не маєте акаунту? <a href="/sign_up">Зареєструйтеся</a>
        </p>
      </form>
    </section>
  )
}

export default LoginForm
