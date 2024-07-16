from typing import List, Dict, Optional, Any, Union
from pydantic import BaseModel, Field, root_validator

class EpubDCMetadata(BaseModel):
    title: Optional[str] = Field(None, alias="title")
    language: Optional[str] = Field(None, alias="language")
    identifier: Optional[str] = Field(None, alias="identifier")
    publisher: Optional[str] = Field(None, alias="publisher")
    date: Optional[str] = Field(None, alias="date")
    subject: Optional[List[str]] = Field(None, alias="subject")
    description: Optional[str] = Field(None, alias="description")
    rights: Optional[str] = Field(None, alias="rights")
    coverImage: Optional[str] = Field(None, alias="coverImage")
    uuid: Optional[str] = Field(None, alias="uuid")
    contributor: Optional[str] = Field(None, alias="contributor")
    source: Optional[str] = Field(None, alias="source")
    type: Optional[str] = Field(None, alias="type")
    format: Optional[str] = Field(None, alias="format")
    relation: Optional[str] = Field(None, alias="relation")
    coverage: Optional[str] = Field(None, alias="coverage")
    creator: Optional[str] = Field(None, alias="creator")
    languageTerms: Optional[str] = Field(None, alias="languageTerms")
    modified: Optional[str] = Field(None, alias="modified")
    direction: Optional[str] = Field(None, alias="direction")
    renditionLayout: Optional[str] = Field(None, alias="renditionLayout")
    renditionOrientation: Optional[str] = Field(None, alias="renditionOrientation")
    renditionSpread: Optional[str] = Field(None, alias="renditionSpread")
    renditionViewport: Optional[str] = Field(None, alias="renditionViewport")
    renditionFlow: Optional[str] = Field(None, alias="renditionFlow")
    renditionScript: Optional[str] = Field(None, alias="renditionScript")
    renditionContent: Optional[str] = Field(None, alias="renditionContent")
    alternateScript: Optional[str] = Field(None, alias="alternateScript")
    primaryIdentifier: Optional[str] = Field(None, alias="primaryIdentifier")
    belongsToCollection: Optional[str] = Field(None, alias="belongsToCollection")
    accessibilitySummary: Optional[str] = Field(None, alias="accessibilitySummary")
    groupPosition: Optional[str] = Field(None, alias="groupPosition")
    renditionManifest: Optional[str] = Field(None, alias="renditionManifest")
    readingProgression: Optional[str] = Field(None, alias="readingProgression")
    accessibilityMode: Optional[str] = Field(None, alias="accessibilityMode")
    accessibilityFeature: Optional[str] = Field(None, alias="accessibilityFeature")
    accessibilityHazard: Optional[str] = Field(None, alias="accessibilityHazard")
    accessibilitySummaryLink: Optional[str] = Field(None, alias="accessibilitySummaryLink")
    displayOptionsPlatform: Optional[str] = Field(None, alias="displayOptionsPlatform")
    fixedLayout: Optional[str] = Field(None, alias="fixedLayout")
    openToSpread: Optional[str] = Field(None, alias="openToSpread")
    pageProgressionDirection: Optional[str] = Field(None, alias="pageProgressionDirection")
    sourceDescriptions: Optional[str] = Field(None, alias="sourceDescriptions")
    other_metadata: Optional[str] = Field(None, alias="other_metadata")
    
    class Config:
        extra = "allow"

    @root_validator(pre=True)
    def check_extra_fields(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        extra_fields = set(values) - set(cls.__fields__.keys())
        if extra_fields:
            print(f"Unknown fields encountered: {extra_fields}")
        return values

# from typing import List, Dict, Optional, Any, Union
# from pydantic import BaseModel, Field, root_validator
#
# class EpubDCMetadata(BaseModel):
#     title: Optional[str] = Field(None, alias="title")
#     language: Optional[str] = Field(None, alias="language")
#     identifiers: Optional[Dict[str, str]] = Field(None, alias="identifier")
#     publisher: Optional[str] = Field(None, alias="publisher")
#     publication_date: Optional[str] = Field(None, alias="date")
#     subjects: Optional[List[str]] = Field(None, alias="subject")
#     description: Optional[str] = Field(None, alias="description")
#     rights: Optional[str] = Field(None, alias="rights")
#     cover_image: Optional[str] = Field(None, alias="coverImage")
#     uuid: Optional[str] = Field(None, alias="uuid")
#     contributors: Optional[List[str]] = Field(None, alias="contributor")
#     source: Optional[str] = Field(None, alias="source")
#     type: Optional[str] = Field(None, alias="type")
#     format: Optional[str] = Field(None, alias="format")
#     relation: Optional[str] = Field(None, alias="relation")
#     coverage: Optional[str] = Field(None, alias="coverage")
#     creator: Optional[Union[str, Dict[str, str]]] = Field(None, alias="creator")
#     date: Optional[str] = Field(None, alias="date")
#     language_terms: Optional[str] = Field(None, alias="languageTerms")
#     modified: Optional[str] = Field(None, alias="modified")
#     direction: Optional[str] = Field(None, alias="direction")
#     rendition_layout: Optional[str] = Field(None, alias="renditionLayout")
#     rendition_orientation: Optional[str] = Field(None, alias="renditionOrientation")
#     rendition_spread: Optional[str] = Field(None, alias="renditionSpread")
#     rendition_viewport: Optional[str] = Field(None, alias="renditionViewport")
#     rendition_flow: Optional[str] = Field(None, alias="renditionFlow")
#     rendition_script: Optional[str] = Field(None, alias="renditionScript")
#     rendition_content: Optional[str] = Field(None, alias="renditionContent")
#     alternate_script: Optional[str] = Field(None, alias="alternateScript")
#     primary_identifier: Optional[str] = Field(None, alias="primaryIdentifier")
#     belongs_to_collection: Optional[str] = Field(None, alias="belongsToCollection")
#     accessibility_summary: Optional[str] = Field(None, alias="accessibilitySummary")
#     group_position: Optional[str] = Field(None, alias="groupPosition")
#     rendition_manifest: Optional[str] = Field(None, alias="renditionManifest")
#     reading_progression: Optional[str] = Field(None, alias="readingProgression")
#     accessibility_mode: Optional[str] = Field(None, alias="accessibilityMode")
#     accessibility_feature: Optional[str] = Field(None, alias="accessibilityFeature")
#     accessibility_hazard: Optional[str] = Field(None, alias="accessibilityHazard")
#     accessibility_summary_link: Optional[str] = Field(None, alias="accessibilitySummaryLink")
#     display_options_platform: Optional[str] = Field(None, alias="displayOptionsPlatform")
#     fixed_layout: Optional[str] = Field(None, alias="fixedLayout")
#     open_to_spread: Optional[str] = Field(None, alias="openToSpread")
#     page_progression_direction: Optional[str] = Field(None, alias="pageProgressionDirection")
#     source_descriptions: Optional[str] = Field(None, alias="sourceDescriptions")
#     other_metadata: Optional[Dict[str, str]] = None
#
#     class Config:
#         extra = "allow"
#
#     @root_validator(pre=True)
#     def check_extra_fields(cls, values: Dict[str, Any]) -> Dict[str, Any]:
#         extra_fields = set(values) - set(cls.__fields__.keys())
#         if extra_fields:
#             print(f"Unknown fields encountered: {extra_fields}")
#         return values


# from typing import List, Dict, Optional, Any
# from pydantic import BaseModel, Field, root_validator
#
# class EpubDCMetadata(BaseModel):
#     title: Optional[str] = Field(None, alias="dc:title")
#     authors: Optional[List[str]] = Field(None, alias="dc:authors")
#     language: Optional[str] = Field(None, alias="dc:language")
#     identifiers: Optional[Dict[str, str]] = Field(None, alias="dc:identifier")
#     publisher: Optional[str] = Field(None, alias="dc:publisher")
#     publication_date: Optional[str] = Field(None, alias="dc:date")
#     subjects: Optional[List[str]] = Field(None, alias="dc:subject")
#     description: Optional[str] = Field(None, alias="dc:description")
#     rights: Optional[str] = Field(None, alias="dc:rights")
#     cover_image: Optional[str] = Field(None, alias="dc:coverImage")
#     uuid: Optional[str] = Field(None, alias="dc:uuid")
#     contributors: Optional[List[str]] = Field(None, alias="dc:contributor")
#     source: Optional[str] = Field(None, alias="dc:source")
#     type: Optional[str] = Field(None, alias="dc:type")
#     format: Optional[str] = Field(None, alias="dc:format")
#     relation: Optional[str] = Field(None, alias="dc:relation")
#     coverage: Optional[str] = Field(None, alias="dc:coverage")
#     creator: Optional[str] = Field(None, alias="dc:creator")
#     date: Optional[str] = Field(None, alias="dc:date")
#     language_terms: Optional[str] = Field(None, alias="dc:languageTerms")
#     modified: Optional[str] = Field(None, alias="dc:modified")
#     direction: Optional[str] = Field(None, alias="dc:direction")
#     rendition_layout: Optional[str] = Field(None, alias="dc:renditionLayout")
#     rendition_orientation: Optional[str] = Field(None, alias="dc:renditionOrientation")
#     rendition_spread: Optional[str] = Field(None, alias="dc:renditionSpread")
#     rendition_viewport: Optional[str] = Field(None, alias="dc:renditionViewport")
#     rendition_flow: Optional[str] = Field(None, alias="dc:renditionFlow")
#     rendition_script: Optional[str] = Field(None, alias="dc:renditionScript")
#     rendition_content: Optional[str] = Field(None, alias="dc:renditionContent")
#     alternate_script: Optional[str] = Field(None, alias="dc:alternateScript")
#     primary_identifier: Optional[str] = Field(None, alias="dc:primaryIdentifier")
#     belongs_to_collection: Optional[str] = Field(None, alias="dc:belongsToCollection")
#     accessibility_summary: Optional[str] = Field(None, alias="dc:accessibilitySummary")
#     group_position: Optional[str] = Field(None, alias="dc:groupPosition")
#     rendition_manifest: Optional[str] = Field(None, alias="dc:renditionManifest")
#     reading_progression: Optional[str] = Field(None, alias="dc:readingProgression")
#     accessibility_mode: Optional[str] = Field(None, alias="dc:accessibilityMode")
#     accessibility_feature: Optional[str] = Field(None, alias="dc:accessibilityFeature")
#     accessibility_hazard: Optional[str] = Field(None, alias="dc:accessibilityHazard")
#     accessibility_summary_link: Optional[str] = Field(None, alias="dc:accessibilitySummaryLink")
#     display_options_platform: Optional[str] = Field(None, alias="dc:displayOptionsPlatform")
#     fixed_layout: Optional[str] = Field(None, alias="dc:fixedLayout")
#     open_to_spread: Optional[str] = Field(None, alias="dc:openToSpread")
#     page_progression_direction: Optional[str] = Field(None, alias="dc:pageProgressionDirection")
#     source_descriptions: Optional[str] = Field(None, alias="dc:sourceDescriptions")
#     other_metadata: Optional[Dict[str, str]] = None
#
#     class Config:
#         extra = "allow"
#
#     @root_validator(pre=True)
#     def check_extra_fields(cls, values: Dict[str, Any]) -> Dict[str, Any]:
#         extra_fields = set(values) - set(cls.__fields__.keys())
#         if extra_fields:
#             print(f"Unknown fields encountered: {extra_fields}")
#         return values
#
