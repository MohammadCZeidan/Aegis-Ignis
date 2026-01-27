import React, {useEffect, useState} from 'react';
import {
  View,
  Text,
  StyleSheet,
  FlatList,
  TouchableOpacity,
  RefreshControl,
  ActivityIndicator,
  Switch,
  Alert,
} from 'react-native';
import api, {Camera} from '../services/api';

const CamerasScreen: React.FC = () => {
  const [cameras, setCameras] = useState<Camera[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadCameras = async () => {
    try {
      setError(null);
      console.log('[CamerasScreen] Loading cameras...');
      const data = await api.getCameras();
      console.log('[CamerasScreen] Cameras loaded:', data);
      console.log('[CamerasScreen] Data type:', typeof data);
      console.log('[CamerasScreen] Is array?', Array.isArray(data));
      console.log('[CamerasScreen] Data length:', Array.isArray(data) ? data.length : 'N/A');
      
      if (Array.isArray(data)) {
        setCameras(data);
        if (data.length === 0) {
          console.warn('[CamerasScreen] Received empty cameras array from API');
          setError('No cameras found in database');
        }
      } else {
        console.error('[CamerasScreen] Data is not an array:', data);
        setCameras([]);
        setError('Invalid response format from server');
      }
    } catch (error: any) {
      console.error('[CamerasScreen] Error loading cameras:', error);
      console.error('[CamerasScreen] Error details:', {
        message: error.message,
        status: error.response?.status,
        statusText: error.response?.statusText,
        data: error.response?.data,
        url: error.config?.url,
        baseURL: error.config?.baseURL,
      });
      const errorMessage = error.response?.data?.message || error.message || 'Failed to load cameras';
      setError(errorMessage);
      Alert.alert(
        'Error Loading Cameras',
        errorMessage + '\n\nStatus: ' + (error.response?.status || 'Unknown') + '\nURL: ' + (error.config?.url || 'Unknown'),
        [{text: 'OK'}]
      );
      setCameras([]);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    loadCameras();
  }, []);

  const onRefresh = () => {
    setRefreshing(true);
    loadCameras();
  };

  const renderCamera = ({item}: {item: Camera}) => (
    <TouchableOpacity style={styles.cameraCard}>
      <View style={styles.cameraHeader}>
        <View style={styles.cameraInfo}>
          <Text style={styles.cameraName}>{item.name}</Text>
          <Text style={styles.cameraId}>Camera ID: {item.id}</Text>
        </View>
        <Switch
          value={item.is_active}
          onValueChange={() => {
            // Handle toggle
          }}
          trackColor={{false: '#d1d5db', true: '#1e40af'}}
        />
      </View>
      <Text style={styles.cameraUrl} numberOfLines={1}>
        {item.rtsp_url}
      </Text>
      <Text style={styles.cameraFloor}>Floor ID: {item.floor_id}</Text>
    </TouchableOpacity>
  );

  if (loading) {
    return (
      <View style={styles.center}>
        <ActivityIndicator size="large" color="#1e40af" />
      </View>
    );
  }

  return (
    <FlatList
      data={cameras}
      renderItem={renderCamera}
      keyExtractor={item => item.id.toString()}
      contentContainerStyle={styles.list}
      refreshControl={
        <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
      }
      ListEmptyComponent={
        <View style={styles.emptyContainer}>
          <Text style={styles.emptyText}>
            {error ? `Error: ${error}` : 'No cameras found'}
          </Text>
          {error && (
            <TouchableOpacity style={styles.retryButton} onPress={loadCameras}>
              <Text style={styles.retryButtonText}>Retry</Text>
            </TouchableOpacity>
          )}
          {!error && !loading && (
            <Text style={styles.emptySubtext}>
              Make sure cameras are configured in the web dashboard.
            </Text>
          )}
        </View>
      }
    />
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f3f4f6',
  },
  list: {
    padding: 16,
  },
  center: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  cameraCard: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
    shadowColor: '#000',
    shadowOffset: {width: 0, height: 2},
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  cameraHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  cameraInfo: {
    flex: 1,
  },
  cameraName: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#1f2937',
    marginBottom: 4,
  },
  cameraId: {
    fontSize: 12,
    color: '#6b7280',
  },
  cameraUrl: {
    fontSize: 12,
    color: '#6b7280',
    marginBottom: 4,
  },
  cameraFloor: {
    fontSize: 14,
    color: '#6b7280',
  },
  emptyContainer: {
    padding: 40,
    alignItems: 'center',
  },
  emptyText: {
    textAlign: 'center',
    color: '#9ca3af',
    fontSize: 16,
    marginBottom: 8,
  },
  emptySubtext: {
    textAlign: 'center',
    color: '#9ca3af',
    fontSize: 12,
    marginTop: 8,
  },
  retryButton: {
    backgroundColor: '#1e40af',
    paddingHorizontal: 24,
    paddingVertical: 12,
    borderRadius: 8,
  },
  retryButtonText: {
    color: '#fff',
    fontWeight: '600',
  },
});

export default CamerasScreen;
