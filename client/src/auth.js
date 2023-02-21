import { initializeApp } from 'firebase/app';
import { getAuth } from 'firebase/auth';

const firebaseConfig = {
  apiKey: 'AIzaSyCy261Dj82etz9-AwMgKG0o6HCbv3HNzbc',
  authDomain: 'cp-identity.firebaseapp.com',
  projectId: 'cp-identity',
  messagingSenderId: '462735301864',
};

export const app = initializeApp(firebaseConfig);
export const auth = getAuth();
