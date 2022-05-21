/* eslint-disable no-undef */
/* eslint-disable no-console */
import React, { useState, useEffect } from 'react'
import { useHistory } from 'react-router-dom'
import api from '../../../api'

const AuthButton = () => {
  // const history = useHistory()
  // const [isLoggedIn, setIsLoggedIn] = useState(false)

  // const checkUserStatus = () => {
  //   const accessToken = localStorage.getItem('access_token')
  //   let status = false
  //   if (accessToken) {
  //     status = true
  //   }
  //   setIsLoggedIn(status)

  //   // For now, force the pages to return home when reloaded
  //   // Otherwise need to persist the data
  //   return false // status
  // }

  // useEffect(() => {
  //   if (!checkUserStatus()) {
  //     history.push('/')
  //   }
  // }, [])

  // history.listen(() => {
  //   checkUserStatus()
  // })

  // const handleLogout = async () => {
  //   try {
  //     const apiResp = await api
  //       .logout()
  //       .then(resp => {
  //         console.log('logout successful')
  //         return resp
  //       })
  //       .catch(err => {
  //         console.log('tokens blocked')
  //         return err
  //       })
  //     console.log('apiResp', apiResp)
  //     localStorage.removeItem('access_token')
  //     localStorage.removeItem('refresh_token')
  //     console.log('tokens removed')
  //     setIsLoggedIn(false)
  //   } catch (error) {
  //     console.error(error)
  //   }
  //   history.push('/')
  // }

  return (
    // <button type="button" className={styles.logout} onClick={handleLogout}>
    //   Log out
    // </button>
    <button class="bank-btn black login-btn">
      <span>Продовжити</span>
    </button>
  )
}

export default AuthButton
