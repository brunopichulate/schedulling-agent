from pydantic import BaseModel, Field, TypeAdapter
from typing import Literal, Annotated


class TextContent(BaseModel):
  body: str


class ImageContent(BaseModel):
  id: str
  mime_type: str
  sha256: str
  caption: str | None = None


class StickerContent(BaseModel):
  id: str
  mime_type: str
  sha256: str
  animated: bool | None = None


class AudioContent(BaseModel):
  id: str
  mime_type: str
  sha256: str
  voice: bool | None = (
    None  # True if voice recording, False or None for audio files
  )


class VideoContent(BaseModel):
  id: str
  mime_type: str
  caption: str | None = None


class DocumentContent(BaseModel):
  id: str
  filename: str
  mime_type: str
  caption: str | None = None


class LocationContent(BaseModel):
  latitude: float
  longitude: float
  name: str | None = None
  address: str | None = None


class ButtonContent(BaseModel):
  text: str
  payload: str


class InteractiveContent(BaseModel):
  type: str  # "button_reply", "list_reply"
  button_reply: dict | None = None
  list_reply: dict | None = None


class ContactsContent(BaseModel):
  # Simplified - full schema is complex with many optional fields
  pass


class ReactionContent(BaseModel):
  message_id: str
  emoji: str | None = None


class OrderContent(BaseModel):
  # Simplified - full schema is complex
  pass


class SystemContent(BaseModel):
  # System messages like number changes, etc
  body: str | None = None
  type: str | None = None


# Separate model for each message type
class TextMessage(BaseModel):
  type: Literal["text"]
  from_: str = Field(alias="from")
  id: str
  timestamp: str
  text: TextContent


class ImageMessage(BaseModel):
  type: Literal["image"]
  from_: str = Field(alias="from")
  id: str
  timestamp: str
  image: ImageContent


class StickerMessage(BaseModel):
  type: Literal["sticker"]
  from_: str = Field(alias="from")
  id: str
  timestamp: str
  sticker: StickerContent


class AudioMessage(BaseModel):
  type: Literal["audio"]
  from_: str = Field(alias="from")
  id: str
  timestamp: str
  audio: AudioContent


class VideoMessage(BaseModel):
  type: Literal["video"]
  from_: str = Field(alias="from")
  id: str
  timestamp: str
  video: VideoContent


class DocumentMessage(BaseModel):
  type: Literal["document"]
  from_: str = Field(alias="from")
  id: str
  timestamp: str
  document: DocumentContent


class LocationMessage(BaseModel):
  type: Literal["location"]
  from_: str = Field(alias="from")
  id: str
  timestamp: str
  location: LocationContent


class ButtonMessage(BaseModel):
  type: Literal["button"]
  from_: str = Field(alias="from")
  id: str
  timestamp: str
  button: ButtonContent


class InteractiveMessage(BaseModel):
  type: Literal["interactive"]
  from_: str = Field(alias="from")
  id: str
  timestamp: str
  interactive: InteractiveContent


class UnsupportedMessage(BaseModel):
  """Catch-all for message types we don't handle: contacts, reaction, order, system, unsupported, etc."""

  type: Literal["contacts", "reaction", "order", "system", "unsupported"]
  from_: str = Field(alias="from")
  id: str
  timestamp: str
  # Keep the rest as generic dict since we won't process them
  contacts: list[dict] | None = None
  reaction: dict | None = None
  order: dict | None = None
  system: dict | None = None


# Discriminated union
WhatsAppMessage = Annotated[
  TextMessage
  | ImageMessage
  | StickerMessage
  | AudioMessage
  | VideoMessage
  | DocumentMessage
  | LocationMessage
  | ButtonMessage
  | InteractiveMessage
  | UnsupportedMessage,
  Field(discriminator="type"),
]

WhatsAppMessageAdapter = TypeAdapter(WhatsAppMessage)


# Webhook payload models
class Contact(BaseModel):
  profile: dict
  wa_id: str


class Metadata(BaseModel):
  display_phone_number: str
  phone_number_id: str


class Value(BaseModel):
  messaging_product: str
  metadata: Metadata
  contacts: list[Contact] | None = None
  messages: list[dict] | None = None  # Keep as dict for now


class Change(BaseModel):
  value: Value
  field: str


class Entry(BaseModel):
  id: str
  changes: list[Change]


class WhatsAppWebhook(BaseModel):
  object: str
  entry: list[Entry]
