from datetime import datetime
from fastapi import Query
from pydantic import BaseModel, Field
from typing import Annotated, Literal, Optional

Symbols = Annotated[
    Literal["BA", "LMT", "ERJ"],
    Query(
        title="Company",
        description="Company to display.",
        json_schema_extra={
            "x-widget_config": {
                "options": [
                    {"label": "Boeing", "value": "BA"},
                    {"label": "Lockheed Martin", "value": "LMT"},
                    {"label": "Embraer", "value": "ERJ"},
                ],
            }
        },
    ),
]


class PriceActionData(BaseModel):
    """Model for price action data."""

    date: datetime = Field(description="The date and time of the interval.")
    open: float = Field(description="The opening price for the interval.")
    high: float = Field(description="The highest price for the interval.")
    low: float = Field(description="The lowest price for the interval.")
    close: float = Field(description="The closing price for the interval.")
    volume: int = Field(description="The trading volume during the interval.")
    vwap: float = Field(
        description="The volume-weighted average price during the interval.",
        title="VWAP",
    )
    transactions: int = Field(
        description="The number of transactions during the interval."
    )


class MarketsEqData(BaseModel):
    """Model for MarketsEq transcript analysis data."""

    ticker: str = Field(
        description="Company ticker symbol",
        title="Ticker",
        json_schema_extra={
            "x-widget_config": {
                "width": 100,
                "hide": True,
            }
        },
    )
    name_entity: str = Field(
        description="Name of the entity",
        title="Entity Name",
        json_schema_extra={
            "x-widget_config": {
                "width": 150,
                "hide": True,
            }
        },
    )
    factsetid: str = Field(
        description="FactSet identifier",
        title="FactSet ID",
        json_schema_extra={
            "x-widget_config": {
                "width": 120,
                "hide": True,
            }
        },
    )
    type_entity: str = Field(
        description="Type of entity",
        title="Entity Type",
        json_schema_extra={
            "x-widget_config": {
                "width": 120,
                "hide": True,
            }
        },
    )
    name_participant: str = Field(
        description="Name of the participant",
        title="Participant",
        json_schema_extra={
            "x-widget_config": {
                "width": 150,
                "pinned": "left",
            }
        },
    )
    title: str = Field(
        description="Participant's title",
        title="Title",
        json_schema_extra={
            "x-widget_config": {
                "width": 150,
                "hide": True,
            }
        },
    )
    type_participant: str = Field(
        description="Type of participant",
        title="Participant Type",
        json_schema_extra={
            "x-widget_config": {
                "width": 120,
            }
        },
    )
    event: str = Field(
        description="Period",
        title="Period",
        json_schema_extra={
            "x-widget_config": {
                "width": 150,
                "hide": True,
            }
        },
    )
    event_phase: str = Field(
        description="Phase of the event",
        title="Event Phase",
        json_schema_extra={
            "x-widget_config": {
                "width": 120,
            }
        },
    )
    timestamps_start: datetime = Field(
        description="Start timestamp of the segment",
        title="Start Time",
        json_schema_extra={
            "x-widget_config": {
                "width": 160,
            }
        },
    )
    timestamps_end: datetime = Field(
        description="End timestamp of the segment",
        title="End Time",
        json_schema_extra={
            "x-widget_config": {
                "width": 160,
            }
        },
    )
    transcription_value: str = Field(
        description="Transcribed text",
        title="Transcription",
        json_schema_extra={
            "x-widget_config": {
                "width": 300,
            }
        },
    )
    speaker_confidence: Optional[float] = Field(
        default=None,
        description="Confidence score for speaker identification",
        title="Speaker Confidence",
        json_schema_extra={
            "x-widget_config": {
                "width": 140,
            }
        },
    )
    transcription_confidence: Optional[float] = Field(
        default=None,
        description="Confidence score for transcription",
        title="Transcription Confidence",
        json_schema_extra={
            "x-widget_config": {
                "width": 140,
            }
        },
    )
    quality_snr: Optional[float] = Field(
        default=None,
        description="Signal-to-Noise Ratio",
        title="SNR",
        json_schema_extra={
            "x-widget_config": {
                "width": 100,
            }
        },
    )
    quality_rt60: Optional[float] = Field(
        default=None,
        description="Reverberation Time",
        title="RT60",
        json_schema_extra={
            "x-widget_config": {
                "width": 100,
            }
        },
    )
    angry: Optional[float] = Field(
        default=None,
        description="Anger emotion score",
        title="Angry",
        json_schema_extra={
            "x-widget_config": {
                "width": 100,
            }
        },
    )
    happy: Optional[float] = Field(
        default=None,
        description="Happiness emotion score",
        title="Happy",
        json_schema_extra={
            "x-widget_config": {
                "width": 100,
            }
        },
    )
    neutral: Optional[float] = Field(
        default=None,
        description="Neutral emotion score",
        title="Neutral",
        json_schema_extra={
            "x-widget_config": {
                "width": 100,
            }
        },
    )
    sad: Optional[float] = Field(
        default=None,
        description="Sadness emotion score",
        title="Sad",
        json_schema_extra={
            "x-widget_config": {
                "width": 100,
            }
        },
    )
    arousal: Optional[float] = Field(
        default=None,
        description="Emotional arousal level",
        title="Arousal",
        json_schema_extra={
            "x-widget_config": {
                "width": 100,
            }
        },
    )
    dominance: Optional[float] = Field(
        default=None,
        description="Dominance level in speech",
        title="Dominance",
        json_schema_extra={
            "x-widget_config": {
                "width": 100,
            }
        },
    )
    valence: Optional[float] = Field(
        default=None,
        description="Emotional valence score",
        title="Valence",
        json_schema_extra={
            "x-widget_config": {
                "width": 100,
            }
        },
    )
    f0_minimum: Optional[float] = Field(
        default=None,
        description="Minimum fundamental frequency",
        title="Min F0",
        json_schema_extra={
            "x-widget_config": {
                "width": 100,
            }
        },
    )
    f0_maximum: Optional[float] = Field(
        default=None,
        description="Maximum fundamental frequency",
        title="Max F0",
        json_schema_extra={
            "x-widget_config": {
                "width": 100,
            }
        },
    )
    f0_average: Optional[float] = Field(
        default=None,
        description="Average fundamental frequency",
        title="Avg F0",
        json_schema_extra={
            "x-widget_config": {
                "width": 100,
            }
        },
    )
    f0_variation: Optional[float] = Field(
        default=None,
        description="Variation in fundamental frequency",
        title="F0 Variation",
        json_schema_extra={
            "x-widget_config": {
                "width": 100,
            }
        },
    )
    loudness_minimum: Optional[float] = Field(
        default=None,
        description="Minimum loudness level",
        title="Min Loudness",
        json_schema_extra={
            "x-widget_config": {
                "width": 120,
            }
        },
    )
    loudness_maximum: Optional[float] = Field(
        default=None,
        description="Maximum loudness level",
        title="Max Loudness",
        json_schema_extra={
            "x-widget_config": {
                "width": 120,
            }
        },
    )
    loudness_average: Optional[float] = Field(
        default=None,
        description="Average loudness level",
        title="Avg Loudness",
        json_schema_extra={
            "x-widget_config": {
                "width": 120,
            }
        },
    )
    loudness_variation: Optional[float] = Field(
        default=None,
        description="Variation in loudness",
        title="Loudness Variation",
        json_schema_extra={
            "x-widget_config": {
                "width": 120,
            }
        },
    )
    speaking_rate: Optional[float] = Field(
        default=None,
        description="Rate of speech",
        title="Speaking Rate",
        json_schema_extra={
            "x-widget_config": {
                "width": 120,
            }
        },
    )
    speaking_rate_variation: Optional[float] = Field(
        default=None,
        description="Variation in speaking rate",
        title="Speaking Rate Var",
        json_schema_extra={
            "x-widget_config": {
                "width": 120,
            }
        },
    )
    intonation_score: Optional[float] = Field(
        default=None,
        description="Intonation score",
        title="Intonation",
        json_schema_extra={
            "x-widget_config": {
                "width": 100,
            }
        },
    )


