import React, {useEffect, useState} from 'react';
import {
  View,
  Text,
  StyleSheet,
  FlatList,
  TouchableOpacity,
  RefreshControl,
  Image,
  ActivityIndicator,
  Alert,
} from 'react-native';
import api, {Alert as AlertType} from '../services/api';
import {getStorageUrl} from '../config/api';

const AlertsScreen: React.FC = () => {
  const [alerts, setAlerts] = useState<AlertType[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadAlerts = async () => {
    try {
      setError(null);
      console.log('Loading alerts...');
      const data = await api.getAlerts({limit: 50});
      console.log('Alerts loaded:', data);
      setAlerts(Array.isArray(data) ? data : []);
    } catch (error: any) {
      console.error('Error loading alerts:', error);
      const errorMessage = error.response?.data?.message || error.message || 'Failed to load alerts';
      setError(errorMessage);
      Alert.alert(
        'Error Loading Alerts',
        errorMessage + '\n\nStatus: ' + (error.response?.status || 'Unknown'),
        [{text: 'OK'}]
      );
      setAlerts([]);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    loadAlerts();
  }, []);

  const onRefresh = () => {
    setRefreshing(true);
    loadAlerts();
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical':
        return '#dc2626';
      case 'high':
        return '#ea580c';
      case 'medium':
        return '#f59e0b';
      default:
        return '#6b7280';
    }
  };

  const renderAlert = ({item}: {item: AlertType}) => (
    <TouchableOpacity style={styles.alertCard}>
      <View style={styles.alertHeader}>
        <View style={styles.alertInfo}>
          <Text style={styles.alertType}>{item.event_type}</Text>
          <Text style={styles.alertTime}>
            {new Date(item.created_at).toLocaleString()}
          </Text>
        </View>
        <View
          style={[
            styles.severityBadge,
            {backgroundColor: getSeverityColor(item.severity)},
          ]}>
          <Text style={styles.severityText}>{item.severity.toUpperCase()}</Text>
        </View>
      </View>

      {item.screenshot_path && (
        <Image
          source={{uri: getStorageUrl(item.screenshot_path)}}
          style={styles.alertImage}
          resizeMode="cover"
        />
      )}

      <View style={styles.alertFooter}>
        <Text style={styles.alertStatus}>Status: {item.status}</Text>
        {item.confidence && (
          <Text style={styles.confidence}>
            Confidence: {(item.confidence * 100).toFixed(0)}%
          </Text>
        )}
      </View>
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
      data={alerts}
      renderItem={renderAlert}
      keyExtractor={item => item.id.toString()}
      contentContainerStyle={styles.list}
      refreshControl={
        <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
      }
      ListEmptyComponent={
        <View style={styles.emptyContainer}>
          <Text style={styles.emptyText}>
            {error ? `Error: ${error}` : 'No alerts found'}
          </Text>
          {error && (
            <TouchableOpacity style={styles.retryButton} onPress={loadAlerts}>
              <Text style={styles.retryButtonText}>Retry</Text>
            </TouchableOpacity>
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
  alertCard: {
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
  alertHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 12,
  },
  alertInfo: {
    flex: 1,
  },
  alertType: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#1f2937',
    marginBottom: 4,
  },
  alertTime: {
    fontSize: 12,
    color: '#6b7280',
  },
  severityBadge: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 4,
  },
  severityText: {
    color: '#fff',
    fontSize: 10,
    fontWeight: 'bold',
  },
  alertImage: {
    width: '100%',
    height: 200,
    borderRadius: 8,
    marginBottom: 12,
  },
  alertFooter: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  alertStatus: {
    fontSize: 14,
    color: '#6b7280',
  },
  confidence: {
    fontSize: 14,
    fontWeight: '600',
    color: '#1e40af',
  },
  emptyContainer: {
    padding: 40,
    alignItems: 'center',
  },
  emptyText: {
    textAlign: 'center',
    color: '#9ca3af',
    fontSize: 16,
    marginBottom: 16,
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

export default AlertsScreen;
