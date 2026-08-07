import numpy as np
import pandas as pd

def calculate_metrics(equity_curve, trades_df):
    """
    Computes standard performance metrics for a backtest result.
    
    equity_curve: pd.Series of daily portfolio value
    trades_df: pd.DataFrame containing trade records with at least ['pnl_pct', 'direction', 'duration_days']
    
    Output:
        dict containing Sharpe, Sortino, Max Drawdown, Calmar, Win Rate, Profit Factor,
        Avg Trade Duration, Expectancy, and Total Trades.
    """
    metrics = {
        "total_trades": 0,
        "win_rate": 0.0,
        "sharpe_ratio": 0.0,
        "sortino_ratio": 0.0,
        "max_drawdown": 0.0,
        "calmar_ratio": 0.0,
        "profit_factor": 0.0,
        "avg_trade_duration": 0.0,
        "expectancy": 0.0,
        "total_return": 0.0,
        "annualized_return": 0.0
    }
    
    if len(equity_curve) < 2:
        return metrics
        
    # Calculate daily returns
    daily_returns = equity_curve.pct_change().dropna()
    
    # Total return
    total_return = (equity_curve.iloc[-1] / equity_curve.iloc[0]) - 1.0
    metrics["total_return"] = float(total_return)
    
    # Annualized return (assuming 252 trading days per year)
    years = len(equity_curve) / 252.0
    if years > 0:
        annualized_return = (equity_curve.iloc[-1] / equity_curve.iloc[0]) ** (1.0 / years) - 1.0
    else:
        annualized_return = total_return
    metrics["annualized_return"] = float(annualized_return)
    
    # Sharpe Ratio
    std_returns = daily_returns.std()
    if std_returns > 1e-8:
        # Sharpe = mean / std * sqrt(252)
        sharpe = (daily_returns.mean() / std_returns) * np.sqrt(252)
        metrics["sharpe_ratio"] = float(sharpe)
        
    # Sortino Ratio
    downside_returns = daily_returns[daily_returns < 0]
    if len(downside_returns) > 1:
        downside_std = downside_returns.std()
        if downside_std > 1e-8:
            sortino = (daily_returns.mean() / downside_std) * np.sqrt(252)
            metrics["sortino_ratio"] = float(sortino)
            
    # Max Drawdown
    peaks = equity_curve.cummax()
    drawdowns = (equity_curve - peaks) / peaks
    max_dd = drawdowns.min()
    metrics["max_drawdown"] = float(max_dd)
    
    # Calmar Ratio
    if abs(max_dd) > 1e-8:
        metrics["calmar_ratio"] = float(annualized_return / abs(max_dd))
    else:
        metrics["calmar_ratio"] = 0.0
        
    # Trade-based metrics
    if trades_df is not None and not trades_df.empty:
        total_trades = len(trades_df)
        metrics["total_trades"] = total_trades
        
        winning_trades = trades_df[trades_df["pnl_pct"] > 0]
        losing_trades = trades_df[trades_df["pnl_pct"] <= 0]
        
        # Win Rate
        win_rate = len(winning_trades) / total_trades
        metrics["win_rate"] = float(win_rate)
        
        # Profit Factor
        sum_gains = winning_trades["pnl_pct"].sum()
        sum_losses = abs(losing_trades["pnl_pct"].sum())
        if sum_losses > 1e-8:
            metrics["profit_factor"] = float(sum_gains / sum_losses)
        else:
            metrics["profit_factor"] = float(sum_gains) if sum_gains > 0 else 0.0
            
        # Expectancy
        avg_win = winning_trades["pnl_pct"].mean() if len(winning_trades) > 0 else 0.0
        avg_loss = losing_trades["pnl_pct"].mean() if len(losing_trades) > 0 else 0.0
        expectancy = (win_rate * avg_win) + ((1.0 - win_rate) * avg_loss)
        metrics["expectancy"] = float(expectancy)
        
        # Avg Trade Duration
        if "duration_days" in trades_df.columns:
            metrics["avg_trade_duration"] = float(trades_df["duration_days"].mean())
            
    return metrics

def extract_trades(signals, prices, dates):
    """
    Parses position signals and price series into a list of completed trades.
    
    signals: pd.Series of positions (+1, -1, 0)
    prices: pd.Series of matching close prices
    dates: pd.Series of matching dates
    
    Output:
        pd.DataFrame containing trade logs:
        ['entry_date', 'exit_date', 'direction', 'entry_price', 'exit_price', 'pnl_pct', 'duration_days']
    """
    trades = []
    active_trade = None
    
    # Align indexes by converting to raw values/numpy arrays
    dates_val = dates.values if hasattr(dates, "values") else dates
    prices_val = prices.values if hasattr(prices, "values") else prices
    signals_val = signals.values if hasattr(signals, "values") else signals

    df = pd.DataFrame({
        "date": pd.to_datetime(dates_val),
        "price": pd.Series(prices_val).astype(float),
        "signal": pd.Series(signals_val).astype(int)
    }).reset_index(drop=True)
    
    for i in range(len(df)):
        current_sig = df.loc[i, "signal"]
        current_price = df.loc[i, "price"]
        current_date = df.loc[i, "date"]
        
        prev_sig = df.loc[i-1, "signal"] if i > 0 else 0
        
        # Position change detected
        if current_sig != prev_sig:
            # 1. Close active trade if we had one
            if active_trade is not None:
                active_trade["exit_date"] = current_date
                active_trade["exit_price"] = current_price
                
                # Compute return
                entry_p = active_trade["entry_price"]
                exit_p = active_trade["exit_price"]
                direction = active_trade["direction"]
                
                if direction == 1:
                    pnl_pct = (exit_p - entry_p) / entry_p
                else:
                    pnl_pct = (entry_p - exit_p) / entry_p
                    
                active_trade["pnl_pct"] = pnl_pct
                active_trade["duration_days"] = (current_date - active_trade["entry_date"]).days
                trades.append(active_trade)
                active_trade = None
                
            # 2. Open new trade if current signal is not cash (0)
            if current_sig != 0:
                active_trade = {
                    "entry_date": current_date,
                    "direction": current_sig,
                    "entry_price": current_price,
                    "exit_date": None,
                    "exit_price": None,
                    "pnl_pct": 0.0,
                    "duration_days": 0
                }
                
    # Close any remaining open trade on the last day of data
    if active_trade is not None:
        last_idx = len(df) - 1
        active_trade["exit_date"] = df.loc[last_idx, "date"]
        active_trade["exit_price"] = df.loc[last_idx, "price"]
        entry_p = active_trade["entry_price"]
        exit_p = active_trade["exit_price"]
        direction = active_trade["direction"]
        
        if direction == 1:
            pnl_pct = (exit_p - entry_p) / entry_p
        else:
            pnl_pct = (entry_p - exit_p) / entry_p
            
        active_trade["pnl_pct"] = pnl_pct
        active_trade["duration_days"] = (df.loc[last_idx, "date"] - active_trade["entry_date"]).days
        trades.append(active_trade)
        
    return pd.DataFrame(trades)
