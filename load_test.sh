#!/bin/bash

# Load Test Script for RealDiag Backend
# Tests critical endpoints with concurrent requests

API_BASE="https://realdiag-software.onrender.com"
RESULTS_FILE="load_test_results.txt"

echo "=== RealDiag Load Test ===" > $RESULTS_FILE
echo "Started: $(date)" >> $RESULTS_FILE
echo "" >> $RESULTS_FILE

# Test 1: Symptom Search Endpoint
echo "Test 1: Symptom Search (/search/by-symptoms)" | tee -a $RESULTS_FILE
echo "Testing with 20 concurrent requests..." | tee -a $RESULTS_FILE

start_time=$(date +%s)
for i in {1..20}; do
  {
    response=$(curl -s -w "\n%{time_total}" -X POST "$API_BASE/search/by-symptoms" \
      -H "Content-Type: application/json" \
      -d '{"symptoms":["headache","nausea","dizziness"]}' 2>&1)
    echo "$response" | tail -1
  } &
done
wait

end_time=$(date +%s)
duration=$((end_time - start_time))
echo "Duration: ${duration}s" | tee -a $RESULTS_FILE
echo "" | tee -a $RESULTS_FILE

# Test 2: Health Check
echo "Test 2: Health Endpoint (/health)" | tee -a $RESULTS_FILE
echo "Testing with 50 concurrent requests..." | tee -a $RESULTS_FILE

start_time=$(date +%s)
for i in {1..50}; do
  {
    curl -s -w "%{time_total}\n" -o /dev/null "$API_BASE/health"
  } &
done
wait

end_time=$(date +%s)
duration=$((end_time - start_time))
echo "Duration: ${duration}s" | tee -a $RESULTS_FILE
echo "" | tee -a $RESULTS_FILE

# Test 3: Education Cases
echo "Test 3: Education Cases (/education/cases)" | tee -a $RESULTS_FILE
echo "Testing with 15 concurrent requests..." | tee -a $RESULTS_FILE

start_time=$(date +%s)
for i in {1..15}; do
  {
    curl -s -w "%{time_total}\n" -o /dev/null "$API_BASE/education/cases"
  } &
done
wait

end_time=$(date +%s)
duration=$((end_time - start_time))
echo "Duration: ${duration}s" | tee -a $RESULTS_FILE
echo "" | tee -a $RESULTS_FILE

# Test 4: Quiz Questions
echo "Test 4: Quiz Questions (/education/quiz/questions)" | tee -a $RESULTS_FILE
echo "Testing with 15 concurrent requests..." | tee -a $RESULTS_FILE

start_time=$(date +%s)
for i in {1..15}; do
  {
    curl -s -w "%{time_total}\n" -o /dev/null "$API_BASE/education/quiz/questions?count=5"
  } &
done
wait

end_time=$(date +%s)
duration=$((end_time - start_time))
echo "Duration: ${duration}s" | tee -a $RESULTS_FILE
echo "" | tee -a $RESULTS_FILE

# Test 5: Rate Limit Test (Symptom Search)
echo "Test 5: Rate Limiting Test" | tee -a $RESULTS_FILE
echo "Sending 65 requests in rapid succession (should hit 60/min limit)..." | tee -a $RESULTS_FILE

rate_limited=0
successful=0
start_time=$(date +%s)

for i in {1..65}; do
  response_code=$(curl -s -w "%{http_code}" -o /dev/null -X POST "$API_BASE/search/by-symptoms" \
    -H "Content-Type: application/json" \
    -d '{"symptoms":["test"]}')
  
  if [ "$response_code" = "429" ]; then
    rate_limited=$((rate_limited + 1))
  elif [ "$response_code" = "200" ]; then
    successful=$((successful + 1))
  fi
done

end_time=$(date +%s)
duration=$((end_time - start_time))
echo "Successful: $successful, Rate Limited: $rate_limited, Duration: ${duration}s" | tee -a $RESULTS_FILE
echo "" | tee -a $RESULTS_FILE

echo "Completed: $(date)" | tee -a $RESULTS_FILE
echo "=== Results saved to $RESULTS_FILE ===" | tee -a $RESULTS_FILE
