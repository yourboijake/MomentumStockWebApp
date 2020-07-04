import yfinance as yf
import pandas as pd
import statistics as st

#get tickers for all NYSE, NASDAQ, and AMEX stocks
tick_df = pd.read_excel("US-Stock-Symbols.xlsx")
tickers = list(tick_df["Symbol"])

# get monthly price data for the last 12 months,
# and compute cumulative, mean, and risk-adj returns
met_df = pd.DataFrame(columns=['Ticker', 'Mean_Ret', 'Cum_Ret', 'Risk-Adj_Ret'])

missing = 0
for i in range(100):
    # retrieve data
    try:
        raw_info = yf.Ticker(tickers[i])
        raw_data = raw_info.history(period="1y", interval="1wk", actions=False)
        raw_data = raw_data.dropna()
    except:
        missing += 1

    if raw_data.empty == False and len(raw_data.index) >= 51:
        # compute monthly return values, and get mean, cumulative, and risk-adj vals
        rets = [raw_data.iloc[j + 1][4] / raw_data.iloc[j][4] - 1 for j in range(50)]
        ret_mean = st.mean(rets)
        ret_cum = sum(rets)
        ret_radj = ret_mean / st.stdev(rets)

        # append to main dataframe
        met_df = met_df.append(
            {'Ticker': tickers[i], 'Mean_Ret': ret_mean, 'Cum_Ret': ret_cum, 'Risk-Adj_Ret': ret_radj},
            ignore_index=True)

print(missing)
#cleans dataframe
met_df = met_df.dropna()

#outputs CSV for use in app.py
met_df = met_df.sort_values(by=['Risk-Adj_Ret'], ascending = False)
met_df_radj = met_df
met_df.to_csv("main_data.csv")

met_df.set_index(['Ticker'], inplace=True)

#creates sorted list for top and bottom stocks by
#risk-adjusted return, mean return, and cumulative return
met_df_mean = met_df.sort_values(by=['Mean_Ret'], ascending = False)
met_df_cum = met_df.sort_values(by=['Cum_Ret'], ascending = False)

#gets top and bottom 10 for each of the filter criteria
top_radj = met_df_radj.iloc[0:10, 1:]
bottom_radj = met_df_radj.iloc[-10:len(met_df), 1:]
top_mean = met_df_mean.iloc[0:10, 1:]
bottom_mean = met_df_mean.iloc[-10:len(met_df), 1:]
top_cum = met_df_cum.iloc[0:10, 1:]
bottom_cum = met_df_cum.iloc[-10:len(met_df), 1:]

#compiles the top and bottom 10 into one dataframe, and exports as csv file
chart_df = pd.concat([top_radj, bottom_radj, top_mean, bottom_mean, top_cum, bottom_cum])
chart_df.to_csv("chart_data.csv")
