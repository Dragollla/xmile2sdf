module Main where

    --import Xmile
    --import Model

    step :: [Stock] -> [Flow] -> [Stock]
    step stocks flows = map (calc flows) stocks

    calc :: [Flows] -> Stock -> Stock
    calc flows stock = (find (\f -> any (\i -> name f == i) inflows) flows) stock dt

    prompt s = do
        putStr s
        line <- getLine
        return (read line)

    main = iterate step stocks flows !! (stop - start / dt)
