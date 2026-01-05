/**
 * Home Screen
 */
import React, {useEffect} from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  ActivityIndicator,
} from 'react-native';
import {useSelector, useDispatch} from 'react-redux';
import {useNavigation} from '@react-navigation/native';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';
import {RootState} from '../store/store';
import {colors, spacing, typography} from '../constants/theme';
import type {MainTabNavigationProp} from '../types';

const HomeScreen = () => {
  const {user} = useSelector((state: RootState) => state.auth);
  const {recentSearches} = useSelector((state: RootState) => state.diagnostics);
  const navigation = useNavigation<MainTabNavigationProp>();

  const quickActions = [
    {
      id: 'search',
      title: 'New Search',
      icon: 'magnify',
      color: colors.primary,
      onPress: () => navigation.navigate('Search'),
    },
    {
      id: 'patient',
      title: 'Patient Data',
      icon: 'account-heart',
      color: colors.success,
      onPress: () => navigation.navigate('Patient'),
    },
    {
      id: 'favorites',
      title: 'Favorites',
      icon: 'heart',
      color: colors.error,
      onPress: () => navigation.navigate('Search'),
    },
    {
      id: 'history',
      title: 'History',
      icon: 'history',
      color: colors.warning,
      onPress: () => navigation.navigate('Search'),
    },
  ];

  return (
    <ScrollView style={styles.container}>
      <View style={styles.header}>
        <View>
          <Text style={styles.greeting}>
            Welcome back, {user?.full_name?.split(' ')[0]}
          </Text>
          <Text style={styles.subtitle}>{user?.role} • {user?.specialty}</Text>
        </View>
        <Icon name="stethoscope" size={40} color={colors.primary} />
      </View>

      {/* Quick Actions */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Quick Actions</Text>
        <View style={styles.actionGrid}>
          {quickActions.map(action => (
            <TouchableOpacity
              key={action.id}
              style={styles.actionCard}
              onPress={action.onPress}>
              <Icon name={action.icon} size={32} color={action.color} />
              <Text style={styles.actionText}>{action.title}</Text>
            </TouchableOpacity>
          ))}
        </View>
      </View>

      {/* Recent Searches */}
      {recentSearches.length > 0 && (
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Recent Searches</Text>
          {recentSearches.slice(0, 5).map((search, index) => (
            <TouchableOpacity key={index} style={styles.searchCard}>
              <Icon name="clock-outline" size={20} color={colors.textSecondary} />
              <View style={styles.searchContent}>
                <Text style={styles.searchQuery}>{search.query}</Text>
                <Text style={styles.searchMeta}>
                  {search.results.length} results • {search.timestamp}
                </Text>
              </View>
              <Icon name="chevron-right" size={20} color={colors.textSecondary} />
            </TouchableOpacity>
          ))}
        </View>
      )}

      {/* Info Card */}
      <View style={[styles.section, styles.infoCard]}>
        <Icon name="information-outline" size={24} color={colors.primary} />
        <View style={styles.infoContent}>
          <Text style={styles.infoTitle}>Clinical Decision Support</Text>
          <Text style={styles.infoText}>
            This tool assists with differential diagnosis. Always use clinical
            judgment and consider patient context.
          </Text>
        </View>
      </View>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: spacing.xl,
    backgroundColor: colors.surface,
  },
  greeting: {
    ...typography.h2,
    color: colors.text,
  },
  subtitle: {
    ...typography.body,
    color: colors.textSecondary,
    marginTop: spacing.xs,
  },
  section: {
    padding: spacing.xl,
  },
  sectionTitle: {
    ...typography.h3,
    color: colors.text,
    marginBottom: spacing.md,
  },
  actionGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    marginHorizontal: -spacing.sm,
  },
  actionCard: {
    width: '50%',
    padding: spacing.sm,
  },
  actionCardInner: {
    backgroundColor: colors.surface,
    borderRadius: 12,
    padding: spacing.lg,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: {width: 0, height: 2},
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  actionText: {
    ...typography.body,
    color: colors.text,
    marginTop: spacing.sm,
    textAlign: 'center',
  },
  searchCard: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: colors.surface,
    borderRadius: 8,
    padding: spacing.md,
    marginBottom: spacing.sm,
  },
  searchContent: {
    flex: 1,
    marginLeft: spacing.md,
  },
  searchQuery: {
    ...typography.body,
    color: colors.text,
  },
  searchMeta: {
    ...typography.caption,
    color: colors.textSecondary,
    marginTop: spacing.xs,
  },
  infoCard: {
    flexDirection: 'row',
    backgroundColor: colors.primaryLight,
    borderRadius: 8,
    marginBottom: spacing.xl,
  },
  infoContent: {
    flex: 1,
    marginLeft: spacing.md,
  },
  infoTitle: {
    ...typography.h4,
    color: colors.primary,
    marginBottom: spacing.xs,
  },
  infoText: {
    ...typography.caption,
    color: colors.text,
  },
});

export default HomeScreen;
