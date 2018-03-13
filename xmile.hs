module Xmile(
    Flow,
    Stock,
    Aux,
    changeStockAmount
) where

    data Flow = Flow {
        name :: String,
        eqn  :: (Stock -> Num -> [Stock] -> Stock)
    } deriving (Show)

    data Stock = Stock {
        name     :: String,
        amount   :: Num,
        inflows  :: [String],
        outflows :: [String]
    } deriving (Show)

    data Aux = Aux {
        name :: String,
        eqn  :: Num
    } deriving (Show)

    changeStockAmount :: Stock -> Num -> Stock
    changeStockAmount s a = Stock (name s) a (inflows s) (outflows s)
