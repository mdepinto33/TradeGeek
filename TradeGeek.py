import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import pandas as pd
import backtrader as bt
import matplotlib
import datetime

matplotlib.use("TkAgg")

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure


# --------------------------------------------------------------
# 1) STRATEGIES
# (unchanged: SmaCross, RsiStrategy, SmaRsiCombo, BollingerBandStrategy, MACDStrategy)
# --------------------------------------------------------------

class SmaCross(bt.Strategy):
    params = (
        ('fast_period', 10),
        ('slow_period', 30),
        ('printlog', True),
    )

    def __init__(self):
        sma_fast = bt.ind.SMA(period=self.params.fast_period)
        sma_slow = bt.ind.SMA(period=self.params.slow_period)
        self.crossover = bt.ind.CrossOver(sma_fast, sma_slow)

    def next(self):
        if not self.position:
            if self.crossover > 0:
                self.buy()
        else:
            if self.crossover < 0:
                self.close()

    def log(self, txt, dt=None):
        if self.params.printlog:
            dt = dt or self.datas[0].datetime.date(0)
            print(f'[{dt.isoformat()}] {txt}')

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(f'BUY EXECUTED at Price: {order.executed.price:.2f}')
            else:
                self.log(f'SELL EXECUTED at Price: {order.executed.price:.2f}')
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

    def notify_trade(self, trade):
        if trade.isclosed:
            self.log(f'Trade PnL: {trade.pnl:.2f}')


class RsiStrategy(bt.Strategy):
    params = (
        ('rsi_period', 14),
        ('rsi_lower', 30),
        ('rsi_upper', 70),
        ('printlog', True),
    )

    def __init__(self):
        self.rsi = bt.ind.RSI(period=self.params.rsi_period)

    def next(self):
        if not self.position:
            if self.rsi < self.params.rsi_lower:
                self.buy()
        else:
            if self.rsi > self.params.rsi_upper:
                self.close()

    def log(self, txt, dt=None):
        if self.params.printlog:
            dt = dt or self.datas[0].datetime.date(0)
            print(f'[{dt.isoformat()}] {txt}')

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(f'BUY EXECUTED at Price: {order.executed.price:.2f}')
            else:
                self.log(f'SELL EXECUTED at Price: {order.executed.price:.2f}')
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

    def notify_trade(self, trade):
        if trade.isclosed:
            self.log(f'Trade PnL: {trade.pnl:.2f}')


class SmaRsiCombo(bt.Strategy):
    params = (
        ('fast_period', 10),
        ('slow_period', 30),
        ('rsi_period', 14),
        ('rsi_upper', 70),
        ('rsi_lower', 30),
        ('printlog', True)
    )

    def __init__(self):
        self.sma_fast = bt.ind.SMA(period=self.params.fast_period)
        self.sma_slow = bt.ind.SMA(period=self.params.slow_period)
        self.rsi = bt.ind.RSI(period=self.params.rsi_period)
        self.crossover = bt.ind.CrossOver(self.sma_fast, self.sma_slow)

    def next(self):
        if not self.position:
            if self.crossover > 0 and self.rsi < self.params.rsi_upper:
                self.buy()
        else:
            if self.crossover < 0 or self.rsi > self.params.rsi_upper:
                self.close()

    def log(self, txt, dt=None):
        if self.params.printlog:
            dt = dt or self.datas[0].datetime.date(0)
            print(f'[{dt.isoformat()}] {txt}')

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(f'BUY EXECUTED at Price: {order.executed.price:.2f}')
            else:
                self.log(f'SELL EXECUTED at Price: {order.executed.price:.2f}')
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

    def notify_trade(self, trade):
        if trade.isclosed:
            self.log(f'Trade PnL: {trade.pnl:.2f}')


