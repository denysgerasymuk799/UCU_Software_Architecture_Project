import React, { useState } from 'react';

import TextField from '@material-ui/core/TextField';
import { makeStyles } from "@material-ui/core/styles";

import styles from './styles.module.scss'

const useStyles = makeStyles({
  root: {
    "& .MuiOutlinedInput-root.Mui-focused .MuiOutlinedInput-notchedOutline": {
      borderColor: "#6200EE"
    },
    "& .MuiInputLabel-outlined.Mui-focused": {
      color: "#6200EE"
    }
  }
});

const SettingsModal = () => {
  const classes = useStyles();

  const [formState, setFormState] = useState({
    email: 'dmytrolopushanskyyyy@gmail.com',
    password: '12345',
    name: 'Лопушанський Дмитро Андрійович',
  })

  const handleChange = e => {
    setFormState({ ...formState, [e.target.name]: e.target.value })
  }

  const handleSubmit = async e => {
    e.preventDefault()
    const { email, password, name } = formState
    
    // await api
    //   .login(formData)
    //   .then(apiResponse => {
    //     console.log('apiResponse', apiResponse.data)
    //     const accessToken = apiResponse.data.access_token
    //     const refreshToken = apiResponse.data.refresh_token
    //     console.log('accessToken, refreshToken', accessToken, refreshToken)

    //     localStorage.setItem('access_token', accessToken)
    //     localStorage.setItem('refresh_token', refreshToken)
    //     history.go('/profile')
    //   })
    //   .catch(error => {
    //     console.log('error', error)
    //     setFormState({ ...formState, error: 'Сталася помилка: ' + error })
    //   })
  }

  return (
    <div className="modal fade" id="settingsModal" tabIndex="-1" role="dialog" aria-labelledby="settingsModal" aria-hidden="true">
      <div className="modal-dialog modal-dialog-centered" role="document">
        <div className="modal-content bank-modal">
          <div className="modal-header">
            <div className="icon-holder blue-gradient">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"> <path d="M12 15C13.6569 15 15 13.6569 15 12C15 10.3431 13.6569 9 12 9C10.3431 9 9 10.3431 9 12C9 13.6569 10.3431 15 12 15Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"></path> <path d="M19.4 15.0009C19.2669 15.3025 19.2272 15.6371 19.286 15.9615C19.3448 16.2859 19.4995 16.5852 19.73 16.8209L19.79 16.8809C19.976 17.0667 20.1235 17.2872 20.2241 17.53C20.3248 17.7728 20.3766 18.0331 20.3766 18.2959C20.3766 18.5587 20.3248 18.819 20.2241 19.0618C20.1235 19.3046 19.976 19.5252 19.79 19.7109C19.6043 19.8969 19.3837 20.0444 19.1409 20.145C18.8981 20.2457 18.6378 20.2975 18.375 20.2975C18.1122 20.2975 17.8519 20.2457 17.6091 20.145C17.3663 20.0444 17.1457 19.8969 16.96 19.7109L16.9 19.6509C16.6643 19.4204 16.365 19.2657 16.0406 19.2069C15.7162 19.1481 15.3816 19.1878 15.08 19.3209C14.7842 19.4477 14.532 19.6582 14.3543 19.9265C14.1766 20.1947 14.0813 20.5091 14.08 20.8309V21.0009C14.08 21.5313 13.8693 22.0401 13.4942 22.4151C13.1191 22.7902 12.6104 23.0009 12.08 23.0009C11.5496 23.0009 11.0409 22.7902 10.6658 22.4151C10.2907 22.0401 10.08 21.5313 10.08 21.0009V20.9109C10.0723 20.5799 9.96512 20.2589 9.77251 19.9896C9.5799 19.7203 9.31074 19.5152 9 19.4009C8.69838 19.2678 8.36381 19.2281 8.03941 19.2869C7.71502 19.3457 7.41568 19.5004 7.18 19.7309L7.12 19.7909C6.93425 19.9769 6.71368 20.1244 6.47088 20.225C6.22808 20.3257 5.96783 20.3775 5.705 20.3775C5.44217 20.3775 5.18192 20.3257 4.93912 20.225C4.69632 20.1244 4.47575 19.9769 4.29 19.7909C4.10405 19.6052 3.95653 19.3846 3.85588 19.1418C3.75523 18.899 3.70343 18.6387 3.70343 18.3759C3.70343 18.1131 3.75523 17.8528 3.85588 17.61C3.95653 17.3672 4.10405 17.1467 4.29 16.9609L4.35 16.9009C4.58054 16.6652 4.73519 16.3659 4.794 16.0415C4.85282 15.7171 4.81312 15.3825 4.68 15.0809C4.55324 14.7851 4.34276 14.5329 4.07447 14.3552C3.80618 14.1775 3.49179 14.0822 3.17 14.0809H3C2.46957 14.0809 1.96086 13.8702 1.58579 13.4951C1.21071 13.1201 1 12.6113 1 12.0809C1 11.5505 1.21071 11.0418 1.58579 10.6667C1.96086 10.2916 2.46957 10.0809 3 10.0809H3.09C3.42099 10.0732 3.742 9.96603 4.0113 9.77343C4.28059 9.58082 4.48572 9.31165 4.6 9.00092C4.73312 8.6993 4.77282 8.36472 4.714 8.04033C4.65519 7.71593 4.50054 7.41659 4.27 7.18092L4.21 7.12092C4.02405 6.93517 3.87653 6.71459 3.77588 6.4718C3.67523 6.229 3.62343 5.96875 3.62343 5.70592C3.62343 5.44308 3.67523 5.18283 3.77588 4.94003C3.87653 4.69724 4.02405 4.47666 4.21 4.29092C4.39575 4.10496 4.61632 3.95744 4.85912 3.8568C5.10192 3.75615 5.36217 3.70434 5.625 3.70434C5.88783 3.70434 6.14808 3.75615 6.39088 3.8568C6.63368 3.95744 6.85425 4.10496 7.04 4.29092L7.1 4.35092C7.33568 4.58145 7.63502 4.7361 7.95941 4.79492C8.28381 4.85374 8.61838 4.81403 8.92 4.68092H9C9.29577 4.55415 9.54802 4.34367 9.72569 4.07538C9.90337 3.80709 9.99872 3.4927 10 3.17092V3.00092C10 2.47048 10.2107 1.96177 10.5858 1.5867C10.9609 1.21163 11.4696 1.00092 12 1.00092C12.5304 1.00092 13.0391 1.21163 13.4142 1.5867C13.7893 1.96177 14 2.47048 14 3.00092V3.09092C14.0013 3.4127 14.0966 3.72709 14.2743 3.99538C14.452 4.26367 14.7042 4.47415 15 4.60092C15.3016 4.73403 15.6362 4.77374 15.9606 4.71492C16.285 4.6561 16.5843 4.50145 16.82 4.27092L16.88 4.21092C17.0657 4.02496 17.2863 3.87744 17.5291 3.7768C17.7719 3.67615 18.0322 3.62434 18.295 3.62434C18.5578 3.62434 18.8181 3.67615 19.0609 3.7768C19.3037 3.87744 19.5243 4.02496 19.71 4.21092C19.896 4.39666 20.0435 4.61724 20.1441 4.86003C20.2448 5.10283 20.2966 5.36308 20.2966 5.62592C20.2966 5.88875 20.2448 6.149 20.1441 6.3918C20.0435 6.63459 19.896 6.85517 19.71 7.04092L19.65 7.10092C19.4195 7.33659 19.2648 7.63593 19.206 7.96033C19.1472 8.28472 19.1869 8.6193 19.32 8.92092V9.00092C19.4468 9.29668 19.6572 9.54893 19.9255 9.72661C20.1938 9.90428 20.5082 9.99963 20.83 10.0009H21C21.5304 10.0009 22.0391 10.2116 22.4142 10.5867C22.7893 10.9618 23 11.4705 23 12.0009C23 12.5313 22.7893 13.0401 22.4142 13.4151C22.0391 13.7902 21.5304 14.0009 21 14.0009H20.91C20.5882 14.0022 20.2738 14.0975 20.0055 14.2752C19.7372 14.4529 19.5268 14.7051 19.4 15.0009V15.0009Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"></path> </svg>
            </div>
            <h3>Налаштування</h3>
            <button type="button" className="bank-close close" data-dismiss="modal" aria-label="Close">
              <svg data-v-5fa6b797="" width="32" height="32" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg"><circle data-v-5fa6b797="" cx="16" cy="16" r="15.5" stroke="#E6E6E6"></circle><path data-v-5fa6b797="" d="M20 12L12 20" stroke="#A6A6A6" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"></path><path data-v-5fa6b797="" d="M12 12L20 20" stroke="#A6A6A6" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"></path></svg>
            </button>
          </div>
          <div className="bank-modal-content">
            <form noValidate> 
              <p>Оновіть дані профілю нижче:</p>
              <TextField
                fullWidth
                label="E-mail"
                name="email"
                variant="outlined"
                className={styles.customInput + " " + classes.root}
                value={formState.email}
                onChange={e => handleChange(e)}
              />
              <TextField
                fullWidth
                label="Password"
                name="password"
                type="password"
                variant="outlined"
                className={styles.customInput + " " + classes.root}
                value={formState.password}
                onChange={e => handleChange(e)}
              />
              <TextField
                fullWidth
                label="Name"
                name="name"
                variant="outlined"
                className={styles.customInput + " " + classes.root}
                value={formState.name}
                onChange={e => handleChange(e)}
              />
              <button className="bank-btn">
                <i className="fa fa-save" aria-hidden="true"></i>
                <span>Зберегти</span>
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>
  )
}

export default SettingsModal
