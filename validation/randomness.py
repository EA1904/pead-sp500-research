import numpy as np
import scipy.stats as stats

def run_runs_test(returns):
    """
    Performs a Runs Test for randomness on the returns series.
    Returns:
        z_statistic: float
        p_value: float
    """
    # Convert returns to binary states: 1 for positive, 0 for negative/zero
    binary_seq = (returns > 0).astype(int)
    
    n = len(binary_seq)
    if n < 2:
        return 0.0, 1.0
        
    n1 = np.sum(binary_seq == 1)
    n2 = np.sum(binary_seq == 0)
    
    if n1 == 0 or n2 == 0:
        return 0.0, 1.0
        
    # Count runs
    runs = 1 + np.sum(binary_seq[1:] != binary_seq[:-1])
    
    # Expected number of runs
    expected_runs = ((2.0 * n1 * n2) / n) + 1.0
    
    # Variance of runs
    var_runs = (2.0 * n1 * n2 * (2.0 * n1 * n2 - n)) / (n**2 * (n - 1))
    
    if var_runs <= 0:
        return 0.0, 1.0
        
    std_runs = np.sqrt(var_runs)
    
    # Z statistic
    z_stat = (runs - expected_runs) / std_runs
    
    # Two-tailed p-value
    p_val = 2 * (1 - stats.norm.cdf(abs(z_stat)))
    
    return float(z_stat), float(p_val)

def run_t_test(returns):
    """
    Performs a 1-sample t-test to see if returns are significantly different from zero.
    Returns:
        t_statistic: float
        p_value: float
    """
    if len(returns) < 2:
        return 0.0, 1.0
        
    t_stat, p_val = stats.ttest_1samp(returns, 0.0)
    return float(t_stat), float(p_val)

def analyze_randomness(returns):
    """
    Aggregates statistical tests for randomness.
    Returns a dictionary of statistics and conclusions.
    """
    returns_arr = np.array(returns)
    returns_arr = returns_arr[~np.isnan(returns_arr)]
    
    if len(returns_arr) == 0:
        return {"runs_p_value": 1.0, "t_test_p_value": 1.0, "is_random": True}
        
    z_runs, p_runs = run_runs_test(returns_arr)
    t_stat, p_t = run_t_test(returns_arr)
    
    # If runs p-value < 0.05, we reject the null hypothesis of randomness (non-random, which is good for trading!)
    # If t-test p-value < 0.05, the returns are significantly different from 0 (good for trading!)
    
    return {
        "runs_test_z": z_runs,
        "runs_test_p_value": p_runs,
        "t_test_stat": t_stat,
        "t_test_p_value": p_t,
        "is_random_seq": p_runs >= 0.05,
        "is_mean_zero": p_t >= 0.05
    }
