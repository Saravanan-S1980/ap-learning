import { CapacitorConfig } from '@capacitor/cli';

const config: CapacitorConfig = {
  appId: 'com.healthprotocol.app',
  appName: 'Health Protocol',
  webDir: 'dist',
  server: {
    // For dev: uncomment and set to your LAN IP
    // url: 'http://192.168.x.x:5173',
    // cleartext: true
  },
  plugins: {
    Camera: {
      presentationStyle: 'fullScreen',
    },
    PushNotifications: {
      presentationOptions: ['badge', 'sound', 'alert'],
    },
  },
};

export default config;
