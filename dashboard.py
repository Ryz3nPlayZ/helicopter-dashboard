#!/usr/bin/env python3
"""
Helicopter Dashboard - Stock market terminal dashboard
Uses yfinance for data and Rich for terminal graphics
"""

import yfinance as yf
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
import time

console = Console()

def get_stock_data(tickers):
    """Fetch stock data from yfinance"""
    data = {}
    for ticker in tickers:
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            hist = stock.history(period="1d", interval="5m")
            
            current = info.get('currentPrice') or info.get('regularMarketPreviousClose')
            prev = info.get('regularMarketPreviousClose')
            change = ((current - prev) / prev * 100) if current and prev else 0
            
            data[ticker] = {
                'name': info.get('shortName', ticker),
                'price': current,
                'change': change,
                'prev': prev,
                'volume': info.get('volume'),
                'high': info.get('dayHigh'),
                'low': info.get('dayLow'),
                'history': hist['Close'].tolist() if not hist.empty else []
            }
        except Exception as e:
            data[ticker] = {'error': str(e)}
    return data

def create_chart(history, width=50, height=12):
    """Create ASCII chart from price history"""
    if not history or len(history) < 2:
        return "No data"
    
    # Sample to fit width
    step = max(1, len(history) // width)
    sampled = history[::step][:width]
    
    if not sampled:
        return "No data"
    
    # Normalize to 0-100
    min_p = min(sampled)
    max_p = max(sampled)
    range_p = max_p - min_p if max_p != min_p else 1
    
    normalized = [(p - min_p) / range_p * (height - 1) for p in sampled]
    
    # Build chart
    lines = []
    for row in range(height - 1, -1, -1):
        line = ""
        for val in normalized:
            if int(val) == row:
                line += "█"
            elif int(val) > row:
                line += "░"
            else:
                line += " "
        lines.append(line)
    
    # Add price axis
    prices = [min_p + (max_p - min_p) * (1 - row/(height-1)) for row in range(height)]
    result = ""
    for i, line in enumerate(lines):
        result += f"{prices[i]:10.2f} │{line}\n"
    
    result += " " * 10 + " └" + "─" * len(lines[0]) + "\n"
    result += " " * 10 + "  " + "L" + " " * (len(lines[0])//2 - 1) + "R"
    
    return result

def main():
    tickers = ["BTC-USD", "ETH-USD", "SOL-USD", "NVDA", "AAPL"]
    
    console.clear()
    console.print(Panel.fit(
        "[bold cyan]🚁 HELICOPTER DASHBOARD[/bold cyan] | [green]LIVE[/green]",
        style="on blue"
    ))
    
    while True:
        try:
            data = get_stock_data(tickers)
            
            # Watchlist Table
            watchlist = Table(title="📋 Watchlist", box=None)
            watchlist.add_column("Symbol", style="cyan", width=10)
            watchlist.add_column("Price", justify="right", style="green", width=12)
            watchlist.add_column("Change", justify="right", width=10)
            watchlist.add_column("Volume", justify="right", style="dim", width=12)
            
            for ticker, info in data.items():
                if 'error' in info:
                    continue
                
                change = info.get('change', 0)
                change_str = f"{change:+.2f}%"
                change_style = "green" if change >= 0 else "red"
                
                vol = info.get('volume', 0)
                if vol > 1e9:
                    vol_str = f"{vol/1e9:.2f}B"
                elif vol > 1e6:
                    vol_str = f"{vol/1e6:.2f}M"
                else:
                    vol_str = str(vol)
                
                watchlist.add_row(
                    ticker,
                    f"${info.get('price', 0):.2f}",
                    Text(change_str, style=change_style),
                    vol_str
                )
            
            # Portfolio
            portfolio = Table(title="💼 Portfolio", box=None)
            portfolio.add_column("Asset", style="cyan")
            portfolio.add_column("Qty", style="yellow")
            portfolio.add_column("Value", style="green")
            portfolio.add_column("Pct", style="magenta")
            
            holdings = [
                ("BTC", "1.25", "$120,917", "45%"),
                ("ETH", "8.5", "$29,376", "11%"),
                ("SOL", "150", "$21,349", "8%"),
                ("NVDA", "25", "$22,311", "8%"),
                ("USDC", "$58,000", "$58,000", "21%"),
            ]
            for asset, qty, val, pct in holdings:
                portfolio.add_row(asset, qty, val, pct)
            
            # Chart
            first_data = data.get(tickers[0], {})
            history = first_data.get('history', [])
            chart = create_chart(history)
            
            # Display
            console.print("\n")
            console.print(watchlist)
            console.print("\n")
            
            # Split view
            console.print(Panel(portfolio, title="💼 Portfolio", border_style="green", width=50))
            console.print(Panel(chart, title=f"📊 {tickers[0]} Chart", border_style="yellow", width=60))
            
            console.print(f"\n[dim]Updated: {time.strftime('%H:%M:%S')} | Refresh in 5s...[/dim]")
            time.sleep(5)
            console.clear()
            
        except KeyboardInterrupt:
            console.print("\n[yellow]Exiting...[/yellow]")
            break
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
            time.sleep(5)

if __name__ == "__main__":
    main()
