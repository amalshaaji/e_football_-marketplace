from typing import Literal

from pydantic import BaseModel

from app.database.models import ListingStatus, ReportStatus


class ListingModeration(BaseModel):
    status: Literal["ACTIVE", "REJECTED"]


class ReportModeration(BaseModel):
    status: Literal["UNDER_REVIEW", "RESOLVED", "DISMISSED"]


class UserStatusUpdate(BaseModel):
    is_active: bool