class BollingerBandStrategy(bt.Strategy):
    params = (
        ('period', 20),
        ('devfactor', 2.0),
        ('printlog', True),
    )

    def __init__(self):
        self.bb = bt.ind.BollingerBands(period=self.params.period, devfactor=self.params.devfactor)
        self.close_price = self.datas[0].close

    def next(self):
        if not self.position:
            if self.close_price[0] < self.bb.lines.bot[0]:
                self.buy()
        else:
            if self.close_price[0] > self.bb.lines.top[0]:
                self.close()

    def log(self, txt, dt=None):
        if self.params.printlog:
            dt = dt or self.datas[0].datetime.date(0)
            print(f'[{dt.isoformat()}] {txt}')

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(f'BUY EXECUTED at Price: {order.executed.price:.2f}')
            else:
                self.log(f'SELL EXECUTED at Price: {order.executed.price:.2f}')
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

    def notify_trade(self, trade):
        if trade.isclosed:
            self.log(f'Trade PnL: {trade.pnl:.2f}')


class MACDStrategy(bt.Strategy):
    params = (
        ('fast_period', 12),
        ('slow_period', 26),
        ('signal_period', 9),
        ('printlog', True),
    )

    def __init__(self):
        macd = bt.ind.MACD(
            fast=self.params.fast_period,
            slow=self.params.slow_period,
            signal=self.params.signal_period
        )
        self.macd_line = macd.macd
        self.signal_line = macd.signal
        self.crossover = bt.ind.CrossOver(self.macd_line, self.signal_line)

    def next(self):
        if not self.position:
            if self.crossover > 0:
                self.buy()
        else:
            if self.crossover < 0:
                self.close()

    def log(self, txt, dt=None):
        if self.params.printlog:
            dt = dt or self.datas[0].datetime.date(0)
            print(f'[{dt.isoformat()}] {txt}')

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(f'BUY EXECUTED at Price: {order.executed.price:.2f}')
            else:
                self.log(f'SELL EXECUTED at Price: {order.executed.price:.2f}')
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

    def notify_trade(self, trade):
        if trade.isclosed:
            self.log(f'Trade PnL: {trade.pnl:.2f}')

class MyNewStrategy(bt.Strategy):
    params = (
        ('stoch_period', 14),
        ('stoch_d_period', 3),
        ('sma_period', 50),
        ('printlog', True),
    )
    def __init__(self):
        self.stoch = bt.ind.Stochastic(self.data,
                                       period=self.params.stoch_period,
                                       period_dfast=self.params.stoch_d_period,
                                       period_dslow=1)
        self.sma = bt.ind.SMA(self.data.close, period=self.params.sma_period)
        self.k = self.stoch.percK
        self.d = self.stoch.percD
        self.cross = bt.ind.CrossOver(self.k, self.d)

    def next(self):
        if not self.position:
            if self.cross > 0 and self.data.close[0] > self.sma[0]:
                self.buy()
        else:
            if self.cross < 0 or self.data.close[0] < self.sma[0]:
                self.close()

    def log(self, txt, dt=None):
        if self.params.printlog:
            dt = dt or self.datas[0].datetime.date(0)
            print(f'[{dt.isoformat()}] {txt}')

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(f'BUY EXECUTED at Price: {order.executed.price:.2f}')
            else:
                self.log(f'SELL EXECUTED at Price: {order.executed.price:.2f}')
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')
    def notify_trade(self, trade):
        if trade.isclosed:
            self.log(f'Trade PnL: {trade.pnl:.2f}')
