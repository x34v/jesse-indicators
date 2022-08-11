# Copyright 2022 - x34v@proton.me
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from dis import dis
import talib
import numpy as np
from typing import Union

from jesse.helpers import get_candle_source, slice_candles, np_shift
from jesse.indicators import sma, ema, alma, wma, smma, hma

# Jesse port of TrandingView ASHv2 by author jiehonglim
# https://www.tradingview.com/script/PORR7A3k-Absolute-Strength-Histogram-v2-jh/ 

def ash(candles: np.ndarray, evaluation_period: int = 9, smoothing_period: int = 3, method = "RSI", source_type="close", ma_type = "EMA", sigma: float = 6.0, distribution_offset: float = 0.85, sequential = False) -> Union[float, np.ndarray]:
    """
    Absolute Strength Histogram v2 
    :param candles: np.ndarray
    :param evaluation_period: int - default: 9
    :param smoothing_period: int - default: 3
    :param method: str - default: RSI
    :param source_type: str - default: close
    :param ma_type: str - default: EMA
    :param sigma: float - default: 6.0
    :param distribution_offset: float - default: 0.85
    :param sequential: bool - default: False
    :return: Union[float, np.ndarray]
    """
    candles = slice_candles(candles, sequential)

    bulls0, bears0 = prices_for_method(candles, evaluation_period, source_type, method)
    
    avg_bulls = ma(bulls0, type = ma_type, len = evaluation_period, sigma = sigma, distribution_offset=distribution_offset)
    avg_bears = ma(bears0, type = ma_type, len = evaluation_period, sigma = sigma, distribution_offset=distribution_offset)

    smth_bulls = ma(avg_bulls, ma_type, smoothing_period, sigma = sigma, distribution_offset=distribution_offset)
    smth_bears = ma(avg_bears, ma_type, smoothing_period, sigma = sigma, distribution_offset=distribution_offset)

    difference = abs(smth_bulls - smth_bears)

    trend_strength = "NEUTRAL"

    if difference[-1] > smth_bulls[-1]:
        if smth_bears[-1] < smth_bears[-2]:
            trend_strength = "LIGHT_DOWNTREND"
        else:
            trend_strength = "STRONG_DOWNTREND"
    elif difference[-1] > smth_bears[-1]:
        if smth_bulls[-1] < smth_bulls[-2]:
            trend_strength = "LIGHT_UPTREND"
        else:
            trend_strength = "STRONG_UPTREND"

    if sequential:
        return smth_bulls, smth_bears, trend_strength
    else:
        return smth_bulls[-1], smth_bears[-1], trend_strength

def ma(src: np.ndarray, type: str, len: int, sequential: bool = True, sigma: float = 6.0, distribution_offset: float = 0.85):
    result = 0.0
    
    if type == "SMA":
        result = sma(src, period=len, sequential=sequential)    
    elif type == "EMA":
        result = ema(src, period = len, sequential = sequential)
    elif type == "WMA":
        result = wma(src, period = len, sequential=sequential)
    elif type == "SMMA": 
        # WARNING: Jesse's SMMA indicator implementation does not yield the same result as TradingView's one.
        result = smma(src, period = len, sequential=sequential)
    elif type == "HMA":
        # WARNING: Jesse's HMA indicator implementation does not yield the same result as TradingView's one.
        result = hma(src, period = len, sequential=sequential)
    elif type == "ALMA":
        result = alma(src, period = len, sigma = sigma, distribution_offset = distribution_offset, sequential=sequential)
    else:
        raise ValueError(f"Invalid moving average type: {type}")

    return result

def prices_for_method(candles: np.ndarray, length: int, source_type="close", method = "RSI"): 
    src = get_candle_source(candles, source_type)

    price1 = src
    price2 = np_shift(src, 1)

    if method == "RSI":
        bulls = 0.5*(abs(price1-price2)+(price1-price2))
        bears = 0.5*(abs(price1-price2)-(price1-price2))
        return bulls, bears  
    elif method == "STOCHASTIC":
        lowest = talib.MIN(price1, length)   
        highest = talib.MAX(price1, length)
        bulls = price1 - lowest
        bears = highest - price1

        return bulls, bears
    elif method == "ADX":
        low = get_candle_source(candles, "low")
        high = get_candle_source(candles, "high")
        bulls = 0.5*(abs(high-np_shift(high, 1)) + (high - np_shift(high, 1)))
        bears = 0.5*(abs(np_shift(low, 1)-low) + (np_shift(low, 1)-low))
        return bulls, bears
    else:
        raise ValueError(f"Invalid method: {method}")

