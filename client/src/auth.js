import { initializeApp } from 'firebase/app';
import { getAuth } from 'firebase/auth';

const hostname = window.location.hostname;

let firebaseConfig = {
  apiKey: 'AIzaSyCy261Dj82etz9-AwMgKG0o6HCbv3HNzbc',
  authDomain: 'cp-identity.firebaseapp.com',
  projectId: 'cp-identity',
  messagingSenderId: '462735301864',
};

if (hostname.includes("cp-dev")) {
  firebaseConfig = {
    apiKey: 'AIzaSyCWlQ7VjJZemeGjhs8DsRavoeEbX3Sa13A',
    authDomain: 'cp-identity-dev.firebaseapp.com',
    projectId: 'cp-identity-dev',
    messagingSenderId: '792706405207',
  };
}

export const app = initializeApp(firebaseConfig);
export const auth = getAuth();
