// Scripts for firebase and firebase messaging
importScripts("https://www.gstatic.com/firebasejs/8.2.0/firebase-app.js");
importScripts("https://www.gstatic.com/firebasejs/8.2.0/firebase-messaging.js");

// Initialize the Firebase app in the service worker by passing the generated config
const firebaseConfig = {
    apiKey: "AIzaSyB8r5lC-hEaba36X6hSrubEZyvmzY8bRZ0",
    authDomain: "smooth-helper-219601.firebaseapp.com",
    databaseURL: "https://smooth-helper-219601.firebaseio.com",
    projectId: "smooth-helper-219601",
    storageBucket: "smooth-helper-219601.appspot.com",
    messagingSenderId: "890373965726",
    appId: "1:890373965726:web:0d5fe6a26fa0501055b88f",
    measurementId: "G-2W562DVY3F"
};

firebase.initializeApp(firebaseConfig);

// Retrieve firebase messaging
const messaging = firebase.messaging();

messaging.onBackgroundMessage(function(payload) {
  console.log("Received background message ", payload);

  const notificationTitle = payload.notification.title;
  const notificationOptions = {
    body: payload.notification.body,
  };

  self.registration.showNotification(notificationTitle, notificationOptions);
});