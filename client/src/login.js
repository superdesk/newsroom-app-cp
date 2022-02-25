import { initializeApp } from 'firebase/app';
import { getAuth, signInWithEmailAndPassword, signOut } from 'firebase/auth';

const firebaseConfig = {
  apiKey: 'AIzaSyCy261Dj82etz9-AwMgKG0o6HCbv3HNzbc',
  authDomain: 'cp-identity.firebaseapp.com',
  projectId: 'cp-identity',
  messagingSenderId: '462735301864',
};

const app = initializeApp(firebaseConfig);
const auth = getAuth();
const form = document.getElementById('formLogin');
const params = new URLSearchParams(window.location.search);

const sendTokenToServer = (token) => {
  document.cookie = `token=${token}`;
  window.location.replace('/auth_token');
}

// get firebase auth status
auth.onAuthStateChanged((user) => {
  if (user != null) { // there is a firebase user authenticated

    if (params.get('user_error') === '1') { // but missing in newshub
      return;
    }

    if (params.get('logout') === '1') { // force logout from firebase
      document.cookie = 'token=';
      signOut(auth);
      return;
    }

    user.getIdToken(params.get('token_error') === '1').then(sendTokenToServer);
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