from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_validator, model_validator

from src.models.catalog import ContentType


def slugify(value: str) -> str:
    value = "-".join(value.strip().lower().split())
    if not value or any(not (char.isalnum() or char == "-") for char in value):
        raise ValueError("slug may contain lowercase letters, numbers, and hyphens only")
    return value


class GenreBase(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    slug: str = Field(min_length=1, max_length=80)
    description: str | None = Field(default=None, max_length=255)

    _slug = field_validator("slug")(slugify)


class GenreCreate(GenreBase):
    pass


class GenreUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=80)
    slug: str | None = Field(default=None, min_length=1, max_length=80)
    description: str | None = Field(default=None, max_length=255)
    _slug = field_validator("slug")(slugify)


class GenreRead(GenreBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime


class PlatformBase(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    slug: str = Field(min_length=1, max_length=100)
    website_url: HttpUrl | None = None
    is_active: bool = True
    _slug = field_validator("slug")(slugify)


class PlatformCreate(PlatformBase):
    pass


class PlatformUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    slug: str | None = Field(default=None, min_length=1, max_length=100)
    website_url: HttpUrl | None = None
    is_active: bool | None = None
    _slug = field_validator("slug")(slugify)


class PlatformRead(PlatformBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime


class TitleBase(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    synopsis: str | None = Field(default=None, max_length=5000)
    content_type: ContentType
    release_year: int | None = Field(default=None, ge=1888, le=2100)
    maturity_rating: str | None = Field(default=None, max_length=20)
    runtime_minutes: int | None = Field(default=None, ge=1, le=1440)
    is_published: bool = False
    genre_ids: list[int] = Field(default_factory=list, max_length=20)
    platform_ids: list[int] = Field(default_factory=list, max_length=20)


class TitleCreate(TitleBase):
    pass


class TitleUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    synopsis: str | None = Field(default=None, max_length=5000)
    content_type: ContentType | None = None
    release_year: int | None = Field(default=None, ge=1888, le=2100)
    maturity_rating: str | None = Field(default=None, max_length=20)
    runtime_minutes: int | None = Field(default=None, ge=1, le=1440)
    is_published: bool | None = None
    genre_ids: list[int] | None = Field(default=None, max_length=20)
    platform_ids: list[int] | None = Field(default=None, max_length=20)


class TitleRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    synopsis: str | None
    content_type: ContentType
    release_year: int | None
    maturity_rating: str | None
    runtime_minutes: int | None
    is_published: bool
    created_at: datetime
    updated_at: datetime
    genres: list[GenreRead]
    platforms: list[PlatformRead]


class PageMeta(BaseModel):
    offset: int
    limit: int
    total: int


class TitlePage(BaseModel):
    data: list[TitleRead]
    meta: PageMeta


class WatchlistUpdate(BaseModel):
    is_favorite: bool


class WatchlistEntryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    is_favorite: bool
    created_at: datetime
    title: TitleRead


class WatchlistPage(BaseModel):
    data: list[WatchlistEntryRead]
    meta: PageMeta


class AvailabilityBase(BaseModel):
    platform_id: int = Field(gt=0)
    country_code: str = Field(min_length=2, max_length=2)
    provider_content_id: str | None = Field(default=None, max_length=255)
    url: HttpUrl
    available_from: datetime | None = None
    available_until: datetime | None = None

    @field_validator("country_code")
    @classmethod
    def normalize_country(cls, value: str) -> str:
        value = value.upper()
        if not value.isalpha():
            raise ValueError("country_code must be a two-letter ISO country code")
        return value

    @model_validator(mode="after")
    def validate_window(self):
        if self.available_from and self.available_until and self.available_until <= self.available_from:
            raise ValueError("available_until must be after available_from")
        return self


class AvailabilityCreate(AvailabilityBase):
    pass


class AvailabilityRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    country_code: str
    provider_content_id: str | None
    url: HttpUrl
    available_from: datetime | None
    available_until: datetime | None
    last_synced_at: datetime
    platform: PlatformRead
