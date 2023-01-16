import pandas as pd
from scipy.signal import firwin, filtfilt

def remove_eda_stream_artifacts(df_eda):
    #this method implements the method from https://www.nature.com/articles/s41746-018-0074-9
    fs_eda = 4
    min_eda_value = 0.035
    ratio_good_values = 0.9
    window_size_5sec = fs_eda * 5
    window_size_half_sec = int(fs_eda * 0.5)
    min_samples_above_threshold_5sec = ratio_good_values * window_size_5sec
    # sum_threshold_5sec = min_eda_value * ratio_good_values * window_size_5sec
    max_increased_eda_ratio = 1.2
    max_decreased_eda_ratio = 0.9
    # set abs values
    df_eda_abs = df_eda.abs()
    #######remove values below threshold
    # calculate rolling window (5 sec) sum
    print('Calculating rolling sum')
    df_eda_abs['eda_above_min_threashold'] = 0
    df_eda_abs.loc[df_eda_abs['eda'] > min_eda_value, 'eda_above_min_threashold'] = 1
    df_eda_abs['window_samples_above_threshold'] = df_eda_abs['eda_above_min_threashold'].rolling('5s').sum()
    # keep only values < max threshold
    df_eda_abs.loc[df_eda_abs['window_samples_above_threshold'] > min_samples_above_threshold_5sec,'eda_above_min_threashold'] = np.nan
    df_eda_abs['eda_above_min_threashold'].fillna(method = 'bfill', inplace = True, limit = window_size_5sec )
    #######remove values with increasing slope > 20%
    print('Removing values with increasing slope > 20%')
    df_eda_abs['eda_increased_from_previous_max'] = df_eda_abs.eda.shift()
    df_eda_abs['eda_increased_from_previous_max'] = df_eda_abs['eda_increased_from_previous_max'].multiply(
        max_increased_eda_ratio)
    df_eda_abs['eda_increased_above_threshold'] = df_eda_abs.eda - df_eda_abs.eda_increased_from_previous_max
    df_eda_abs.loc[df_eda_abs['eda_increased_above_threshold'] <= 0, 'eda_increased_above_threshold'] = np.nan
    df_eda_abs['eda_increased_above_threshold'].fillna(method='bfill', inplace=True, limit=window_size_half_sec)
    df_eda_abs['eda_increased_above_threshold'].fillna(method='ffill', inplace=True, limit=window_size_half_sec)
    #######remove values with decrease slope > 10%
    print('Removing values with decreasing slope > 10%')
    df_eda_abs['eda_decreased_from_previous_max'] = df_eda_abs.eda.shift()
    df_eda_abs['eda_decreased_from_previous_max'] = df_eda_abs['eda_decreased_from_previous_max'].multiply(
        max_decreased_eda_ratio)
    df_eda_abs['eda_decreased_above_threshold'] = df_eda_abs.eda - df_eda_abs.eda_decreased_from_previous_max
    df_eda_abs.loc[df_eda_abs['eda_decreased_above_threshold'] >= 0, 'eda_decreased_above_threshold'] = np.nan
    df_eda_abs['eda_decreased_above_threshold'].fillna(method='bfill', inplace=True, limit=window_size_half_sec)
    df_eda_abs['eda_decreased_above_threshold'].fillna(method='ffill', inplace=True, limit=window_size_half_sec)
    ####keep clean signal####
    df_eda_clean_signal = df_eda_abs.loc[
            (df_eda_abs.eda_decreased_above_threshold.isna()) & (df_eda_abs.eda_increased_above_threshold.isna()) & (
                df_eda_abs.eda_above_min_threashold.isna())]
    df_eda_clean_signal_eda_column = df_eda_clean_signal[['eda']]
    print('finished slicing EDA column')
    return df_eda_clean_signal_eda_column

def apply_low_pass_fir_filtfilt(df, sampl_freq, signal):
    highcut_hz = 1
    N = 64
    # fs_eda = int(1000000 / ((df.index[1] - df.index[0]).microseconds))#identify signal sampling freq from content
    h = firwin(N, highcut_hz, fs = sampl_freq, pass_zero = 'lowpass')
    df_out = filtfilt(h, [1.0], df.values)
    return pd.DataFrame(df_out, index=df.index, columns = [signal])


def main():


if __name__ == "__main__":
    main()