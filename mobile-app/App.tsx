import React from 'react';
import {NavigationContainer} from '@react-navigation/native';
import {createNativeStackNavigator} from '@react-navigation/native-stack';
import {StatusBar, useColorScheme} from 'react-native';
import {SafeAreaProvider} from 'react-native-safe-area-context';

import DashboardScreen from './src/screens/DashboardScreen';
import LoginScreen from './src/screens/LoginScreen';
import AlertsScreen from './src/screens/AlertsScreen';
import FloorsScreen from './src/screens/FloorsScreen';
import CamerasScreen from './src/screens/CamerasScreen';
import SettingsScreen from './src/screens/SettingsScreen';

const Stack = createNativeStackNavigator();

function App(): React.JSX.Element {
  const isDarkMode = useColorScheme() === 'dark';

  return (
    <SafeAreaProvider>
      <StatusBar
        barStyle={isDarkMode ? 'light-content' : 'dark-content'}
        backgroundColor="#ffffff"
      />
      <NavigationContainer>
        <Stack.Navigator
          initialRouteName="Login"
          screenOptions={{
            headerStyle: {
              backgroundColor: '#1e40af',
            },
            headerTintColor: '#fff',
            headerTitleStyle: {
              fontWeight: 'bold',
            },
          }}>
          <Stack.Screen
            name="Login"
            component={LoginScreen}
            options={{headerShown: false}}
          />
          <Stack.Screen
            name="Dashboard"
            component={DashboardScreen}
            options={{title: 'Aegis Ignis Dashboard'}}
          />
          <Stack.Screen
            name="Alerts"
            component={AlertsScreen}
            options={{title: 'Fire Alerts'}}
          />
          <Stack.Screen
            name="Floors"
            component={FloorsScreen}
            options={{title: 'Floor Monitoring'}}
          />
          <Stack.Screen
            name="Cameras"
            component={CamerasScreen}
            options={{title: 'Camera Management'}}
          />
          <Stack.Screen
            name="Settings"
            component={SettingsScreen}
            options={{title: 'Settings'}}
          />
        </Stack.Navigator>
      </NavigationContainer>
    </SafeAreaProvider>
  );
}

export default App;
