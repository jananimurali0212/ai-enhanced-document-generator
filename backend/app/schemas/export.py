from typing import Optional, Dict, Any, Union
from pydantic import BaseModel, Field, model_validator

class ExportRequest(BaseModel):
    document_id: Optional[str] = Field(None, description="UUID of saved document to export")
    title: Optional[str] = Field(None, max_length=500, description="Title for raw content export")
    content: Optional[Union[str, Dict[str, Any]]] = Field(None, description="Raw content for export")
    document_type: Optional[str] = Field("General Document", description="Document type")

    @model_validator(mode="after")
    def validate_document_or_content(self):
        if not self.document_id and not self.content:
            raise ValueError("Either 'document_id' or 'content' must be provided for export.")
        return self
