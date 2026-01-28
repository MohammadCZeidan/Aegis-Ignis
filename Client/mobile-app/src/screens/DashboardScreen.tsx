import React, {useEffect, useState} from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  RefreshControl,
  ActivityIndicator,
  Alert,
} from 'react-native';
import {useNavigation} from '@react-navigation/native';
import api, {Alert as AlertType, Floor} from '../services/api';
const DashboardScreen: React.FC = () => {
  const [alerts, setAlerts] = useState<AlertType[]>([]);
  const [floors, setFloors] = useState<Floor[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const navigation = useNavigation();

  const loadData = async () => {
    try {
      console.log('Loading dashboard data...');
      const [alertsData, floorsData] = await Promise.all([
        api.getAlerts({limit: 5}),
        api.getFloors(),
      ]);
      console.log('Dashboard data loaded - Alerts:', alertsData, 'Floors:', floorsData);
      // Ensure we always have arrays, even if API returns undefined/null
      setAlerts(Array.isArray(alertsData) ? alertsData : []);
      setFloors(Array.isArray(floorsData) ? floorsData : []);
    } catch (error: any) {
      console.error('Error loading dashboard data:', error);
      console.error('Error details:', {
        message: error.message,
        status: error.response?.status,
        data: error.response?.data,
        url: error.config?.url,
      });
      // Set empty arrays on error to prevent undefined errors
      setAlerts([]);
      setFloors([]);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const onRefresh = () => {
    setRefreshing(true);
    loadData();
  };

  if (loading) {
    return (
      <View style={styles.center}>
        <ActivityIndicator size="large" color="#1e40af" />
      </View>
    );
  }

  // Ensure alerts is always an array before filtering
  const alertsArray = Array.isArray(alerts) ? alerts : [];
  const activeAlerts = alertsArray.filter(a => a.status !== 'resolved');
  const criticalAlerts = alertsArray.filter(a => a.severity === 'critical');

  return (
    <ScrollView
      style={styles.container}
      refreshControl={
        <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
      }>
      <View style={styles.content}>
        {/* Stats Cards */}
        <View style={styles.statsRow}>
          <View style={styles.statCard}>
            <Text style={styles.statValue}>{Array.isArray(floors) ? floors.length : 0}</Text>
            <Text style={styles.statLabel}>Floors</Text>
          </View>
          <View style={styles.statCard}>
            <Text style={styles.statValue}>{activeAlerts.length}</Text>
            <Text style={styles.statLabel}>Active Alerts</Text>
          </View>
          <View style={[styles.statCard, criticalAlerts.length > 0 && styles.criticalCard]}>
            <Text style={[styles.statValue, criticalAlerts.length > 0 && styles.criticalText]}>
              {criticalAlerts.length}
            </Text>
            <Text style={styles.statLabel}>Critical</Text>
          </View>
        </View>

        {/* Quick Actions */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Quick Actions</Text>
          <View style={styles.actionRow}>
            <TouchableOpacity
              style={styles.actionButton}
              onPress={() => navigation.navigate('Alerts' as never)}>
              <Text style={styles.actionButtonText}>View Alerts</Text>
            </TouchableOpacity>
            <TouchableOpacity
              style={styles.actionButton}
              onPress={() => navigation.navigate('Floors' as never)}>
              <Text style={styles.actionButtonText}>Floor Monitor</Text>
            </TouchableOpacity>
            <TouchableOpacity
              style={styles.actionButton}
              onPress={() => navigation.navigate('Cameras' as never)}>
              <Text style={styles.actionButtonText}>Cameras</Text>
            </TouchableOpacity>
          </View>
        </View>

        {/* Recent Alerts */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Recent Alerts</Text>
          {alertsArray.length === 0 ? (
            <Text style={styles.emptyText}>No alerts</Text>
          ) : (
            alertsArray.map(alert => (
              <TouchableOpacity
                key={alert.id}
                style={[
                  styles.alertCard,
                  alert.severity === 'critical' && styles.criticalAlert,
                ]}
                onPress={() => navigation.navigate('Alerts' as never)}>
                <Text style={styles.alertType}>{alert.event_type}</Text>
                <Text style={styles.alertTime}>
                  {new Date(alert.created_at).toLocaleString()}
                </Text>
                <Text style={styles.alertStatus}>Status: {alert.status}</Text>
              </TouchableOpacity>
            ))
          )}
        </View>
      </View>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f3f4f6',
  },
  content: {
    padding: 16,
  },
  center: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  statsRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 20,
  },
  statCard: {
    flex: 1,
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 16,
    marginHorizontal: 4,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: {width: 0, height: 2},
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  criticalCard: {
    backgroundColor: '#fee2e2',
  },
  statValue: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#1e40af',
    marginBottom: 4,
  },
  criticalText: {
    color: '#dc2626',
  },
  statLabel: {
    fontSize: 12,
    color: '#6b7280',
  },
  section: {
    marginBottom: 24,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#1f2937',
    marginBottom: 12,
  },
  actionRow: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
  },
  actionButton: {
    backgroundColor: '#1e40af',
    borderRadius: 8,
    padding: 12,
    flex: 1,
    minWidth: '30%',
    alignItems: 'center',
  },
  actionButtonText: {
    color: '#fff',
    fontWeight: '600',
  },
  alertCard: {
    backgroundColor: '#fff',
    borderRadius: 8,
    padding: 16,
    marginBottom: 8,
    shadowColor: '#000',
    shadowOffset: {width: 0, height: 1},
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 2,
  },
  criticalAlert: {
    borderLeftWidth: 4,
    borderLeftColor: '#dc2626',
  },
  alertType: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#1f2937',
    marginBottom: 4,
  },
  alertTime: {
    fontSize: 12,
    color: '#6b7280',
    marginBottom: 4,
  },
  alertStatus: {
    fontSize: 14,
    color: '#6b7280',
  },
  emptyText: {
    textAlign: 'center',
    color: '#9ca3af',
    padding: 20,
  },
});

export default DashboardScreen;
