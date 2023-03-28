import { auth } from './auth'
import { sendPasswordResetEmail } from 'firebase/auth';

const form = document.getElementById('formToken');
const sendButton = document.getElementById('reset-btn');

form.onsubmit = (event) => {
  event.preventDefault();

  if (sendButton.disabled) {
    return false;
  }

  const data = new FormData(form);
  const email = data.get("email");
  const url = new URL(window.nextUrl);
  const params = new URLSearchParams();

  params.append("email", email);
  url.search = params;

  sendButton.disabled = true;
  sendPasswordResetEmail(auth, email, { url: url.toString() })
    .then(() => {
      location.replace(window.externalSuccessUrl);
    })
    .catch((reason) => {
      console.error(reason);
      form.submit();
    });

  return false;
};