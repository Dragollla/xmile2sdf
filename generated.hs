module Model(
    stocks,
    flows,
    dt,
    start,
    stop
) where

import           Xmile

start :: Num
start = 0.0

stop :: Num
stop = 30.0

dt :: Num
dt = 0.125

flows :: [Flow]
flows = (Flow "Heat Loss to Room" (\s dt -> changeStockAmount s (amount s + dt * ((180-70)/10)):[]

stocks :: [Stock]
stocks = (Stock "Teacup Temperature" 180 [] ["Heat Loss to Room"]):[]

