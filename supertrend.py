# Copyright 2022 - x34v
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
import talib
import numpy as np
from typing import Union

from .truerange import atr, truerange
from jesse.indicators import sma
from jesse.helpers import get_candle_source, slice_candles, np_shift, np_ffill

def supertrend(candles: np.ndarray, period: int = 21, multiplier: float = 3.0, source_type="close", change_atr: bool = True, sequential: bool = False) -> Union[float, np.ndarray]:
    """
    SupertTrend by author Kinvanc Ozbilic
    :param candles: np.ndarray
    :param period: int - default: 21
    :param multiplier: float - default: 3.0
    :param source_type: string - default: "close"
    :param change_atr: bool - default: True
    :param sequential: bool - default: False
    :return: Union[float, np.ndarray]
    """
    candles = slice_candles(candles, sequential)
    close = get_candle_source(candles, "close")
    src = get_candle_source(candles, source_type)

    _atr = atr(candles, period, True) if change_atr else sma(truerange(candles), period, True)
    
    up_before = src - multiplier*_atr
    dn_before = src + multiplier*_atr
    up1 = np.full(up_before.shape, np.nan)
    dn1 = np.full(up_before.shape, np.nan)
    st = np.full(up_before.shape, np.nan)
    st_up = np.full(up_before.shape, np.nan)
    st_dn = np.full(dn_before.shape, np.nan)
    trend = np.full(dn_before.shape, np.nan)

    for index, value in np.ndenumerate(src):
        i = index[0]

        if i < period-1:
            continue
        elif i == period-1:
            up1[i] = up_before[i]
            dn1[i] = dn_before[i]
            trend[i] = 1
        else:
            up1[i] = st_up[i-1]
            dn1[i] = st_dn[i-1]

            if trend[i-1] == -1 and src[i] > dn1[i]:
                trend[i] = 1
            elif trend[i-1] == 1 and src[i] < up1[i]:
                trend[i] = -1
            else:
                trend[i] = trend[i-1]
        
        st_up[i] = stu(i, src, up1, up_before)
        st_dn[i] = std(i, src, dn1, dn_before)

        if trend[i] == 1:
            st[i] = st_up[i]
        elif trend[i] == -1:
            st[i] = st_dn[i]

    if sequential:
        return st, trend, trend[-1] != trend[-2]
    else:
        return st[-1], trend[-1], trend[-1] != trend[-2]
    

def stu(i: int, src: np.ndarray, up1: np.ndarray, up_before: np.ndarray):
    if src[i-1] > up1[i]:
        return max(up1[i], up_before[i])
    else:
        return up_before[i]
    
def std(i: int, src: np.ndarray, dn1: np.ndarray, dn_before: np.ndarray):
    if src[i-1] < dn1[i]:
        return min(dn1[i], dn_before[i])
    else:
        return dn_before[i]
