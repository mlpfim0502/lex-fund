"""
Test script for backtest engine date handling
Tests various date scenarios to ensure robustness
"""
import sys
sys.path.insert(0, '/Users/chenyulee/Backtest')

from backtest_engine import run_backtest
import traceback

def test_scenario(name, start, end, ma_period=200, leverage=3.0, expect_error=False):
    """Test a specific date scenario."""
    print(f"\n{'='*60}")
    print(f"TEST: {name}")
    print(f"  Start: {start}, End: {end}, MA Period: {ma_period}")
    print('='*60)
    
    try:
        result = run_backtest(start=start, end=end, ma_period=ma_period, leverage=leverage)
        
        # Check MA data
        ma_valid = result.stock_ma.notna().sum()
        ma_total = len(result.stock_ma)
        ma_pct = (ma_valid / ma_total * 100) if ma_total > 0 else 0
        
        print(f"\n✅ SUCCESS")
        print(f"  Period: {result.metrics['start_date']} → {result.metrics['end_date']}")
        print(f"  Data points: {len(result.nav)}")
        print(f"  MA coverage: {ma_valid}/{ma_total} ({ma_pct:.1f}%)")
        print(f"  Final NAV: {result.metrics['final_nav']:.2f}")
        print(f"  CAGR: {result.metrics['cagr']*100:.2f}%")
        
        if expect_error:
            print(f"  ⚠️  Expected error but got success")
            return False
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        if expect_error:
            print(f"  ✓ Error was expected")
            return True
        traceback.print_exc()
        return False

def run_all_tests():
    """Run all test scenarios."""
    print("\n" + "="*60)
    print(" BACKTEST ENGINE DATE HANDLING TESTS")
    print("="*60)
    
    results = []
    
    # Test 1: Normal long-term range
    results.append(("Normal range (1990-2024)", 
        test_scenario("Normal Long-Term Range", "1990-01-01", "2024-12-01")))
    
    # Test 2: Short recent range (should have MA from start due to extended fetch)
    results.append(("Short recent range (2024)", 
        test_scenario("Short Recent Range (1 year)", "2024-01-01", "2024-12-01")))
    
    # Test 3: Even shorter range
    results.append(("Very short range (6 months)", 
        test_scenario("Very Short Range (6 months)", "2024-06-01", "2024-12-01")))
    
    # Test 4: Old date range (should work fine)
    results.append(("Old range (1950-1980)", 
        test_scenario("Old Historical Range", "1950-01-01", "1980-12-31")))
    
    # Test 5: Very old date (before 1928 - should auto-adjust)
    results.append(("Extreme old date (1900)", 
        test_scenario("Extreme Old Date (auto-adjust to 1928)", "1900-01-01", "1970-12-31")))
    
    # Test 6: Date range starting near the beginning (1928-1930)
    results.append(("Early data range (1928-1930)", 
        test_scenario("Early Data Range (limited MA history)", "1928-01-01", "1930-12-31")))
    
    # Test 7: End date close to today (may fail)
    results.append(("End date close to today", 
        test_scenario("End Date Close to Today", "2024-01-01", "2025-12-09")))
    
    # Test 8: Invalid date range (start > end)
    results.append(("Invalid range (start > end)", 
        test_scenario("Invalid Date Range", "2024-12-01", "2020-01-01", expect_error=True)))
    
    # Test 9: Small MA period with short range
    results.append(("Short range with small MA", 
        test_scenario("Short Range + Small MA Period", "2024-06-01", "2024-12-01", ma_period=50)))
    
    # Summary
    print("\n" + "="*60)
    print(" TEST SUMMARY")
    print("="*60)
    
    passed = 0
    failed = 0
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status}: {name}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print(f"\nTotal: {passed} passed, {failed} failed out of {len(results)} tests")
    return failed == 0

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
