import { signInWithEmailAndPassword, signOut } from "firebase/auth";
import { auth } from "newsroom-core/assets/auth/firebase/init";

const form = document.querySelector<HTMLFormElement>("#formLogin");
if (!form) {
  throw new Error("#formLogin not found");
}

const firebaseStatus =
  document.querySelector<HTMLInputElement>("#firebase-status");
if (!firebaseStatus) {
  throw new Error("#firebase-status not found");
}

const params = new URLSearchParams(window.location.search);
if (params.get("email")) {
  form["email"].value = params.get("email");
}

const sendTokenToServer = (token: string) => {
  window.location.replace(`/firebase_auth_token?token=${token}`);
};

auth.onAuthStateChanged((user) => {
  if (user === null) return;
  if (params.get("user_error") === "1") return;
  if (params.get("logout") === "1") {
    signOut(auth);
    return;
  }

  const tokenError = params.get("token_error");
  user.getIdToken(tokenError === "1").then(sendTokenToServer);
});

form.onsubmit = (event) => {
  event.preventDefault();

  const data = new FormData(form);

  const email = data.get("email");
  if (typeof email !== "string") return;

  const password = data.get("password");
  if (typeof password !== "string") return;

  signInWithEmailAndPassword(auth, email, password)
    .then((userCredential) => userCredential.user.getIdToken())
    .then((token) => sendTokenToServer(token))
    .catch((reason) => {
      firebaseStatus.value = reason.code;
      form.submit();
    });

  return false;
};
