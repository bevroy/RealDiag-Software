/**
 * Search Screen
 */
import React, {useState, useEffect} from 'react';
import {
  View,
  Text,
  TextInput,
  StyleSheet,
  FlatList,
  TouchableOpacity,
  ActivityIndicator,
} from 'react-native';
import {useDispatch, useSelector} from 'react-redux';
import {useNavigation} from '@react-navigation/native';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';
import Voice from '@react-native-voice/voice';
import {setSearchResults, addRecentSearch} from '../store/slices/diagnosticsSlice';
import {diagnosticsApi} from '../api/diagnostics';
import {RootState} from '../store/store';
import {colors, spacing, typography} from '../constants/theme';
import type {SearchResult, MainTabNavigationProp} from '../types';

const SearchScreen = () => {
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const dispatch = useDispatch();
  const navigation = useNavigation<MainTabNavigationProp>();
  const {searchResults, recentSearches} = useSelector(
    (state: RootState) => state.diagnostics,
  );

  useEffect(() => {
    Voice.onSpeechResults = onSpeechResults;
    Voice.onSpeechEnd = onSpeechEnd;

    return () => {
      Voice.destroy().then(Voice.removeAllListeners);
    };
  }, []);

  const onSpeechResults = (e: any) => {
    if (e.value && e.value[0]) {
      setQuery(e.value[0]);
      handleSearch(e.value[0]);
    }
  };

  const onSpeechEnd = () => {
    setIsListening(false);
  };

  const startVoiceInput = async () => {
    try {
      setIsListening(true);
      await Voice.start('en-US');
    } catch (error) {
      console.error('Voice input error:', error);
      setIsListening(false);
    }
  };

  const stopVoiceInput = async () => {
    try {
      await Voice.stop();
      setIsListening(false);
    } catch (error) {
      console.error('Voice stop error:', error);
    }
  };

  const handleSearch = async (searchQuery?: string) => {
    const q = searchQuery || query;
    if (!q.trim()) return;

    setLoading(true);
    try {
      const response = await diagnosticsApi.searchSymptoms({query: q});
      
      if (response.results) {
        dispatch(setSearchResults(response.results));
        dispatch(addRecentSearch({
          query: q,
          results: response.results,
          timestamp: new Date().toISOString(),
        }));
      }
    } catch (error) {
      console.error('Search error:', error);
    } finally {
      setLoading(false);
    }
  };

  const renderSearchResult = ({item}: {item: SearchResult}) => (
    <TouchableOpacity
      style={styles.resultCard}
      onPress={() => navigation.navigate('TreeDetail', {treeId: item.tree_id})}>
      <View style={styles.resultHeader}>
        <Text style={styles.resultTitle}>{item.diagnosis}</Text>
        <View style={[styles.scoreBadge, {backgroundColor: getScoreColor(item.match_score)}]}>
          <Text style={styles.scoreText}>{Math.round(item.match_score * 100)}%</Text>
        </View>
      </View>
      
      <View style={styles.resultDetails}>
        <Icon name="family-tree" size={16} color={colors.textSecondary} />
        <Text style={styles.resultMeta}>{item.family}</Text>
      </View>

      {item.matched_symptoms.length > 0 && (
        <View style={styles.symptomsContainer}>
          <Text style={styles.symptomsLabel}>Matched Symptoms:</Text>
          <Text style={styles.symptomsText}>
            {item.matched_symptoms.slice(0, 3).join(', ')}
            {item.matched_symptoms.length > 3 && '...'}
          </Text>
        </View>
      )}
    </TouchableOpacity>
  );

  const getScoreColor = (score: number) => {
    if (score >= 0.8) return colors.success;
    if (score >= 0.6) return colors.warning;
    return colors.error;
  };

  return (
    <View style={styles.container}>
      {/* Search Header */}
      <View style={styles.header}>
        <Text style={styles.title}>Symptom Search</Text>
        <View style={styles.searchContainer}>
          <Icon name="magnify" size={20} color={colors.textSecondary} />
          <TextInput
            style={styles.searchInput}
            placeholder="Enter symptoms..."
            value={query}
            onChangeText={setQuery}
            onSubmitEditing={() => handleSearch()}
            returnKeyType="search"
          />
          {query.length > 0 && (
            <TouchableOpacity onPress={() => setQuery('')}>
              <Icon name="close-circle" size={20} color={colors.textSecondary} />
            </TouchableOpacity>
          )}
          <TouchableOpacity
            onPress={isListening ? stopVoiceInput : startVoiceInput}
            style={[styles.voiceButton, isListening && styles.voiceButtonActive]}>
            <Icon
              name={isListening ? 'microphone' : 'microphone-outline'}
              size={20}
              color={isListening ? colors.error : colors.primary}
            />
          </TouchableOpacity>
        </View>
      </View>

      {/* Results */}
      {loading ? (
        <View style={styles.centerContent}>
          <ActivityIndicator size="large" color={colors.primary} />
          <Text style={styles.loadingText}>Searching...</Text>
        </View>
      ) : searchResults.length > 0 ? (
        <FlatList
          data={searchResults}
          renderItem={renderSearchResult}
          keyExtractor={(item, index) => `${item.tree_id}-${index}`}
          contentContainerStyle={styles.resultsContainer}
        />
      ) : query.length > 0 ? (
        <View style={styles.centerContent}>
          <Icon name="alert-circle-outline" size={48} color={colors.textSecondary} />
          <Text style={styles.emptyText}>No results found</Text>
        </View>
      ) : (
        <View style={styles.centerContent}>
          <Icon name="stethoscope" size={48} color={colors.textSecondary} />
          <Text style={styles.emptyText}>
            Enter symptoms to search for differential diagnoses
          </Text>
        </View>
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
  },
  header: {
    backgroundColor: colors.surface,
    padding: spacing.xl,
    paddingTop: spacing.xxl,
  },
  title: {
    ...typography.h2,
    color: colors.text,
    marginBottom: spacing.md,
  },
  searchContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: colors.background,
    borderRadius: 8,
    paddingHorizontal: spacing.md,
    borderWidth: 1,
    borderColor: colors.border,
  },
  searchInput: {
    flex: 1,
    height: 48,
    marginLeft: spacing.sm,
    ...typography.body,
    color: colors.text,
  },
  voiceButton: {
    marginLeft: spacing.sm,
    padding: spacing.sm,
  },
  voiceButtonActive: {
    backgroundColor: colors.errorLight,
    borderRadius: 20,
  },
  resultsContainer: {
    padding: spacing.lg,
  },
  resultCard: {
    backgroundColor: colors.surface,
    borderRadius: 12,
    padding: spacing.lg,
    marginBottom: spacing.md,
    shadowColor: '#000',
    shadowOffset: {width: 0, height: 2},
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  resultHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: spacing.sm,
  },
  resultTitle: {
    ...typography.h4,
    color: colors.text,
    flex: 1,
  },
  scoreBadge: {
    paddingHorizontal: spacing.sm,
    paddingVertical: spacing.xs,
    borderRadius: 12,
    marginLeft: spacing.sm,
  },
  scoreText: {
    ...typography.caption,
    color: colors.white,
    fontWeight: 'bold',
  },
  resultDetails: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: spacing.sm,
  },
  resultMeta: {
    ...typography.caption,
    color: colors.textSecondary,
    marginLeft: spacing.xs,
  },
  symptomsContainer: {
    marginTop: spacing.sm,
    paddingTop: spacing.sm,
    borderTopWidth: 1,
    borderTopColor: colors.border,
  },
  symptomsLabel: {
    ...typography.caption,
    color: colors.textSecondary,
    marginBottom: spacing.xs,
  },
  symptomsText: {
    ...typography.body,
    color: colors.text,
  },
  centerContent: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: spacing.xl,
  },
  loadingText: {
    ...typography.body,
    color: colors.textSecondary,
    marginTop: spacing.md,
  },
  emptyText: {
    ...typography.body,
    color: colors.textSecondary,
    marginTop: spacing.md,
    textAlign: 'center',
  },
});

export default SearchScreen;
