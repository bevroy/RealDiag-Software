/**
 * Settings Screen
 */
import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Switch,
  Alert,
} from 'react-native';
import {useSelector, useDispatch} from 'react-redux';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';
import {logout} from '../store/slices/authSlice';
import {
  toggleVoiceInput,
  toggleBiometrics,
  toggleOfflineMode,
} from '../store/slices/settingsSlice';
import {authApi} from '../api/auth';
import {RootState} from '../store/store';
import {colors, spacing, typography} from '../constants/theme';

const SettingsScreen = () => {
  const {user} = useSelector((state: RootState) => state.auth);
  const settings = useSelector((state: RootState) => state.settings);
  const dispatch = useDispatch();

  const handleLogout = () => {
    Alert.alert('Logout', 'Are you sure you want to logout?', [
      {text: 'Cancel', style: 'cancel'},
      {
        text: 'Logout',
        style: 'destructive',
        onPress: async () => {
          await authApi.logout();
          dispatch(logout());
        },
      },
    ]);
  };

  return (
    <ScrollView style={styles.container}>
      {/* User Profile */}
      <View style={styles.profileSection}>
        <View style={styles.avatarContainer}>
          <Icon name="account" size={48} color={colors.white} />
        </View>
        <Text style={styles.userName}>{user?.full_name}</Text>
        <Text style={styles.userEmail}>{user?.email}</Text>
        <Text style={styles.userRole}>{user?.role} • {user?.specialty}</Text>
      </View>

      {/* App Settings */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>App Settings</Text>
        
        <SettingRow
          icon="microphone"
          title="Voice Input"
          subtitle="Use voice for symptom search"
          value={settings.voiceInputEnabled}
          onValueChange={() => dispatch(toggleVoiceInput())}
        />

        <SettingRow
          icon="fingerprint"
          title="Biometric Authentication"
          subtitle="Use Face ID / Touch ID"
          value={settings.biometricsEnabled}
          onValueChange={() => dispatch(toggleBiometrics())}
        />

        <SettingRow
          icon="cloud-off-outline"
          title="Offline Mode"
          subtitle="Cache rules for offline use"
          value={settings.offlineMode}
          onValueChange={() => dispatch(toggleOfflineMode())}
        />
      </View>

      {/* Account Actions */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Account</Text>
        
        <TouchableOpacity style={styles.actionButton}>
          <Icon name="account-edit" size={24} color={colors.primary} />
          <Text style={styles.actionText}>Edit Profile</Text>
          <Icon name="chevron-right" size={24} color={colors.textSecondary} />
        </TouchableOpacity>

        <TouchableOpacity style={styles.actionButton}>
          <Icon name="lock-reset" size={24} color={colors.primary} />
          <Text style={styles.actionText}>Change Password</Text>
          <Icon name="chevron-right" size={24} color={colors.textSecondary} />
        </TouchableOpacity>

        <TouchableOpacity style={styles.actionButton}>
          <Icon name="shield-check" size={24} color={colors.primary} />
          <Text style={styles.actionText}>Privacy & Security</Text>
          <Icon name="chevron-right" size={24} color={colors.textSecondary} />
        </TouchableOpacity>
      </View>

      {/* App Info */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>About</Text>
        
        <TouchableOpacity style={styles.actionButton}>
          <Icon name="information" size={24} color={colors.textSecondary} />
          <Text style={styles.actionText}>About RealDiag</Text>
          <Icon name="chevron-right" size={24} color={colors.textSecondary} />
        </TouchableOpacity>

        <TouchableOpacity style={styles.actionButton}>
          <Icon name="file-document" size={24} color={colors.textSecondary} />
          <Text style={styles.actionText}>Terms of Service</Text>
          <Icon name="chevron-right" size={24} color={colors.textSecondary} />
        </TouchableOpacity>

        <TouchableOpacity style={styles.actionButton}>
          <Icon name="shield" size={24} color={colors.textSecondary} />
          <Text style={styles.actionText}>Privacy Policy</Text>
          <Icon name="chevron-right" size={24} color={colors.textSecondary} />
        </TouchableOpacity>

        <View style={styles.versionInfo}>
          <Text style={styles.versionText}>Version 1.0.0</Text>
        </View>
      </View>

      {/* Logout Button */}
      <TouchableOpacity
        style={styles.logoutButton}
        onPress={handleLogout}>
        <Icon name="logout" size={24} color={colors.error} />
        <Text style={styles.logoutText}>Logout</Text>
      </TouchableOpacity>
    </ScrollView>
  );
};

const SettingRow = ({
  icon,
  title,
  subtitle,
  value,
  onValueChange,
}: {
  icon: string;
  title: string;
  subtitle: string;
  value: boolean;
  onValueChange: () => void;
}) => (
  <View style={styles.settingRow}>
    <Icon name={icon} size={24} color={colors.primary} />
    <View style={styles.settingContent}>
      <Text style={styles.settingTitle}>{title}</Text>
      <Text style={styles.settingSubtitle}>{subtitle}</Text>
    </View>
    <Switch
      value={value}
      onValueChange={onValueChange}
      trackColor={{false: colors.border, true: colors.primaryLight}}
      thumbColor={value ? colors.primary : colors.textSecondary}
    />
  </View>
);

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
  },
  profileSection: {
    alignItems: 'center',
    padding: spacing.xl,
    backgroundColor: colors.surface,
  },
  avatarContainer: {
    width: 100,
    height: 100,
    borderRadius: 50,
    backgroundColor: colors.primary,
    justifyContent: 'center',
    alignItems: 'center',
  },
  userName: {
    ...typography.h2,
    color: colors.text,
    marginTop: spacing.md,
  },
  userEmail: {
    ...typography.body,
    color: colors.textSecondary,
    marginTop: spacing.xs,
  },
  userRole: {
    ...typography.caption,
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
  settingRow: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: colors.surface,
    borderRadius: 8,
    padding: spacing.md,
    marginBottom: spacing.sm,
  },
  settingContent: {
    flex: 1,
    marginLeft: spacing.md,
  },
  settingTitle: {
    ...typography.body,
    color: colors.text,
  },
  settingSubtitle: {
    ...typography.caption,
    color: colors.textSecondary,
    marginTop: spacing.xs,
  },
  actionButton: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: colors.surface,
    borderRadius: 8,
    padding: spacing.md,
    marginBottom: spacing.sm,
  },
  actionText: {
    flex: 1,
    ...typography.body,
    color: colors.text,
    marginLeft: spacing.md,
  },
  versionInfo: {
    alignItems: 'center',
    marginTop: spacing.lg,
  },
  versionText: {
    ...typography.caption,
    color: colors.textSecondary,
  },
  logoutButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: colors.errorLight,
    borderRadius: 8,
    padding: spacing.lg,
    margin: spacing.xl,
    marginTop: 0,
  },
  logoutText: {
    ...typography.button,
    color: colors.error,
    marginLeft: spacing.sm,
  },
});

export default SettingsScreen;
