import { auth } from './auth'
import { sendPasswordResetEmail } from 'firebase/auth';

const form = document.getElementById('reset-password-form');
const url = new URL(window.nextUrl);
const params = new URLSearchParams(url.search);
const sendButton = document.getElementById('send-email');

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
    form.submit();
    return true;
  })
  .catch((reason) => {
    console.error(reason);
    sendButton.disabled = false; // allow another request if there was an error
  });

  return false;
};