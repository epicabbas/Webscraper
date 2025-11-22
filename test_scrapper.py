"""
Test Suite for Web Scraper
Demonstrates testing best practices

"""
import unittest
from unittest.mock import Mock, patch
from scraper import WebScraper
from bs4 import BeautifulSoup
import pandas as pd

class TestWebScraper(unittest.TestCase):
    """ Test cases for WebScraper class."""
    def setUp(self):
        """Set up test fixtures - runs before each test."""
        self.scraper = WebScraper("http://example.com",delay=0.1)

    def test_initialization(self):
        """Test that scraper initializes correctly."""
        self.assertEqual(self.scraper.base_url, "http://example.com")
        self.assertEqual(self.scraper.delay, 0.1)
        self.assertIsNotNone(self.scraper.session)
        print("✓ Test 1 passed: Initialization works")

    def test_user_agent_set(self):
        """Test that user agent is set properly."""
        user_agent = self.scraper.session.headers.get('User-Agent')
        self.assertIsNotNone(user_agent)
        self.assertIn('Mozilla', user_agent)
        print("✓ Test 2 passed: User agent is set")

    @patch('scraper.requests.Session.get')
    def test_fetch_page_success(self, mock_get):
        """Test successful page fetch with mock."""
        # Create a fake response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b'<html><body><h1>Test Page</h1></body></html>'
        mock_get.return_value = mock_response
        
        # Test fetch_page
        soup = self.scraper.fetch_page("http://example.com")
        
        # Verify it worked
        self.assertIsNotNone(soup)
        self.assertIsInstance(soup, BeautifulSoup)
        self.assertEqual(soup.find('h1').text, 'Test Page')
        print("✓ Test 3 passed: Fetch page works with mock")
    
    def test_fetch_page_failure(self):
        """Test that fetch_page handles errors gracefully."""
        # Test with an invalid URL (will fail naturally)
        soup = self.scraper.fetch_page("http://this-definitely-does-not-exist-12345.com")
        
        # Should return None on error
        self.assertIsNone(soup)
        print("✓ Test 4 passed: Handles errors gracefully")
    
    def test_save_to_csv_with_data(self):
        """Test saving data to CSV."""
        test_data = [
            {'name': 'Item 1', 'price': 10.99},
            {'name': 'Item 2', 'price': 20.99}
        ]
        
        filename = 'test_output.csv'
        self.scraper.save_to_csv(test_data, filename)
        
        # Verify file was created
        import os
        self.assertTrue(os.path.exists(filename))
        
        # Verify content
        df = pd.read_csv(filename)
        self.assertEqual(len(df), 2)
        self.assertEqual(df['name'].iloc[0], 'Item 1')
        
        # Cleanup
        os.remove(filename)
        print("✓ Test 5 passed: CSV export works")
    
    def test_save_to_csv_empty_data(self):
        """Test that empty data is handled gracefully."""
        self.scraper.save_to_csv([], 'test_empty.csv')
        
        # File should not be created for empty data
        import os
        self.assertFalse(os.path.exists('test_empty.csv'))
        print("✓ Test 6 passed: Handles empty data")

        #@patch() - replaces real HTTP requests with fake ones
        #Mock() - Creates fake objects to simulate testing
        #mock.get.side_effect - simulates errors

def run_tests():
    """Run all tests with nice output."""
    print("\n" + "=" * 70)
    print("RUNNING WEB SCRAPER TESTS")
    print("=" * 70 + "\n")
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestWebScraper)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"Tests run: {result.testsRun}")
    print(f"✅ Passed: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"❌ Failed: {len(result.failures)}")
    print(f"⚠️  Errors: {len(result.errors)}")
    print("=" * 70 + "\n")
    
    return result.wasSuccessful()


if __name__ == '__main__':
    run_tests()
