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
import numpy as np
from jesse.helpers import get_candle_source, np_shift
from .rma import rma

def atr(candles: np.ndarray, length: int = 14, sequential: bool = False):
    """
    Average True Range as computed by TradingView
    :param candles: np.ndarray
    :param length: int - default: 14
    :param sequential: bool - default: False
    :return: the ATR
    """
    tr = truerange(candles, True, True)
    return rma(tr, length, sequential)

def truerange(candles: np.ndarray, handle_na: bool = False, sequential: bool = False):
    """
    True Range as computed by TradingView
    :param candles: np.ndarray
    :param handle_na: bool - default: False
    :param sequential: bool - default: False
    :return: the TR
    """
    low = get_candle_source(candles, "low")
    high = get_candle_source(candles, "high")
    close = get_candle_source(candles, "close")
    shifted_close = np_shift(close, 1)
    tr0 = np.maximum(high - low, np.abs(high - shifted_close))
    res = np.maximum(tr0, np.abs(low - shifted_close))

    if (not handle_na):
        res[0] = np.nan
    else:
        res[0] = high[0] - low[0]

    if sequential:
        return res
    else:
        return res[-1]