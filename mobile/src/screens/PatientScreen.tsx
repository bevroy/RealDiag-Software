/**
 * Patient Screen
 */
import React, {useEffect} from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  ActivityIndicator,
  RefreshControl,
} from 'react-native';
import {useSelector, useDispatch} from 'react-redux';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';
import {RootState} from '../store/store';
import {colors, spacing, typography} from '../constants/theme';

const PatientScreen = () => {
  const {patient, loading} = useSelector((state: RootState) => state.patient);
  const [refreshing, setRefreshing] = React.useState(false);

  const onRefresh = async () => {
    setRefreshing(true);
    // TODO: Fetch patient data from EHR
    setTimeout(() => setRefreshing(false), 1000);
  };

  if (!patient) {
    return (
      <View style={styles.container}>
        <View style={styles.emptyState}>
          <Icon name="account-alert-outline" size={64} color={colors.textSecondary} />
          <Text style={styles.emptyTitle}>No Patient Selected</Text>
          <Text style={styles.emptyText}>
            Connect to your EHR system to view patient data
          </Text>
        </View>
      </View>
    );
  }

  return (
    <ScrollView
      style={styles.container}
      refreshControl={
        <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
      }>
      {/* Patient Header */}
      <View style={styles.header}>
        <View style={styles.avatarContainer}>
          <Icon name="account" size={48} color={colors.white} />
        </View>
        <View style={styles.headerInfo}>
          <Text style={styles.patientName}>{patient.name}</Text>
          <Text style={styles.patientMeta}>
            MRN: {patient.mrn} • Age: {patient.age} • {patient.sex}
          </Text>
        </View>
      </View>

      {/* Demographics */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Demographics</Text>
        <View style={styles.card}>
          <InfoRow icon="calendar" label="Date of Birth" value={patient.date_of_birth} />
          <InfoRow icon="gender-male-female" label="Sex" value={patient.sex} />
          <InfoRow icon="cake-variant" label="Age" value={`${patient.age} years`} />
        </View>
      </View>

      {/* Medications */}
      {patient.medications && patient.medications.length > 0 && (
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Current Medications</Text>
          <View style={styles.card}>
            {patient.medications.map((med, index) => (
              <View key={index} style={styles.medicationItem}>
                <Icon name="pill" size={20} color={colors.primary} />
                <View style={styles.medicationInfo}>
                  <Text style={styles.medicationName}>{med.name}</Text>
                  <Text style={styles.medicationDose}>{med.dosage}</Text>
                </View>
              </View>
            ))}
          </View>
        </View>
      )}

      {/* Allergies */}
      {patient.allergies && patient.allergies.length > 0 && (
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Allergies</Text>
          <View style={[styles.card, styles.allergyCard]}>
            {patient.allergies.map((allergy, index) => (
              <View key={index} style={styles.allergyItem}>
                <Icon name="alert-circle" size={20} color={colors.error} />
                <Text style={styles.allergyText}>{allergy}</Text>
              </View>
            ))}
          </View>
        </View>
      )}

      {/* Vitals */}
      {patient.vitals && (
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Recent Vitals</Text>
          <View style={styles.card}>
            <View style={styles.vitalsGrid}>
              <VitalCard
                icon="heart-pulse"
                label="Blood Pressure"
                value={patient.vitals.blood_pressure}
                color={colors.error}
              />
              <VitalCard
                icon="temperature-celsius"
                label="Temperature"
                value={patient.vitals.temperature}
                color={colors.warning}
              />
              <VitalCard
                icon="speedometer"
                label="Heart Rate"
                value={patient.vitals.heart_rate}
                color={colors.success}
              />
              <VitalCard
                icon="weight"
                label="Weight"
                value={patient.vitals.weight}
                color={colors.primary}
              />
            </View>
          </View>
        </View>
      )}
    </ScrollView>
  );
};

const InfoRow = ({
  icon,
  label,
  value,
}: {
  icon: string;
  label: string;
  value: string;
}) => (
  <View style={styles.infoRow}>
    <Icon name={icon} size={20} color={colors.textSecondary} />
    <View style={styles.infoContent}>
      <Text style={styles.infoLabel}>{label}</Text>
      <Text style={styles.infoValue}>{value}</Text>
    </View>
  </View>
);

const VitalCard = ({
  icon,
  label,
  value,
  color,
}: {
  icon: string;
  label: string;
  value: string;
  color: string;
}) => (
  <View style={styles.vitalCard}>
    <Icon name={icon} size={32} color={color} />
    <Text style={styles.vitalValue}>{value}</Text>
    <Text style={styles.vitalLabel}>{label}</Text>
  </View>
);

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: spacing.xl,
    backgroundColor: colors.surface,
  },
  avatarContainer: {
    width: 80,
    height: 80,
    borderRadius: 40,
    backgroundColor: colors.primary,
    justifyContent: 'center',
    alignItems: 'center',
  },
  headerInfo: {
    flex: 1,
    marginLeft: spacing.lg,
  },
  patientName: {
    ...typography.h2,
    color: colors.text,
  },
  patientMeta: {
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
  card: {
    backgroundColor: colors.surface,
    borderRadius: 12,
    padding: spacing.lg,
  },
  infoRow: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: spacing.md,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
  },
  infoContent: {
    flex: 1,
    marginLeft: spacing.md,
  },
  infoLabel: {
    ...typography.caption,
    color: colors.textSecondary,
  },
  infoValue: {
    ...typography.body,
    color: colors.text,
    marginTop: spacing.xs,
  },
  medicationItem: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: spacing.md,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
  },
  medicationInfo: {
    flex: 1,
    marginLeft: spacing.md,
  },
  medicationName: {
    ...typography.body,
    color: colors.text,
  },
  medicationDose: {
    ...typography.caption,
    color: colors.textSecondary,
    marginTop: spacing.xs,
  },
  allergyCard: {
    backgroundColor: colors.errorLight,
  },
  allergyItem: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: spacing.sm,
  },
  allergyText: {
    ...typography.body,
    color: colors.error,
    marginLeft: spacing.md,
    fontWeight: 'bold',
  },
  vitalsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    marginHorizontal: -spacing.sm,
  },
  vitalCard: {
    width: '50%',
    padding: spacing.sm,
    alignItems: 'center',
  },
  vitalValue: {
    ...typography.h3,
    color: colors.text,
    marginTop: spacing.sm,
  },
  vitalLabel: {
    ...typography.caption,
    color: colors.textSecondary,
    marginTop: spacing.xs,
    textAlign: 'center',
  },
  emptyState: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: spacing.xl,
  },
  emptyTitle: {
    ...typography.h3,
    color: colors.text,
    marginTop: spacing.lg,
  },
  emptyText: {
    ...typography.body,
    color: colors.textSecondary,
    marginTop: spacing.sm,
    textAlign: 'center',
  },
});

export default PatientScreen;
