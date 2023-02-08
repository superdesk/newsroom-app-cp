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

  sendPasswordResetEmail(auth, email, {url: url.toString()}).then(() => {
    sendButton.disabled = true;
  }, (reason) => {
    console.error(reason);
  });

  return false;
};


document.getElementById('reset-password').onclick = (event) => {

  sendPasswordResetEmail(auth, "petr.jasek@sourcefabric.org", {url: window.location.href});
  console.info("IN");
}