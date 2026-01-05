/**
 * Diagnostic Tree Detail Screen
 */
import React, {useEffect, useState} from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  ActivityIndicator,
} from 'react-native';
import {RouteProp} from '@react-navigation/native';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';
import {diagnosticsApi} from '../api/diagnostics';
import {DiagnosticTree} from '../types';
import {colors, spacing, typography} from '../constants/theme';
import type {RootStackParamList} from '../types';

type TreeDetailScreenRouteProp = RouteProp<RootStackParamList, 'TreeDetail'>;

interface Props {
  route: TreeDetailScreenRouteProp;
}

const TreeDetailScreen: React.FC<Props> = ({route}) => {
  const {treeId} = route.params;
  const [tree, setTree] = useState<DiagnosticTree | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadTree();
  }, [treeId]);

  const loadTree = async () => {
    try {
      const data = await diagnosticsApi.getTree(treeId);
      setTree(data);
    } catch (error) {
      console.error('Failed to load tree:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <View style={styles.centerContent}>
        <ActivityIndicator size="large" color={colors.primary} />
      </View>
    );
  }

  if (!tree) {
    return (
      <View style={styles.centerContent}>
        <Icon name="alert-circle" size={48} color={colors.error} />
        <Text style={styles.errorText}>Failed to load diagnostic tree</Text>
      </View>
    );
  }

  return (
    <ScrollView style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.title}>{tree.diagnosis}</Text>
        <View style={styles.metaContainer}>
          <View style={styles.metaItem}>
            <Icon name="family-tree" size={16} color={colors.textSecondary} />
            <Text style={styles.metaText}>{tree.family}</Text>
          </View>
          {tree.icd10 && tree.icd10.length > 0 && (
            <View style={styles.metaItem}>
              <Icon name="code-tags" size={16} color={colors.textSecondary} />
              <Text style={styles.metaText}>{tree.icd10.join(', ')}</Text>
            </View>
          )}
        </View>
      </View>

      {/* Description */}
      {tree.description && (
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Description</Text>
          <Text style={styles.description}>{tree.description}</Text>
        </View>
      )}

      {/* Symptoms */}
      {tree.symptoms && tree.symptoms.length > 0 && (
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Associated Symptoms</Text>
          <View style={styles.chipContainer}>
            {tree.symptoms.map((symptom, index) => (
              <View key={index} style={styles.chip}>
                <Text style={styles.chipText}>{symptom}</Text>
              </View>
            ))}
          </View>
        </View>
      )}

      {/* Risk Factors */}
      {tree.risk_factors && tree.risk_factors.length > 0 && (
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Risk Factors</Text>
          {tree.risk_factors.map((factor, index) => (
            <View key={index} style={styles.listItem}>
              <Icon name="alert" size={16} color={colors.warning} />
              <Text style={styles.listItemText}>{factor}</Text>
            </View>
          ))}
        </View>
      )}

      {/* Diagnostic Criteria */}
      {tree.diagnostic_criteria && tree.diagnostic_criteria.length > 0 && (
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Diagnostic Criteria</Text>
          {tree.diagnostic_criteria.map((criteria, index) => (
            <View key={index} style={styles.listItem}>
              <Icon name="checkbox-marked-circle" size={16} color={colors.success} />
              <Text style={styles.listItemText}>{criteria}</Text>
            </View>
          ))}
        </View>
      )}

      {/* Red Flags */}
      {tree.red_flags && tree.red_flags.length > 0 && (
        <View style={[styles.section, styles.redFlagsSection]}>
          <Text style={[styles.sectionTitle, styles.redFlagsTitle]}>
            ⚠️ Red Flags
          </Text>
          {tree.red_flags.map((flag, index) => (
            <View key={index} style={styles.listItem}>
              <Icon name="alert-octagon" size={16} color={colors.error} />
              <Text style={[styles.listItemText, styles.redFlagText]}>{flag}</Text>
            </View>
          ))}
        </View>
      )}

      {/* Actions */}
      <View style={styles.actions}>
        <TouchableOpacity style={styles.actionButton}>
          <Icon name="heart-outline" size={24} color={colors.primary} />
          <Text style={styles.actionButtonText}>Add to Favorites</Text>
        </TouchableOpacity>
        <TouchableOpacity style={styles.actionButton}>
          <Icon name="share-variant" size={24} color={colors.primary} />
          <Text style={styles.actionButtonText}>Share</Text>
        </TouchableOpacity>
      </View>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
  },
  centerContent: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  errorText: {
    ...typography.body,
    color: colors.error,
    marginTop: spacing.md,
  },
  header: {
    padding: spacing.xl,
    backgroundColor: colors.surface,
  },
  title: {
    ...typography.h2,
    color: colors.text,
  },
  metaContainer: {
    marginTop: spacing.md,
  },
  metaItem: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: spacing.xs,
  },
  metaText: {
    ...typography.caption,
    color: colors.textSecondary,
    marginLeft: spacing.xs,
  },
  section: {
    padding: spacing.xl,
  },
  sectionTitle: {
    ...typography.h3,
    color: colors.text,
    marginBottom: spacing.md,
  },
  description: {
    ...typography.body,
    color: colors.text,
    lineHeight: 24,
  },
  chipContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    marginHorizontal: -spacing.xs,
  },
  chip: {
    backgroundColor: colors.primaryLight,
    borderRadius: 16,
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.xs,
    margin: spacing.xs,
  },
  chipText: {
    ...typography.caption,
    color: colors.primary,
  },
  listItem: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    marginBottom: spacing.md,
  },
  listItemText: {
    ...typography.body,
    color: colors.text,
    marginLeft: spacing.sm,
    flex: 1,
  },
  redFlagsSection: {
    backgroundColor: colors.errorLight,
  },
  redFlagsTitle: {
    color: colors.error,
  },
  redFlagText: {
    color: colors.error,
    fontWeight: 'bold',
  },
  actions: {
    flexDirection: 'row',
    padding: spacing.xl,
    gap: spacing.md,
  },
  actionButton: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: colors.surface,
    borderRadius: 8,
    padding: spacing.md,
  },
  actionButtonText: {
    ...typography.body,
    color: colors.primary,
    marginLeft: spacing.sm,
  },
});

export default TreeDetailScreen;
