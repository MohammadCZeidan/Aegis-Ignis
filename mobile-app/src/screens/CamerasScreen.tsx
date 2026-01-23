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
} from 'react-native';
import api, {Camera} from '../services/api';

const CamerasScreen: React.FC = () => {
  const [cameras, setCameras] = useState<Camera[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const loadCameras = async () => {
    try {
      const data = await api.getCameras();
      setCameras(data);
    } catch (error) {
      console.error('Error loading cameras:', error);
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
        <Text style={styles.emptyText}>No cameras found</Text>
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
  emptyText: {
    textAlign: 'center',
    color: '#9ca3af',
    padding: 40,
    fontSize: 16,
  },
});

export default CamerasScreen;
