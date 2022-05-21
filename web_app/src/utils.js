import ReactDOM from 'react-dom';
import React, { useEffect, useRef } from 'react';
import SnackBar from './modules/_shared/Notification/SnackBar';

const triggerSnackbar = (title, messageType) => {
    const validMessageTypes = ['error', 'info', 'warning', 'success'];
    if (!validMessageTypes.includes(messageType)) {
        throw Error("Invalid snackbar message type");
    }
    
    ReactDOM.render(
        <SnackBar messageType={messageType} timer={2000} title={title} />,
        document.getElementById('snackbar-fixed-container')
    );
}

export const showErrorMessage = title => {
    triggerSnackbar(title, 'error');
}

export const showInfoMessage = title => {
    triggerSnackbar(title, 'info');
}

export const showSuccessMessage = title => {
    triggerSnackbar(title, 'success');
}

export const showWarningMessage = title => {
    triggerSnackbar(title, 'warning');
}

export const useInterval = (callback, delay) => {
    const savedCallback = useRef();
  
    useEffect(() => {
      savedCallback.current = callback;
    }, [callback]);
  
  
    useEffect(() => {
      function tick() {
        savedCallback.current();
      }
      if (delay !== null) {
        const id = setInterval(tick, delay);
        return () => clearInterval(id);
      }
    }, [delay]);
  }