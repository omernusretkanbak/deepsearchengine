from pydantic import BaseModel, field_validator, Field
from enum import Enum
from typing import List


class SafetyCategory(str, Enum):
    SAFE_AND_EDUCATIONAL           = "SAFE_AND_EDUCATIONAL"
    DEVELOPMENTALLY_HARMFUL        = "DEVELOPMENTALLY_HARMFUL"
    RELIGIOUS_OR_POLITICAL         = "RELIGIOUS_OR_POLITICAL"
    SEXUALLY_SUGGESTIVE            = "SEXUALLY_SUGGESTIVE"
    SUBSTANCE_ABUSE_OR_ASSOCIATION = "SUBSTANCE_ABUSE_OR_ASSOCIATION"
    EXCESSIVE_VIOLENCE             = "EXCESSIVE_VIOLENCE"


class ParentalTrust(str, Enum):
    HIGH       = "HIGH"
    MEDIUM     = "MEDIUM"
    LOW        = "LOW"
    DO_NOT_USE = "DO_NOT_USE"


class MacroTrend(BaseModel):
    video_format:        str
    view_volume_estimate: str
    why_it_works:        str


class SearchResult(BaseModel):
    title:                    str
    url:                      str
    summary:                  str
    key_metrics:              str
    content_safety_category:  SafetyCategory
    parental_trust_potential: ParentalTrust
    niche_recommendation_value: str
    tags:                     list[str]
    server_debug_snapshot:    str = Field(default="N/A", description="Server Playwright Literal text")

    @field_validator("content_safety_category", "parental_trust_potential", mode="before")
    @classmethod
    def normalize_enums(cls, v: str) -> str:
        if isinstance(v, str):
            # "Safe and Educational" -> "SAFE_AND_EDUCATIONAL"
            return v.upper().replace(" ", "_").replace("-", "_")
        return v



class AutomationMetadata(BaseModel):
    execution_time_seconds: float
    model_used:             str


class Scene(BaseModel):
    scene_number:        int   = Field(description="Sequential scene number")
    start_timestamp_sec: int   = Field(description="Start time of the scene in seconds (e.g. 0)")
    end_timestamp_sec:   int   = Field(description="End time of the scene in seconds (e.g. 5)")
    video_prompt:        str   = Field(description="Prompt for Luma/Runway to animate this exact scene")
    voiceover_text:      str   = Field(description="Clean English speech text to be narrated during this scene")

class ProductionPrompts(BaseModel):
    hero_concept:        str           = Field(default="", description="English. Ethical hero concept (healthy foods, etc.)")
    image_anchor_prompt: str           = Field(default="", description="Universal AI prompt for the main character/anchor image. 9:16 vertical.")
    scenes:              list[Scene]   = Field(default_factory=list, description="Array of scenes for automated N8N looping and assembly")


class DeepSearchOutput(BaseModel):
    research_topic:           str
    macro_trends_4_to_12_age: list[MacroTrend]
    results:                  list[SearchResult]
    strategic_consulting_tr:  str = Field(default="", description="Turkish ethical strategy text")
    production_prompts_en:    ProductionPrompts = Field(default_factory=lambda: ProductionPrompts(), description="English nested AI prompts object")
    automation_metadata:      AutomationMetadata
