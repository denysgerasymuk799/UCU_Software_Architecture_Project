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

const RegistrationForm = () => {
  const history = useHistory()
  const classes = useStyles();

  const [formState, setFormState] = useState({
    firstname: '',
    lastname: '',
    email: '',
    password: '',
    repeat_password: '',
    birthday_date: '',
    city: '',
    address: '',
    error: '',
  })

  useEffect(() => {
    const accessToken = localStorage.getItem('access_token')
    const refreshToken = localStorage.getItem('refresh_token')
    console.log('tokens', accessToken, refreshToken)
    if (accessToken) {
      window.location.href = '/profile';
    }
  }, [formState, history])

  const handleOnlyLetters = e => {
    const onlyLetters = e.target.value.replace(/[^a-zA-Z]/g, '');
    setFormState({ ...formState, [e.target.name]: onlyLetters })
  }

  const handleChange = e => {
    setFormState({ ...formState, [e.target.name]: e.target.value })
  }

  function validate(form) {
    for(var field of form.entries()) {
      if (field[1] === "") {
        return [false, 'One or more fields are missing'];
      }
    }
    console.log('hello');
    const emailPattern = /[a-zA-Z0-9]+[\.]?([a-zA-Z0-9]+)?[\@][a-z]{3,9}[\.][a-z]{2,5}/g;
    const result = emailPattern.test(form.get('email'));
    if(!result){ return [false, 'Wrong email'] };

    if (form.get('password').length < 4) { return [false, 'Password too short'] }

    return [true, ''];
  }

  const handleSubmit = async e => {
    e.preventDefault();

    const { firstname, lastname, email, password, repeat_password, 
      birthday_date, city, address } = formState
    
    const formData = new FormData()
    formData.append('firstname', firstname)
    formData.append('lastname', lastname)
    formData.append('email', email)
    formData.append('password', password)
    formData.append('repeat_password', repeat_password)
    formData.append('birthday_date', birthday_date)
    formData.append('city', city)
    formData.append('address', address)

    const [validResult, errorText] = validate(formData);

    console.log("validResult", validResult, errorText);
    
    if (!validResult) { return setFormState({ ...formState, 'error': errorText }) }

    await api
      .register(formData)
      .then(apiResponse => {
        console.log('apiResponse', apiResponse.data)
        window.location.href = '/login';
      })
      .catch(error => {
        console.log('error', error)
        setFormState({ ...formState, error: '?????????????? ??????????????: ' + error })
      })
  }

  return (
    <section id="right-section">
      <form>
        <h3>????????????????????</h3>
        <p className={styles.message}>{formState.error} ??????????????????????????, ???? ???????? ???????????????????? ?????????????? ?? ?????????????? ????/????/????????.</p>
        <TextField
          fullWidth
          label="????'??"
          name="firstname"
          variant="outlined"
          className={styles.nomoInput + " " + classes.root}
          value={formState.firstname}
          onChange={e => handleOnlyLetters(e)}
        />
        <TextField
          fullWidth
          label="????????????????"
          name="lastname"
          variant="outlined"
          className={styles.nomoInput + " " + classes.root}
          value={formState.lastname}
          onChange={e => handleOnlyLetters(e)}
        />
        <TextField
          fullWidth
          label="??-??????????"
          name="email"
          variant="outlined"
          className={styles.nomoInput + " " + classes.root}
          value={formState.email}
          onChange={e => handleChange(e)}
        />
        <TextField
          fullWidth
          label="????????????"
          name="password"
          type="password"
          variant="outlined"
          className={styles.nomoInput + " " + classes.root}
          value={formState.password}
          onChange={e => handleChange(e)}
        />
        <TextField
          fullWidth
          label="?????????????????? ????????????"
          name="repeat_password"
          type="password"
          variant="outlined"
          className={styles.nomoInput + " " + classes.root}
          value={formState.repeat_password}
          onChange={e => handleChange(e)}
        />
        <TextField
          fullWidth
          label="???????? ???????????????????? ?? ?????????????? ????/????/????????"
          name="birthday_date"
          variant="outlined"
          className={styles.nomoInput + " " + classes.root}
          value={formState.birthday_date}
          onChange={e => handleChange(e)}
        />
        {/* <TextField
          fullWidth
          InputLabelProps={{ shrink: true, required: true }}
          label="???????? ????????????????????"
          name="birthday_date"
          type="date"
          variant="outlined"
          className={styles.nomoInput + " " + classes.root}
          value={formState.repeat_password}
          onChange={e => handleChange(e)}
        /> */}
        <TextField
          fullWidth
          label="?????????? ????????????????????"
          name="city"
          variant="outlined"
          className={styles.nomoInput + " " + classes.root}
          value={formState.city}
          onChange={e => handleChange(e)}
        />
        <TextField
          fullWidth
          label="??????????"
          name="address"
          variant="outlined"
          className={styles.nomoInput + " " + classes.root}
          value={formState.address}
          onChange={e => handleChange(e)}
        />
        <button 
          className="bank-btn black login-btn"
          onClick={e => handleSubmit(e)}
        >
          <span>????????????????????</span>
        </button>
        <p className={styles.additionalText}>
          ?????? ?????????? ????????????? <a href="/">????????????????</a>
        </p>
      </form>
    </section>
  )
}

export default RegistrationForm
