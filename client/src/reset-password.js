import { auth } from './auth'
import { sendPasswordResetEmail } from 'firebase/auth';

const form = document.getElementById('reset-password-form');
const url = new URL(window.nextUrl);
const params = new URLSearchParams(url.search);
const sendButton = document.getElementById('send-email');
const emailSentCheckbox = document.getElementById('email_sent_checkbox');

form.onsubmit = (event) => {
  event.preventDefault();

  if (sendButton.disabled) {
    return false;
  }

  const data = new FormData(form);
  const email = data.get("email");

  params.append("email", email);
  url.search = params;

  sendButton.disabled = true;
  sendPasswordResetEmail(auth, email, {url: url.toString()})
  .then(() => {
    // set `email_sent` to true, so server knows password reset was handled by firebase
    emailSentCheckbox.checked = true;
    form.submit();
    return true;
  })
  .catch((reason) => {
    if (reason.code === 'auth/user-not-found') {
      // User not registered with OAuth, try attempting normal password reset
      form.submit();
    } else {
      console.error(reason);
      sendButton.disabled = false; // allow another request if there was an error
    }
  });

  return false;
};