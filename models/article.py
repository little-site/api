from mongoengine.fields import (
    StringField,
    BooleanField,
    IntField,
    UUIDField
)
import uuid
from markdown import markdown as HTML_from_markdown
from slugify import slugify

from models.base import Base


class Article(Base):
    title = StringField(max_length=512, min_length=1, required=True)
    content = StringField(min_length=1, required=True)
    html_content = StringField()
    published = BooleanField(default=False)
    shared = BooleanField(default=False)
    love_count = IntField(default=0)
    read_count = IntField(default=0)
    share_handle = UUIDField(default=uuid.uuid4)
    slug = StringField(
        min_length=1, max_length=256, required=True, unique=True)

    meta = {
        "indexes": ["share_handle", "slug"]
    }

    # MARK - Private methods

    def _generate_html(self):
        self.html_content = HTML_from_markdown(
            self.content, extensions=["fenced_code"]
        )

    def _increment_count(self, key, factor):
        if key == "love":
            self.love_count += factor
        elif key == "read":
            self.read_count += factor

    def _generate_slug(self):
        """
        Generate the unique, URL-safe "slug" (human-friendly identifier)
        """
        self.slug = slugify(self.title)[:256]

    # MARK - Public methods

    def increment_love_count(self, factor=1):
        # Increments the love counter when an Article is loved
        self._increment_count("love", factor)

    def increment_read_count(self, factor=1):
        # Increments the read counter when an Article is read
        self._increment_count("read", factor)

    def save(self, *args, **kwargs):
        # Runs some tasks that always have to be run when saved
        if self.slug is None:
            self._generate_slug()

        self._generate_html()

        # Run normal mongoengine save method
        super(Article, self).save(*args, **kwargs)
