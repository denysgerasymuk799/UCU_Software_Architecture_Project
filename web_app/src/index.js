import React from 'react'
import { createRoot } from 'react-dom/client';
import { BrowserRouter as Router, Switch, Route } from 'react-router-dom'

import LoginView from './views/LoginView'
import RegistrationView from './views/RegistrationView';
import ProfileView from './views/ProfileView';

const container = document.getElementById('root');
const root = createRoot(container);

root.render(
  <React.StrictMode>
      <Router>
        <Switch>
          <Route path="/sign_up">
            <RegistrationView />
          </Route>
          <Route path="/profile">
            <ProfileView />
          </Route>
          <Route path="/">
            <LoginView />
          </Route>
        </Switch>
      </Router>
  </React.StrictMode>
)
