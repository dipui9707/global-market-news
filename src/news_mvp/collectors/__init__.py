from news_mvp.collectors.base import ArticlePayload, BaseCollector
from news_mvp.collectors.bls import BLSCollector
from news_mvp.collectors.federal_reserve import FederalReserveCollector
from news_mvp.collectors.media_rss import (
    AIHOTCollector,
    AxiosCollector,
    BloombergCollector,
    CNBCCollector,
    CNNCollector,
    CoinDeskCollector,
    FreightWavesCollector,
    FTCollector,
    InvestingCommoditiesCollector,
    MarketWatchCollector,
    MiningDotComCollector,
    OilPriceCollector,
    SeekingAlphaCollector,
    TechCrunchAICollector,
    VentureBeatAICollector,
    WesternProducerCollector,
    WSJCollector,
    YahooFinanceCollector,
)
from news_mvp.collectors.mktnews import MktNewsCollector
from news_mvp.collectors.reuters import ReutersCollector

__all__ = [
    "ArticlePayload",
    "BaseCollector",
    "AIHOTCollector",
    "ReutersCollector",
    "FederalReserveCollector",
    "BLSCollector",
    "BloombergCollector",
    "CNBCCollector",
    "CNNCollector",
    "WSJCollector",
    "FTCollector",
    "YahooFinanceCollector",
    "AxiosCollector",
    "VentureBeatAICollector",
    "TechCrunchAICollector",
    "OilPriceCollector",
    "MiningDotComCollector",
    "WesternProducerCollector",
    "MarketWatchCollector",
    "FreightWavesCollector",
    "SeekingAlphaCollector",
    "InvestingCommoditiesCollector",
    "CoinDeskCollector",
    "MktNewsCollector",
]
