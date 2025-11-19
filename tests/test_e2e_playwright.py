"""
End-to-End Tests with Playwright
Tests critical user workflows across the application
"""

import pytest
from playwright.sync_api import Page, expect
import time


@pytest.fixture(scope="session")
def browser_context(playwright):
    """Create a browser context for all tests"""
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context()
    yield context
    context.close()
    browser.close()


@pytest.fixture
def page(browser_context):
    """Create a new page for each test"""
    page = browser_context.new_page()
    yield page
    page.close()


class TestSymptomSearchWorkflow:
    """Test symptom search user workflow"""
    
    @pytest.mark.skip(reason="Requires live frontend deployment")
    def test_symptom_search_flow(self, page: Page):
        """Test complete symptom search workflow"""
        # Navigate to symptom search
        page.goto("http://localhost:3000/symptom-search")
        
        # Wait for page to load
        expect(page.locator("h1")).to_contain_text("Symptom Search")
        
        # Enter symptoms
        symptom_input = page.locator('input[placeholder*="symptom" i]')
        symptom_input.fill("chest pain")
        symptom_input.press("Enter")
        
        # Add more symptoms
        symptom_input.fill("shortness of breath")
        symptom_input.press("Enter")
        
        # Submit search
        search_button = page.locator('button:has-text("Search")')
        search_button.click()
        
        # Wait for results
        time.sleep(2)
        results = page.locator('[data-testid="search-results"]')
        expect(results).to_be_visible()
        
        # Verify results contain diagnostic suggestions
        expect(page.locator('text=/CARD-|diagnosis/i')).to_be_visible()


class TestDiagnosticWorkflow:
    """Test diagnostic decision tree workflow"""
    
    @pytest.mark.skip(reason="Requires live frontend deployment")
    def test_diagnostic_flow(self, page: Page):
        """Test complete diagnostic workflow"""
        # Navigate to diagnostic page
        page.goto("http://localhost:3000/diagnostic")
        
        # Select a condition family
        cardiology_button = page.locator('button:has-text("Cardiology")')
        cardiology_button.click()
        
        # Wait for decision tree to load
        time.sleep(1)
        
        # Answer first question
        yes_button = page.locator('button:has-text("Yes")').first
        yes_button.click()
        
        # Continue through decision tree
        time.sleep(1)
        next_yes = page.locator('button:has-text("Yes")').first
        if next_yes.is_visible():
            next_yes.click()
        
        # Wait for diagnosis
        time.sleep(2)
        diagnosis = page.locator('[data-testid="final-diagnosis"]')
        expect(diagnosis).to_be_visible()


class TestEducationWorkflow:
    """Test education feature workflows"""
    
    @pytest.mark.skip(reason="Requires live frontend deployment")
    def test_case_library_flow(self, page: Page):
        """Test browsing clinical cases"""
        # Navigate to education page
        page.goto("http://localhost:3000/education")
        
        # Select cases tab
        cases_tab = page.locator('button:has-text("Clinical Cases")')
        cases_tab.click()
        
        # Wait for cases to load
        time.sleep(1)
        
        # Filter by specialty
        specialty_select = page.locator('select[name="specialty"]')
        specialty_select.select_option("cardiology")
        
        # Verify cases are displayed
        case_card = page.locator('[data-testid="case-card"]').first
        expect(case_card).to_be_visible()
        
        # Open a case
        case_card.click()
        
        # Verify case details
        time.sleep(1)
        expect(page.locator('text=/presentation|diagnosis/i')).to_be_visible()
    
    @pytest.mark.skip(reason="Requires live frontend deployment")
    def test_quiz_flow(self, page: Page):
        """Test quiz workflow"""
        # Navigate to education page
        page.goto("http://localhost:3000/education")
        
        # Select quiz tab
        quiz_tab = page.locator('button:has-text("Quiz")')
        quiz_tab.click()
        
        # Start quiz
        start_button = page.locator('button:has-text("Start Quiz")')
        start_button.click()
        
        # Wait for question
        time.sleep(1)
        
        # Select an answer
        answer_option = page.locator('input[type="radio"]').first
        answer_option.click()
        
        # Submit answer
        submit_button = page.locator('button:has-text("Submit")')
        submit_button.click()
        
        # Verify feedback
        time.sleep(1)
        expect(page.locator('text=/correct|incorrect/i')).to_be_visible()


class TestAccountWorkflow:
    """Test user account workflows"""
    
    @pytest.mark.skip(reason="Requires live frontend deployment and auth")
    def test_login_flow(self, page: Page):
        """Test user login workflow"""
        # Navigate to account page
        page.goto("http://localhost:3000/account")
        
        # Fill login form
        email_input = page.locator('input[type="email"]')
        email_input.fill("test@example.com")
        
        password_input = page.locator('input[type="password"]')
        password_input.fill("testpassword123")
        
        # Submit login
        login_button = page.locator('button:has-text("Login")')
        login_button.click()
        
        # Wait for redirect/success
        time.sleep(2)
        expect(page.locator('text=/welcome|dashboard/i')).to_be_visible()


class TestIntegrationWorkflow:
    """Test EHR integration workflows"""
    
    @pytest.mark.skip(reason="Requires live frontend deployment")
    def test_ehr_connection_flow(self, page: Page):
        """Test EHR connection workflow"""
        # Navigate to integration page
        page.goto("http://localhost:3000/integration")
        
        # Select FHIR connection
        fhir_tab = page.locator('button:has-text("FHIR")')
        fhir_tab.click()
        
        # Enter FHIR endpoint
        endpoint_input = page.locator('input[placeholder*="endpoint" i]')
        endpoint_input.fill("https://fhir.example.com/api")
        
        # Test connection
        test_button = page.locator('button:has-text("Test Connection")')
        test_button.click()
        
        # Verify connection status
        time.sleep(2)
        expect(page.locator('text=/connected|success/i')).to_be_visible()


# Accessibility Tests
class TestAccessibility:
    """Test accessibility compliance"""
    
    @pytest.mark.skip(reason="Requires axe-core integration")
    def test_symptom_search_a11y(self, page: Page):
        """Test symptom search page accessibility"""
        page.goto("http://localhost:3000/symptom-search")
        # Would use axe-playwright here
        # violations = page.accessibility.check()
        # assert len(violations) == 0


# Performance Tests
class TestPerformance:
    """Test page load performance"""
    
    @pytest.mark.skip(reason="Requires live frontend deployment")
    def test_page_load_times(self, page: Page):
        """Test that pages load within acceptable time"""
        pages_to_test = [
            "/",
            "/symptom-search",
            "/diagnostic",
            "/education",
            "/rules"
        ]
        
        for path in pages_to_test:
            start_time = time.time()
            page.goto(f"http://localhost:3000{path}")
            page.wait_for_load_state("networkidle")
            load_time = time.time() - start_time
            
            # Page should load in under 3 seconds
            assert load_time < 3.0, f"{path} took {load_time:.2f}s to load"
