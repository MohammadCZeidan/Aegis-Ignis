/*
 * Compatibility shim for BaseReactPackage in React Native 0.73
 * This provides BaseReactPackage for modules that require React Native 0.74+ API
 */
package com.facebook.react;

import androidx.annotation.NonNull;
import com.facebook.react.bridge.NativeModule;
import com.facebook.react.bridge.ReactApplicationContext;
import com.facebook.react.module.model.ReactModuleInfo;
import com.facebook.react.module.model.ReactModuleInfoProvider;
import com.facebook.react.uimanager.ViewManager;
import java.util.Collections;
import java.util.List;
import java.util.Map;

/**
 * Base class for React Native packages compatible with React Native 0.73
 * Provides default implementations for modules expecting BaseReactPackage
 */
public abstract class BaseReactPackage extends TurboReactPackage {
    
    @Override
    @NonNull
    public List<ViewManager> createViewManagers(@NonNull ReactApplicationContext reactContext) {
        return Collections.emptyList();
    }
    
    @Override
    @NonNull
    public ReactModuleInfoProvider getReactModuleInfoProvider() {
        return () -> Collections.<String, ReactModuleInfo>emptyMap();
    }
}
