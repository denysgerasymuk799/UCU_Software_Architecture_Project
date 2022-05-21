/* eslint-disable jsx-a11y/anchor-is-valid */
// import api from '../../../api'

const NavDropdown = () => {
  const handleLogout = async (e) => {
    e.preventDefault();
    try {
      // const apiResp = await api
      //   .logout()
      //   .then(resp => {
      //     console.log('logout successful')
      //     return resp
      //   })
      //   .catch(err => {
      //     console.log('tokens blocked')
      //     return err
      //   })
      // console.log('apiResp', apiResp)
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      console.log('tokens removed')
    } catch (error) {
      console.error(error)
    }
    window.location.href = '/';
  }

  return (
    <div className="dropdown-menu dropdown-menu-end bank-dropdown">
        {/* <a href="#" className="dropdown-item" data-toggle="modal" data-target="#settingsModal">Налаштування</a>
        <a href="#" className="dropdown-item">Довідка</a>
        <div className="dropdown-divider"></div> */}
        <a href="#" className="dropdown-item" onClick={handleLogout}>
          Вихід
          <i className="fa fa-sign-out ml-75" aria-hidden="true"></i>
        </a>
    </div>
  )
}

export default NavDropdown
