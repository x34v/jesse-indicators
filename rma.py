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

# Jesse port of PineScript RMA function. 
# Jesse's RMA in the indicators collection does not yield the same results as PineScript's.

import talib
import numpy as np

def na(x: float):
    return np.isnan(x)

def nz(x: float):
    if na(x):
        return 0
    else:
        return x

def rma(src: np.ndarray, length: int = 14, sequential: bool = False):
    """
    RSI Moving Average as computed by TradingView
    :param src: np.ndarray
    :param length: int - default: 14
    :param sequential: bool - default: False
    :return: the RMA
    """
    alpha = 1.0/length

    res = np.full(src.shape, np.nan)

    _sma = talib.SMA(src, length)

    for index, value in np.ndenumerate(src):
        if index == 0:
            continue
        elif na(res[index[0]-1]):
            res[index] = _sma[index]
        else:
            res[index] = alpha * value + (1-alpha)*nz(res[index[0]-1])
    
    if sequential:
        return res
    else:
        return res[-1]