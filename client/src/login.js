import { auth } from './auth';
import { signInWithEmailAndPassword, signOut } from 'firebase/auth';

const form = document.getElementById('formLogin');
const params = new URLSearchParams(window.location.search);

if (params.get("email")) {
  form['email'].value = params.get("email");
}

const sendTokenToServer = (token) => {
  window.location.replace(`/auth_token?token=${token}`);
}

// get firebase auth status
auth.onAuthStateChanged((user) => {
  if (user != null) { // there is a firebase user authenticated

    if (params.get('user_error') === '1') { // but missing in newshub
      return;
    }

    if (params.get('logout') === '1') { // force logout from firebase
      signOut(auth);
      return;
    }

    user.getIdToken(params.get('token_error') === '1')
      .then(
        sendTokenToServer,
        () => { // on error we sign out the user and let him login again
          signOut(auth);
        },
      );
  }
});

// override submit form action to authenticate using firebase
// and fallback to newshub when credentials are invalid
form.onsubmit = (event) => {
  event.preventDefault();

  const data = new FormData(form);
  const email = data.get("email");
  const password = data.get("password");

  signInWithEmailAndPassword(auth, email, password).then((userCredential) => {
    userCredential.user.getIdToken().then(sendTokenToServer);
  }, (reason) => {
    // login via firebase didn't work out,
    // try standard newshub login
    console.error(reason);
    form.submit();
  });

  return false;
};