class DeliveriesData(BaseModel):
    """Model for deliveries data."""

    period: str = Field(title="Period", alias="Period")
    four_twenty_two: int = Field(
        title="4-22",
        alias="4-22",
    )
    five_seven: int = Field(
        title="5-7",
        alias="5-7",
    )


class ProductionData(BaseModel):
    """Model for production data."""

    revision: str = Field(
        description="",
        json_schema_extra={"x-widget_config": {"chartDataType": "category"}},
        alias="Revision",
    )
    q1: int = Field(
        description="2025 Q1 production.",
        title="2025Q1",
        alias="2025Q1",
    )
    q2: int = Field(
        description="2025 Q2 production.",
        title="2025Q2",
        alias="2025Q2",
    )
    q3: int = Field(
        description="2025 Q3 production.",
        title="2025Q3",
        alias="2025Q3",
    )
    q4: int = Field(
        description="2025 Q4 production.",
        title="2025Q4",
        alias="2025Q4",
    )


class PriceTargetsData(BaseModel):
    """Model for price targets data."""

    date: str = Field(
        description="The date of publication.", alias="Date", title="Date"
    )
    analyst_name: Optional[str] = Field(
        default=None,
        description="Name of the analyst.",
        alias="Analyst Name",
        title="Analyst Name",
    )
    firm_name: str = Field(
        description="Name of the firm.",
        alias="Firm Name",
        title="Firm Name",
    )
    adjusted_price_target: Optional[float] = Field(
        default=None,
        description="Adjusted price target.",
        alias="Adjusted Price Target",
        title="Adjusted Price Target",
    )
    adjusted_previous_price_target: Optional[float] = Field(
        default=None,
        description="Adjusted previous price target.",
        alias="Adjusted Previous Price Target",
        title="Adjusted Previous Price Target",
    )
    rating_change: Optional[str] = Field(
        default=None,
        description="Rating change.",
        alias="Rating Change",
        title="Rating Change",
    )
    current_rating: Optional[str] = Field(
        default=None,
        description="Current rating.",
        alias="Current Rating",
        title="Current Rating",
    )
    previous_rating: Optional[str] = Field(
        default=None,
        description="Previous rating.",
        alias="Previous Rating",
        title="Previous Rating",
    )
