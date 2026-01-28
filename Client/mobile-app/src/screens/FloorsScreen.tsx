import React, {useEffect, useState} from 'react';
import {
  View,
  Text,
  StyleSheet,
  FlatList,
  TouchableOpacity,
  RefreshControl,
  ActivityIndicator,
} from 'react-native';
import api, {Floor} from '../services/api';
const FloorsScreen: React.FC = () => {
  const [floors, setFloors] = useState<Floor[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [occupancy, setOccupancy] = useState<Record<number, number>>({});

  const loadFloors = async () => {
    try {
      const data = await api.getFloors();
      setFloors(data);

      // Load occupancy for each floor
      const occupancyData: Record<number, number> = {};
      for (const floor of data) {
        try {
          const occ = await api.getFloorOccupancy(floor.id);
          occupancyData[floor.id] = occ.person_count;
        } catch (error) {
          occupancyData[floor.id] = 0;
        }
      }
      setOccupancy(occupancyData);
    } catch (error) {
      console.error('Error loading floors:', error);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    loadFloors();
  }, []);

  const onRefresh = () => {
    setRefreshing(true);
    loadFloors();
  };

  const renderFloor = ({item}: {item: Floor}) => (
    <TouchableOpacity style={styles.floorCard}>
      <View style={styles.floorHeader}>
        <Text style={styles.floorName}>
          {item.name || `Floor ${item.floor_number}`}
        </Text>
        <View style={styles.occupancyBadge}>
          <Text style={styles.occupancyText}>
            {occupancy[item.id] || 0} people
          </Text>
        </View>
      </View>
      <Text style={styles.floorNumber}>Floor #{item.floor_number}</Text>
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
      data={floors}
      renderItem={renderFloor}
      keyExtractor={item => item.id.toString()}
      contentContainerStyle={styles.list}
      refreshControl={
        <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
      }
      ListEmptyComponent={
        <Text style={styles.emptyText}>No floors found</Text>
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
  floorCard: {
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
  floorHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  floorName: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#1f2937',
    flex: 1,
  },
  occupancyBadge: {
    backgroundColor: '#dbeafe',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 16,
  },
  occupancyText: {
    color: '#1e40af',
    fontSize: 14,
    fontWeight: '600',
  },
  floorNumber: {
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

export default FloorsScreen;