# --------------------------------------------------------------
# 2) MAIN APPLICATION (Tkinter + Backtrader)
# --------------------------------------------------------------
class BacktestApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Pro Backtesting & Trading Algorithm Framework")
        self.geometry("1200x800")

        # Dictionary: symbol -> DataFrame
        self.dataframes = {}
        self.strategy_params = {}
        self.cerebro = None

        self.fig = None
        self.canvas = None

        self.create_widgets()

    def create_widgets(self):
        """
        We only add STYLING changes in this method, without altering any functionality.
        """
        # 1) Create and configure a custom Style for a unique design
        style = ttk.Style()
        # Use a built-in theme as a base; "clam", "alt", "default", or "classic"
        style.theme_use("clam")

        # Customize colors/fonts for frames, labels, etc.
        style.configure("TFrame", background="#E9EEF7")
        style.configure("TLabelFrame", background="#DDE6F2", foreground="#333333", font=("Helvetica", 10, "bold"))
        style.configure("TLabel", background="#DDE6F2", foreground="#333333", font=("Helvetica", 10))
        style.configure("TButton", background="#648DE5", foreground="#ffffff", font=("Helvetica", 9, "bold"))
        style.map("TButton",
                  background=[("active", "#426EB4")],
                  foreground=[("active", "#ffffff")])
        style.configure("TCheckbutton", background="#DDE6F2", foreground="#333333")
        style.configure("TRadiobutton", background="#DDE6F2", foreground="#333333")
        style.configure("TCombobox", fieldbackground="#FFFFFF", background="#DDE6F2")

        # 2) The existing code for frames and widgets
        file_frame = ttk.LabelFrame(self, text="Data Input")
        file_frame.pack(fill="x", padx=5, pady=5)

        self.load_button = ttk.Button(file_frame, text="Load CSV", command=self.load_csv)
        self.load_button.pack(side="left", padx=5, pady=5)

        self.timeframe_label = ttk.Label(file_frame, text="Timeframe:")
        self.timeframe_label.pack(side="left", padx=5)

        self.timeframe_var = tk.StringVar(value="Daily")
        self.timeframe_dropdown = ttk.Combobox(file_frame, textvariable=self.timeframe_var,
                                               values=["Daily", "Hourly", "Minutes"])
        self.timeframe_dropdown.pack(side="left", padx=5)

        strat_frame = ttk.LabelFrame(self, text="Strategy Selection")
        strat_frame.pack(fill="x", padx=5, pady=5)

        strat_label = ttk.Label(strat_frame, text="Select Strategy:")
        strat_label.pack(side="left", padx=5)

        self.strategy_var = tk.StringVar(value="SmaCross")
        self.strategy_dropdown = ttk.Combobox(
            strat_frame,
            textvariable=self.strategy_var,
            values=[
                "SmaCross",
                "RsiStrategy",
                "SmaRsiCombo",
                "BollingerBandStrategy",
                "MACDStrategy",
                "MyNewStrategy"
            ]
        )
        self.strategy_dropdown.pack(side="left", padx=5)

        self.param_button = ttk.Button(strat_frame, text="Strategy Params", command=self.open_param_window)
        self.param_button.pack(side="left", padx=5)

        broker_frame = ttk.LabelFrame(self, text="Broker/Sim Settings")
        broker_frame.pack(fill="x", padx=5, pady=5)

        ttk.Label(broker_frame, text="Initial Cash:").pack(side="left", padx=5)
        self.initial_cash_var = tk.StringVar(value="10000")
        ttk.Entry(broker_frame, textvariable=self.initial_cash_var, width=10).pack(side="left", padx=5)

        ttk.Label(broker_frame, text="Commission (%):").pack(side="left", padx=5)
        self.comm_var = tk.StringVar(value="0.1")
        ttk.Entry(broker_frame, textvariable=self.comm_var, width=10).pack(side="left", padx=5)

        ttk.Label(broker_frame, text="Slippage (pct):").pack(side="left", padx=5)
        self.slippage_var = tk.StringVar(value="0.0")
        ttk.Entry(broker_frame, textvariable=self.slippage_var, width=10).pack(side="left", padx=5)

        run_frame = ttk.LabelFrame(self, text="Run & Analyze")
        run_frame.pack(fill="x", padx=5, pady=5)

        self.run_button = ttk.Button(run_frame, text="Run Backtest", command=self.run_backtest)
        self.run_button.pack(side="left", padx=5, pady=5)

        self.clear_data_button = ttk.Button(run_frame, text="Clear Data", command=self.clear_data)
        self.clear_data_button.pack(side="left", padx=5, pady=5)

        self.plot_choice_var = tk.StringVar(value="Separate Window")
        ttk.Radiobutton(run_frame, text="Separate Window", variable=self.plot_choice_var, value="Separate Window") \
            .pack(side="left", padx=5)
        ttk.Radiobutton(run_frame, text="Embedded Plot", variable=self.plot_choice_var, value="Embedded Plot") \
            .pack(side="left", padx=5)

        output_frame = ttk.LabelFrame(self, text="Output/Logs")
        output_frame.pack(fill="both", expand=True, padx=5, pady=5)

        self.text_area = tk.Text(output_frame, wrap="word", height=10)
        # Give the text area a subtle background color
        self.text_area.config(bg="#F7FBFF", fg="#333333", font=("Courier New", 10))
        self.text_area.pack(fill="both", expand=True)

        plot_frame = ttk.LabelFrame(self, text="Chart")
        plot_frame.pack(fill="both", expand=True, padx=5, pady=5)

        self.fig = Figure(figsize=(6, 4), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.fig, master=plot_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

    def load_csv(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")])
        if not file_path:
            return

        try:
            df = pd.read_csv(file_path)
            if 'Date' in df.columns:
                df['Date'] = pd.to_datetime(df['Date'])
                df.set_index('Date', inplace=True)
            elif 'Datetime' in df.columns:
                df['Datetime'] = pd.to_datetime(df['Datetime'])
                df.set_index('Datetime', inplace=True)
            else:
                messagebox.showwarning("Warning", "No 'Date' or 'Datetime' column found.")
                return

            symbol = file_path.split('/')[-1].split('.')[0]
            self.dataframes[symbol] = df
            self.append_text(f"Loaded {symbol} with {len(df)} rows. Columns: {list(df.columns)}\n")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load CSV: {e}")

    def run_backtest(self):
        if not self.dataframes:
            messagebox.showwarning("Warning", "No data loaded.")
            return

        try:
            initial_cash = float(self.initial_cash_var.get())
            commission = float(self.comm_var.get()) / 100.0
            slippage_pct = float(self.slippage_var.get())
        except ValueError:
            messagebox.showerror("Error", "Invalid numeric inputs in broker settings.")
            return

        self.text_area.delete('1.0', tk.END)
        self.cerebro = bt.Cerebro()
        self.cerebro.broker.setcash(initial_cash)
        self.cerebro.broker.setcommission(commission=commission)

        if slippage_pct > 0:
            self.cerebro.broker.set_slippage_perc(slippage_pct / 100.0)

        tf_str = self.timeframe_var.get()
        if tf_str == "Daily":
            timeframe_bt = bt.TimeFrame.Days
        elif tf_str == "Hourly":
            timeframe_bt = bt.TimeFrame.Minutes
        else:
            timeframe_bt = bt.TimeFrame.Minutes

        for symbol, df in self.dataframes.items():
            data_feed = bt.feeds.PandasData(dataname=df, timeframe=timeframe_bt)
            self.cerebro.adddata(data_feed, name=symbol)

        self.cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')
        self.cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
        self.cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='tradeanalyzer')

        strat_name = self.strategy_var.get()
        StratClass, params = self.get_strategy_and_params(strat_name)
        self.cerebro.addstrategy(StratClass, **params)

        self.append_text(f"Running backtest with {strat_name}...\n")
        results = self.cerebro.run()
        strat = results[0]

        sharpe_analyzer = strat.analyzers.sharpe.get_analysis()
        drawdown_analyzer = strat.analyzers.drawdown.get_analysis()
        trade_analyzer = strat.analyzers.tradeanalyzer.get_analysis()

        final_value = self.cerebro.broker.getvalue()
        self.append_text(f"Final Portfolio Value: {final_value:.2f}\n")
        if 'sharperatio' in sharpe_analyzer and sharpe_analyzer['sharperatio'] is not None:
            self.append_text(f"Sharpe Ratio: {sharpe_analyzer['sharperatio']:.2f}\n")
        self.append_text(f"Max DrawDown: {drawdown_analyzer.max.drawdown:.2f}%\n")
        self.append_text(f"DrawDown Duration: {drawdown_analyzer.max.len}\n")

        if 'total' in trade_analyzer and trade_analyzer.total.total != 0:
            total_trades = trade_analyzer.total.total
            won = trade_analyzer.won.total
            lost = trade_analyzer.lost.total
            pnl_net = trade_analyzer.pnl.net.total
            self.append_text(f"Total Trades: {total_trades}\n")
            self.append_text(f"Wins: {won}, Losses: {lost}\n")
            self.append_text(f"Net PnL: {pnl_net:.2f}\n")
        else:
            self.append_text("No trades were made.\n")

        if self.plot_choice_var.get() == "Separate Window":
            self.cerebro.plot(style='candlestick')
        else:
            self.fig.clear()
            plots = self.cerebro.plot(style='candlestick', iplot=False)
            for f, axs in plots:
                for ax in axs:
                    for name, _ax in ax.items():
                        new_ax = self.fig.add_subplot(111)
                        lines = _ax.get_lines()
                        for line in lines:
                            new_ax.plot(line.get_xdata(), line.get_ydata(), label=line.get_label())
                        new_ax.legend()
                        new_ax.set_title("Embedded Backtest Chart")
                        new_ax.grid()
            self.canvas.draw()

    def clear_data(self):
        self.dataframes.clear()
        self.append_text("Cleared all loaded data.\n")

    def append_text(self, text: str):
        self.text_area.insert(tk.END, text)
        self.text_area.see(tk.END)

    def open_param_window(self):
        strat_name = self.strategy_var.get()
        StratClass, current_params = self.get_strategy_and_params(strat_name)

        param_win = tk.Toplevel(self)
        param_win.title(f"{strat_name} Parameters")

        row = 0
        for k, v in current_params.items():
            ttk.Label(param_win, text=k).grid(row=row, column=0, padx=5, pady=5)
            var = tk.StringVar(value=str(v))
            e = ttk.Entry(param_win, textvariable=var)
            e.grid(row=row, column=1, padx=5, pady=5)
            self.strategy_params[k] = var
            row += 1

        ttk.Button(param_win, text="Close", command=param_win.destroy).grid(row=row, column=0, columnspan=2, pady=10)

    def get_strategy_and_params(self, strat_name):
        if strat_name == "SmaCross":
            StratClass = SmaCross
            default = dict(fast_period=10, slow_period=30, printlog=False)
        elif strat_name == "RsiStrategy":
            StratClass = RsiStrategy
            default = dict(rsi_period=14, rsi_lower=30, rsi_upper=70, printlog=False)
        elif strat_name == "SmaRsiCombo":
            StratClass = SmaRsiCombo
            default = dict(fast_period=10, slow_period=30, rsi_period=14, rsi_upper=70, rsi_lower=30, printlog=False)
        elif strat_name == "BollingerBandStrategy":
            StratClass = BollingerBandStrategy
            default = dict(period=20, devfactor=2.0, printlog=False)
        elif strat_name == "MACDStrategy":
            StratClass = MACDStrategy
            default = dict(fast_period=12, slow_period=26, signal_period=9, printlog=False)
        elif strat_name == "MyNewStrategy":
            StratClass = MyNewStrategy
            default = dict(stoch_period=14, stoch_d_period=3, sma_period=50, printlog=False)
        else:
            StratClass = SmaCross
            default = dict(fast_period=10, slow_period=30, printlog=False)

        final_params = {}
        for k, v in default.items():
            if k in self.strategy_params:
                try:
                    val_str = self.strategy_params[k].get()
                    if '.' in val_str:
                        final_params[k] = float(val_str)
                    else:
                        final_params[k] = int(val_str)
                except ValueError:
                    if val_str.lower() in ['true', 'false']:
                        final_params[k] = (val_str.lower() == 'true')
                    else:
                        final_params[k] = default[k]
            else:
                final_params[k] = default[k]

        return StratClass, final_params


if __name__ == "__main__":
    app = BacktestApp()
    app.mainloop()
