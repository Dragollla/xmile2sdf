module Model(
    stocks,
    flows,
    dt,
    start,
    stop
) where

import           Xmile

stocks :: [Stock]
stocks = (Stock "Teacup Temperature" 180 [] ["Heat Loss to Room"]):[]

flows :: [Flow]
flows = (Flow "Heat Loss to Room" (\s dt -> changeStockAmount s (amount s + dt * (- 70 / 10)))):[]

start :: Num
start = 0

stop :: Num
stop = 30

dt :: Num
dt = 0.125
