/*
 * Compatibility shim for ViewManagerWithGeneratedInterface in React Native 0.73
 * This provides ViewManagerWithGeneratedInterface for modules that require React Native 0.74+ API
 */
package com.facebook.react.uimanager;

/**
 * Marker interface for ViewManagers that have generated interfaces.
 * This is a compatibility shim for React Native 0.73 where this interface doesn't exist.
 * Modules expecting this interface (like react-native-gesture-handler) can use it.
 */
public interface ViewManagerWithGeneratedInterface {
    // Marker interface - no methods required
}
