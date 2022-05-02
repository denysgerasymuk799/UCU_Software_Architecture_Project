/* eslint-disable jsx-a11y/media-has-caption */
import React from 'react'
import RegistrationForm from '../../modules/Auth/RegistrationForm'

const RegistrationView = () => (
  <div>
    <section id="left-section">
      <h1 className="main-logo login-logo">
        <a href="index.html">
          unobank
          <span className="gray">| Ukrainian Catholic University</span>
        </a>
      </h1>
      <h2>Спробуйте новий веб-банкінг зі зручним інтерфейсом</h2>
      <img alt="" src="https://fop.monobank.ua/assets/v0.6.60/img/cat-fop.cb4b3443.svg" />
    </section>

    <RegistrationForm />
  </div>
)

export default RegistrationView