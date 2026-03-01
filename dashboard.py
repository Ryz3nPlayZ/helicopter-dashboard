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
            
            # Get close prices for chart
            closes = hist['Close'].tolist() if not hist.empty else []
            
            data[ticker] = {
                'name': info.get('shortName', ticker),
                'price': current,
                'change': change,
                'prev': prev,
                'volume': info.get('volume'),
                'high': info.get('dayHigh'),
                'low': info.get('dayLow'),
                'closes': closes
            }
        except Exception as e:
            data[ticker] = {'error': str(e)}
    return data

def create_line_chart(closes, width=50, height=10):
    """Create a readable line chart"""
    if not closes or len(closes) < 2:
        return "No data"
    
    # Sample data
    step = max(1, len(closes) // width)
    sampled = closes[::step][:width]
    
    min_p = min(sampled)
    max_p = max(sampled)
    price_range = max_p - min_p if max_p != min_p else 1
    
    # Build chart
    lines = []
    for row in range(height - 1, -1, -1):
        line = ""
        for p in sampled:
            pct = (p - min_p) / price_range
            if pct >= (row + 1) / height:
                line += "█"
            elif pct >= row / height:
                line += "▄"
            else:
                line += " "
        lines.append(line)
    
    # Add price labels
    result = ""
    prices = [max_p - (max_p - min_p) * i / (height - 1) for i in range(height)]
    for i, line in enumerate(lines):
        result += f"{prices[i]:8.0f} │{line}\n"
    
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
            
            # Watchlist
            watchlist = Table(title="📋 Watchlist", box=None)
            watchlist.add_column("Sym", style="cyan", width=8)
            watchlist.add_column("Price", justify="right", style="green", width=12)
            watchlist.add_column("Chg", justify="right", width=8)
            
            for ticker, info in data.items():
                if 'error' in info:
                    continue
                
                change = info.get('change', 0)
                change_str = f"{change:+.2f}%"
                change_style = "green" if change >= 0 else "red"
                
                watchlist.add_row(
                    ticker,
                    f"${info.get('price', 0):,.2f}",
                    Text(change_str, style=change_style)
                )
            
            # Portfolio
            portfolio = Table(title="💼 Portfolio", box=None)
            portfolio.add_column("Asset", style="cyan")
            portfolio.add_column("Value", style="green")
            portfolio.add_column("Pct", style="magenta")
            
            holdings = [
                ("BTC", "$120,917", "45%"),
                ("ETH", "$29,376", "11%"),
                ("SOL", "$21,349", "8%"),
                ("NVDA", "$22,311", "8%"),
                ("USDC", "$58,000", "21%"),
            ]
            for asset, val, pct in holdings:
                portfolio.add_row(asset, val, pct)
            
            # Charts
            charts = Table(box=None)
            charts.add_column("Sym", style="cyan", width=8)
            charts.add_column("Chart", width=55)
            
            for ticker in tickers[:3]:
                info = data.get(ticker, {})
                closes = info.get('closes', [])
                chart = create_line_chart(closes)
                charts.add_row(ticker, f"[yellow]{chart}[/yellow]")
            
            # Display
            console.print("\n")
            console.print(watchlist)
            console.print("\n")
            console.print(Panel(portfolio, border_style="green", width=30))
            console.print("\n")
            console.print(charts)
            
            console.print(f"\n[dim]Updated: {time.strftime('%H:%M:%S')} | Ctrl+C to exit[/dim]")
            time.sleep(10)
            console.clear()
            
        except KeyboardInterrupt:
            console.print("\n[yellow]Exiting...[/yellow]")
            break
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
            time.sleep(5)

if __name__ == "__main__":
    main()
